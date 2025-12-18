import inspect
import time
from html import unescape
from logging import debug, error, info, warning
from typing import Any, Dict, List, Optional, Tuple

from eveo7_mumbleserver_ice import ServerUpdatingAuthenticator, UserInfo
from prometheus_client import Enum, Summary

from .db import ConnectionPoolDB
from .decorators import check_secret, fortify_ice
from .mixin_avatarcache import AvatarCacheMixin
from .mixin_dataaccess import DataAccessMixin
from .mixin_idconversion import IDConversionMixin
from .password import allianceauth_check_hash
from .state import (
    AuthenticationState,
    GetInfoState,
    IdToNameState,
    IdToTextureState,
    NameToIdState,
    RegisterUserState,
    SetInfoState,
    SetTextureState,
    UnregisterUserState,
)

USER_AUTHENTICATION_STATE = Enum(
    "user_authentication_state",
    "Authentication state of users",
    labelnames=["username"],
    states=["success", "failure", "fallthrough", "temporarily"],
)

USER_AUTHENTICATION_LATENCY = Summary(
    "user_authentication_latency",
    "Time taken to authenticate users",
)


class Authenticator(
    ServerUpdatingAuthenticator, IDConversionMixin, DataAccessMixin, AvatarCacheMixin
):
    def __init__(self, cfg: Dict[str, Any], db: ConnectionPoolDB):
        super().__init__()
        DataAccessMixin.__init__(self, db=db)
        IDConversionMixin.__init__(self, base_offset=cfg["user"]["id_offset"])
        AvatarCacheMixin.__init__(
            self,
            cache_dir=cfg["avatar"]["cache_dir"],
            cache_ttl=cfg["avatar"]["cache_ttl"],
            cache_max_size=cfg["avatar"]["cache_max_size"],
            cache_max_age=cfg["avatar"]["cache_max_age"],
            url_template=cfg["avatar"]["url"],
        )
        self.db = db
        self.cfg = cfg
        self._decorate_methods()

    def _decorate_methods(self) -> None:
        """
        Decorates class methods with security checks and fallback return values.
        """
        secret = self.cfg["ice_server"]["secret"]
        fallback_results = {
            "authenticate": (
                (AuthenticationState.FAILURE.value, None, None)
                if self.cfg["user"]["reject_on_error"]
                else (AuthenticationState.FALLTHROUGH.value, None, None)
            ),
            "getInfo": (GetInfoState.FALLTHROUGH.value, None),
            "nameToId": NameToIdState.UNKNOWN.value,
            "registerUser": RegisterUserState.FALLTHROUGH.value,
            "idToName": IdToNameState.UNKNOWN.value,
            "idToTexture": IdToTextureState.UNKNOWN.value,
            "getRegisteredUsers": {},
        }
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith("_"):
                fallback_result = fallback_results.get(name)
                # debug(f"Decorating {name} in Authenticator with fallback {fallback_result}")
                if fallback_result:
                    decorated_method = fortify_ice(retval=fallback_result)(
                        check_secret(secret=secret)(method)
                    )
                else:
                    decorated_method = check_secret(secret=secret)(method)
                setattr(self, name, decorated_method)

    @staticmethod
    def _user_authentication_state(username: str, state: str) -> None:
        """
        Sets the prometheus metric for the user authentication state

        :param username: The username of the user
        :param state: The authentication state
        """
        USER_AUTHENTICATION_STATE.labels(username=username).state(state)

    def _authenticate_fallthrough(self, username: str) -> Tuple[int, None, None]:
        """
        Helper method to set authentication state to fallthrough

        :param username: The username of the user
        :return: The authentication state
        """
        self._user_authentication_state(username, "fallthrough")
        return (AuthenticationState.FALLTHROUGH.value, None, None)

    def _authenticate_failure(self, username: str) -> Tuple[int, None, None]:
        """
        Helper method to set authentication state to failure

        :param username: The username of the user
        :return: The authentication state
        """
        self._user_authentication_state(username, "failure")
        return (AuthenticationState.FAILURE.value, None, None)

    def _authenticate_success(
        self, username: str, mumble_user_id: int, display_name: str, groups: List[str]
    ) -> Tuple[int, str, List[str]]:
        """
        Helper method to set authentication state to success

        :param username: The username of the user
        :param mumble_user_id: The mumble user id
        :param display_name: The display name
        :param groups: The groups list
        :return: The authentication state tuple
        """
        self._user_authentication_state(username, "success")
        return (
            mumble_user_id,
            unescape(display_name),
            groups,
        )

    @USER_AUTHENTICATION_LATENCY.time()
    def authenticate(
        self, name, pw, certlist, certhash, strong, current=None
    ) -> Tuple[int, Optional[str], Optional[List[str]]]:
        """
        Called to authenticate a user. If you do not know the username in question,
        always return -2 from this method to fall through to normal database authentication.
        Note that if authentication succeeds, murmur will create a record of the user in it's
        database, reserving the username and id so it cannot be used for normal database
        authentication.
        The data in the certificate (name, email addresses etc), as well as the list of signing
        certificates, should only be trusted if certstrong is true.
        Internally, Murmur treats usernames as case-insensitive. It is recommended
        that authenticators do the same. Murmur checks if a username is in use when
        a user connects. If the connecting user is registered, the other username is
        kicked. If the connecting user is not registered, the connecting user is not
        allowed to join the server.
        Arguments:
            name: Username to authenticate.
            pw: Password to authenticate with.
            certificates: List of der encoded certificates the user connected with.
            certhash: Hash of user certificate, as used by murmur internally when matching.
            certstrong: True if certificate was valid and signed by a trusted CA.
            context: The request context for the invocation.
        Returns a tuple containing the following:
        _retval: UserID of authenticated user,
                    -1 for authentication failures,
                    -2 for unknown user (fallthrough),
                    -3 for authentication failures where the data could (temporarily)
                       not be verified.
        newname: Set this to change the username from the supplied one.
        groups: List of groups on the root channel that
                the user will be added to for the duration of the connection.
        """
        if name == "SuperUser":
            debug("Forced fall through for SuperUser")
            return self._authenticate_fallthrough(name)
        try:
            user = self._load_user(where={"username": name})
        except Exception as e:
            error(f"Fetching mumble user failed: {e}")
            return self._authenticate_fallthrough(name)
        if not user:
            return self._authenticate_templink(name, pw)
        uid = user.get("user_id")
        if not uid:
            error(f"User without ID: {user}")
            return self._authenticate_fallthrough(name)
        mumble_user_id = self._to_mumble_baseuser_id(int(uid))
        display_name = user.get("display_name", f"Noname user {uid}")
        upwhash = user.get("pwhash")
        uhashfn = user.get("hashfn")
        groups = user.get("groups", "").split(",")
        if allianceauth_check_hash(pw, upwhash, uhashfn):
            info(f"User authenticated: {display_name} ({mumble_user_id}). Group: {groups}.")
            return self._authenticate_success(name, mumble_user_id, display_name, groups)
        info(
            f"Failed authentication attempt for user: {name} ({uid})",
        )
        return self._authenticate_failure(name)

    def _authenticate_templink(self, name, pw) -> Tuple[int, Optional[str], Optional[List[str]]]:
        """
        Authenticate a user via Templink

        :param name: The user name
        :param pw: The password
        """
        try:
            user = self._load_temp_user(where={"username": name})
        except Exception as e:
            error(f"Fetching Templink user failed: {e}")
            return self._authenticate_fallthrough(name)
        if not user:
            info(f"User {name} not found in Templink")
            return self._authenticate_fallthrough(name)
        password = user.get("password")
        if not password:
            info(f"Templink user {name} has no password")
            return self._authenticate_failure(name)
        if pw != password:
            info(f"Templink user {name} failed password")
            return self._authenticate_failure(name)
        uid = user.get("id")
        if not uid:
            error(f"Templink user without ID: {user}")
            return self._authenticate_fallthrough(name)
        expire = user.get("expires", 0)
        unix_now = time.time()
        if unix_now >= expire:
            info(f"Templink user {name} expired: {expire}")
            return self._authenticate_failure(name)
        display_name = user.get("name", f"Templink User {uid}")
        groups = ["Guest"]
        mumble_user_id = self._to_mumble_tempuser_id(int(uid))
        info(f"User Templink authorized: {display_name} ({mumble_user_id}). Groups: {groups}")
        return self._authenticate_success(name, mumble_user_id, display_name, groups)

    def getInfo(self, id, current=None) -> Tuple[bool, Any]:
        """
        Fetch information about a user. This is used to retrieve information
        like email address, keyhash etc. If you want murmur to take care of this
        information itself, simply return false to fall through.
        Arguments:
            id: User id.
            context: The request context for the invocation.
        Returns a tuple containing the following:
            _retval: true if information is present, false to fall through.
            info: Information about user. This needs to include at least "name".
        """
        if not self._is_baseuser(id):
            debug(f"User {id} not base user, fall through")
            return (GetInfoState.FALLTHROUGH.value, None)
        name = self._id_to_name(id)
        if not name:
            warning(f"User with id {id} not found, fall through")
            return (GetInfoState.FALLTHROUGH.value, None)
        info = {UserInfo.UserName: name}
        debug(f"Present info for user {id}: {info}")
        return (GetInfoState.SUCCESS.value, info)

    def nameToId(self, name, current=None) -> int:
        """
        Map a name to a user id. For example, used in ACLs

        Arguments:
            name: Username to map.
            context: The request context for the invocation.
        Returns: User id or -2 for unknown name.
        """
        debug(f"Starting name to id mapping for name {name}")
        if name.lower() == "superuser":
            debug("Name to id mapping for 'superuser' -> forced fall through")
            return NameToIdState.UNKNOWN.value
        try:
            # Internally, Murmur treats usernames as case-insensitive,
            # so the LIKE operator is used
            user = self._load_user(where={"username": name}, where_operator="LIKE")
        except Exception as e:
            error(f"Failed to fetch the user by username '{name}' from the database: {e}")
            return NameToIdState.UNKNOWN.value
        if not user:
            debug(f"Name {name} to id mapping not found, fall through")
            return NameToIdState.UNKNOWN.value
        uid = user.get("user_id")
        if not uid:
            error(f"User without ID: {user}")
            return NameToIdState.UNKNOWN.value
        mumble_user_id = self._to_mumble_baseuser_id(int(uid))
        debug(f"Mapped name {name} to id {mumble_user_id}")
        return int(mumble_user_id)

    def idToName(self, id, current=None) -> str:
        """
        Map a user id to a username. For example, it is also used in ACLs

        Arguments:
            id: User id to map.
            context: The request context for the invocation.
        Returns: Name of user or empty string for unknown id.
        """
        debug(f"Starting id to name mapping for id {id}")
        if not self._is_baseuser(id):
            debug(f"Id {id} not in baseuser range, fall through")
            return IdToNameState.UNKNOWN.value
        name = self._id_to_name(id)
        if not name:
            warning(f"User id {id} not found, fall through")
            return IdToNameState.UNKNOWN.value
        if name == "superuser":
            warning(f"The 'superuser' ({id}) not allowed, fall through")
            return IdToNameState.UNKNOWN.value
        debug(f"Mapped id {id} to name {name}")
        return name

    def _id_to_name(self, id) -> Optional[str]:
        """
        Makes the Mumble ID to name mapping

        Arguments:
            id: The ID
        Returns: The name if found, otherwise None
        """
        id = self._to_baseuser_id(int(id))
        try:
            user = self._load_user(where={"user_id": id})
        except Exception as e:
            error(f"Failed to fetch the user by ID {id} from the database: {e}")
            return None
        if not user:
            error(f"Failed to find user by ID {id}")
            return None
        # Internally, Murmur treats usernames as case-insensitive,
        # so the lower() function is used
        return str(user.get("username", f"Noname user {id}")).lower()

    def idToTexture(self, id, current=None) -> bytes:
        """
        Map a user to a custom Texture.
        Arguments:
            id: User id to map.
            context: The request context for the invocation.
        Returns: User texture or an empty texture for unknown users or users without textures.
        """

        if not self.cfg["avatar"]["enabled"]:
            info(
                "Avatars are disabled, fall through",
            )
            return IdToTextureState.UNKNOWN.value
        if id >= self.tempuser_offset:
            character_id = self._id_to_character_id_templink(id)
        elif id >= self.base_offset:
            character_id = self._id_to_character_id(id)
        else:
            warning(f"User ID {id} is not in the valid range")
            return IdToTextureState.UNKNOWN.value
        if not character_id:
            warning(f"Character ID for user ID {id} is empty")
            return IdToTextureState.UNKNOWN.value
        return self._avatar_get(character_id)

    def _id_to_character_id(self, id) -> Optional[int]:
        """
        Gets the character ID for the user ID

        :param id: The user ID
        :return: The character ID or None
        """
        user_id = self._to_baseuser_id(int(id))
        try:
            profile = self._load_item_from_database(
                table="authentication_userprofile",
                columns=["main_character_id"],
                where={"user_id": user_id},
            )
        except Exception as e:
            error(f"Failed to fetch the user profile by ID {user_id}: {e}")
            return None
        if not profile:
            error(f"Failed to find user profile by ID {user_id}")
            return None
        main_character_id = profile.get("main_character_id")
        if not main_character_id:
            error(f"User {user_id} not associated with any character")
            return None
        try:
            character = self._load_item_from_database(
                table="eveonline_evecharacter",
                columns=["character_id"],
                where={"id": main_character_id},
            )
        except Exception as e:
            error(f"Failed to fetch the character by user ID {user_id}: {e}")
            return None
        if not character:
            error(f"Failed to find character by user ID {user_id}")
            return None
        character_id = character.get("character_id")
        if not character_id:
            error(f"Character without ID: {character}")
            return None
        return int(character_id)

    def _id_to_character_id_templink(self, id) -> Optional[int]:
        """
        Gets the character ID for the user ID

        :param id: The user ID
        :return: The character ID or None
        """
        user_id = self._to_tempuser_id(int(id))
        try:
            user = self._load_temp_user(where={"id": user_id})
        except Exception as e:
            error(f"Failed to fetch the Templink character by ID {user_id}: {e}")
            return None
        if not user:
            error(f"Failed to find Templink character by ID {user_id}")
            return None
        character_id = user.get("character_id")
        if not character_id:
            error(f"Templink character without ID: {user}")
            return None
        return int(character_id)

    def registerUser(self, name, current=None) -> int:
        """
        Register a new user.
        Arguments:
            info: Information about user to register.
            context: The request context for the invocation.
        Returns: User id of new user, -1 for registration failure, or -2 to fall through.
        """
        self._method_debug("registerUser", name)
        return RegisterUserState.FALLTHROUGH.value

    def unregisterUser(self, id, current=None) -> int:
        """
        Unregister a user.
        Arguments:
            id: Userid to unregister.
            context: The request context for the invocation.
        Returns: 1 for successful unregistration,
                 0 for unsuccessful unregistration,
                 -1 to fall through.
        """
        self._method_debug("unregisterUser", id)
        return UnregisterUserState.FALLTHROUGH.value

    def getRegisteredUsers(self, filter, current=None) -> Dict[int, str]:
        """
        Get a list of registered users matching filter.
        Arguments:
            filter: Substring usernames must contain. If empty, return all registered users.
            context: The request context for the invocation.
        Returns: List of matching registered users.
        """

        if not filter:
            filter = "%"

        try:
            res = self.db.search(
                table="mumble_mumbleuser",
                columns=["user_id", "username"],
                where={"username": filter},
            )
        except Exception as e:
            error(f"Failed to fetch users by substring {filter} from the database: {e}")
            return {}

        if not res:
            debug(f"Empty user list for filter {filter}")
            return {}
        debug(f"Found {len(res)} users for filter {filter}")
        return dict(
            [
                (
                    self._to_mumble_baseuser_id(user.get("user_id")),
                    str(user.get("username")).lower(),
                )
                for user in res
            ]
        )

    def setInfo(self, id, info, current=None) -> int:
        """
        Set additional information for user registration.
        Arguments:
            id: Userid of registered user.
            info: Information to set about user. This should be merged with existing information.
            context: The request context for the invocation.
        Returns: 1 for successful update, 0 for unsuccessful update, -1 to fall through.
        """
        self._method_debug("setInfo", id)
        return SetInfoState.FALLTHROUGH.value

    def setTexture(self, id, texture, current=None) -> int:
        """
        Set texture (now called avatar) of user registration.
        Arguments:
            id: registrationId of registered user.
            tex: New texture.
            context: The request context for the invocation.
        Returns: 1 for successful update, 0 for unsuccessful update, -1 to fall through.
        """
        self._method_debug("setTexture", id)
        return SetTextureState.FALLTHROUGH.value

    def _method_debug(self, fn: str, val: Any) -> None:
        """
        Debugging helper to print the method call.
        """
        debug(f"Process {fn}({val}) -> fall through")

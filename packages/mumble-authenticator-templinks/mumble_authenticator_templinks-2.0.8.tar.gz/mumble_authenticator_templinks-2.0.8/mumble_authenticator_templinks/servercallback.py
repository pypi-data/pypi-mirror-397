import datetime
import inspect
from logging import debug, error, info
from typing import Any, Dict

from eveo7_mumbleserver_ice import ServerCallback as MumbleServerCallback

from .db import ConnectionPoolDB
from .decorators import check_secret
from .mixin_idconversion import IDConversionMixin


class ServerCallback(MumbleServerCallback, IDConversionMixin):
    def __init__(self, server, cfg: Dict[str, Any], db: ConnectionPoolDB):
        super().__init__()
        IDConversionMixin.__init__(self, base_offset=cfg["user"]["id_offset"])
        self.server = server
        self.db = db
        self.cfg = cfg
        self._decorate_methods()

    def _decorate_methods(self) -> None:
        secret = self.cfg["ice_server"]["secret"]
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith("_"):
                decorated_method = check_secret(secret=secret)(method)
                setattr(self, name, decorated_method)

    def _user_update(self, user, updates: Dict[str, str]) -> None:
        if not self._is_baseuser(user.userid):
            debug(f"Avoid update of user {user.name} with ID {user.userid}")
            return
        try:
            self.db.update(
                table="mumble_mumbleuser",
                updates=updates,
                where={"user_id": self._to_baseuser_id(user.userid)},
            )
        except Exception as e:
            error(
                f"Failed to update user {user.name} in the database: {e}"
                " Maybe you need to update and migrate the database?"
            )

    def userConnected(self, user, current=None):
        self._user_update(
            user,
            updates={
                "release": user.release,
                "version": user.version,
                "last_connect": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        info(f"User {user.name} connected to the server")

    def userDisconnected(self, user, current=None):
        self._user_update(
            user,
            updates={"last_disconnect": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        )
        info(f"User {user.name} disconnected from the server")

    def userStateChanged(self, user, current=None):
        pass

    def channelCreated(self, channel, current=None):
        pass

    def channelRemoved(self, channel, current=None):
        pass

    def channelStateChanged(self, channel, current=None):
        pass

    def userTextMessage(self, user, message, current=None):
        if message.text == "!kicktemps":
            if self.server.hasPermission(user.session, 0, 0x10000):
                self.server.sendMessage(user.session, "Kicking all templink clients!")

                users = self.server.getUsers()
                for _, auser in users.items():
                    if auser.userid > self.tempuser_offset:
                        # print(auser)
                        self.server.kickUser(auser.session, "Kicking all temp users! :-)")

                self.server.sendMessage(user.session, "All templink clients kicked!")

            else:
                self.server.sendMessage(user.session, "You do not have kick permissions!")

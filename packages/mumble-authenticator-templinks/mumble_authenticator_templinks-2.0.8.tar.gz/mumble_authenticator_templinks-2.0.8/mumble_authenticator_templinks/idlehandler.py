from logging import debug, info, warning
from threading import Timer
from typing import Any, List, Optional

from eveo7_mumbleserver_ice import InvalidChannelException
from prometheus_client import Counter, Summary

AFK_USERS_MOVED_FAILURE = Counter(
    "afk_users_moved_failure", "Number of failed moves of users to AFK channel"
)
AFK_USERS_MOVED_SUCCESS = Counter(
    "afk_users_moved_success", "Number of successful moves of users to AFK channel"
)
AFK_USERS_PROCESS_LATENCY = Summary("afk_users_process_latency", "Time spent processing users")


class IdleHandler:
    """
    Class to handle idle users in the server
    and move them to a specified channel if they are AFK.
    """

    def __init__(
        self,
        server: Any,
        enabled: bool = False,
        idle_timeout: int = 3600,
        check_interval: int = 600,
        afk_channel: int = 1,
        allowlist: List[int] = [],
        denylist: List[int] = [],
    ) -> None:
        """
        Initializes the IdleHandler.

        :param server: Reference to the server object to manage users.
        :param enabled: Whether the handler is enabled.
        :param idle_timeout: Idle time in seconds after which user is considered AFK.
        :param check_interval: Interval in seconds to check for idle users.
        :param afk_channel: The channel ID to move idle users to.
        :param allowlist: List of channel IDs where users are allowed to stay even if idle.
        :param denylist: List of channel IDs where users should not be moved from.
        """
        self.server = server
        self.enabled = enabled
        self.idle_timeout = idle_timeout
        self.check_interval = check_interval
        self.afk_channel = afk_channel
        self.allowlist = allowlist
        self.denylist = denylist
        self._timer: Optional[Timer] = None

    def start(self) -> None:
        """
        Starts the idle handler
        """
        if self.enabled:
            info(f"IdleHandler started for server {self.server.id()}")
            self._process_users()
            self._timer = Timer(self.check_interval, self.start)
            self._timer.start()
        else:
            debug("IdleHandler is disabled")

    def stop(self) -> None:
        """
        Stops the idle handler
        """
        if self._timer:
            self._timer.cancel()

    @AFK_USERS_PROCESS_LATENCY.time()
    def _process_users(self) -> None:
        """
        Fetches and processes all users to check their idle status.
        """
        try:
            users = self.server.getUsers().values()
            debug(f"Fetched All Users: {users}")
            for user in users:
                self._process_user(user)
        except Exception as e:
            warning(f"Failed to fetch or process users: {e}")

    def _process_user(self, user: Any) -> None:
        """
        Processes a user if they are idle and should be moved.

        :param user: The user object to process.
        """
        if isinstance(user, int):
            debug(f"Skipping User {user}. This happens occasionally")
            return
        if user.idlesecs <= self.idle_timeout:
            return
        debug(f"User {user.name} is AFK, for {user.idlesecs}/{self.idle_timeout}")
        try:
            state = self.server.getState(user.session)
            if state and self._should_be_moved(state.channel):
                state.channel = self.afk_channel
                state.selfMute = True
                state.selfDeaf = True
                self.server.setState(state)
                info(f"Moving user {user.name} to the AFK channel {self.afk_channel}.")
                AFK_USERS_MOVED_SUCCESS.inc()
        except InvalidChannelException:
            warning(f"Channel {self.afk_channel} not found.")
            AFK_USERS_MOVED_FAILURE.inc()
        except Exception as e:
            warning(f"Failed to process user {user.name}: {e}")
            AFK_USERS_MOVED_FAILURE.inc()

    def _should_be_moved(self, channel: int) -> bool:
        """
        Checks if the user should be moved to the AFK channel.

        :param channel: The current channel of the user.
        :return: True if the user should be moved, otherwise False.
        """
        # Skip if the user is already in the AFK channel
        if channel == self.afk_channel:
            return False
        # If denylist is used, allowlist is ignored
        if self.denylist is not None:
            if channel in self.denylist:
                return False
            else:
                return True
        if self.allowlist is not None:
            if channel in self.allowlist:
                return True
            else:
                return False
        return True

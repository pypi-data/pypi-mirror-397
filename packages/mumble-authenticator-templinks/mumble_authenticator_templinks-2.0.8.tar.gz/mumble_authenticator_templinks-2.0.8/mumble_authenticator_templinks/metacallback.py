import inspect
from logging import debug, error, info

import Ice
from eveo7_mumbleserver_ice import InvalidSecretException
from eveo7_mumbleserver_ice import MetaCallback as MumbleMetaCallback

from .decorators import check_secret, fortify_ice


class MetaCallback(MumbleMetaCallback):
    def __init__(self, app, cfg):
        super().__init__()
        self.app = app
        self.cfg = cfg
        self._decorate_methods()

    def _decorate_methods(self) -> None:
        """
        Applies `check_secret` and `fortify_ice` decorators to all public methods of the class.
        """
        secret = self.cfg["ice_server"]["secret"]
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # debug(f"Decorating method {name} for meta callback")
            if not name.startswith("_"):
                decorated_method = check_secret(secret=secret)(fortify_ice()(method))
                setattr(self, name, decorated_method)

    def _should_handle_server(self, server_id: int) -> bool:
        """
        Checks if the server with the given server_id should be handled
        based on the configuration.

        :param server_id: ID of the virtual server.
        :return: True if the server should be handled, False otherwise.
        """
        return not self.cfg["mumble"]["servers"] or server_id in self.cfg["mumble"]["servers"]

    def started(self, server, current=None):
        """
        Called when a virtual server starts. Attaches an authenticator if necessary.

        :param server: The virtual server instance.
        :param current: Current Ice context (default: None).
        """
        server_id = server.id()
        if self._should_handle_server(server_id):
            info(f"Setting authenticator for virtual server {server_id}")
            try:
                server.setAuthenticator(self.app.auth)
            # Apparently this server was restarted without us noticing
            except (
                InvalidSecretException,
                Ice.UnknownUserException,
            ) as e:
                error(f"Invalid ice secret: {e}")
                return
        else:
            debug(f"Virtual server {server_id} got started")

    def stopped(self, server, current=None):
        """
        Called when a virtual server stops.

        :param server: The virtual server instance.
        :param current: Current Ice context (default: None).
        """
        if self.app.connected:
            # Only try to output the server id if we think we are still connected to prevent
            # flooding of our thread pool
            try:
                server_id = server.id()
                if self._should_handle_server(server_id):
                    info(f"Authenticated virtual server {server_id} got stopped")
                else:
                    debug(f"Virtual server {server_id} got stopped")
                return
            except Ice.ConnectionRefusedException:
                self.app.connected = False

        debug("Server shutdown stopped a virtual server")

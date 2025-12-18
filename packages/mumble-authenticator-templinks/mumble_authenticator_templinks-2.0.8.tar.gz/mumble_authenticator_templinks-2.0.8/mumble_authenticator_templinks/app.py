from logging import debug, error, info, warning
from threading import Timer
from typing import Any, Dict, List, Optional

import Ice
from eveo7_mumbleserver_ice import (
    InvalidSecretException,
    MetaCallbackPrx,
    MetaPrx,
    ServerCallbackPrx,
    ServerUpdatingAuthenticatorPrx,
)
from prometheus_client import Enum

from .authenticator import Authenticator
from .db import ConnectionPoolDB
from .idlehandler import IdleHandler
from .metacallback import MetaCallback
from .servercallback import ServerCallback

ICE_HEALTHCHECK = Enum(
    "ice_healthcheck",
    "Healthcheck for ICE server",
    states=["healthy", "unhealthy", "disabled", "unknown"],
)


class App(Ice.Application):
    def __init__(self, cfg: Dict[str, Any], db: ConnectionPoolDB):
        super().__init__()
        self.db = db
        self.cfg = cfg
        self.meta = None
        self.auth = None
        self.metacb = None
        self.adapter: Ice.ObjectAdapter
        self.connected = False
        self.healthcheck: Optional[Timer] = None
        self._idlehandlers: List[IdleHandler] = []

    def run(self, args):
        self.shutdownOnInterrupt()
        if not self._initialize_ice_connection():
            return 1
        # Start the healthcheck timer if configured
        if self.cfg["ice_healthcheck"]["enabled"]:
            ICE_HEALTHCHECK.state("unknown")
            self._start_healthcheck()
        else:
            ICE_HEALTHCHECK.state("disabled")
        # Wait for the application to shut down
        self.communicator().waitForShutdown()
        # Stop the healthcheck timer if it's running
        if self.healthcheck:
            self.healthcheck.cancel()
        for idlehandler in self._idlehandlers:
            idlehandler.stop()
        if self.interrupted():
            warning("Caught interrupt signal, shutting down application.")
        # Disconnect from the database before exiting
        self.db.disconnect()
        return 0

    def _initialize_ice_connection(self):
        """
        Establishes the Ice connection and sets up the authenticator for servers.
        """
        ice = self.communicator()
        # Set Ice secret if configured
        secret = self.cfg["ice_server"]["secret"]
        glacier_enabled = self.cfg["glacier"]["enabled"]
        if secret:
            debug("Using shared Ice secret.")
            ice.getImplicitContext().put("secret", secret)
        elif not glacier_enabled:
            warning("Consider using an Ice secret to improve security.")
        if glacier_enabled:
            error("Glacier support is not implemented yet.")
            return False
        # Connect to the Ice server
        host = self.cfg["ice_server"]["host"]
        port = self.cfg["ice_server"]["port"]
        info(f"Connecting to Ice server at {host}:{port}.")
        try:
            # Create a proxy and connect to the Meta object
            base = ice.stringToProxy(f"Meta:tcp -h {host} -p {port}")
            self.meta = MetaPrx.uncheckedCast(base)
            # Create an adapter for callbacks
            host = self.cfg["ice_client"]["bind_address"]
            port = self.cfg["ice_client"]["port"]
            self.adapter = ice.createObjectAdapterWithEndpoints(
                "Callback.Client", f"tcp -h {host} -p {port}"
            )
            self.adapter.activate()
            # Set up MetaCallback and Authenticator proxies
            self.metacb = MetaCallbackPrx.uncheckedCast(
                self.adapter.addWithUUID(MetaCallback(self, self.cfg))
            )
            self.auth = ServerUpdatingAuthenticatorPrx.uncheckedCast(
                self.adapter.addWithUUID(Authenticator(self.cfg, self.db))
            )
            return self._attach_callbacks()
        except Exception as e:
            self._handle_ice_exception(e)
            return False

    def _attach_callbacks(self):
        """
        Attaches all necessary callbacks to Meta and the authenticator.
        """
        try:
            debug("Attaching Meta callback.")
            # Attach Meta callback
            self.meta.addCallback(self.metacb)
            # Attach callbacks for each virtual server
            for server in self.meta.getBootedServers():
                if (
                    not self.cfg["mumble"]["servers"]
                    or server.id() in self.cfg["mumble"]["servers"]
                ):
                    self._attach_callbacks_for_server(server)
        except Exception as e:
            self._handle_ice_exception(e)
            return False
        self.connected = True
        return True

    def _attach_callbacks_for_server(self, server) -> None:
        """
        Attaches callbacks to a virtual server.

        :param server: The virtual server to attach callbacks to.
        """
        server_id = server.id()
        info(f"Setting authenticator for virtual server {server_id}.")
        # Create and attach server callback
        servercb = ServerCallbackPrx.uncheckedCast(
            self.adapter.addWithUUID(ServerCallback(server, self.cfg, self.db))
        )
        server.setAuthenticator(self.auth)
        server.addCallback(servercb)
        # Start IdleHandler for the server
        idlehandler = IdleHandler(server, **self.cfg["idlehandler"])
        idlehandler.start()
        self._idlehandlers.append(idlehandler)

    def _reattach(self):
        """
        Attempts to reconnect to the Ice server upon connection closure or exception.
        """
        info("Reconnecting to Ice server...")
        if not self._attach_callbacks():
            error(
                "Reconnection attempt failed. Will retry in next %s seconds.",
                self.cfg["ice_healthcheck"]["check_interval"],
            )

    def _start_healthcheck(self) -> None:
        """
        Starts the healthcheck timer to monitor the connection state periodically.
        """
        self.healthcheck = Timer(
            self.cfg["ice_healthcheck"]["check_interval"], self._start_healthcheck
        )
        self.healthcheck.start()
        self._check_connection()

    def _check_connection(self) -> None:
        """
        Checks the connection state and reconnects if needed.

        I haven't found any other adequate way to check
        the connection other than pinging every second.
        """
        if not self.meta:
            self._initialize_ice_connection()
            return
        try:
            self.meta.ice_ping()
            if not self.connected:
                error("Connection is inactive. Attempting to reconnect...")
                ICE_HEALTHCHECK.state("unhealthy")
                self._reattach()
            else:
                debug("Connection is active.")
                ICE_HEALTHCHECK.state("healthy")
        except Ice.ConnectionLostException:
            error("Connection lost. Attempting to reconnect...")
            ICE_HEALTHCHECK.state("unhealthy")
            self._reattach()
        except Ice.Exception as e:
            error(f"Failed to ping the Ice server: {e}. Trying to reconnect...")
            ICE_HEALTHCHECK.state("unhealthy")
            self._reattach()

    def _handle_ice_exception(self, e: Exception) -> None:
        """
        Handles Ice-related exceptions and logs appropriate messages.
        """
        if isinstance(e, Ice.ConnectionRefusedException):
            error("Connection refused by server.")
        elif isinstance(e, (InvalidSecretException, Ice.UnknownUserException)):
            error("Invalid Ice secret or unknown user.")
        else:
            error(f"Unexpected Ice exception: {e}")
            raise e
        self.connected = False

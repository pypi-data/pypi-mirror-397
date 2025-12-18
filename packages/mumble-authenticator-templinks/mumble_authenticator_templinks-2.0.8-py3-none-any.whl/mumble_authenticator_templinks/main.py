import argparse
import sys
import threading
from logging import debug, info
from typing import Any, Dict

import Ice
from prometheus_client import start_http_server

from .app import App
from .config import DEFAULT_CONFIG_FILE, Config
from .db import ConnectionPoolDB
from .logger import AppLogger


def initialize_ice_properties(cfg: Dict[str, Any]) -> Ice.InitializationData:
    initdata = Ice.InitializationData()
    initdata.properties = Ice.createProperties([], initdata.properties)
    for line in cfg.get("ice_properties", []):
        prop, val = line.split("=", 2)
        if prop and val:
            debug(f"Ice property {prop}={val}")
            initdata.properties.setProperty(prop.strip(), val.strip())
    initdata.properties.setProperty("Ice.ImplicitContext", "Shared")
    initdata.logger = AppLogger()
    return initdata


def start_metrics_server(port: int) -> None:
    start_http_server(port)


def main() -> None:
    parser = argparse.ArgumentParser(description="AllianceAuth Mumble Authenticator")
    parser.add_argument(
        "config_file",
        type=str,
        help="Path to config file",
        default=DEFAULT_CONFIG_FILE,
        nargs="?",
    )
    parser.add_argument(
        "--default-config",
        type=str,
        help="Export default config to YAML file. If this flag is used, all other arguments will be ignored.",
    )
    args = parser.parse_args()
    if args.default_config:
        config = Config()
        config.export(args.default_config)
        sys.exit()

    config = Config(args.config_file)
    if config.config["prometheus"]["enabled"]:
        debug(f"Starting metrics server on port {config.config['prometheus']['port']}")
        metrics_thread = threading.Thread(
            target=start_metrics_server, args=(config.config["prometheus"]["port"],)
        )
        metrics_thread.start()
    info("Starting AllianceAuth Mumble authenticator")
    app = App(config.config, ConnectionPoolDB(**config.get_database_config()))
    state = app.main(sys.argv[:1], initData=initialize_ice_properties(config.config))
    info(f"Shutdown complete with state {state}")
    sys.exit(state)


if __name__ == "__main__":
    main()

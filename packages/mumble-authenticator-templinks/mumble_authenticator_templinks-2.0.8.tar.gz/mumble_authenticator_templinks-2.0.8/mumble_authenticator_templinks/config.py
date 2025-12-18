import logging
import os
import sys
from logging import debug, error, info, warning
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

ENV_PREFIX = "MA__"

DEFAULT_CONFIG_FILE = "authenticator.yml"

DEFAULT_CONFIG = {
    "database": {
        "name": "alliance_auth",
        "user": "allianceserver",
        "password": "password",
        "prefix": "",
        "host": "127.0.0.1",
        "port": 3306,
        "connection_pool_initial_size": 1,
        "connection_pool_max_size": 10,
        "cache_dir": "database_cache",
        "cache_ttl": 5,
        "cache_max_size": 10737418240,  # 10GB
        "cache_max_age": 7776000,  # 90 days
    },
    "user": {
        "id_offset": 1000000000,
        "reject_on_error": True,
    },
    "avatar": {
        "enabled": False,
        "url": "https://images.evetech.net/characters/{character_id}/portrait?size=256",
        "cache_dir": "avatar_cache",
        "cache_max_size": 10737418240,  # 10GB
        "cache_ttl": 2592000,  # 30 days
        "cache_max_age": 7776000,  # 90 days
    },
    "ice_server": {
        "host": "127.0.0.1",
        "port": 6502,
        "secret": "",
    },
    "ice_healthcheck": {
        "enabled": True,
        "check_interval": 1,  # I don't recommend changing
    },
    "ice_client": {
        "bind_address": "127.0.0.1",
        "port": 13004,
    },
    "ice_properties": [],
    "mumble": {
        "servers": [1],
    },
    "glacier": {  # Unsupported!
        "enabled": False,
        "user": "allianceserver",
        "password": "password",
        "host": "localhost",
        "port": 4063,
    },
    "log": {
        "level": "debug",
        "file": None,
        "format": "%(asctime)s %(levelname)s %(module)s %(message)s",
    },
    "idlehandler": {
        "enabled": False,
        "idle_timeout": 3600,
        "check_interval": 600,
        "afk_channel": 0,
        "allowlist": None,
        "denylist": None,
    },
    "prometheus": {
        "enabled": False,
        "port": 8000,
    },
}


class Config:
    def __init__(
        self,
        config_file: Union[str, Path] = DEFAULT_CONFIG_FILE,
        default_config: Dict[str, Any] = DEFAULT_CONFIG,
        env_prefix: str = ENV_PREFIX,
    ) -> None:
        """
        Initialize the class with a default configuration
        and optionally a user configuration file.

        :param config_file: Path to the YAML file with user configuration
        :param default_config: Dictionary with default configuration
        """
        self.env_prefix = env_prefix
        self.default_config = default_config
        self.config = default_config.copy()
        self._logging_config()
        self.config_file = Path(config_file) if isinstance(config_file, str) else config_file
        self._load()
        self._apply_env_vars()
        self._logging_config()

    def _load(self) -> None:
        """
        Load user configuration from a YAML file and merge it with the default configuration.
        """
        if not self.config_file.exists():
            warning(f"Config file '{self.config_file}' not found. Using default values.")
            return

        try:
            with self.config_file.open("r") as file:
                user_config = yaml.safe_load(file)
                self._merge(self.config, user_config or {})
                debug(f"Loaded configuration from {self.config_file}: {self.config}")
        except yaml.YAMLError as e:
            error(f"Error loading YAML from '{self.config_file}': {e}")
            sys.exit(1)
        except Exception as e:
            error(f"Unexpected error loading config '{self.config_file}': {e}")
            sys.exit(1)

    def _merge(self, defaults: Dict[str, Any], custom: Dict[str, Any]) -> None:
        """
        Recursively merge user settings with default settings.

        :param defaults: Dictionary with default settings
        :param custom: Dictionary with user settings
        """
        for key, value in custom.items():
            if isinstance(value, dict) and key in defaults:
                self._merge(defaults[key], value)
            else:
                defaults[key] = value

    def _apply_env_vars(self) -> None:
        """
        Override configuration values using environment variables.
        Environment variables should use the format MA__SECTION__SUBSECTION__KEY.
        List items should be specified as
        MA__SECTION__SUBSECTION__0, MA__SECTION__SUBSECTION__1, etc.
        """
        for env_var, env_value in os.environ.items():
            if not env_var.startswith(self.env_prefix):
                continue
            prefix_size = len(self.env_prefix)
            keys = env_var[prefix_size:].split("__")
            processed_keys: List[Union[str, int]] = []
            for key in keys:
                if key.isdigit():
                    processed_keys.append(int(key))
                else:
                    processed_keys.append(key.lower())
            self._set_nested_value(self.config, processed_keys, env_value)
        debug(f"Loaded configuration from environment: {self.config}")

    def _set_nested_value(
        self, dictionary: Union[Dict[str, Any], list], keys: list, value: Any
    ) -> None:
        """
        Sets a value in an existing multidimensional dictionary using a list of keys.
        Assumes that the dictionary structure already exists according to DEFAULT_CONFIG.

        :param dictionary: The dictionary or list to set the value to.
        :param keys: A list of keys representing the path in the dictionary or list.
        :param value: The value to set on the specified path.
        """
        value = self._convert_value(value)
        for key in keys[:-1]:
            if isinstance(dictionary, dict):
                if key not in dictionary:
                    if isinstance(keys[keys.index(key) + 1], int):
                        dictionary[key] = []
                    else:
                        dictionary[key] = {}
                dictionary = dictionary[key]
            elif isinstance(dictionary, list) and isinstance(key, int):
                while len(dictionary) <= key:
                    next_key = keys[keys.index(key) + 1]
                    if isinstance(next_key, int):
                        dictionary.append([])
                    else:
                        dictionary.append({})
                dictionary = dictionary[key]
            else:
                return
        if isinstance(dictionary, dict):
            dictionary[keys[-1]] = value
        elif isinstance(dictionary, list) and isinstance(keys[-1], int):
            while len(dictionary) <= keys[-1]:
                dictionary.append(None)
            dictionary[keys[-1]] = value

    @staticmethod
    def _convert_value(value: str) -> Optional[Union[int, float, bool, str]]:
        """
        Convert a string value to an appropriate type (int, float, bool, or str).

        :param value: The string value to convert
        :return: The converted value in an appropriate type
        """
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        if value.lower() == "none":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def export(self, export_file: Union[str, Path] = DEFAULT_CONFIG_FILE) -> None:
        """
        Export the current configuration to a YAML file.

        :param export_file: Path to the file where configuration should be saved
        """
        export_file = Path(export_file) if isinstance(export_file, str) else export_file
        try:
            with export_file.open("w") as file:
                yaml.dump(self.config, file, default_flow_style=False)
                info(f"Configuration exported to '{export_file}'")
        except Exception as e:
            error(f"Failed to export configuration: {e}")

    def _logging_config(self) -> None:
        """
        Get settings for the logging configuration.

        :return: Dictionary with logging settings
        """
        level_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "warn": logging.WARNING,
            "error": logging.ERROR,
            "err": logging.ERROR,
            "critical": logging.CRITICAL,
            "crit": logging.CRITICAL,
        }
        handler: Union[logging.StreamHandler, logging.FileHandler]
        if self.config["log"]["file"]:
            handler = logging.FileHandler(self.config["log"]["file"])
        else:
            handler = logging.StreamHandler()
        logger = logging.getLogger()
        handler.setFormatter(logging.Formatter(self.config["log"]["format"]))
        level = level_mapping.get(self.config["log"]["level"].lower(), logging.INFO)
        logger.setLevel(level)
        for old_handler in logger.handlers[:]:
            logger.removeHandler(old_handler)
        logger.addHandler(handler)

    def get_database_config(self) -> dict:
        """
        Get settings for the database connection.

        :return: Dictionary with database connection settings
        """
        config = {
            "user": self.config["database"]["user"],
            "password": self.config["database"]["password"],
            "database": self.config["database"]["name"],
        }
        for key in [
            "cache_dir",
            "cache_max_age",
            "cache_max_size",
            "cache_ttl",
            "host",
            "port",
            "prefix",
            "connection_pool_max_size",
            "connection_pool_initial_size",
        ]:
            if self.config["database"][key]:
                config[key] = self.config["database"][key]
        return config

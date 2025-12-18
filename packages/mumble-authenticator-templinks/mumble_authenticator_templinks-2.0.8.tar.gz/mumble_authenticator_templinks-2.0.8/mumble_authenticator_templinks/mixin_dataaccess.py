from typing import Any, Dict, List, Optional

from .db import ConnectionPoolDB


class MultipleRecordsFoundError(Exception):
    """
    Thrown if multiple records are found in the database
    and there should be one.
    """

    pass


class DataAccessMixin:
    def __init__(self, db: ConnectionPoolDB):
        self.db = db

    def _load_item_from_database(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_operator: str = "=",
    ) -> Any:
        """
        Loads a single item from the database.

        :param table: Name of the table.
        :param columns: List of columns to select (defaults to all columns).
        :param where: WHERE conditions as a dictionary.
        :return: item as a dictionary.
        """
        try:
            res = self.db.select(
                table=table, columns=columns, where=where, where_operator=where_operator
            )
        except Exception:
            raise
        count = len(res)
        if count == 0:
            return None
        if count != 1:
            raise MultipleRecordsFoundError(f"Found {count} records in {table}")
        return res[0]

    def _load_user(
        self,
        where: Dict[str, Any],
        where_operator: str = "=",
        columns: List[str] = [
            "user_id",
            "username",
            "pwhash",
            "groups",
            "hashfn",
            "display_name",
            "certhash",
            "last_connect",
            "last_disconnect",
            "release",
            "version",
        ],
    ) -> Any:
        """
        Loads a user from the database.

        Database table:
        `user_id` int(11) NOT NULL,
        `username` varchar(254) NOT NULL, UNIQUE
        `pwhash` varchar(90) NOT NULL,
        `groups` longtext DEFAULT NULL,
        `hashfn` varchar(20) NOT NULL,
        `display_name` varchar(254) NOT NULL, UNIQUE
        `certhash` varchar(254) DEFAULT NULL,
        `last_connect` datetime(6) DEFAULT NULL,
        `last_disconnect` datetime(6) DEFAULT NULL,
        `release` longtext DEFAULT NULL,
        `version` int(11) DEFAULT NULL,

        :param name: Name of the user
        """
        return self._load_item_from_database(
            table="mumble_mumbleuser", columns=columns, where=where, where_operator=where_operator
        )

    def _load_temp_user(
        self,
        where: Dict[str, Any],
        where_operator: str = "=",
        columns: List[str] = [
            "id",
            "name",
            "username",
            "password",
            "expires",
            "templink_id",
            "character_id",
        ],
    ) -> Any:
        """
        Loads a temp user from the database.

        Database table:
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(200) NOT NULL,
        `username` varchar(20) NOT NULL, UNIQUE
        `password` varchar(20) NOT NULL,
        `expires` int(11) NOT NULL,
        `templink_id` int(11) DEFAULT NULL,
        `character_id` int(11) NOT NULL,

        :param where: WHERE conditions as a dictionary.
        :param columns: List of columns to select
        (defaults: id, name, username, password, expires, templink_id, character_id).
        """
        return self._load_item_from_database(
            table="mumbletemps_tempuser",
            columns=columns,
            where=where,
            where_operator=where_operator,
        )

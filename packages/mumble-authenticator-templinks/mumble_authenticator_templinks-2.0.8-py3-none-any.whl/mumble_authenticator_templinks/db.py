from contextlib import contextmanager
from logging import debug, error, warning
from queue import Empty, Full, Queue
from typing import Any, Dict, List, Optional, Tuple

import pymysql
from prometheus_client import Counter, Gauge, Summary
from pymysql.connections import Connection

from .mixin_basecache import BaseCacheMixin

# Metrics for the connection
DB_CONNECTION_SUCCESS = Counter(
    "db_connection_success", "Number of successful connections to the database"
)
DB_CONNECTION_FAILURE = Counter(
    "db_connection_failure", "Number of failed connections to the database"
)
# Metrics for the connection pool
DB_POOL_SIZE = Gauge("db_pool_size", "Current size of the connection pool")
DB_POOL_MAX_SIZE = Gauge("db_pool_max_size", "Maximum size of the connection pool")
DB_POOL_CONNECTION_REUSE = Counter(
    "db_pool_connection_reuse",
    "Number of successful reuses of existing connections from the pool",
)
DB_POOL_CONNECTION_NEW = Counter("db_pool_connection_new", "Number of new connections created")
DB_POOL_CONNECTION_ERROR = Counter(
    "db_pool_connection_error",
    "Number of connection errors when reusing an existing connection",
)
# Metrics for the query
DB_QUERY_SUCCESS = Counter("db_query_success", "Number of successful queries")
DB_QUERY_FAILURE = Counter("db_query_failure", "Number of failed queries")
DB_QUERY_LATENCY = Summary("db_query_latency", "Latency of queries")
# Metrics for the cache
DB_CACHE_SELECT_MISS = Counter(
    "db_cache_select_miss", "Number of cache misses for SELECT queries"
)
DB_CACHE_SELECT_HIT = Counter("db_cache_select_hit", "Number of cache hits for SELECT queries")
DB_CACHE_SELECT_STALE = Counter(
    "db_cache_select_stale", "Number of times stale cache was used for SELECT queries"
)


class ConnectionPoolDBException(Exception):
    pass


class ConnectionPoolDB(BaseCacheMixin):
    """
    Small abstraction to handle database connections for multiple threads.
    """

    def __init__(
        self,
        user: str,
        password: str,
        database: str,
        host: str = "127.0.0.1",
        port: int = 3306,
        prefix: str = "",
        connection_pool_max_size: int = 10,
        connection_pool_initial_size: int = 2,
        cache_dir: str = "database",
        cache_ttl: int = 10,
        cache_max_size: int = 10737418240,
        cache_max_age: int = 7776000,
    ) -> None:
        super().__init__(cache_dir, cache_ttl, cache_max_size, cache_max_age)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.prefix = prefix
        # Fixed-size connection pool
        DB_POOL_MAX_SIZE.set(connection_pool_max_size)
        self.pool: Queue[Connection] = Queue(maxsize=connection_pool_max_size)
        for _ in range(connection_pool_initial_size):
            try:
                self.pool.put(self._create_new_connection())
            except Exception as e:
                error(f"Could not create connection: {e}")
        DB_POOL_SIZE.set(self.pool.qsize())

    def _create_new_connection(self) -> Connection:
        """
        Creates a new connection to the database.
        """
        try:
            con = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
            DB_CONNECTION_SUCCESS.inc()
            return con
        except pymysql.MySQLError as e:
            DB_CONNECTION_FAILURE.inc()
            error(f"Could not connect to database: {e}")
            raise ConnectionPoolDBException(str(e))

    def _get_connection(self) -> Connection:
        """
        Gets a connection from the pool or creates a new one if the pool is empty.
        """
        DB_POOL_SIZE.set(self.pool.qsize())
        try:
            con = self.pool.get_nowait()
            # Check if the connection is still active
            try:
                con.ping(reconnect=True)
                DB_POOL_CONNECTION_REUSE.inc()
                debug("Re-using existing connection from pool")
                return con
            except pymysql.MySQLError:
                DB_POOL_CONNECTION_NEW.inc()
                warning("Connection is no longer active, creating a new one")
                con = self._create_new_connection()
            self._return_connection(con)
            return con
        except Empty:
            DB_POOL_CONNECTION_ERROR.inc()
            warning("No available connections in pool, creating a new connection")
            return self._create_new_connection()

    def _return_connection(self, con: Connection) -> None:
        """
        Returns the connection to the pool if it is still active.
        """
        try:
            if con.open:
                self.pool.put_nowait(con)
            else:
                debug("Connection is closed, not returning to pool")
        except Full:
            con.close()
            warning("Connection pool is full, closing connection")
        DB_POOL_SIZE.set(self.pool.qsize())

    @contextmanager
    def _cursor(self) -> Any:
        """
        Context manager for creating and closing cursors.
        """
        connection = self._get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
        except Exception as e:
            error(f"Error occurred during cursor operation: {e}")
            raise
        finally:
            cursor.close()
            self._return_connection(connection)

    @contextmanager
    @DB_QUERY_LATENCY.time()
    def execute(
        self, query: str, params: Optional[Tuple[Any]] = None, max_retries: int = 3
    ) -> Any:
        """
        Execute a database query with retry support.

        :param query: SQL query string.
        :param params: Optional parameters to use with the query.
        :param max_retries: Maximum number of retries in case of failure.
        :return: Result of the executed query.
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                with self._cursor() as cursor:
                    debug(f"Executing query: {query} with params: {params}")
                    cursor.execute(query, params)
                    DB_QUERY_SUCCESS.inc()
                    yield cursor
                    return
            except pymysql.MySQLError as e:
                DB_QUERY_FAILURE.inc()
                warning(f"Query execution failed: {e}, retrying {retry_count + 1}/{max_retries}")
                retry_count += 1
            if retry_count >= max_retries:
                raise ConnectionPoolDBException(
                    f"Query failed after {max_retries} attempts: {query}"
                )

    def select(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_operator: str = "=",
    ) -> Any:
        """
        Execute a SELECT query and return the result.

        :param table: Name of the table.
        :param columns: List of columns to select (defaults to all columns).
        :param where: WHERE conditions as a dictionary.
        :param where_operator: Operator used for WHERE conditions.
        :return: List of tuples with the query results.
        """
        columns_clause = ", ".join([f"`{col}`" for col in columns]) if columns else "*"
        where_clause, params = self._build_where_clause(where, where_operator)
        query = f"SELECT {columns_clause} FROM `{self.table_name(table)}` {where_clause}"
        cache_key = f"{query}:{params}"
        cache_data, cache_time = self._cache_get(cache_key)
        if cache_data is not None and self._cache_is_fresh(cache_time):
            debug(f"Returning data from cache for query {query} with params {params}")
            DB_CACHE_SELECT_HIT.inc()
            return cache_data
        try:
            with self.execute(query, tuple(params)) as cursor:
                result = cursor.fetchall()
                self._cache_set(cache_key, result)
                DB_CACHE_SELECT_MISS.inc()
                return result
        except Exception as e:
            if cache_data is not None:
                DB_CACHE_SELECT_STALE.inc()
                warning(f"Returning stale data from cache due to query failure: {e}")
                return cache_data
            else:
                raise

    def update(
        self,
        table: str,
        updates: Dict[str, Any],
        where: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute an UPDATE query and return the number of affected rows.

        :param table: Name of the table.
        :param updates: Dictionary of columns and their new values.
        :param where: WHERE conditions as a dictionary.
        :return: Number of affected rows.
        """
        set_clause = ", ".join([f"`{col}` = %s" for col in updates.keys()])
        params = list(updates.values())
        where_clause, where_params = self._build_where_clause(where)
        params.extend(where_params)

        query = f"UPDATE `{self.table_name(table)}` SET {set_clause} {where_clause}"
        with self.execute(query, tuple(params)) as cursor:
            count = cursor.rowcount
            debug(f"Updated {count} rows in table {table}")
            return count

    def search(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.select(table=table, columns=columns, where=where, where_operator="LIKE")

    def _build_where_clause(
        self, where: Optional[Dict[str, Any]], operator: str = "="
    ) -> Tuple[str, List[Any]]:
        """
        Build a WHERE clause for a query.

        :param where: Dictionary of WHERE conditions.
        :return: Tuple of WHERE clause and parameter list.
        """
        if not where:
            return "", []

        where_clause = "WHERE " + " AND ".join([f"`{col}` {operator} %s" for col in where.keys()])
        return where_clause, list(where.values())

    def disconnect(self) -> None:
        """
        Closes all connections in the pool.
        """
        while not self.pool.empty():
            connection = self.pool.get()
            connection.close()
            debug("Closing database connection")

    def table_name(self, name: str) -> str:
        """
        Return the full table name, including any prefixes.
        """
        return f"{self.prefix}{name}"

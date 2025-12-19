"""Connection class for ducklingaling - DB-API 2.0 compliant connection interface.

This module provides the Connection class that wraps psycopg2 connections
with ducklingaling's exception hierarchy and provides DB-API 2.0 compliant
connection management.
"""

from __future__ import annotations

from types import TracebackType
from typing import Any, Literal

import psycopg2
import psycopg2.extensions

from .cursor import Cursor
from .ducklake import DuckLakeMixin
from .exceptions import (
    InterfaceError,
    map_psycopg2_exception,
)

__all__ = ["Connection", "Cursor", "TransactionContext"]


class Connection(DuckLakeMixin):
    """
    Database connection object (DB-API 2.0 compliant).

    Represents an active connection to a DuckDBLayer server. Connections manage
    transaction state and provide cursors for query execution.

    Attributes:
        autocommit: Whether to automatically commit after each statement
        isolation_level: Transaction isolation level
        closed: Whether the connection is closed

    Example:
        >>> import ducklingaling
        >>> conn = ducklingaling.connect(host="localhost", database="main")
        >>> try:
        ...     cursor = conn.cursor()
        ...     cursor.execute("INSERT INTO users VALUES (%s, %s)", (1, "Alice"))
        ...     conn.commit()
        ... except Exception:
        ...     conn.rollback()
        ...     raise
        ... finally:
        ...     conn.close()

        Using as context manager:
        >>> with ducklingaling.connect(host="localhost") as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
        ...     rows = cursor.fetchall()
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "main",
        user: str | None = None,
        password: str | None = None,
        timeout: float | None = None,
        autocommit: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a connection (prefer using ducklingaling.connect()).

        Args:
            host: Server hostname or IP address (default: "localhost")
            port: Server port number (default: 5432)
            database: Database name (default: "main")
            user: Username for authentication (default: None, uses system user)
            password: Password for authentication (default: None)
            timeout: Connection timeout in seconds (default: None, no timeout)
            autocommit: Enable autocommit mode (default: False)
            **kwargs: Additional connection parameters passed to psycopg2

        Raises:
            OperationalError: If connection fails

        Example:
            >>> conn = Connection(host="localhost", port=5432, database="mydb")
            >>> conn.close()
        """
        # Build connection parameters
        conn_params: dict[str, Any] = {
            "host": host,
            "port": port,
            "dbname": database,
        }

        if user is not None:
            conn_params["user"] = user
        if password is not None:
            conn_params["password"] = password
        if timeout is not None:
            conn_params["connect_timeout"] = int(timeout)

        # Add any additional kwargs
        conn_params.update(kwargs)

        # Establish connection
        try:
            self._conn: psycopg2.extensions.connection = psycopg2.connect(**conn_params)
        except Exception as e:
            raise map_psycopg2_exception(e)

        # Set autocommit mode if requested
        if autocommit:
            self._conn.autocommit = True

    @property
    def closed(self) -> bool:
        """
        Whether the connection is closed.

        Returns:
            True if connection is closed, False otherwise

        Example:
            >>> conn = Connection()
            >>> conn.closed
            False
            >>> conn.close()
            >>> conn.closed
            True
        """
        return self._conn.closed != 0

    @property
    def autocommit(self) -> bool:
        """
        Whether autocommit mode is enabled.

        When autocommit is enabled, each statement is automatically committed
        after execution. When disabled, you must explicitly call commit() or
        rollback() to end transactions.

        Returns:
            True if autocommit is enabled, False otherwise

        Example:
            >>> conn = Connection()
            >>> conn.autocommit
            False
            >>> conn.autocommit = True
            >>> conn.autocommit
            True
        """
        return self._conn.autocommit

    @autocommit.setter
    def autocommit(self, value: bool) -> None:
        """
        Set autocommit mode.

        Args:
            value: True to enable autocommit, False to disable

        Raises:
            InterfaceError: If connection is closed

        Example:
            >>> conn = Connection()
            >>> conn.autocommit = True
        """
        if self.closed:
            raise InterfaceError("Cannot set autocommit on closed connection")
        try:
            self._conn.autocommit = value
        except Exception as e:
            raise map_psycopg2_exception(e)

    @property
    def isolation_level(
        self,
    ) -> Literal["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"] | None:
        """
        Get the current transaction isolation level.

        Returns:
            The isolation level string, or None if in autocommit mode

        Example:
            >>> conn = Connection()
            >>> conn.isolation_level
            'READ COMMITTED'
        """
        if self._conn.isolation_level is None:
            return None

        # Map psycopg2 isolation level constants to strings
        iso_map = {
            psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED: "READ UNCOMMITTED",
            psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED: "READ COMMITTED",
            psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ: "REPEATABLE READ",
            psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE: "SERIALIZABLE",
        }
        return iso_map.get(self._conn.isolation_level, "READ COMMITTED")

    @isolation_level.setter
    def isolation_level(
        self,
        level: Literal["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]
        | None,
    ) -> None:
        """
        Set the transaction isolation level.

        Args:
            level: Isolation level to set, or None for autocommit

        Raises:
            InterfaceError: If connection is closed

        Example:
            >>> conn = Connection()
            >>> conn.isolation_level = "SERIALIZABLE"
        """
        if self.closed:
            raise InterfaceError("Cannot set isolation_level on closed connection")

        # Map string to psycopg2 constant
        level_map = {
            "READ UNCOMMITTED": psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED,
            "READ COMMITTED": psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
            "REPEATABLE READ": psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ,
            "SERIALIZABLE": psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
            None: psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT,
        }

        try:
            self._conn.set_isolation_level(level_map[level])
        except Exception as e:
            raise map_psycopg2_exception(e)

    def close(self) -> None:
        """
        Close the connection.

        Closes the connection and releases all associated resources. Any
        uncommitted transaction will be rolled back. Cursors created from
        this connection become unusable.

        Raises:
            InterfaceError: If connection is already closed

        Example:
            >>> conn = Connection()
            >>> conn.close()
            >>> conn.closed
            True
        """
        if self.closed:
            raise InterfaceError("Connection already closed")

        try:
            self._conn.close()
        except Exception as e:
            raise map_psycopg2_exception(e)

    def commit(self) -> None:
        """
        Commit the current transaction.

        Commits all pending changes to the database. Has no effect if
        autocommit is enabled.

        Raises:
            DatabaseError: If commit fails
            InterfaceError: If connection is closed

        Example:
            >>> conn = Connection()
            >>> cursor = conn.cursor()
            >>> cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
            >>> conn.commit()
        """
        if self.closed:
            raise InterfaceError("Cannot commit on closed connection")

        try:
            self._conn.commit()
        except Exception as e:
            raise map_psycopg2_exception(e)

    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Discards all pending changes since the last commit. Has no effect
        if autocommit is enabled.

        Raises:
            DatabaseError: If rollback fails
            InterfaceError: If connection is closed

        Example:
            >>> conn = Connection()
            >>> cursor = conn.cursor()
            >>> try:
            ...     cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
            ...     raise ValueError("Something went wrong")
            ... except ValueError:
            ...     conn.rollback()
        """
        if self.closed:
            raise InterfaceError("Cannot rollback on closed connection")

        try:
            self._conn.rollback()
        except Exception as e:
            raise map_psycopg2_exception(e)

    def begin(self) -> None:
        """
        Start a new transaction explicitly.

        In non-autocommit mode, transactions start implicitly on the first
        query. This method is provided for explicit transaction control.

        Raises:
            InterfaceError: If connection is closed
            DatabaseError: If already in a transaction

        Example:
            >>> conn.begin()
            >>> cursor = conn.cursor()
            >>> cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
            >>> conn.commit()
        """
        if self.closed:
            raise InterfaceError("Cannot begin transaction on closed connection")

        try:
            with self._conn.cursor() as cur:
                cur.execute("BEGIN")
        except Exception as e:
            raise map_psycopg2_exception(e)

    def transaction(self) -> TransactionContext:
        """
        Return a context manager for transaction handling.

        Example:
            >>> with conn.transaction():
            ...     cursor = conn.cursor()
            ...     cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
            ...     # Auto-commits on success, rolls back on exception
        """
        return TransactionContext(self)

    def cursor(self) -> Cursor:
        """
        Create a new cursor for this connection.

        Returns:
            A new Cursor instance for executing queries

        Raises:
            InterfaceError: If connection is closed

        Example:
            >>> conn = Connection()
            >>> cursor = conn.cursor()
            >>> cursor.execute("SELECT * FROM users")
        """
        if self.closed:
            raise InterfaceError("Cannot create cursor on closed connection")

        return Cursor(self)

    def execute(
        self,
        operation: str,
        parameters: Any | None = None,
    ) -> Cursor:
        """
        Execute a database operation (query or command) and return a cursor.

        This is a convenience method that creates a cursor, executes the
        operation, and returns the cursor for fetching results or chaining.

        Args:
            operation: SQL query or command string
            parameters: Query parameters as sequence or mapping (optional)

        Returns:
            Cursor with the executed operation

        Raises:
            InterfaceError: If connection is closed
            DatabaseError: If the operation fails

        Example:
            >>> cursor = conn.execute("SELECT * FROM users WHERE id = %s", (1,))
            >>> row = cursor.fetchone()
            >>>
            >>> conn.execute("INSERT INTO users (name) VALUES (%s)", ("Alice",))
            >>> conn.commit()
        """
        if self.closed:
            raise InterfaceError("Cannot execute on closed connection")

        try:
            cursor = self.cursor()
            cursor.execute(operation, parameters)
            return cursor
        except Exception as e:
            raise map_psycopg2_exception(e)

    def executemany(
        self,
        operation: str,
        seq_of_parameters: Any,
    ) -> Cursor:
        """
        Execute a database operation multiple times with different parameters.

        This is a convenience method for batch operations like bulk inserts.
        Creates a cursor, executes the operation for each parameter set, and
        returns the cursor.

        Args:
            operation: SQL query or command string
            seq_of_parameters: Sequence of parameter sets

        Returns:
            Cursor with the executed batch operation

        Raises:
            InterfaceError: If connection is closed
            DatabaseError: If the operation fails

        Example:
            >>> conn.executemany(
            ...     "INSERT INTO users (name) VALUES (%s)",
            ...     [("Alice",), ("Bob",), ("Charlie",)]
            ... )
            >>> conn.commit()
        """
        if self.closed:
            raise InterfaceError("Cannot executemany on closed connection")

        try:
            cursor = self.cursor()
            cursor.executemany(operation, seq_of_parameters)
            return cursor
        except Exception as e:
            raise map_psycopg2_exception(e)

    def __enter__(self) -> Connection:
        """
        Enter connection context (returns self).

        Returns:
            self

        Example:
            >>> with Connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT 1")
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit connection context.

        Commits on success, rolls back on exception, then closes connection.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        Example:
            >>> with Connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
            ...     # Automatically commits on successful exit
            ...     # Automatically rolls back if exception occurs
            ...     # Always closes connection
        """
        try:
            if exc_type is None:
                # No exception, commit the transaction
                if not self.closed:
                    self.commit()
            else:
                # Exception occurred, rollback
                if not self.closed:
                    self.rollback()
        finally:
            # Always close the connection
            if not self.closed:
                self.close()


class TransactionContext:
    """Context manager for transactions."""

    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    def __enter__(self) -> TransactionContext:
        self._conn.begin()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()

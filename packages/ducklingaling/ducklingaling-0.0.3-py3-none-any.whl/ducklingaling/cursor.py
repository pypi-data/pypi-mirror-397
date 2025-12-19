"""
Database cursor for query execution (DB-API 2.0 compliant).

This module provides the Cursor class that wraps psycopg2.cursor and implements
the Python Database API Specification v2.0 (PEP 249).
"""

from __future__ import annotations

from collections.abc import Generator, Sequence
from typing import TYPE_CHECKING, Any, TypeAlias

from .exceptions import (
    InterfaceError,
    map_psycopg2_exception,
)

if TYPE_CHECKING:
    from .connection import Connection

__all__ = ["Cursor", "ColumnDescription"]


# Type alias for column description tuples
ColumnDescription: TypeAlias = tuple[
    str,  # name
    int,  # type_code
    int | None,  # display_size
    int | None,  # internal_size
    int | None,  # precision
    int | None,  # scale
    bool | None,  # null_ok
]


class Cursor:
    """
    Database cursor for query execution (DB-API 2.0 compliant).

    Cursors are created from connections and used to execute queries and
    fetch results. Each cursor maintains its own result set.

    Attributes:
        description: Column metadata for current result set
        rowcount: Number of rows affected/returned by last query
        arraysize: Default number of rows to fetch in fetchmany()
        connection: Parent connection object
        closed: Whether the cursor is closed
        query: Last executed query string

    Example:
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT id, name FROM users WHERE id > %s", (100,))
        >>> cursor.description
        [('id', 23, None, None, None, None, None), ('name', 25, None, None, None, None, None)]
        >>> cursor.rowcount
        42
        >>> for row in cursor:
        ...     print(row)
    """

    def __init__(self, connection: Connection) -> None:
        """
        Initialize a cursor (prefer using Connection.cursor()).

        Args:
            connection: Parent connection object
        """
        import psycopg2

        self.connection = connection
        self._cursor: psycopg2.extensions.cursor = connection._conn.cursor()
        self.arraysize: int = 1
        self.closed: bool = False

    @property
    def description(self) -> Sequence[ColumnDescription] | None:
        """
        Column metadata for current result set.

        Returns None if no query has been executed or if the query doesn't
        return rows (e.g., INSERT, UPDATE, DELETE).

        Returns:
            Sequence of 7-tuples containing column metadata, or None

        Example:
            >>> cursor.execute("SELECT id, name FROM users")
            >>> cursor.description
            [('id', 23, None, None, None, None, None), ('name', 25, None, None, None, None, None)]
        """
        self._check_closed()
        if self._cursor.description is None:
            return None
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        """
        Number of rows affected/returned by last query.

        Returns -1 if no query has been executed or if the operation
        doesn't affect rows.

        Returns:
            Number of rows affected, or -1

        Example:
            >>> cursor.execute("UPDATE users SET active = true WHERE id > %s", (100,))
            >>> cursor.rowcount
            42
        """
        self._check_closed()
        return self._cursor.rowcount

    @property
    def query(self) -> str | None:
        """
        Last executed query string.

        Returns:
            Last query string, or None if no query executed

        Example:
            >>> cursor.execute("SELECT * FROM users")
            >>> cursor.query
            'SELECT * FROM users'
        """
        self._check_closed()
        if hasattr(self._cursor, "query"):
            query = self._cursor.query
            if query is not None and isinstance(query, bytes):
                return query.decode("utf-8")
            return query
        return None

    @property
    def statusmessage(self) -> str | None:
        """
        Status message from last query.

        Returns:
            Status message string, or None

        Example:
            >>> cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
            >>> cursor.statusmessage
            'INSERT 0 1'
        """
        self._check_closed()
        if hasattr(self._cursor, "statusmessage"):
            return self._cursor.statusmessage
        return None

    @property
    def name(self) -> str | None:
        """
        Get cursor name (for server-side cursors).

        Returns:
            Cursor name or None for client-side cursors

        Example:
            >>> cursor.name
            None
        """
        self._check_closed()
        if hasattr(self._cursor, "name"):
            return self._cursor.name
        return None

    def _check_closed(self) -> None:
        """
        Check if cursor is closed and raise InterfaceError if so.

        Raises:
            InterfaceError: If cursor is closed
        """
        if self.closed:
            raise InterfaceError("Cursor is closed")

    def close(self) -> None:
        """
        Close the cursor.

        Closes the cursor and releases resources. The cursor becomes unusable
        after calling this method.

        Raises:
            InterfaceError: If cursor is already closed

        Example:
            >>> cursor.close()
            >>> cursor.closed
            True
        """
        self._check_closed()
        try:
            self._cursor.close()
            self.closed = True
        except Exception as e:
            raise map_psycopg2_exception(e)

    def execute(
        self,
        query: str,
        parameters: Sequence[Any] | dict[str, Any] | None = None,
    ) -> Cursor:
        """
        Execute a database query.

        Args:
            query: SQL query string (may contain parameter placeholders)
            parameters: Query parameters as sequence or mapping

        Returns:
            Self for method chaining

        Raises:
            ProgrammingError: If query has syntax errors
            DataError: If parameters don't match query placeholders
            OperationalError: If query execution fails
            InterfaceError: If cursor is closed

        Example:
            >>> cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
            >>> cursor.execute("SELECT * FROM users WHERE name = %(name)s", {"name": "Alice"})
        """
        self._check_closed()
        try:
            self._cursor.execute(query, parameters)
        except Exception as e:
            raise map_psycopg2_exception(e)
        return self

    def executemany(
        self,
        query: str,
        parameters_seq: Sequence[Sequence[Any] | dict[str, Any]],
    ) -> Cursor:
        """
        Execute a query multiple times with different parameter sets.

        Useful for bulk INSERT, UPDATE, or DELETE operations.

        Args:
            query: SQL query string
            parameters_seq: Sequence of parameter sets

        Returns:
            Self for method chaining

        Raises:
            ProgrammingError: If query has syntax errors
            DataError: If parameters don't match query
            OperationalError: If execution fails
            InterfaceError: If cursor is closed

        Example:
            >>> users = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
            >>> cursor.executemany("INSERT INTO users (id, name) VALUES (%s, %s)", users)
        """
        self._check_closed()
        try:
            self._cursor.executemany(query, parameters_seq)
        except Exception as e:
            raise map_psycopg2_exception(e)
        return self

    def fetchone(self) -> tuple[Any, ...] | None:
        """
        Fetch the next row from the result set.

        Returns:
            Next row as a tuple, or None if no more rows

        Raises:
            InterfaceError: If cursor is closed or no query executed
            OperationalError: If fetching fails

        Example:
            >>> cursor.execute("SELECT id, name FROM users")
            >>> row = cursor.fetchone()
            >>> if row:
            ...     print(f"ID: {row[0]}, Name: {row[1]}")
        """
        self._check_closed()
        try:
            return self._cursor.fetchone()
        except Exception as e:
            raise map_psycopg2_exception(e)

    def fetchmany(self, size: int | None = None) -> list[tuple[Any, ...]]:
        """
        Fetch the next set of rows from the result set.

        Args:
            size: Number of rows to fetch (defaults to arraysize)

        Returns:
            List of rows (may be empty if no more rows)

        Raises:
            InterfaceError: If cursor is closed or no query executed
            OperationalError: If fetching fails

        Example:
            >>> cursor.arraysize = 100
            >>> cursor.execute("SELECT * FROM large_table")
            >>> while True:
            ...     rows = cursor.fetchmany()
            ...     if not rows:
            ...         break
            ...     process_batch(rows)
        """
        self._check_closed()
        if size is None:
            size = self.arraysize
        try:
            return self._cursor.fetchmany(size)
        except Exception as e:
            raise map_psycopg2_exception(e)

    def fetchall(self) -> list[tuple[Any, ...]]:
        """
        Fetch all remaining rows from the result set.

        Warning: This loads all rows into memory. For large result sets,
        consider using fetchmany() or iterating over the cursor.

        Returns:
            List of all remaining rows

        Raises:
            InterfaceError: If cursor is closed or no query executed
            OperationalError: If fetching fails
            MemoryError: If result set is too large

        Example:
            >>> cursor.execute("SELECT * FROM users")
            >>> all_users = cursor.fetchall()
        """
        self._check_closed()
        try:
            return self._cursor.fetchall()
        except Exception as e:
            raise map_psycopg2_exception(e)

    def fetchdf(self) -> Any:
        """
        Fetch all remaining results as a pandas DataFrame.

        This is a convenience method that combines fetchall() with
        DataFrame construction using column names from cursor.description.

        Returns:
            pandas DataFrame with results

        Raises:
            ImportError: If pandas is not installed
            InterfaceError: If cursor has no results

        Example:
            >>> cursor.execute("SELECT id, name FROM users")
            >>> df = cursor.fetchdf()
            >>> print(df)
               id    name
            0   1   Alice
            1   2     Bob
        """
        from ._pandas import fetchdf

        return fetchdf(self)

    def __iter__(self) -> Generator[tuple[Any, ...], None, None]:
        """
        Iterate over result rows.

        Yields:
            Result rows one at a time

        Example:
            >>> cursor.execute("SELECT * FROM users")
            >>> for row in cursor:
            ...     print(row)
        """
        self._check_closed()
        try:
            yield from self._cursor
        except Exception as e:
            raise map_psycopg2_exception(e)

    def __next__(self) -> tuple[Any, ...]:
        """
        Get next row in iteration.

        Returns:
            Next row

        Raises:
            StopIteration: If no more rows
        """
        self._check_closed()
        try:
            row = self._cursor.fetchone()
            if row is None:
                raise StopIteration
            return row
        except StopIteration:
            raise
        except Exception as e:
            raise map_psycopg2_exception(e)

    def setinputsizes(self, sizes: Sequence[int | None]) -> None:
        """
        Set input parameter sizes (optional, for DB-API 2.0 compatibility).

        This method is provided for DB-API 2.0 compliance but has no effect
        in this implementation.

        Args:
            sizes: Sequence of parameter sizes
        """
        # No-op for compatibility
        pass

    def setoutputsize(self, size: int, column: int | None = None) -> None:
        """
        Set output column buffer size (optional, for DB-API 2.0 compatibility).

        This method is provided for DB-API 2.0 compliance but has no effect
        in this implementation.

        Args:
            size: Buffer size
            column: Column index (None for all columns)
        """
        # No-op for compatibility
        pass

    def scroll(self, value: int, mode: str = "relative") -> None:
        """
        Scroll the cursor in the result set.

        Args:
            value: Number of rows to scroll
            mode: "relative" (from current) or "absolute" (from start)

        Raises:
            NotSupportedError: If scrolling is not supported
            IndexError: If scroll position is invalid
            InterfaceError: If cursor is closed

        Example:
            >>> cursor.execute("SELECT * FROM users")
            >>> cursor.scroll(5)  # Skip 5 rows
            >>> row = cursor.fetchone()
        """
        self._check_closed()
        try:
            self._cursor.scroll(value, mode)
        except Exception as e:
            raise map_psycopg2_exception(e)

    def nextset(self) -> bool | None:
        """
        Skip to the next result set (for multiple result queries).

        Returns:
            True if another result set is available, None otherwise

        Raises:
            InterfaceError: If cursor is closed

        Note:
            Most queries return a single result set. This is primarily
            useful for stored procedures returning multiple results.
        """
        self._check_closed()
        try:
            return self._cursor.nextset()
        except Exception as e:
            raise map_psycopg2_exception(e)

    # Extension methods (non-DB-API)

    def copy_from(
        self,
        file: Any,
        table: str,
        *,
        sep: str = "\t",
        null: str = "\\N",
        size: int = 8192,
        columns: Sequence[str] | None = None,
    ) -> None:
        """
        Copy data from a file-like object to a table.

        Args:
            file: File-like object to read from
            table: Target table name
            sep: Column separator character
            null: String representing NULL
            size: Buffer size for reading
            columns: List of column names (None for all columns)

        Raises:
            ProgrammingError: If table doesn't exist
            DataError: If data format is invalid
            InterfaceError: If cursor is closed

        Example:
            >>> with open("users.csv") as f:
            ...     cursor.copy_from(f, "users", sep=",", columns=["id", "name"])
        """
        self._check_closed()
        try:
            self._cursor.copy_from(
                file, table, sep=sep, null=null, size=size, columns=columns
            )
        except Exception as e:
            raise map_psycopg2_exception(e)

    def copy_to(
        self,
        file: Any,
        table: str,
        *,
        sep: str = "\t",
        null: str = "\\N",
        columns: Sequence[str] | None = None,
    ) -> None:
        """
        Copy data from a table to a file-like object.

        Args:
            file: File-like object to write to
            table: Source table name
            sep: Column separator character
            null: String representing NULL
            columns: List of column names (None for all columns)

        Raises:
            ProgrammingError: If table doesn't exist
            InterfaceError: If cursor is closed

        Example:
            >>> with open("users.csv", "w") as f:
            ...     cursor.copy_to(f, "users", sep=",")
        """
        self._check_closed()
        try:
            self._cursor.copy_to(file, table, sep=sep, null=null, columns=columns)
        except Exception as e:
            raise map_psycopg2_exception(e)

    def mogrify(
        self,
        query: str,
        parameters: Sequence[Any] | dict[str, Any] | None = None,
    ) -> str:
        """
        Return query string with parameters bound.

        Useful for debugging parameterized queries.

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            Query string with parameters substituted

        Example:
            >>> sql = cursor.mogrify("SELECT * FROM users WHERE id = %s", (1,))
            >>> print(sql)
            "SELECT * FROM users WHERE id = 1"
        """
        self._check_closed()
        try:
            result = self._cursor.mogrify(query, parameters)
            if isinstance(result, bytes):
                return result.decode("utf-8")
            return result
        except Exception as e:
            raise map_psycopg2_exception(e)

    def __enter__(self) -> Cursor:
        """
        Enter cursor context (returns self).

        Returns:
            Self for use in context manager

        Example:
            >>> with conn.cursor() as cursor:
            ...     cursor.execute("SELECT * FROM users")
            ...     rows = cursor.fetchall()
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """
        Exit cursor context (closes cursor).

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised

        Example:
            >>> with conn.cursor() as cursor:
            ...     cursor.execute("SELECT * FROM users")
            # Cursor is automatically closed here
        """
        if not self.closed:
            self.close()

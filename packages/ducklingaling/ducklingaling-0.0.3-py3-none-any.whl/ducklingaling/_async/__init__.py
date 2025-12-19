"""Async support for ducklingaling using asyncpg.

This module provides async database operations using asyncpg as the backend.
It requires asyncpg to be installed separately.

Example:
    >>> from ducklingaling._async import connect
    >>> async with connect("postgresql://user:pass@host/db") as conn:
    ...     async with conn.cursor() as cur:
    ...         await cur.execute("SELECT 1")
    ...         result = await cur.fetchone()
"""

from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Any, Optional

# Import guard for asyncpg
try:
    import asyncpg

    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False
    asyncpg = None  # type: ignore

# Re-export exceptions from parent module
from ducklingaling.exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
)

__all__ = [
    # Import guard
    "HAS_ASYNCPG",
    "ensure_asyncpg",
    # Async classes (to be implemented)
    "AsyncConnection",
    "AsyncCursor",
    "AsyncTransaction",
    "AsyncConnectionPool",
    "AsyncPoolAcquireContext",
    # Connection function
    "connect",
    "create_pool",
    # Exception mapping
    "map_asyncpg_exception",
    # Re-exported exceptions
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
]


def ensure_asyncpg() -> None:
    """Raise ImportError if asyncpg is not installed.

    Raises:
        ImportError: If asyncpg is not available.
    """
    if not HAS_ASYNCPG:
        raise ImportError(
            "asyncpg is required for async support. "
            "Install it with: pip install ducklingaling[async]"
        )


def map_asyncpg_exception(exc: BaseException) -> Error:
    """
    Map asyncpg exceptions to ducklingaling exception hierarchy.

    Args:
        exc: An exception raised by asyncpg

    Returns:
        A ducklingaling exception with appropriate type

    Raises:
        The original exception if it's not an asyncpg exception
    """
    if not HAS_ASYNCPG:
        raise exc

    # asyncpg uses PostgresError as base class
    if isinstance(exc, asyncpg.PostgresError):
        sqlstate = getattr(exc, "sqlstate", None)
        message = str(exc)

        # Map SQLSTATE classes to exception types
        # See: https://www.postgresql.org/docs/current/errcodes-appendix.html
        if sqlstate:
            # Class 08 - Connection Exception
            if sqlstate.startswith("08"):
                return OperationalError(message, sqlstate=sqlstate)
            # Class 22 - Data Exception
            if sqlstate.startswith("22"):
                return DataError(message, sqlstate=sqlstate)
            # Class 23 - Integrity Constraint Violation
            if sqlstate.startswith("23"):
                return IntegrityError(message, sqlstate=sqlstate)
            # Class 42 - Syntax Error or Access Rule Violation
            if sqlstate.startswith("42"):
                return ProgrammingError(message, sqlstate=sqlstate)
            # Class XX - Internal Error
            if sqlstate.startswith("XX"):
                return InternalError(message, sqlstate=sqlstate)
            # Class 0A - Feature Not Supported
            if sqlstate.startswith("0A"):
                return NotSupportedError(message, sqlstate=sqlstate)

        # Default to DatabaseError for other PostgresError
        return DatabaseError(message, sqlstate=sqlstate)

    # asyncpg interface errors
    if isinstance(exc, asyncpg.InterfaceError):
        return InterfaceError(str(exc))

    # Re-raise unknown exceptions
    raise exc


# Placeholder classes (to be implemented in future tasks)


class AsyncConnection:
    """
    Async database connection wrapping asyncpg.Connection.

    Attributes:
        closed: Whether connection is closed

    Example:
        >>> async with connect(host="localhost") as conn:
        ...     result = await conn.fetch("SELECT 1")
    """

    def __init__(self, conn: Any) -> None:
        """
        Initialize from asyncpg connection (use connect() instead).

        Args:
            conn: An asyncpg.Connection instance
        """
        ensure_asyncpg()
        self._conn: Any = conn
        self._closed = False

    @property
    def closed(self) -> bool:
        """Whether connection is closed."""
        return self._closed or self._conn.is_closed()

    async def close(self) -> None:
        """Close the connection."""
        if not self._closed:
            try:
                await self._conn.close()
            finally:
                self._closed = True

    async def execute(self, query: str, *args: Any, timeout: Optional[float] = None) -> str:
        """
        Execute a query.

        Args:
            query: SQL query with $1, $2 style placeholders
            *args: Query parameters
            timeout: Query timeout

        Returns:
            Status string (e.g., "SELECT 1")
        """
        try:
            return await self._conn.execute(query, *args, timeout=timeout)
        except Exception as e:
            raise map_asyncpg_exception(e)

    async def fetch(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> list[tuple[Any, ...]]:
        """Fetch all rows."""
        try:
            records = await self._conn.fetch(query, *args, timeout=timeout)
            return [tuple(r.values()) for r in records]
        except Exception as e:
            raise map_asyncpg_exception(e)

    async def fetchrow(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> Optional[tuple[Any, ...]]:
        """Fetch one row."""
        try:
            record = await self._conn.fetchrow(query, *args, timeout=timeout)
            return tuple(record.values()) if record else None
        except Exception as e:
            raise map_asyncpg_exception(e)

    async def fetchval(
        self, query: str, *args: Any, column: int = 0, timeout: Optional[float] = None
    ) -> Any:
        """Fetch single value."""
        try:
            return await self._conn.fetchval(query, *args, column=column, timeout=timeout)
        except Exception as e:
            raise map_asyncpg_exception(e)

    def cursor(self) -> AsyncCursor:
        """
        Create a new cursor for this connection.

        Returns:
            AsyncCursor instance

        Example:
            >>> cursor = conn.cursor()
            >>> await cursor.execute("SELECT * FROM users")
            >>> row = await cursor.fetchone()
        """
        if self._closed:
            raise InterfaceError("Connection is closed")
        return AsyncCursor(self)

    def transaction(self) -> AsyncTransaction:
        """Return transaction context manager."""
        return AsyncTransaction(self)

    async def __aenter__(self) -> AsyncConnection:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()


class AsyncCursor:
    """
    Async database cursor providing DB-API-like interface.

    Note: asyncpg doesn't use cursors in the traditional sense.
    This class wraps an AsyncConnection to provide familiar cursor methods.

    Attributes:
        description: Column metadata (available after execute)
        rowcount: Number of rows affected
        closed: Whether cursor is closed
    """

    def __init__(self, connection: AsyncConnection) -> None:
        """Initialize cursor from connection."""
        self._conn = connection
        self._results: list[tuple[Any, ...]] = []
        self._position: int = 0
        self._description: Optional[Sequence[tuple[str, int, None, None, None, None, None]]] = None
        self._rowcount: int = -1
        self._closed = False

    @property
    def description(self) -> Optional[Sequence[tuple]]:
        """Column metadata for last query."""
        return self._description

    @property
    def rowcount(self) -> int:
        """Number of rows affected/returned."""
        return self._rowcount

    @property
    def closed(self) -> bool:
        """Whether cursor is closed."""
        return self._closed

    async def close(self) -> None:
        """Close the cursor."""
        self._closed = True
        self._results = []

    async def execute(
        self, query: str, parameters: Optional[Sequence[Any]] = None
    ) -> AsyncCursor:
        """
        Execute a query.

        Args:
            query: SQL query with $1, $2 placeholders
            parameters: Query parameters
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        try:
            # asyncpg uses $1, $2 style parameters
            args = parameters or ()
            records = await self._conn._conn.fetch(query, *args)

            # Convert to tuples and set description
            self._results = [tuple(r.values()) for r in records]
            self._position = 0
            self._rowcount = len(self._results)

            # Build description from first record if available
            if records:
                self._description = [
                    (key, 0, None, None, None, None, None) for key in records[0].keys()
                ]
            else:
                self._description = None

        except Exception as e:
            raise map_asyncpg_exception(e)

        return self

    async def fetchone(self) -> Optional[tuple[Any, ...]]:
        """Fetch next row."""
        if self._closed:
            raise InterfaceError("Cursor is closed")
        if self._position >= len(self._results):
            return None
        row = self._results[self._position]
        self._position += 1
        return row

    async def fetchmany(self, size: Optional[int] = None) -> list[tuple[Any, ...]]:
        """Fetch next batch of rows."""
        if self._closed:
            raise InterfaceError("Cursor is closed")
        if size is None:
            size = 1
        end = min(self._position + size, len(self._results))
        rows = self._results[self._position : end]
        self._position = end
        return rows

    async def fetchall(self) -> list[tuple[Any, ...]]:
        """Fetch all remaining rows."""
        if self._closed:
            raise InterfaceError("Cursor is closed")
        rows = self._results[self._position :]
        self._position = len(self._results)
        return rows

    def __aiter__(self) -> AsyncCursor:
        return self

    async def __anext__(self) -> tuple[Any, ...]:
        row = await self.fetchone()
        if row is None:
            raise StopAsyncIteration
        return row

    async def __aenter__(self) -> AsyncCursor:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()


class AsyncTransaction:
    """
    Async transaction context manager.

    Example:
        >>> async with conn.transaction():
        ...     await conn.execute("INSERT INTO users VALUES ($1, $2)", 1, "Alice")
        ...     # Auto-commits on success, rolls back on exception
    """

    def __init__(self, connection: AsyncConnection) -> None:
        """Initialize transaction."""
        self._conn = connection
        self._transaction: Any = None

    async def start(self) -> None:
        """Start the transaction."""
        if self._transaction is not None:
            raise InterfaceError("Transaction already started")
        self._transaction = self._conn._conn.transaction()
        await self._transaction.start()

    async def commit(self) -> None:
        """Commit the transaction."""
        if self._transaction is None:
            raise InterfaceError("Transaction not started")
        try:
            await self._transaction.commit()
        finally:
            self._transaction = None

    async def rollback(self) -> None:
        """Rollback the transaction."""
        if self._transaction is None:
            raise InterfaceError("Transaction not started")
        try:
            await self._transaction.rollback()
        finally:
            self._transaction = None

    async def __aenter__(self) -> AsyncTransaction:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()


async def connect(
    dsn: Optional[str] = None,
    *,
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    timeout: Optional[float] = None,
    **kwargs: Any,
) -> AsyncConnection:
    """
    Connect to database asynchronously.

    Args:
        dsn: Connection string (postgresql://user:pass@host:port/database)
        host: Database host
        port: Database port
        user: Username
        password: Password
        database: Database name
        timeout: Connection timeout
        **kwargs: Additional asyncpg parameters

    Returns:
        AsyncConnection instance

    Example:
        >>> conn = await connect(host="localhost", database="main")
        >>> result = await conn.fetch("SELECT 1")
        >>> await conn.close()
    """
    ensure_asyncpg()

    try:
        conn = await asyncpg.connect(
            dsn=dsn,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            timeout=timeout,
            **kwargs,
        )
        return AsyncConnection(conn)
    except Exception as e:
        raise map_asyncpg_exception(e)


class AsyncConnectionPool:
    """
    Async connection pool for managing database connections.

    Example:
        >>> pool = await create_pool(min_size=2, max_size=10, host="localhost")
        >>> async with pool.acquire() as conn:
        ...     result = await conn.fetch("SELECT 1")
        >>> await pool.close()
    """

    def __init__(
        self,
        pool: Any,
        min_size: int,
        max_size: int,
    ) -> None:
        """Initialize pool (use create_pool() instead)."""
        self._pool = pool
        self._min_size = min_size
        self._max_size = max_size
        self._closed = False

    @property
    def min_size(self) -> int:
        return self._min_size

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def size(self) -> int:
        return self._pool.get_size()

    @property
    def free_size(self) -> int:
        return self._pool.get_idle_size()

    @property
    def closed(self) -> bool:
        return self._closed

    def acquire(self, timeout: Optional[float] = None) -> AsyncPoolAcquireContext:
        """Acquire connection from pool."""
        return AsyncPoolAcquireContext(self, timeout)

    async def release(self, connection: AsyncConnection) -> None:
        """Release connection back to pool."""
        await self._pool.release(connection._conn)

    async def close(self) -> None:
        """Close all connections in pool."""
        if not self._closed:
            await self._pool.close()
            self._closed = True

    async def terminate(self) -> None:
        """Terminate all connections immediately."""
        if not self._closed:
            self._pool.terminate()
            self._closed = True

    async def __aenter__(self) -> AsyncConnectionPool:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()


class AsyncPoolAcquireContext:
    """Context manager for pool connection acquisition."""

    def __init__(self, pool: AsyncConnectionPool, timeout: Optional[float]) -> None:
        self._pool = pool
        self._timeout = timeout
        self._conn: Optional[AsyncConnection] = None

    async def __aenter__(self) -> AsyncConnection:
        raw_conn = await self._pool._pool.acquire(timeout=self._timeout)
        self._conn = AsyncConnection(raw_conn)
        return self._conn

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._conn:
            await self._pool._pool.release(self._conn._conn)
            self._conn = None


async def create_pool(
    min_size: int = 1,
    max_size: int = 10,
    *,
    dsn: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    **kwargs: Any,
) -> AsyncConnectionPool:
    """
    Create an async connection pool.

    Args:
        min_size: Minimum pool size
        max_size: Maximum pool size
        dsn: Connection string
        host: Database host
        port: Database port
        user: Username
        password: Password
        database: Database name
        **kwargs: Additional asyncpg parameters

    Returns:
        AsyncConnectionPool instance
    """
    ensure_asyncpg()

    try:
        pool = await asyncpg.create_pool(
            dsn=dsn,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            min_size=min_size,
            max_size=max_size,
            **kwargs,
        )
        return AsyncConnectionPool(pool, min_size, max_size)
    except Exception as e:
        raise map_asyncpg_exception(e)

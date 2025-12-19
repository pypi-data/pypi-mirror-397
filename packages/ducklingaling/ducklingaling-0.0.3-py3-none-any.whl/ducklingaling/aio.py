"""
Async interface for ducklingaling.

Provides async database operations using asyncpg as the backend.

Example:
    >>> from ducklingaling import aio
    >>> async with aio.connect(host="localhost") as conn:
    ...     result = await conn.fetch("SELECT 1")

    >>> async with aio.create_pool(min_size=2, max_size=10) as pool:
    ...     async with pool.acquire() as conn:
    ...         result = await conn.fetch("SELECT 1")
"""

from ._async import (
    HAS_ASYNCPG,
    AsyncConnection,
    AsyncConnectionPool,
    AsyncCursor,
    AsyncPoolAcquireContext,
    AsyncTransaction,
    DatabaseError,
    DataError,
    # Re-export exceptions
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    connect,
    create_pool,
    ensure_asyncpg,
    map_asyncpg_exception,
)

__all__ = [
    "HAS_ASYNCPG",
    "ensure_asyncpg",
    "AsyncConnection",
    "AsyncCursor",
    "AsyncTransaction",
    "AsyncConnectionPool",
    "AsyncPoolAcquireContext",
    "connect",
    "create_pool",
    "map_asyncpg_exception",
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

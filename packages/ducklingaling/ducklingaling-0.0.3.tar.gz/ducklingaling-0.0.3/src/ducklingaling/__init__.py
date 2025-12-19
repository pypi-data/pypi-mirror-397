"""
ducklingaling - DB-API 2.0 compliant client for DuckDBLayer

A Python client library that provides both synchronous and asynchronous interfaces
for connecting to DuckDBLayer, a PostgreSQL-compatible server that exposes DuckDB
through the PostgreSQL wire protocol.

This library follows the Python DB-API 2.0 specification (PEP 249) and provides:
- Synchronous connections using psycopg2
- Asynchronous connections using asyncpg
- Optional pandas integration for DataFrame support
- Full compatibility with PostgreSQL clients

Example:
    Synchronous usage:
        >>> import ducklingaling
        >>> conn = ducklingaling.connect(host='localhost', port=5432)
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM my_table")
        >>> results = cursor.fetchall()

    Asynchronous usage:
        >>> import asyncio
        >>> import ducklingaling.aio
        >>> async def main():
        ...     conn = await ducklingaling.aio.connect(host='localhost', port=5432)
        ...     cursor = await conn.cursor()
        ...     await cursor.execute("SELECT * FROM my_table")
        ...     results = await cursor.fetchall()
"""

from __future__ import annotations

from typing import Any

# Import aio submodule for async support
from . import aio

# Import Connection class
from .connection import Connection

# Import DuckLake mixin
from .ducklake import DuckLakeMixin

# Import exceptions
from .exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)

# Import ConnectionPool class
from .pool import ConnectionPool

# Import type objects and constructors
from .types import (
    BINARY,
    DATETIME,
    NUMBER,
    ROWID,
    STRING,
    Binary,
    Date,
    DateFromTicks,
    DBAPITypeObject,
    Time,
    TimeFromTicks,
    Timestamp,
    TimestampFromTicks,
)

__version__ = "0.1.0"

# DB-API 2.0 required module-level attributes
apilevel = "2.0"
threadsafety = 2  # Threads may share the module and connections
paramstyle = "pyformat"  # Python extended format codes, e.g. ...WHERE name=%(name)s


def connect(
    host: str = "localhost",
    port: int = 5432,
    database: str = "main",
    user: str | None = None,
    password: str | None = None,
    timeout: float | None = None,
    autocommit: bool = True,
    **kwargs: Any,
) -> Connection:
    """
    Create a new database connection.

    This is the main entry point for connecting to a DuckDBLayer server.

    Args:
        host: Server hostname or IP address (default: "localhost")
        port: Server port number (default: 5432)
        database: Database name (default: "main")
        user: Username for authentication
        password: Password for authentication
        timeout: Connection timeout in seconds
        autocommit: Enable autocommit mode (default: False)
        **kwargs: Additional connection parameters

    Returns:
        A new Connection object

    Raises:
        OperationalError: If connection fails

    Example:
        >>> import ducklingaling
        >>> conn = ducklingaling.connect(host="localhost", database="main")
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT 1")
        >>> print(cursor.fetchone())
        (1,)
        >>> conn.close()
    """
    return Connection(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        timeout=timeout,
        autocommit=autocommit,
        **kwargs,
    )


def create_pool(
    minconn: int = 1,
    maxconn: int = 10,
    host: str = "localhost",
    port: int = 5432,
    database: str = "main",
    user: str | None = None,
    password: str | None = None,
    **kwargs: Any,
) -> ConnectionPool:
    """
    Create a connection pool for managing database connections.

    This function provides a convenient way to create a ConnectionPool instance
    for thread-safe connection pooling. The pool maintains a minimum number of
    connections and can grow up to a maximum number as needed.

    Args:
        minconn: Minimum number of connections to maintain (default: 1)
        maxconn: Maximum number of connections allowed (default: 10)
        host: Server hostname or IP address (default: "localhost")
        port: Server port number (default: 5432)
        database: Database name (default: "main")
        user: Username for authentication
        password: Password for authentication
        **kwargs: Additional connection parameters

    Returns:
        A new ConnectionPool object

    Raises:
        InterfaceError: If minconn < 0, maxconn <= 0, or maxconn < minconn
        OperationalError: If initial connection creation fails

    Example:
        >>> import ducklingaling
        >>> pool = ducklingaling.create_pool(
        ...     minconn=2,
        ...     maxconn=10,
        ...     host="localhost",
        ...     database="main"
        ... )
        >>> with pool.connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT 1")
        ...     print(cursor.fetchone())
        (1,)
        >>> pool.closeall()
    """
    return ConnectionPool(
        min_size=minconn,
        max_size=maxconn,
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        **kwargs,
    )


__all__ = [
    # Connection function and class
    "connect",
    "Connection",
    # Connection pool function and class
    "create_pool",
    "ConnectionPool",
    # DuckLake mixin
    "DuckLakeMixin",
    # Async submodule
    "aio",
    # DB-API 2.0 exceptions
    "Error",
    "Warning",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    # DB-API 2.0 type objects
    "STRING",
    "BINARY",
    "NUMBER",
    "DATETIME",
    "ROWID",
    "DBAPITypeObject",
    # DB-API 2.0 type constructors
    "Date",
    "Time",
    "Timestamp",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "Binary",
    # Module metadata
    "__version__",
    "apilevel",
    "threadsafety",
    "paramstyle",
]

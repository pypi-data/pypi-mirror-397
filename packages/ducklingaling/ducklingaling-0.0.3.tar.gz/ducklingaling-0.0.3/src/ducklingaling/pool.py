"""Connection pool for thread-safe connection management.

This module provides the ConnectionPool class for managing a pool of database
connections in a thread-safe manner. It uses a queue-based approach with
configurable minimum and maximum pool sizes.

The pool automatically creates connections on demand up to the maximum size,
maintains a minimum number of idle connections, and supports context manager
usage for automatic cleanup.

Examples:
    Basic usage with context manager:
        >>> from ducklingaling.pool import ConnectionPool
        >>>
        >>> pool = ConnectionPool(
        ...     min_size=2,
        ...     max_size=10,
        ...     timeout=30.0,
        ...     host='localhost',
        ...     database='mydb',
        ...     user='postgres',
        ...     password='secret'
        ... )
        >>>
        >>> # Get a connection from the pool
        >>> conn = pool.getconn()
        >>> try:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
        ...     results = cursor.fetchall()
        ... finally:
        ...     pool.putconn(conn)
        >>>
        >>> # Close all connections when done
        >>> pool.closeall()

    Using as context manager:
        >>> with ConnectionPool(min_size=2, max_size=10, host='localhost') as pool:
        ...     conn = pool.getconn()
        ...     try:
        ...         cursor = conn.cursor()
        ...         cursor.execute("SELECT 1")
        ...     finally:
        ...         pool.putconn(conn)
        ...     # Pool automatically closed on exit

    Thread-safe usage:
        >>> import threading
        >>>
        >>> def worker(pool):
        ...     conn = pool.getconn(timeout=5.0)
        ...     try:
        ...         cursor = conn.cursor()
        ...         cursor.execute("SELECT * FROM data")
        ...         return cursor.fetchall()
        ...     finally:
        ...         pool.putconn(conn)
        >>>
        >>> pool = ConnectionPool(min_size=5, max_size=20, host='localhost')
        >>> threads = [threading.Thread(target=worker, args=(pool,)) for _ in range(10)]
        >>> for t in threads:
        ...     t.start()
        >>> for t in threads:
        ...     t.join()
        >>> pool.closeall()
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType
from typing import TYPE_CHECKING, Any

from .exceptions import InterfaceError, OperationalError

if TYPE_CHECKING:
    from .connection import Connection

__all__ = ["ConnectionPool"]


class ConnectionPool:
    """Thread-safe connection pool for managing database connections.

    This class implements a connection pool that manages a pool of database
    connections in a thread-safe manner. It uses a queue to store available
    connections and a lock to manage the total connection count.

    The pool maintains a minimum number of connections (min_size) and can grow
    up to a maximum number of connections (max_size). When a connection is
    requested and none are available, a new connection is created if the pool
    size is below max_size. If the pool is at max_size, the request will wait
    for a connection to become available up to the specified timeout.

    Attributes:
        min_size: Minimum number of connections to maintain in the pool.
        max_size: Maximum number of connections allowed in the pool.
        timeout: Default timeout in seconds for acquiring a connection.

    Args:
        min_size: Minimum connections to maintain (default: 1). Must be >= 0.
        max_size: Maximum connections allowed (default: 10). Must be > 0 and >= min_size.
        timeout: Default timeout for acquiring connection in seconds (default: 30.0).
        **conn_params: Connection parameters passed to Connection constructor
            (e.g., host, port, database, user, password, etc.).

    Raises:
        InterfaceError: If min_size < 0, max_size <= 0, or max_size < min_size.

    Examples:
        >>> pool = ConnectionPool(
        ...     min_size=2,
        ...     max_size=10,
        ...     timeout=30.0,
        ...     host='localhost',
        ...     database='testdb',
        ...     user='postgres'
        ... )
        >>>
        >>> conn = pool.getconn()
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT 1")
        >>> pool.putconn(conn)
        >>> pool.closeall()

        Using with context manager:
        >>> with ConnectionPool(min_size=1, max_size=5, host='localhost') as pool:
        ...     conn = pool.getconn()
        ...     pool.putconn(conn)
    """

    def __init__(
        self,
        min_size: int = 1,
        max_size: int = 10,
        timeout: float = 30.0,
        **conn_params: Any,
    ) -> None:
        """Initialize connection pool.

        Args:
            min_size: Minimum connections to maintain (must be >= 0).
            max_size: Maximum connections allowed (must be > 0 and >= min_size).
            timeout: Default timeout for acquiring connection in seconds.
            **conn_params: Connection parameters (host, database, user, password, etc.).

        Raises:
            InterfaceError: If min_size < 0, max_size <= 0, or max_size < min_size.
        """
        # Validate parameters
        if min_size < 0:
            raise InterfaceError("min_size must be >= 0")
        if max_size <= 0:
            raise InterfaceError("max_size must be > 0")
        if max_size < min_size:
            raise InterfaceError("max_size must be >= min_size")

        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout

        # Internal state
        self._pool: queue.Queue[Connection] = queue.Queue(maxsize=max_size)
        self._size: int = 0
        self._lock = threading.Lock()
        self._conn_params = conn_params
        self._closed = False

        # Pre-create minimum connections
        for _ in range(min_size):
            conn = self._create_connection()
            self._pool.put_nowait(conn)

    @property
    def closed(self) -> bool:
        """Whether the pool is closed.

        Returns:
            True if the pool has been closed, False otherwise.

        Examples:
            >>> pool = ConnectionPool(min_size=1, max_size=5, host='localhost')
            >>> pool.closed
            False
            >>> pool.closeall()
            >>> pool.closed
            True
        """
        return self._closed

    @property
    def size(self) -> int:
        """Current number of connections (in use + available).

        Returns:
            Total number of connections managed by the pool.

        Examples:
            >>> pool = ConnectionPool(min_size=2, max_size=10, host='localhost')
            >>> pool.size
            2
            >>> conn = pool.getconn()
            >>> pool.size  # Still 2, just one is in use now
            2
        """
        return self._size

    @property
    def available(self) -> int:
        """Number of available connections in the pool.

        Returns:
            Number of connections waiting in the pool queue.

        Examples:
            >>> pool = ConnectionPool(min_size=2, max_size=10, host='localhost')
            >>> pool.available
            2
            >>> conn = pool.getconn()
            >>> pool.available
            1
            >>> pool.putconn(conn)
            >>> pool.available
            2
        """
        return self._pool.qsize()

    @property
    def in_use(self) -> int:
        """Number of connections currently in use.

        Returns:
            Number of connections that have been acquired but not returned.

        Examples:
            >>> pool = ConnectionPool(min_size=2, max_size=10, host='localhost')
            >>> pool.in_use
            0
            >>> conn = pool.getconn()
            >>> pool.in_use
            1
            >>> pool.putconn(conn)
            >>> pool.in_use
            0
        """
        return self._size - self._pool.qsize()

    def _create_connection(self) -> Connection:
        """Create a new database connection.

        Returns:
            A new Connection instance.

        Raises:
            InterfaceError: If called when pool is closed.
            OperationalError: If connection creation fails.

        Note:
            This method should only be called while holding self._lock
            or during initialization.
        """
        # Import here to avoid circular dependency
        from .connection import Connection

        if self._closed:
            raise InterfaceError("Cannot create connection on closed pool")

        conn = Connection(**self._conn_params)
        self._size += 1
        return conn

    def getconn(self, timeout: float | None = None) -> Connection:
        """Get a connection from the pool.

        Attempts to retrieve an available connection from the pool. If no
        connections are available and the pool size is below max_size, a new
        connection is created. If the pool is at max_size, waits up to timeout
        seconds for a connection to become available.

        Args:
            timeout: Maximum time to wait for a connection in seconds.
                If None, uses the pool's default timeout.
                If 0, returns immediately (non-blocking).

        Returns:
            A Connection instance from the pool.

        Raises:
            InterfaceError: If the pool is closed.
            OperationalError: If timeout expires while waiting for a connection.

        Examples:
            >>> pool = ConnectionPool(min_size=1, max_size=5, host='localhost')
            >>>
            >>> # Get connection with default timeout
            >>> conn = pool.getconn()
            >>>
            >>> # Get connection with custom timeout
            >>> conn = pool.getconn(timeout=10.0)
            >>>
            >>> # Non-blocking get
            >>> try:
            ...     conn = pool.getconn(timeout=0)
            ... except OperationalError:
            ...     print("No connections available")
        """
        if self._closed:
            raise InterfaceError("Cannot get connection from closed pool")

        if timeout is None:
            timeout = self.timeout

        # Try to get an existing connection from the pool
        try:
            conn = self._pool.get(block=False)
            return conn
        except queue.Empty:
            # No available connections, try to create a new one
            with self._lock:
                if self._size < self.max_size:
                    # We can create a new connection
                    return self._create_connection()

            # Pool is at max size, wait for a connection to become available
            try:
                conn = self._pool.get(timeout=timeout)
                return conn
            except queue.Empty:
                raise OperationalError(
                    f"Timeout waiting for connection from pool (timeout={timeout}s, "
                    f"pool_size={self._size}, max_size={self.max_size})"
                )

    def putconn(self, conn: Connection) -> None:
        """Return a connection to the pool.

        Returns a connection back to the pool for reuse. The connection should
        be in a clean state (no active transaction, cursors closed, etc.).

        Args:
            conn: The Connection instance to return to the pool.

        Raises:
            InterfaceError: If the pool is closed.
            ValueError: If the queue is full (should not happen in normal usage).

        Examples:
            >>> pool = ConnectionPool(min_size=1, max_size=5, host='localhost')
            >>> conn = pool.getconn()
            >>> try:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT 1")
            ... finally:
            ...     pool.putconn(conn)

        Note:
            It is the caller's responsibility to ensure the connection is in
            a usable state before returning it to the pool. Consider rolling
            back any uncommitted transactions before calling putconn().
        """
        if self._closed:
            raise InterfaceError("Cannot return connection to closed pool")

        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            # This should not happen in normal usage since we control pool size
            raise ValueError(
                f"Pool queue is full (size={self._size}, max_size={self.max_size})"
            )

    def resize(self, min_size: int | None = None, max_size: int | None = None) -> None:
        """Resize the pool.

        Updates the minimum and/or maximum pool size. If the new minimum size
        is greater than the current pool size, additional connections are created
        to meet the minimum. If reducing the minimum size, connections will
        naturally reduce as they are not returned.

        Args:
            min_size: New minimum size (None to keep current). Must be >= 0.
            max_size: New maximum size (None to keep current). Must be > 0.

        Raises:
            InterfaceError: If pool is closed, min_size < 0, max_size <= 0,
                or max_size < min_size.

        Examples:
            >>> pool = ConnectionPool(min_size=2, max_size=10, host='localhost')
            >>> pool.size
            2
            >>> pool.resize(min_size=5)
            >>> pool.size
            5
            >>> pool.resize(max_size=20)
            >>> pool.max_size
            20
            >>> pool.resize(min_size=3, max_size=15)
            >>> pool.min_size, pool.max_size
            (3, 15)

        Note:
            When reducing pool size, existing connections are not forcibly closed.
            The pool will naturally shrink as connections are used and not returned
            if they exceed the new maximum.
        """
        if self._closed:
            raise InterfaceError("Cannot resize closed pool")

        # Validate new sizes if provided
        new_min = min_size if min_size is not None else self.min_size
        new_max = max_size if max_size is not None else self.max_size

        if new_min < 0:
            raise InterfaceError("min_size must be >= 0")
        if new_max <= 0:
            raise InterfaceError("max_size must be > 0")
        if new_max < new_min:
            raise InterfaceError("max_size must be >= min_size")

        with self._lock:
            # Update sizes
            if min_size is not None:
                self.min_size = min_size
            if max_size is not None:
                self.max_size = max_size

            # If new min_size > current size, create additional connections
            if new_min > self._size:
                connections_needed = new_min - self._size
                for _ in range(connections_needed):
                    conn = self._create_connection()
                    self._pool.put_nowait(conn)

    @contextmanager
    def connection(self, timeout: float | None = None) -> Iterator[Connection]:
        """Context manager for acquiring a connection from the pool.

        Automatically returns the connection to the pool when done,
        even if an exception occurs.

        Args:
            timeout: Maximum time to wait for a connection

        Yields:
            A Connection from the pool

        Examples:
            >>> pool = ConnectionPool(min_size=1, max_size=5, host='localhost')
            >>> with pool.connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT * FROM users")
            ...     rows = cursor.fetchall()
            # Connection automatically returned to pool

        Note:
            This is the recommended way to work with connections from the pool
            as it ensures proper cleanup even if an exception occurs.
        """
        conn = self.getconn(timeout=timeout)
        try:
            yield conn
        finally:
            self.putconn(conn)

    def acquire(self, timeout: float | None = None) -> Iterator[Connection]:
        """Alias for connection() for asyncpg-style API.

        This method provides an alternate name that follows the asyncpg
        pool API conventions for consistency across different libraries.

        Args:
            timeout: Maximum time to wait for a connection

        Yields:
            A Connection from the pool

        Examples:
            >>> pool = ConnectionPool(min_size=1, max_size=5, host='localhost')
            >>> with pool.acquire() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT 1")
        """
        return self.connection(timeout=timeout)

    def check(self) -> bool:
        """Check if pool is healthy.

        Verifies that the pool is open and has at least one working connection
        available or can create one.

        Returns:
            True if pool is open and operational, False otherwise.

        Examples:
            >>> pool = ConnectionPool(min_size=1, max_size=5, host='localhost')
            >>> pool.check()
            True
            >>> pool.closeall()
            >>> pool.check()
            False

        Note:
            This method performs a basic health check by verifying the pool
            is not closed and has connections available. It does not test
            actual database connectivity.
        """
        # Pool is healthy if it's open and has connections or can create them
        return not self._closed

    def closeall(self) -> None:
        """Close all connections in the pool.

        Closes all connections in the pool and marks the pool as closed.
        After calling this method, no new connections can be acquired or
        returned to the pool.

        This method is idempotent - calling it multiple times is safe.

        Raises:
            No exceptions are raised. Errors during connection closure are
            silently ignored to ensure all connections are closed.

        Examples:
            >>> pool = ConnectionPool(min_size=2, max_size=10, host='localhost')
            >>> conn = pool.getconn()
            >>> pool.putconn(conn)
            >>> pool.closeall()
            >>> # pool is now closed and cannot be used

        Note:
            This method should be called when the pool is no longer needed,
            typically during application shutdown. It's automatically called
            when using the pool as a context manager.
        """
        if self._closed:
            return

        with self._lock:
            self._closed = True

            # Close all connections currently in the pool
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    try:
                        conn.close()
                    except Exception:
                        # Ignore errors during close to ensure all connections are closed
                        pass
                    finally:
                        self._size -= 1
                except queue.Empty:
                    break

    def __enter__(self) -> ConnectionPool:
        """Enter context manager.

        Returns:
            The ConnectionPool instance.

        Examples:
            >>> with ConnectionPool(min_size=1, max_size=5, host='localhost') as pool:
            ...     conn = pool.getconn()
            ...     try:
            ...         cursor = conn.cursor()
            ...         cursor.execute("SELECT 1")
            ...     finally:
            ...         pool.putconn(conn)
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager and close all connections.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        Examples:
            >>> with ConnectionPool(min_size=1, max_size=5, host='localhost') as pool:
            ...     conn = pool.getconn()
            ...     pool.putconn(conn)
            ...     # Pool automatically closed here
        """
        self.closeall()

    def __repr__(self) -> str:
        """Return string representation of the pool.

        Returns:
            String representation showing pool configuration and state.

        Examples:
            >>> pool = ConnectionPool(min_size=2, max_size=10, host='localhost')
            >>> repr(pool)
            "ConnectionPool(min_size=2, max_size=10, size=2, available=2, closed=False)"
        """
        available = self._pool.qsize()
        return (
            f"ConnectionPool(min_size={self.min_size}, max_size={self.max_size}, "
            f"size={self._size}, available={available}, closed={self._closed})"
        )

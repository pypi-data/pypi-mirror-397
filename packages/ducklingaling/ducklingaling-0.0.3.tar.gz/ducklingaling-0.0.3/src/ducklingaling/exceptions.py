"""DB-API 2.0 exception hierarchy for ducklingaling.

This module implements the standard Python Database API Specification v2.0 (PEP 249)
exception hierarchy, providing clear error handling for database operations.

Exception Hierarchy:
    Exception
        └── Warning
        └── Error (base for all DB errors)
                ├── InterfaceError (client-side errors)
                └── DatabaseError (server-side errors)
                        ├── DataError (data processing error)
                        ├── OperationalError (DB operational error)
                        ├── IntegrityError (constraint violation)
                        ├── InternalError (internal DB error)
                        ├── ProgrammingError (SQL syntax/semantic error)
                        └── NotSupportedError (unsupported operation)
"""

from __future__ import annotations

__all__ = [
    "Warning",
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    "map_psycopg2_exception",
]


class Warning(Exception):
    """Exception raised for important warnings.

    Raised for important warnings like data truncations while inserting, etc.
    This is a subclass of the Python StandardError (Exception).

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    def __init__(self, message: str, sqlstate: str | None = None) -> None:
        """Initialize Warning exception.

        Args:
            message: Human-readable error message
            sqlstate: Optional PostgreSQL SQLSTATE code
        """
        super().__init__(message)
        self.sqlstate = sqlstate


class Error(Exception):
    """Base class for all database-related errors.

    This is the base exception class for all database errors.
    All other database exception classes are derived from this class.

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    def __init__(self, message: str, sqlstate: str | None = None) -> None:
        """Initialize Error exception.

        Args:
            message: Human-readable error message
            sqlstate: Optional PostgreSQL SQLSTATE code
        """
        super().__init__(message)
        self.sqlstate = sqlstate


class InterfaceError(Error):
    """Exception raised for errors related to the database interface.

    Raised for errors that are related to the database interface rather than
    the database itself. Examples include invalid parameters, connection issues
    on the client side, etc.

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class DatabaseError(Error):
    """Exception raised for errors related to the database.

    Base class for errors that are related to the database itself rather than
    the interface. This includes server-side errors, SQL errors, etc.

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class DataError(DatabaseError):
    """Exception raised for errors due to problems with the processed data.

    Raised for errors that are due to problems with the processed data like
    division by zero, numeric value out of range, invalid date/time format, etc.

    Common SQLSTATE codes:
        - 22xxx: Data exception (e.g., 22012 division by zero, 22001 string data right truncation)

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class OperationalError(DatabaseError):
    """Exception raised for errors related to the database's operation.

    Raised for errors that are related to the database's operation and not
    necessarily under the control of the programmer. Examples include:
    - Connection failures
    - Authentication failures
    - Unexpected disconnect
    - Database not found
    - Transaction processing errors

    Common SQLSTATE codes:
        - 08xxx: Connection exception (e.g., 08000 connection exception, 08003 connection does not exist)
        - 28xxx: Invalid authorization specification

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class IntegrityError(DatabaseError):
    """Exception raised when database integrity is affected.

    Raised when the relational integrity of the database is affected, e.g.,
    a foreign key check fails, unique constraint violation, not null violation, etc.

    Common SQLSTATE codes:
        - 23000: Integrity constraint violation
        - 23502: Not null violation
        - 23503: Foreign key violation
        - 23505: Unique violation
        - 23514: Check violation

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error.

    Raised when the database encounters an internal error, e.g., the cursor
    is not valid anymore, the transaction is out of sync, memory allocation
    errors, internal database corruption, etc.

    Common SQLSTATE codes:
        - XX000: Internal error
        - XX001: Data corrupted
        - XX002: Index corrupted

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors.

    Raised for programming errors, e.g.:
    - SQL syntax errors
    - Table not found or already exists
    - Column not found
    - Wrong number of parameters specified
    - Invalid database name
    - Operation requires a connection that was closed

    Common SQLSTATE codes:
        - 42000: Syntax error or access rule violation
        - 42601: Syntax error
        - 42501: Insufficient privilege
        - 42602: Invalid name
        - 42622: Name too long
        - 42939: Reserved name
        - 42703: Undefined column
        - 42883: Undefined function
        - 42P01: Undefined table
        - 42P02: Undefined parameter

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


class NotSupportedError(DatabaseError):
    """Exception raised when a method or database API is not supported.

    Raised in case a method or database API was used which is not supported
    by the database, e.g., requesting a .rollback() on a connection that does
    not support transaction or has transactions turned off.

    Common SQLSTATE codes:
        - 0A000: Feature not supported

    Attributes:
        sqlstate: PostgreSQL SQLSTATE code if available
    """

    pass


def map_psycopg2_exception(exc: Exception) -> Error:
    """Map psycopg2/asyncpg exception to ducklingaling exception.

    This function maps exceptions from psycopg2 or asyncpg to the appropriate
    ducklingaling exception based on the SQLSTATE code or exception type.

    Args:
        exc: The psycopg2 or asyncpg exception to map

    Returns:
        An appropriate ducklingaling Error subclass instance

    Examples:
        >>> import psycopg2
        >>> try:
        ...     # Some database operation
        ...     pass
        ... except Exception as e:
        ...     raise map_psycopg2_exception(e)
    """
    # Get the error message
    message = str(exc)

    # Extract SQLSTATE code if available
    sqlstate: str | None = None
    if hasattr(exc, "pgcode"):
        sqlstate = exc.pgcode
    elif hasattr(exc, "sqlstate"):
        sqlstate = exc.sqlstate

    # If no SQLSTATE, try to map by exception type name
    exc_class_name = exc.__class__.__name__

    # Map by SQLSTATE code (most reliable)
    if sqlstate:
        # Connection exceptions (08xxx)
        if sqlstate.startswith("08"):
            return OperationalError(message, sqlstate)

        # Invalid authorization specification (28xxx)
        if sqlstate.startswith("28"):
            return OperationalError(message, sqlstate)

        # Syntax errors and access violations (42xxx)
        if sqlstate == "42601":  # Syntax error
            return ProgrammingError(message, sqlstate)
        if sqlstate == "42P01":  # Undefined table
            return ProgrammingError(message, sqlstate)
        if sqlstate == "42703":  # Undefined column
            return ProgrammingError(message, sqlstate)
        if sqlstate.startswith("42"):  # Other programming errors
            return ProgrammingError(message, sqlstate)

        # Data exceptions (22xxx)
        if sqlstate.startswith("22"):
            return DataError(message, sqlstate)

        # Integrity constraint violations (23xxx)
        if sqlstate == "23505":  # Unique violation
            return IntegrityError(message, sqlstate)
        if sqlstate == "23503":  # Foreign key violation
            return IntegrityError(message, sqlstate)
        if sqlstate == "23502":  # Not null violation
            return IntegrityError(message, sqlstate)
        if sqlstate.startswith("23"):  # Other integrity errors
            return IntegrityError(message, sqlstate)

        # Feature not supported (0A000)
        if sqlstate == "0A000":
            return NotSupportedError(message, sqlstate)

        # Internal errors (XX000, XX001, XX002)
        if sqlstate.startswith("XX"):
            return InternalError(message, sqlstate)

    # Map by exception class name for psycopg2
    if "InterfaceError" in exc_class_name:
        return InterfaceError(message, sqlstate)
    if "DataError" in exc_class_name:
        return DataError(message, sqlstate)
    if "OperationalError" in exc_class_name:
        return OperationalError(message, sqlstate)
    if "IntegrityError" in exc_class_name:
        return IntegrityError(message, sqlstate)
    if "InternalError" in exc_class_name:
        return InternalError(message, sqlstate)
    if "ProgrammingError" in exc_class_name:
        return ProgrammingError(message, sqlstate)
    if "NotSupportedError" in exc_class_name:
        return NotSupportedError(message, sqlstate)
    if "DatabaseError" in exc_class_name:
        return DatabaseError(message, sqlstate)

    # Default to generic DatabaseError for unknown errors
    return DatabaseError(message, sqlstate)

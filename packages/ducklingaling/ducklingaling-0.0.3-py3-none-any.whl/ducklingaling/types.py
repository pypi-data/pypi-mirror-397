"""
Type system for ducklingaling - DB-API 2.0 type objects and constructors.

This module provides:
1. DBAPITypeObject class for type comparison with PostgreSQL OIDs
2. DB-API 2.0 required type objects (STRING, BINARY, NUMBER, DATETIME, ROWID)
3. DB-API 2.0 type constructors (Date, Time, Timestamp, Binary, etc.)
4. PostgreSQL OID to Python type mapping

Conforms to PEP 249 (Python Database API Specification v2.0).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from datetime import time as time_type
from decimal import Decimal
from typing import Any
from uuid import UUID

__all__ = [
    # DB-API 2.0 Type Objects
    "DBAPITypeObject",
    "STRING",
    "BINARY",
    "NUMBER",
    "DATETIME",
    "ROWID",
    # DB-API 2.0 Type Constructors
    "Date",
    "Time",
    "Timestamp",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "Binary",
    # PostgreSQL Type Mapping
    "PG_TYPE_MAP",
    "get_python_type",
]


class DBAPITypeObject:
    """
    Type object for DB-API 2.0 type comparison.

    Allows comparison with PostgreSQL type OIDs from cursor.description.

    Args:
        values: One or more PostgreSQL type OIDs that belong to this type category.

    Example:
        >>> cursor.execute("SELECT name, age FROM users")
        >>> for i, column in enumerate(cursor.description):
        ...     if column[1] == STRING:
        ...         print(f"Column {i} is a string type")
        ...     elif column[1] == NUMBER:
        ...         print(f"Column {i} is a numeric type")

    Note:
        The type code in cursor.description[i][1] contains the PostgreSQL OID.
        This class allows you to check if that OID belongs to a particular DB-API
        type category (STRING, NUMBER, etc.) without knowing the specific OID values.
    """

    def __init__(self, *values: int) -> None:
        """
        Initialize a type object with one or more PostgreSQL OIDs.

        Args:
            values: PostgreSQL type OIDs that belong to this type category.
        """
        self.values: frozenset[int] = frozenset(values)

    def __eq__(self, other: object) -> bool:
        """
        Check if other is equal to this type object.

        Args:
            other: Either an integer (PostgreSQL OID) or another DBAPITypeObject.

        Returns:
            True if other matches one of this type's OIDs or is an identical type object.
        """
        if isinstance(other, int):
            return other in self.values
        if isinstance(other, DBAPITypeObject):
            return self.values == other.values
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """
        Check if other is not equal to this type object.

        Args:
            other: Either an integer (PostgreSQL OID) or another DBAPITypeObject.

        Returns:
            True if other does not match this type object.
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        """
        Return hash of this type object for use in sets and dicts.

        Returns:
            Hash value based on the frozenset of OID values.
        """
        return hash(self.values)

    def __repr__(self) -> str:
        """Return string representation of this type object."""
        return f"DBAPITypeObject({', '.join(str(v) for v in sorted(self.values))})"


# DB-API 2.0 Type Objects
# These allow portable type comparison across different databases

STRING = DBAPITypeObject(
    25,  # TEXT
    1043,  # VARCHAR
    1042,  # CHAR/BPCHAR
    18,  # CHAR (single character)
    19,  # NAME
)

BINARY = DBAPITypeObject(
    17,  # BYTEA
)

NUMBER = DBAPITypeObject(
    20,  # BIGINT/INT8
    21,  # SMALLINT/INT2
    23,  # INTEGER/INT4
    700,  # REAL/FLOAT4
    701,  # DOUBLE PRECISION/FLOAT8
    1700,  # NUMERIC/DECIMAL
    26,  # OID (also in ROWID, but can be treated as number)
)

DATETIME = DBAPITypeObject(
    1082,  # DATE
    1083,  # TIME (without timezone)
    1114,  # TIMESTAMP (without timezone)
    1184,  # TIMESTAMPTZ (with timezone)
    1186,  # INTERVAL
    1266,  # TIMETZ (time with timezone)
)

ROWID = DBAPITypeObject(
    26,  # OID
)


# DB-API 2.0 Type Constructors


def Date(year: int, month: int, day: int) -> date:
    """
    Construct a date object.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        day: Day of month (1-31)

    Returns:
        A datetime.date object.

    Example:
        >>> d = Date(2025, 12, 16)
        >>> print(d)
        2025-12-16
    """
    return date(year, month, day)


def Time(hour: int, minute: int, second: int) -> time_type:
    """
    Construct a time object.

    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)

    Returns:
        A datetime.time object.

    Example:
        >>> t = Time(14, 30, 0)
        >>> print(t)
        14:30:00
    """
    return time_type(hour, minute, second)


def Timestamp(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
) -> datetime:
    """
    Construct a timestamp object.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)

    Returns:
        A datetime.datetime object.

    Example:
        >>> ts = Timestamp(2025, 12, 16, 14, 30, 0)
        >>> print(ts)
        2025-12-16 14:30:00
    """
    return datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks: float) -> date:
    """
    Construct a date object from a POSIX timestamp.

    Args:
        ticks: Seconds since epoch (1970-01-01 00:00:00 UTC)

    Returns:
        A datetime.date object in local time.

    Example:
        >>> d = DateFromTicks(1734364800.0)  # 2024-12-16 12:00:00 UTC
        >>> print(d)
        2024-12-16
    """
    return datetime.fromtimestamp(ticks).date()


def TimeFromTicks(ticks: float) -> time_type:
    """
    Construct a time object from a POSIX timestamp.

    Args:
        ticks: Seconds since epoch (1970-01-01 00:00:00 UTC)

    Returns:
        A datetime.time object in local time.

    Example:
        >>> t = TimeFromTicks(1734364800.0)  # 2024-12-16 12:00:00 UTC
        >>> print(t)
        12:00:00
    """
    return datetime.fromtimestamp(ticks).time()


def TimestampFromTicks(ticks: float) -> datetime:
    """
    Construct a timestamp object from a POSIX timestamp.

    Args:
        ticks: Seconds since epoch (1970-01-01 00:00:00 UTC)

    Returns:
        A datetime.datetime object in local time.

    Example:
        >>> ts = TimestampFromTicks(1734364800.0)
        >>> print(ts)
        2024-12-16 12:00:00
    """
    return datetime.fromtimestamp(ticks)


def Binary(value: bytes | str) -> bytes:
    """
    Construct a binary object for BYTEA columns.

    Args:
        value: Bytes or string to convert to bytes.

    Returns:
        A bytes object suitable for BYTEA columns.

    Example:
        >>> b = Binary(b"\\x89PNG\\r\\n")
        >>> b = Binary("hello")  # Encodes as UTF-8

    Note:
        If a string is passed, it will be encoded as UTF-8.
    """
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


# PostgreSQL OID to Python Type Mapping
# https://www.postgresql.org/docs/current/datatype-oid.html
# This mapping is used for type hints and introspection

PG_TYPE_MAP: dict[int, type[Any]] = {
    # Boolean
    16: bool,  # BOOLEAN
    # Binary
    17: bytes,  # BYTEA
    # Character/String types
    18: str,  # CHAR (single character)
    19: str,  # NAME
    25: str,  # TEXT
    1042: str,  # CHAR/BPCHAR
    1043: str,  # VARCHAR
    # Integer types
    20: int,  # BIGINT/INT8
    21: int,  # SMALLINT/INT2
    23: int,  # INTEGER/INT4
    26: int,  # OID
    # Floating point types
    700: float,  # REAL/FLOAT4
    701: float,  # DOUBLE PRECISION/FLOAT8
    # Numeric/Decimal
    1700: Decimal,  # NUMERIC/DECIMAL
    # Date/Time types
    1082: date,  # DATE
    1083: time_type,  # TIME (without timezone)
    1114: datetime,  # TIMESTAMP (without timezone)
    1184: datetime,  # TIMESTAMPTZ (with timezone)
    1186: timedelta,  # INTERVAL
    1266: time_type,  # TIMETZ (time with timezone)
    # UUID
    2950: UUID,  # UUID
    # JSON types
    114: dict,  # JSON
    3802: dict,  # JSONB
    # Array types (represented as list)
    1000: list,  # _BOOL (boolean array)
    1001: list,  # _BYTEA (bytea array)
    1005: list,  # _INT2 (smallint array)
    1007: list,  # _INT4 (integer array)
    1016: list,  # _INT8 (bigint array)
    1021: list,  # _FLOAT4 (real array)
    1022: list,  # _FLOAT8 (double precision array)
    1009: list,  # _TEXT (text array)
    1014: list,  # _BPCHAR (char array)
    1015: list,  # _VARCHAR (varchar array)
    1182: list,  # _DATE (date array)
    1183: list,  # _TIME (time array)
    1115: list,  # _TIMESTAMP (timestamp array)
    1185: list,  # _TIMESTAMPTZ (timestamptz array)
    1187: list,  # _INTERVAL (interval array)
    2951: list,  # _UUID (uuid array)
    199: list,  # _JSON (json array)
    3807: list,  # _JSONB (jsonb array)
    # Network types
    869: str,  # INET (IP address)
    650: str,  # CIDR (network address)
    829: str,  # MACADDR (MAC address)
    774: str,  # MACADDR8 (MAC address, EUI-64 format)
    # Geometric types (represented as string for simplicity)
    600: str,  # POINT
    601: str,  # LSEG (line segment)
    602: str,  # PATH
    603: str,  # BOX
    604: str,  # POLYGON
    628: str,  # LINE
    718: str,  # CIRCLE
    # Bit string types
    1560: str,  # BIT
    1562: str,  # VARBIT
    # Money type
    790: str,  # MONEY (represented as string to avoid precision loss)
    # Range types (represented as string for simplicity)
    3904: str,  # INT4RANGE
    3906: str,  # INT8RANGE
    3908: str,  # NUMRANGE
    3910: str,  # TSRANGE
    3912: str,  # TSTZRANGE
    3914: str,  # DATERANGE
    # XML type
    142: str,  # XML
    # Full-text search types
    3614: str,  # TSVECTOR
    3615: str,  # TSQUERY
}


def get_python_type(pg_oid: int) -> type[Any]:
    """
    Get the Python type corresponding to a PostgreSQL OID.

    Args:
        pg_oid: PostgreSQL type OID.

    Returns:
        Python type class, defaults to 'str' for unknown types.

    Example:
        >>> get_python_type(23)  # INTEGER
        <class 'int'>
        >>> get_python_type(25)  # TEXT
        <class 'str'>
        >>> get_python_type(9999)  # Unknown type
        <class 'str'>
    """
    return PG_TYPE_MAP.get(pg_oid, str)

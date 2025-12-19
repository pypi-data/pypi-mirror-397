"""Pandas DataFrame integration for ducklingaling.

This module provides utilities for converting query results to pandas DataFrames.
Pandas is an optional dependency and must be installed separately.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .exceptions import InterfaceError, ProgrammingError

if TYPE_CHECKING:
    import pandas as pd

    from .cursor import Cursor

__all__ = ["fetch_dataframe", "fetchdf", "execute_df"]


def _ensure_pandas() -> Any:
    """Ensure pandas is available and return the module.

    Returns:
        The pandas module.

    Raises:
        ImportError: If pandas is not installed.
    """
    try:
        import pandas as pd

        return pd
    except ImportError as err:
        raise ImportError(
            "pandas is required for DataFrame support. "
            "Install it with: pip install ducklingaling[pandas]"
        ) from err


def fetch_dataframe(cursor: Cursor) -> pd.DataFrame:
    """Fetch query results as a pandas DataFrame.

    Args:
        cursor: A cursor that has already executed a query.

    Returns:
        A pandas DataFrame containing the query results.

    Raises:
        ImportError: If pandas is not installed.
        ProgrammingError: If the cursor has no description (query not executed).

    Example:
        >>> cursor.execute("SELECT id, name FROM users")
        >>> df = fetch_dataframe(cursor)
        >>> print(df)
           id   name
        0   1  Alice
        1   2    Bob
    """
    pd = _ensure_pandas()

    # Check if cursor has a description (i.e., a query was executed)
    if cursor.description is None:
        raise ProgrammingError(
            "Cursor has no description. Execute a query before fetching results."
        )

    # Extract column names from cursor description
    columns: list[str] = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows: list[tuple[Any, ...]] = cursor.fetchall()

    # Create DataFrame
    # If rows is empty, pandas will create an empty DataFrame with the column names
    return pd.DataFrame(rows, columns=columns)


def fetchdf(cursor: Any) -> pd.DataFrame:
    """Fetch all remaining results as a pandas DataFrame.

    This is a convenience function that combines fetchall() with
    DataFrame construction using column names from cursor.description.

    Args:
        cursor: A Cursor object with results to fetch

    Returns:
        pandas DataFrame with results

    Raises:
        ImportError: If pandas is not installed
        InterfaceError: If cursor has no results

    Example:
        >>> cursor.execute("SELECT id, name FROM users")
        >>> df = fetchdf(cursor)
        >>> print(df)
           id    name
        0   1   Alice
        1   2     Bob
    """
    pd = _ensure_pandas()

    if cursor.description is None:
        raise InterfaceError("No results to fetch")

    # Get column names from description
    columns: list[str] = [col[0] for col in cursor.description]

    # Fetch all rows
    rows: list[tuple[Any, ...]] = cursor.fetchall()

    # Create DataFrame
    return pd.DataFrame(rows, columns=columns)


def execute_df(
    cursor: Any,
    query: str,
    df: pd.DataFrame,
    *,
    batch_size: int = 1000,
) -> int:
    """Execute a query using DataFrame rows as parameters.

    This function is useful for bulk INSERT operations where data
    comes from a pandas DataFrame.

    Args:
        cursor: A Cursor object to use for execution
        query: SQL query with parameter placeholders (%s)
        df: DataFrame containing rows to insert
        batch_size: Number of rows to insert per batch (default: 1000)

    Returns:
        Total number of rows affected

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
        >>> cursor.execute("CREATE TABLE users (id INT, name VARCHAR)")
        >>> rows = execute_df(cursor, "INSERT INTO users VALUES (%s, %s)", df)
        >>> print(f"Inserted {rows} rows")
        Inserted 2 rows
    """
    _ensure_pandas()

    total_rows = 0

    # Convert DataFrame to list of tuples
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]

    # Execute in batches
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        cursor.executemany(query, batch)
        total_rows += cursor.rowcount if cursor.rowcount > 0 else len(batch)

    return total_rows

"""DuckLake mixin for ducklingaling connections.

This module provides the DuckLakeMixin class that adds DuckLake-specific
functionality to Connection objects, including:
- Catalog management (attach, detach, use)
- Maintenance operations (checkpoint, expire_snapshots, cleanup)
- Snapshot and time travel queries
- Metadata introspection (list_tables, describe_table)
- S3 configuration and secrets
- Extension management
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from .exceptions import InterfaceError, map_psycopg2_exception

if TYPE_CHECKING:
    import psycopg2.extensions

__all__ = ["DuckLakeMixin"]


class DuckLakeMixin:
    """
    Mixin class providing DuckLake functionality for connections.

    This mixin adds methods for working with DuckLake catalogs, snapshots,
    time travel queries, and DuckDB-specific features.

    Example:
        >>> conn = ducklingaling.connect(host="localhost")
        >>> conn.attach_catalog("/path/to/catalog.db", "/path/to/data")
        >>> snapshots = conn.list_snapshots()
        >>> changes = conn.table_changes('users', start=1, end=5)
    """

    _conn: psycopg2.extensions.connection

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _rows_to_dicts(self, cursor: Any) -> list[dict[str, Any]]:
        """Convert cursor results to list of dictionaries."""
        if cursor.description is None:
            return []
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    # =========================================================================
    # Catalog Management
    # =========================================================================

    def attach_catalog(
        self,
        catalog_path: str,
        data_path: str | None = None,
        name: str = "lake",
    ) -> None:
        """
        Attach a DuckLake catalog to the connection.

        Installs and loads the ducklake extension, then attaches a catalog.

        Args:
            catalog_path: Path to the DuckLake catalog database file
            data_path: Optional path to the data directory
            name: Name to assign to the attached catalog (default: "lake")

        Example:
            >>> conn.attach_catalog("/data/lake.db", "/data/files", "my_lake")
        """
        original_autocommit = self._conn.autocommit
        try:
            self._conn.autocommit = True
            if data_path is None:
                attach_sql = f"ATTACH 'ducklake:{catalog_path}' AS {name}"
            else:
                attach_sql = f"ATTACH 'ducklake:{catalog_path}' AS {name} (DATA_PATH '{data_path}')"

            with self._conn.cursor() as cur:
                cur.execute("INSTALL ducklake")
                cur.execute("LOAD ducklake")
                cur.execute(attach_sql)
        except Exception as e:
            raise map_psycopg2_exception(e) from e
        finally:
            self._conn.autocommit = original_autocommit

    def detach_catalog(self, name: str = "lake") -> None:
        """
        Detach a DuckLake catalog from the connection.

        Args:
            name: Name of the catalog to detach (default: "lake")
        """
        original_autocommit = self._conn.autocommit
        try:
            self._conn.autocommit = True
            with self._conn.cursor() as cur:
                cur.execute(f"DETACH {name}")
        except Exception as e:
            raise map_psycopg2_exception(e) from e
        finally:
            self._conn.autocommit = original_autocommit

    def use_catalog(self, name: str = "lake") -> None:
        """
        Switch to a different catalog context.

        Args:
            name: Name of the catalog to use (default: "lake")
        """
        original_autocommit = self._conn.autocommit
        try:
            self._conn.autocommit = True
            with self._conn.cursor() as cur:
                cur.execute(f"USE {name}")
        except Exception as e:
            raise map_psycopg2_exception(e) from e
        finally:
            self._conn.autocommit = original_autocommit

    # =========================================================================
    # Maintenance Operations
    # =========================================================================

    def checkpoint(self) -> None:
        """
        Execute a checkpoint - the all-in-one maintenance command.

        Ensures all pending writes are flushed to disk and metadata is persisted.
        """
        if self.closed:
            raise InterfaceError("Cannot checkpoint on closed connection")
        cursor = self.cursor()
        try:
            cursor.execute("CHECKPOINT")
        finally:
            cursor.close()

    def expire_snapshots(
        self,
        catalog: str = "lake",
        older_than_days: int = 7,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Expire old snapshots in the DuckLake catalog.

        Args:
            catalog: Name of the DuckLake catalog (default: "lake")
            older_than_days: Expire snapshots older than this many days
            dry_run: If True, show what would be expired without actually expiring

        Returns:
            List of dicts with expired snapshot info
        """
        if self.closed:
            raise InterfaceError("Cannot expire snapshots on closed connection")
        sql = f"CALL ducklake_expire_snapshots('{catalog}', dry_run => {str(dry_run).lower()}, older_than => now() - INTERVAL '{older_than_days} days')"
        cursor = self.cursor()
        try:
            cursor.execute(sql)
            return self._rows_to_dicts(cursor)
        finally:
            cursor.close()

    def cleanup_files(
        self,
        catalog: str = "lake",
        older_than_days: int = 7,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Clean up old files no longer referenced by any snapshot.

        Args:
            catalog: Name of the DuckLake catalog (default: "lake")
            older_than_days: Clean up files older than this many days
            dry_run: If True, show what would be cleaned without actually cleaning

        Returns:
            List of dicts with cleaned file info
        """
        if self.closed:
            raise InterfaceError("Cannot cleanup files on closed connection")
        sql = f"CALL ducklake_cleanup_old_files('{catalog}', dry_run => {str(dry_run).lower()}, older_than => now() - INTERVAL '{older_than_days} days')"
        cursor = self.cursor()
        try:
            cursor.execute(sql)
            return self._rows_to_dicts(cursor)
        finally:
            cursor.close()

    def delete_orphaned_files(
        self,
        catalog: str = "lake",
        older_than_days: int = 7,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Delete orphaned files not referenced in catalog metadata.

        Args:
            catalog: Name of the DuckLake catalog (default: "lake")
            older_than_days: Delete orphaned files older than this many days
            dry_run: If True, show what would be deleted without actually deleting

        Returns:
            List of dicts with deleted file info
        """
        if self.closed:
            raise InterfaceError("Cannot delete orphaned files on closed connection")
        sql = f"CALL ducklake_delete_orphaned_files('{catalog}', dry_run => {str(dry_run).lower()}, older_than => now() - INTERVAL '{older_than_days} days')"
        cursor = self.cursor()
        try:
            cursor.execute(sql)
            return self._rows_to_dicts(cursor)
        finally:
            cursor.close()

    def merge_adjacent_files(self, catalog: str = "lake") -> None:
        """
        Merge small adjacent data files into larger files.

        Improves query performance and reduces metadata overhead.

        Args:
            catalog: Name of the DuckLake catalog (default: "lake")
        """
        if self.closed:
            raise InterfaceError("Cannot merge files on closed connection")
        cursor = self.cursor()
        try:
            cursor.execute(f"CALL ducklake_merge_adjacent_files('{catalog}')")
        finally:
            cursor.close()

    def rewrite_data_files(self, catalog: str = "lake") -> None:
        """
        Rewrite data files for optimization.

        Optimizes layout and compression, especially after many updates/deletes.

        Args:
            catalog: Name of the DuckLake catalog (default: "lake")
        """
        if self.closed:
            raise InterfaceError("Cannot rewrite files on closed connection")
        cursor = self.cursor()
        try:
            cursor.execute(f"CALL ducklake_rewrite_data_files('{catalog}')")
        finally:
            cursor.close()

    # =========================================================================
    # Snapshot & Time Travel
    # =========================================================================

    def list_snapshots(
        self, catalog: str = "lake", limit: int = 1000
    ) -> list[dict[str, Any]]:
        """
        List all snapshots in the catalog.

        Args:
            catalog: Catalog name (default: "lake")
            limit: Maximum number of snapshots to return (default: 1000)

        Returns:
            List of dicts with: snapshot_id, snapshot_time, commit_message, commit_extra_info, changes
        """
        query = f"""
SELECT snapshot_id, snapshot_time, commit_message, commit_extra_info, changes
FROM ducklake_snapshots('{catalog}')
ORDER BY snapshot_id DESC
LIMIT {limit}
"""
        cursor = self.execute(query)
        return self._rows_to_dicts(cursor)

    def get_table_id(self, table: str, catalog: str = "lake") -> int:
        """
        Get the table id for a table.

        Args:
            table: Table name
            catalog: Catalog name (default: "lake")

        Returns:
            Table ID, or 0 if table not found
        """
        query = f"SELECT table_id FROM __ducklake_metadata_{catalog}.ducklake_table WHERE table_name = '{table}'"
        cursor = self.execute(query)
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_snapshots_for_table(
        self, table: str, catalog: str = "lake", limit: int = 1000
    ) -> list[dict[str, Any]]:
        """
        Get all snapshots that modified a specific table.

        Args:
            table: Table name
            catalog: Catalog name (default: "lake")
            limit: Maximum number of snapshots to return (default: 1000)

        Returns:
            List of snapshot dicts that touched this table
        """
        table_id = self.get_table_id(table, catalog)
        if table_id == 0:
            return []
        # Check all change types (inserts, updates, deletes)
        query = f"""
SELECT snapshot_id, snapshot_time, commit_message, commit_extra_info, changes
FROM ducklake_snapshots('{catalog}')
WHERE list_contains(changes['tables_inserted_into'], '{table_id}')
   OR list_contains(changes['tables_updated'], '{table_id}')
   OR list_contains(changes['tables_deleted_from'], '{table_id}')
ORDER BY snapshot_id DESC
LIMIT {limit}
"""
        cursor = self.execute(query)
        return self._rows_to_dicts(cursor)

    def get_current_snapshot(self, catalog: str = "lake") -> int:
        """
        Get the current (most recent) snapshot ID.

        Args:
            catalog: Catalog name (default: "lake")

        Returns:
            Current snapshot ID, or 0 if no snapshots exist
        """
        query = f"SELECT snapshot_id FROM ducklake_snapshots('{catalog}') ORDER BY snapshot_id DESC LIMIT 1"
        cursor = self.execute(query)
        result = cursor.fetchone()
        return result[0] if result else 0

    def table_changes(
        self,
        table: str,
        start: int | str,
        end: int | str,
        catalog: str = "lake",
        limit: int = 10000,
    ) -> list[dict[str, Any]]:
        """
        Get all changes to a table between two snapshots or timestamps.

        This is the key method for tracking what changed between versions.

        Args:
            table: Table name
            start: Starting snapshot ID (int) or timestamp string
            end: Ending snapshot ID (int) or timestamp string
            catalog: Catalog name (default: "lake")
            limit: Maximum number of changes to return (default: 10000)

        Returns:
            List of change dicts containing table columns plus:
            - snapshot_id: Snapshot where change occurred
            - rowid: Row identifier
            - change_type: 'insert', 'delete', 'update_preimage', 'update_postimage'

        Example:
            >>> changes = conn.table_changes('users', start=1, end=5)
            >>> changes = conn.table_changes('users',
            ...     start="now() - INTERVAL '1 week'", end="now()")
        """
        start_param = start if isinstance(start, int) else start
        end_param = end if isinstance(end, int) else end
        schema_name = self.get_schema_name(table, catalog)
        query = f"SELECT * FROM ducklake_table_changes('{catalog}', '{schema_name}', '{table}', {start_param}, {end_param}) LIMIT {limit}"
        cursor = self.execute(query)
        return self._rows_to_dicts(cursor)

    def get_schema_name(self, table: str, catalog: str = "lake") -> str | None:
        """
        Get the schema name for a table.

        Args:
            table: Table name
            catalog: Catalog name (default: "lake")

        Returns:
            Schema name, or None if table not found
        """
        query = f"""
SELECT s.schema_name
FROM __ducklake_metadata_{catalog}.ducklake_table t
JOIN __ducklake_metadata_{catalog}.ducklake_schema s ON s.schema_id = t.schema_id
WHERE t.table_name = '{table}'
"""
        cursor = self.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None

    def query_at_version(
        self,
        table: str,
        version: int,
        catalog: str = "lake",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query a table at a specific snapshot version.

        Args:
            table: Table name
            version: Snapshot ID to query
            catalog: Catalog name (default: "lake")
            limit: Maximum number of rows to return (default: None = all rows)

        Returns:
            List of row dictionaries as they existed at that version
        """
        query = f"SELECT * FROM {catalog}.{table} AT (VERSION => {version})"
        if limit is not None:
            query += f" LIMIT {limit}"
        cursor = self.execute(query)
        return self._rows_to_dicts(cursor)

    def query_at_timestamp(
        self,
        table: str,
        timestamp: str,
        catalog: str = "lake",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query a table at a specific timestamp.

        Args:
            table: Table name
            timestamp: Timestamp string (e.g., '2025-01-15 10:30:00')
            catalog: Catalog name (default: "lake")
            limit: Maximum number of rows to return (default: None = all rows)

        Returns:
            List of row dictionaries as they existed at that timestamp
        """
        query = f"SELECT * FROM {catalog}.{table} AT (TIMESTAMP => '{timestamp}')"
        if limit is not None:
            query += f" LIMIT {limit}"
        cursor = self.execute(query)
        return self._rows_to_dicts(cursor)

    # =========================================================================
    # Metadata Introspection
    # =========================================================================

    def list_tables(self, schema: str | None = None) -> list[dict[str, Any]]:
        """
        List all tables in the database.

        Args:
            schema: Optional schema name to filter by

        Returns:
            List of dicts with table metadata (schema_name, table_name, etc.)
        """
        if schema is None:
            query = "SELECT * FROM duckdb_tables()"
            cursor = self.execute(query)
        else:
            query = "SELECT * FROM duckdb_tables() WHERE schema_name = %s"
            cursor = self.execute(query, (schema,))
        return self._rows_to_dicts(cursor)

    def list_views(self, schema: str | None = None) -> list[dict[str, Any]]:
        """
        List all views in the database.

        Args:
            schema: Optional schema name to filter by

        Returns:
            List of dicts with view metadata (schema_name, view_name, sql, etc.)
        """
        if schema is None:
            query = "SELECT * FROM duckdb_views()"
            cursor = self.execute(query)
        else:
            query = "SELECT * FROM duckdb_views() WHERE schema_name = %s"
            cursor = self.execute(query, (schema,))
        return self._rows_to_dicts(cursor)

    def describe_table(
        self, table: str, schema: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Describe columns of a table.

        Args:
            table: Name of the table to describe
            schema: Optional schema name

        Returns:
            List of dicts with column metadata (column_name, data_type, etc.)
        """
        if schema is None:
            query = "SELECT * FROM duckdb_columns() WHERE table_name = %s"
            cursor = self.execute(query, (table,))
        else:
            query = "SELECT * FROM duckdb_columns() WHERE table_name = %s AND schema_name = %s"
            cursor = self.execute(query, (table, schema))
        return self._rows_to_dicts(cursor)

    def list_schemas(self) -> list[str]:
        """
        List all schemas in the database.

        Returns:
            List of schema names
        """
        cursor = self.execute("SELECT schema_name FROM duckdb_schemas()")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def list_extensions(self) -> list[dict[str, Any]]:
        """
        List all extensions in the database.

        Returns:
            List of dicts with extension metadata
        """
        cursor = self.execute("SELECT * FROM duckdb_extensions()")
        return self._rows_to_dicts(cursor)

    # =========================================================================
    # S3 Configuration
    # =========================================================================

    def configure_s3(self, region: str, endpoint: str | None = None) -> None:
        """
        Configure S3 settings for the connection.

        Args:
            region: AWS region to use (e.g., "us-east-1")
            endpoint: Optional custom S3 endpoint URL
        """
        if self.closed:
            raise InterfaceError("Cannot configure S3 on closed connection")
        try:
            cursor = self.cursor()
            cursor.execute(f"SET s3_region = '{region}'")
            if endpoint is not None:
                cursor.execute(f"SET s3_endpoint = '{endpoint}'")
        except Exception as e:
            raise map_psycopg2_exception(e) from e

    def create_s3_secret(
        self,
        credential_source: Literal["sso", "profile", "env", "iam"],
        region: str,
        profile: str | None = None,
        key_id: str | None = None,
        secret: str | None = None,
        secret_name: str = "s3_secret",
    ) -> None:
        """
        Create an S3 secret for authentication.

        Args:
            credential_source: "sso", "profile", "env", or "iam"
            region: AWS region
            profile: AWS profile name (required for "sso" and "profile")
            key_id: AWS access key ID (required for "env")
            secret: AWS secret access key (required for "env")
            secret_name: Name for the secret (default: "s3_secret")

        Example:
            >>> conn.create_s3_secret("sso", "us-west-2", profile="my-profile")
            >>> conn.create_s3_secret("env", "us-west-2", key_id="...", secret="...")
        """
        if self.closed:
            raise InterfaceError("Cannot create S3 secret on closed connection")

        if credential_source == "sso":
            if profile is None:
                raise ValueError("profile required for 'sso'")
            sql = f"CREATE SECRET {secret_name} (TYPE S3, PROVIDER CREDENTIAL_CHAIN, CHAIN 'sso', PROFILE '{profile}', REGION '{region}')"
        elif credential_source == "profile":
            if profile is None:
                raise ValueError("profile required for 'profile'")
            sql = f"CREATE SECRET {secret_name} (TYPE S3, PROVIDER CREDENTIAL_CHAIN, PROFILE '{profile}', REGION '{region}')"
        elif credential_source == "env":
            if key_id is None or secret is None:
                raise ValueError("key_id and secret required for 'env'")
            sql = f"CREATE SECRET {secret_name} (TYPE S3, KEY_ID '{key_id}', SECRET '{secret}', REGION '{region}')"
        elif credential_source == "iam":
            sql = f"CREATE SECRET {secret_name} (TYPE S3, PROVIDER CREDENTIAL_CHAIN, REGION '{region}')"
        else:
            raise ValueError(f"Invalid credential_source: {credential_source}")

        try:
            cursor = self.cursor()
            cursor.execute(sql)
        except Exception as e:
            raise map_psycopg2_exception(e) from e

    # =========================================================================
    # Extension Management
    # =========================================================================

    def install_extension(self, name: str) -> None:
        """
        Install a DuckDB extension.

        Args:
            name: Name of the extension (e.g., "httpfs", "json")
        """
        if self.closed:
            raise InterfaceError("Cannot install extension on closed connection")
        try:
            cursor = self.cursor()
            cursor.execute(f"INSTALL {name}")
        except Exception as e:
            raise map_psycopg2_exception(e) from e

    def load_extension(self, name: str) -> None:
        """
        Load a DuckDB extension.

        Args:
            name: Name of the extension (e.g., "httpfs", "json")
        """
        if self.closed:
            raise InterfaceError("Cannot load extension on closed connection")
        try:
            cursor = self.cursor()
            cursor.execute(f"LOAD {name}")
        except Exception as e:
            raise map_psycopg2_exception(e) from e

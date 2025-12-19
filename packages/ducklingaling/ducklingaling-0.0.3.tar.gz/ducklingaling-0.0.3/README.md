# ducklingaling

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DB-API 2.0](https://img.shields.io/badge/DB--API-2.0-green.svg)](https://peps.python.org/pep-0249/)

A Python client for [DuckDBLayer](https://github.com/jj-scoll/ducklingaling) - the PostgreSQL-compatible database that stores data as Parquet files.

**Key Features:**
- 🔌 **DB-API 2.0 compliant** - Drop-in replacement for psycopg2
- 🦆 **DuckLake integration** - Time travel, snapshots, and CDC built-in
- ⚡ **Async support** - Native asyncio with asyncpg backend
- 🐼 **DataFrame support** - Query directly to pandas
- 🏊 **Connection pooling** - Thread-safe pool management

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Connection](#connection)
- [Executing Queries](#executing-queries)
- [Transactions](#transactions)
- [DuckLake Features](#ducklake-features)
  - [Catalog Management](#catalog-management)
  - [Snapshots & Time Travel](#snapshots--time-travel)
  - [Change Data Feed (CDC)](#change-data-feed-cdc)
  - [Metadata Introspection](#metadata-introspection)
  - [Maintenance Operations](#maintenance-operations)
  - [S3 Configuration](#s3-configuration)
- [Async API](#async-api)
- [Connection Pooling](#connection-pooling)
- [DataFrame Integration](#dataframe-integration)
- [Error Handling](#error-handling)
- [Type Reference](#type-reference)
- [Migration from psycopg2](#migration-from-psycopg2)
- [Troubleshooting](#troubleshooting)

---

## Installation

```bash
# Basic installation (sync only)
pip install ducklingaling

# With async support (adds asyncpg)
pip install ducklingaling[async]

# With pandas DataFrame support
pip install ducklingaling[pandas]

# Full installation (async + pandas)
pip install ducklingaling[all]

# Development installation
pip install ducklingaling[dev]
```

**Requirements:** Python 3.9+

---

## Quick Start

```python
import ducklingaling

# Connect
conn = ducklingaling.connect(
    host="localhost",
    port=5432,
    user="admin",
    password="secret",
    database="main"
)

# Query
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE active = %s", [True])

for row in cursor:
    print(row)

# Clean up
cursor.close()
conn.close()
```

**With context managers (recommended):**

```python
import ducklingaling

with ducklingaling.connect(host="localhost", user="admin", password="secret") as conn:
    cursor = conn.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    print(f"Total orders: {count}")
# Connection automatically closed
```

---

## Connection

### Connection Parameters

```python
conn = ducklingaling.connect(
    host="localhost",      # Server hostname (default: "localhost")
    port=5432,             # Server port (default: 5432)
    database="main",       # Database name (default: "main")
    user="admin",          # Username (optional)
    password="secret",     # Password (optional)
    timeout=30,            # Connection timeout in seconds (optional)
)
```

### Connection Properties

```python
conn.closed       # bool: True if connection is closed
conn.autocommit   # bool: Get/set autocommit mode
conn.isolation_level  # str: Current isolation level
```

### Connection Methods

```python
conn.cursor()           # Create a new cursor
conn.execute(sql, params)  # Execute and return cursor (convenience)
conn.executemany(sql, seq_of_params)  # Batch execute
conn.commit()           # Commit transaction
conn.rollback()         # Rollback transaction
conn.close()            # Close connection
```

---

## Executing Queries

### Basic Queries

```python
cursor = conn.cursor()

# Simple query
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Parameterized query (ALWAYS use this for user input!)
cursor.execute(
    "SELECT * FROM users WHERE id = %s AND status = %s",
    [42, "active"]
)
row = cursor.fetchone()

# Named parameters
cursor.execute(
    "SELECT * FROM users WHERE name = %(name)s",
    {"name": "Alice"}
)
```

### Fetching Results

```python
cursor.execute("SELECT * FROM users")

# Fetch one row
row = cursor.fetchone()  # Returns tuple or None

# Fetch multiple rows
rows = cursor.fetchmany(size=10)  # Returns list of tuples

# Fetch all rows
all_rows = cursor.fetchall()  # Returns list of tuples

# Iterate directly
cursor.execute("SELECT * FROM users")
for row in cursor:
    print(row)
```

### Insert, Update, Delete

```python
# Insert
cursor.execute(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ["Alice", "alice@example.com"]
)
print(f"Inserted {cursor.rowcount} rows")

# Bulk insert
users = [
    ("Bob", "bob@example.com"),
    ("Charlie", "charlie@example.com"),
]
cursor.executemany(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    users
)

# Update
cursor.execute(
    "UPDATE users SET status = %s WHERE id = %s",
    ["inactive", 42]
)

# Delete
cursor.execute("DELETE FROM users WHERE status = %s", ["deleted"])

# Don't forget to commit!
conn.commit()
```

### Cursor Properties

```python
cursor.description   # Column metadata (name, type_code, ...)
cursor.rowcount      # Number of affected rows
cursor.query         # Last executed query string
cursor.statusmessage # Status message from last operation
```

---

## Transactions

### Explicit Transaction Control

```python
conn.autocommit = False  # Default

try:
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

### Transaction Context Manager

```python
with conn.transaction():
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (message) VALUES (%s)", ["Started"])
    cursor.execute("UPDATE counters SET value = value + 1")
    # Commits automatically on success
    # Rolls back automatically on exception
```

### Isolation Levels

```python
conn.isolation_level = "READ COMMITTED"      # Default
conn.isolation_level = "REPEATABLE READ"
conn.isolation_level = "SERIALIZABLE"
conn.isolation_level = "READ UNCOMMITTED"
```

---

## DuckLake Features

DuckLake provides versioned data storage with time travel, snapshots, and change tracking. All DuckLake methods are available directly on the connection object.

### Catalog Management

```python
# Attach a DuckLake catalog (auto-installs extension)
conn.attach_catalog(
    catalog_path="/data/my_catalog.db",  # Catalog database file
    data_path="/data/parquet/",          # Parquet file directory (optional)
    name="lake"                          # Catalog name (default: "lake")
)

# Switch between catalogs
conn.use_catalog("lake")

# Detach when done
conn.detach_catalog("lake")
```

### Snapshots & Time Travel

Every write creates a new snapshot. Query historical data:

```python
# List all snapshots
snapshots = conn.list_snapshots(catalog="lake")
for snap in snapshots:
    print(f"Snapshot {snap['snapshot_id']} at {snap['timestamp']}")
    print(f"  Tables: {snap['table_count']}")

# Get current snapshot ID
current_id = conn.get_current_snapshot(catalog="lake")

# Query data at a specific version
old_data = conn.query_at_version(
    table="users",
    version=5,
    catalog="lake"
)

# Query data at a specific timestamp
historical = conn.query_at_timestamp(
    table="users",
    timestamp="2025-01-15 10:30:00",
    catalog="lake"
)
```

### Change Data Feed (CDC)

Track exactly what changed between any two points:

```python
# Get changes between snapshot IDs
changes = conn.table_changes(
    table="orders",
    start=10,
    end=20,
    catalog="lake"
)

for change in changes:
    change_type = change['change_type']
    # 'insert'           - New row added
    # 'delete'           - Row removed
    # 'update_preimage'  - Row BEFORE update
    # 'update_postimage' - Row AFTER update

    print(f"{change_type}: order_id={change['id']}")

# Get changes from last week using timestamps
recent = conn.table_changes(
    table="orders",
    start="now() - INTERVAL '7 days'",
    end="now()",
    catalog="lake"
)

# Filter by change type
inserts = [c for c in changes if c['change_type'] == 'insert']
deletes = [c for c in changes if c['change_type'] == 'delete']
updates = [c for c in changes if 'update' in c['change_type']]
```

### Metadata Introspection

Query database structure without raw SQL:

```python
# List all tables
tables = conn.list_tables()
for t in tables:
    print(f"{t['schema_name']}.{t['table_name']}")

# List tables in specific schema
lake_tables = conn.list_tables(schema="lake")

# Describe table columns
columns = conn.describe_table("users")
for col in columns:
    print(f"  {col['column_name']}: {col['data_type']}")
    print(f"    nullable: {col.get('is_nullable')}")

# With schema filter
columns = conn.describe_table("users", schema="lake")

# List all schemas
schemas = conn.list_schemas()  # Returns: ['main', 'lake', ...]

# List all views
views = conn.list_views()
views = conn.list_views(schema="lake")

# List extensions
extensions = conn.list_extensions()
for ext in extensions:
    print(f"{ext['extension_name']}: loaded={ext.get('loaded')}")
```

### Maintenance Operations

Keep your DuckLake catalog healthy:

```python
# Checkpoint - flush writes, persist metadata
conn.checkpoint()

# Expire old snapshots
# Use dry_run=True to preview what would be expired
preview = conn.expire_snapshots(
    catalog="lake",
    older_than_days=30,
    dry_run=True
)
print(f"Would expire {len(preview)} snapshots")

# Actually expire
conn.expire_snapshots(catalog="lake", older_than_days=30)

# Clean up unreferenced files
conn.cleanup_files(catalog="lake", older_than_days=7)

# Delete orphaned files (not in catalog metadata)
conn.delete_orphaned_files(catalog="lake", older_than_days=7)

# Optimize storage
conn.merge_adjacent_files(catalog="lake")   # Combine small files
conn.rewrite_data_files(catalog="lake")     # Rewrite for better compression
```

### S3 Configuration

Configure cloud storage access:

```python
# Set S3 region
conn.configure_s3(region="us-west-2")

# With custom endpoint (MinIO, etc.)
conn.configure_s3(region="us-east-1", endpoint="https://minio.example.com")

# Create S3 credentials

# Option 1: AWS SSO
conn.create_s3_secret(
    credential_source="sso",
    region="us-west-2",
    profile="my-sso-profile"
)

# Option 2: AWS profile (~/.aws/credentials)
conn.create_s3_secret(
    credential_source="profile",
    region="us-west-2",
    profile="default"
)

# Option 3: Explicit credentials
conn.create_s3_secret(
    credential_source="env",
    region="us-west-2",
    key_id="AKIAIOSFODNN7EXAMPLE",
    secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
)

# Option 4: IAM role (EC2, ECS, Lambda)
conn.create_s3_secret(
    credential_source="iam",
    region="us-west-2"
)
```

### Extension Management

```python
# Install an extension
conn.install_extension("httpfs")
conn.install_extension("json")

# Load an extension
conn.load_extension("httpfs")
```

---

## Async API

For asyncio applications, use the async interface:

```python
import asyncio
from ducklingaling import aio

async def main():
    # Connect
    conn = await aio.connect(
        host="localhost",
        port=5432,
        user="admin",
        password="secret"
    )

    # Execute and fetch all
    rows = await conn.fetch("SELECT * FROM users WHERE active = $1", True)

    # Fetch single row
    row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", 42)

    # Fetch single value
    count = await conn.fetchval("SELECT COUNT(*) FROM users")

    # Execute without results
    await conn.execute(
        "INSERT INTO users (name) VALUES ($1)",
        "Alice"
    )

    await conn.close()

asyncio.run(main())
```

### Async Context Manager

```python
async with aio.connect(host="localhost", user="admin", password="secret") as conn:
    rows = await conn.fetch("SELECT * FROM users")
```

### Async Transactions

```python
async with aio.connect(...) as conn:
    async with conn.transaction():
        await conn.execute("UPDATE accounts SET balance = balance - $1 WHERE id = $2", 100, 1)
        await conn.execute("UPDATE accounts SET balance = balance + $1 WHERE id = $2", 100, 2)
        # Auto-commits on success, auto-rollbacks on exception
```

### Async Connection Pool

```python
async def main():
    pool = await aio.create_pool(
        host="localhost",
        user="admin",
        password="secret",
        min_size=5,
        max_size=20
    )

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users")

    await pool.close()
```

---

## Connection Pooling

For multi-threaded applications:

```python
import ducklingaling
from concurrent.futures import ThreadPoolExecutor

# Create pool
pool = ducklingaling.create_pool(
    minconn=5,           # Minimum connections
    maxconn=20,          # Maximum connections
    host="localhost",
    user="admin",
    password="secret"
)

def process_order(order_id):
    with pool.connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM orders WHERE id = %s",
            [order_id]
        )
        return cursor.fetchone()

# Use with thread pool
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(process_order, order_ids))

# Close pool when done
pool.closeall()
```

### Pool Properties & Methods

```python
pool.size       # Current number of connections
pool.available  # Number of available connections
pool.in_use     # Number of connections in use
pool.closed     # Whether pool is closed

pool.getconn()  # Get a connection (manual management)
pool.putconn(conn)  # Return a connection
pool.resize(min_size, max_size)  # Resize pool
pool.check()    # Health check
pool.closeall() # Close all connections
```

---

## DataFrame Integration

Requires `pandas` extra: `pip install ducklingaling[pandas]`

```python
import ducklingaling

with ducklingaling.connect(...) as conn:
    cursor = conn.execute("SELECT * FROM sales WHERE year = 2024")

    # Fetch as DataFrame
    df = cursor.fetchdf()

    # Now use pandas!
    print(df.head())
    print(df.describe())

    top_products = df.groupby('product')['revenue'].sum().nlargest(10)
```

### Insert from DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'score': [95.5, 87.3, 92.1]
})

with ducklingaling.connect(...) as conn:
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO students (id, name, score) VALUES (%s, %s, %s)",
        df.values.tolist()
    )
    conn.commit()
```

---

## Error Handling

The library uses DB-API 2.0 standard exceptions:

```python
from ducklingaling import (
    Error,              # Base exception
    Warning,            # Warnings
    InterfaceError,     # Client/interface errors
    DatabaseError,      # Database errors (base)
    DataError,          # Data processing errors
    OperationalError,   # Connection/operational errors
    IntegrityError,     # Constraint violations
    InternalError,      # Internal database errors
    ProgrammingError,   # SQL syntax/programming errors
    NotSupportedError,  # Unsupported operations
)
```

### Exception Hierarchy

```
Error
├── InterfaceError
└── DatabaseError
    ├── DataError
    ├── OperationalError
    ├── IntegrityError
    ├── InternalError
    ├── ProgrammingError
    └── NotSupportedError
```

### Error Handling Examples

```python
import ducklingaling
from ducklingaling import OperationalError, ProgrammingError, IntegrityError

# Connection errors
try:
    conn = ducklingaling.connect(host="nonexistent", timeout=5)
except OperationalError as e:
    print(f"Could not connect: {e}")

# SQL errors
try:
    cursor.execute("SELEC * FORM users")  # Typos!
except ProgrammingError as e:
    print(f"SQL syntax error: {e}")

# Constraint violations
try:
    cursor.execute("INSERT INTO users (id) VALUES (1)")  # Duplicate key
except IntegrityError as e:
    print(f"Constraint violation: {e}")

# Catch all database errors
try:
    cursor.execute(some_query)
except DatabaseError as e:
    print(f"Database error: {e}")
    conn.rollback()
```

---

## Type Reference

### PostgreSQL to Python Type Mapping

| PostgreSQL Type      | Python Type         |
|---------------------|---------------------|
| `INTEGER`, `BIGINT` | `int`               |
| `FLOAT`, `DOUBLE`   | `float`             |
| `NUMERIC`, `DECIMAL`| `decimal.Decimal`   |
| `TEXT`, `VARCHAR`   | `str`               |
| `BOOLEAN`           | `bool`              |
| `TIMESTAMP`         | `datetime.datetime` |
| `DATE`              | `datetime.date`     |
| `TIME`              | `datetime.time`     |
| `JSON`, `JSONB`     | `dict` or `list`    |
| `UUID`              | `uuid.UUID`         |
| `BYTEA`             | `bytes`             |
| `ARRAY`             | `list`              |

### DB-API Type Objects

```python
from ducklingaling import STRING, BINARY, NUMBER, DATETIME, ROWID

# Check column types
if cursor.description[0][1] == NUMBER:
    print("First column is numeric")
```

---

## Migration from psycopg2

ducklingaling is designed as a drop-in replacement for psycopg2:

```python
# Before (psycopg2)
import psycopg2
conn = psycopg2.connect(host="localhost", dbname="mydb", user="admin", password="secret")

# After (ducklingaling)
import ducklingaling
conn = ducklingaling.connect(host="localhost", database="mydb", user="admin", password="secret")
```

### Key Differences

| Feature | psycopg2 | ducklingaling |
|---------|----------|---------------|
| Parameter name | `dbname` | `database` |
| Backend | PostgreSQL | DuckDBLayer |
| DuckLake methods | ❌ | ✅ `conn.list_snapshots()` etc. |
| DataFrame support | ❌ | ✅ `cursor.fetchdf()` |

### What Works the Same

- `cursor.execute()`, `fetchone()`, `fetchall()`, `fetchmany()`
- `conn.commit()`, `rollback()`, `close()`
- Parameterized queries with `%s` and `%(name)s`
- Context managers
- Exception hierarchy
- `cursor.description`, `cursor.rowcount`

---

## Troubleshooting

### Connection Refused

```python
# Check server is running
# Check host/port are correct
# Check firewall allows connection

conn = ducklingaling.connect(
    host="localhost",
    port=5432,
    timeout=10  # Add timeout to fail faster
)
```

### Authentication Failed

```python
# Verify credentials in users.yaml on server
# Check auth method matches (cleartext vs md5)
```

### Query Timeout

```python
# Large queries may timeout
# Configure server-side: query_timeout in config.yaml
```

### Memory Issues with Large Results

```python
# Don't use fetchall() for large results
# Use fetchmany() or iterate:

cursor.execute("SELECT * FROM huge_table")
while True:
    rows = cursor.fetchmany(size=1000)
    if not rows:
        break
    process(rows)
```

### Connection Pool Exhausted

```python
# Increase max pool size
pool = ducklingaling.create_pool(maxconn=50, ...)

# Make sure to return connections
with pool.connection() as conn:
    # Connection returned when block exits
    pass
```

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Links

- [DuckDBLayer Repository](https://github.com/jj-scoll/ducklingaling)
- [Full Documentation](../quickstart.md)
- [DuckLake](https://ducklake.select/)
- [DB-API 2.0 Specification (PEP 249)](https://peps.python.org/pep-0249/)

"""Apply SQL migration files safely and idempotently."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path


def checksum_of(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations(
            name TEXT PRIMARY KEY,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def is_migration_applied(connection: sqlite3.Connection, name: str, checksum: str) -> bool:
    row = connection.execute(
        "SELECT checksum FROM schema_migrations WHERE name = ?",
        (name,),
    ).fetchone()

    if row is None:
        return False

    existing_checksum = row[0]
    if existing_checksum != checksum:
        raise ValueError(f"Migration {name} exists with a different checksum")

    return True


def record_migration(connection: sqlite3.Connection, name: str, checksum: str) -> None:
    connection.execute(
        """
        INSERT INTO schema_migrations(name, checksum)
        VALUES(?, ?)
        ON CONFLICT(name) DO UPDATE SET checksum = excluded.checksum
        """,
        (name, checksum),
    )


def apply_migration(connection: sqlite3.Connection, migration_path: Path) -> bool:
    sql_content = migration_path.read_text(encoding="utf-8")
    migration_checksum = checksum_of(sql_content)

    ensure_migration_table(connection)
    if is_migration_applied(connection, migration_path.name, migration_checksum):
        return False

    connection.executescript(sql_content)
    record_migration(connection, migration_path.name, migration_checksum)
    connection.commit()
    return True


def main() -> None:
    db_path = Path("buzzing.db")
    migration_path = Path("etc/db_config/v1.sql")

    with sqlite3.connect(db_path) as connection:
        applied = apply_migration(connection, migration_path)

    status = "applied" if applied else "already applied"
    print(f"Migration {migration_path.name}: {status}")


if __name__ == "__main__":
    main()

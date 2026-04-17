import sqlite3
from pathlib import Path

from buzzing.scripts.apply_migration import (
    apply_migration,
    ensure_migration_table,
    is_migration_applied,
)


def test_is_migration_applied_returns_true_for_matching_checksum() -> None:
    conn = sqlite3.connect(":memory:")
    ensure_migration_table(conn)
    conn.execute(
        "INSERT INTO schema_migrations(name, checksum) VALUES(?, ?)",
        ("v1.sql", "abc"),
    )

    assert is_migration_applied(conn, "v1.sql", "abc") is True


def test_apply_migration_idempotent(tmp_path: Path) -> None:
    conn = sqlite3.connect(":memory:")
    migration = tmp_path / "v1.sql"
    migration.write_text("CREATE TABLE IF NOT EXISTS t(id INTEGER);", encoding="utf-8")

    first = apply_migration(conn, migration)
    second = apply_migration(conn, migration)

    assert first is True
    assert second is False

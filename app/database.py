"""SQLite helpers for persisting equipment data."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import get_settings

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS big_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sub_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        big_category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY(big_category_id) REFERENCES big_categories(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        purchase_date TEXT,
        has_warranty INTEGER NOT NULL DEFAULT 0,
        warranty_expiry_date TEXT,
        location TEXT,
        status TEXT NOT NULL,
        price_amount TEXT,
        price_currency TEXT,
        purchase_source_name TEXT,
        purchase_source_url TEXT,
        manual_url TEXT,
        manual_file_path TEXT,
        notes TEXT,
        big_category_id INTEGER NOT NULL,
        sub_category_id INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(big_category_id) REFERENCES big_categories(id) ON DELETE CASCADE,
        FOREIGN KEY(sub_category_id) REFERENCES sub_categories(id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS item_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        stored_path TEXT NOT NULL,
        content_type TEXT,
        is_cover INTEGER NOT NULL DEFAULT 0,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_items_big_category ON items(big_category_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_items_sub_category ON items(sub_category_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
    """,
]


def _make_connection(database_path: Path | None = None) -> sqlite3.Connection:
    settings = get_settings()
    path = Path(database_path) if database_path is not None else settings.database_path
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection(database_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Context manager that yields a SQLite connection with foreign keys enabled."""

    conn = _make_connection(database_path)
    try:
        yield conn
    finally:
        conn.close()


def initialize_database(database_path: Path | None = None) -> None:
    """Ensure the schema exists for the configured database."""

    with get_connection(database_path) as conn:
        cursor = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        conn.commit()

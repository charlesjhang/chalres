"""Application configuration helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Container for runtime configuration values."""

    database_path: Path
    storage_root: Path

    @classmethod
    def build(cls) -> "Settings":
        database_value = os.environ.get("DATABASE_PATH", "./equipment.db")
        storage_value = os.environ.get("STORAGE_ROOT", "./storage")
        database_path = Path(database_value).expanduser().resolve()
        storage_root = Path(storage_value).expanduser().resolve()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        storage_root.mkdir(parents=True, exist_ok=True)
        return cls(database_path=database_path, storage_root=storage_root)


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings.build()


def reset_settings_cache() -> None:
    """Clear cached settings (useful for tests)."""

    get_settings.cache_clear()  # type: ignore[attr-defined]

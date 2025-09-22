"""File storage management for equipment assets."""
from __future__ import annotations

import shutil
from pathlib import Path


class StorageManager:
    """Handles storing and removing item-related files."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def item_directory(self, item_id: int) -> Path:
        directory = self.root / "items" / str(item_id)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def image_directory(self, item_id: int) -> Path:
        directory = self.item_directory(item_id) / "images"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def manual_directory(self, item_id: int) -> Path:
        directory = self.item_directory(item_id) / "manuals"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def store_image(self, item_id: int, filename: str, data: bytes) -> Path:
        safe_name = Path(filename).name
        destination = self.image_directory(item_id) / safe_name
        destination.write_bytes(data)
        return destination

    def store_manual(self, item_id: int, filename: str, data: bytes) -> Path:
        safe_name = Path(filename).name
        destination = self.manual_directory(item_id) / safe_name
        destination.write_bytes(data)
        return destination

    def delete_item_files(self, item_id: int) -> None:
        directory = self.root / "items" / str(item_id)
        if directory.exists():
            shutil.rmtree(directory)

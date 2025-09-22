"""Service layer implementing equipment management operations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from .config import get_settings
from .database import get_connection, initialize_database
from .models import BigCategory, Item, ItemImage, SubCategory
from .storage import StorageManager
from .utils import serialize_date, serialize_decimal, serialize_datetime

ALLOWED_STATUSES = {"available", "checked_out", "maintenance"}


@dataclass(slots=True)
class ItemData:
    name: str
    big_category_id: int
    sub_category_id: Optional[int] = None
    status: str = "available"
    description: Optional[str] = None
    purchase_date: Optional[date] = None
    has_warranty: bool = False
    warranty_expiry_date: Optional[date] = None
    location: Optional[str] = None
    price_amount: Optional[Decimal] = None
    price_currency: Optional[str] = None
    purchase_source_name: Optional[str] = None
    purchase_source_url: Optional[str] = None
    manual_url: Optional[str] = None
    notes: Optional[str] = None


UNSET = object()


@dataclass(slots=True)
class ItemUpdateData:
    name: Any = UNSET
    big_category_id: Any = UNSET
    sub_category_id: Any = UNSET
    status: Any = UNSET
    description: Any = UNSET
    purchase_date: Any = UNSET
    has_warranty: Any = UNSET
    warranty_expiry_date: Any = UNSET
    location: Any = UNSET
    price_amount: Any = UNSET
    price_currency: Any = UNSET
    purchase_source_name: Any = UNSET
    purchase_source_url: Any = UNSET
    manual_url: Any = UNSET
    notes: Any = UNSET


class EquipmentService:
    """High level service for managing equipment records."""

    def __init__(self, database_path: Path | None = None, storage_root: Path | None = None) -> None:
        settings = get_settings()
        self.database_path = Path(database_path) if database_path else settings.database_path
        self.storage_root = Path(storage_root) if storage_root else settings.storage_root
        self.storage = StorageManager(self.storage_root)
        initialize_database(self.database_path)

    # ------------------------------------------------------------------
    # Category operations
    # ------------------------------------------------------------------
    def create_big_category(self, name: str, description: Optional[str] = None) -> BigCategory:
        with get_connection(self.database_path) as conn:
            try:
                cursor = conn.execute(
                    "INSERT INTO big_categories (name, description) VALUES (?, ?)", (name, description)
                )
            except Exception as exc:  # sqlite3.IntegrityError
                raise ValueError("Category name already exists") from exc
            conn.commit()
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM big_categories WHERE id = ?", (new_id,)).fetchone()
        return BigCategory.from_row(row)

    def update_big_category(self, category_id: int, *, name: Optional[str] = None, description: Optional[str] = None) -> BigCategory:
        updates = {}
        params: list[object] = []
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if not updates:
            return self.get_big_category(category_id)

        assignments = ", ".join(f"{key} = ?" for key in updates)
        params.extend(updates.values())
        params.append(category_id)

        with get_connection(self.database_path) as conn:
            conn.execute(f"UPDATE big_categories SET {assignments} WHERE id = ?", params)
            conn.commit()
            row = conn.execute("SELECT * FROM big_categories WHERE id = ?", (category_id,)).fetchone()
            if row is None:
                raise ValueError("Category not found")
        return BigCategory.from_row(row)

    def delete_big_category(self, category_id: int) -> None:
        with get_connection(self.database_path) as conn:
            conn.execute("DELETE FROM big_categories WHERE id = ?", (category_id,))
            conn.commit()

    def get_big_category(self, category_id: int) -> BigCategory:
        with get_connection(self.database_path) as conn:
            row = conn.execute("SELECT * FROM big_categories WHERE id = ?", (category_id,)).fetchone()
            if row is None:
                raise ValueError("Category not found")
        return BigCategory.from_row(row)

    def list_big_categories(self, *, include_subcategories: bool = False) -> list[BigCategory]:
        with get_connection(self.database_path) as conn:
            rows = conn.execute("SELECT * FROM big_categories ORDER BY id").fetchall()
            categories = [BigCategory.from_row(row) for row in rows]
            if include_subcategories and categories:
                mapping = {category.id: category for category in categories}
                sub_rows = conn.execute(
                    "SELECT * FROM sub_categories ORDER BY id"
                ).fetchall()
                for sub_row in sub_rows:
                    subcategory = SubCategory.from_row(sub_row)
                    if subcategory.big_category_id in mapping:
                        mapping[subcategory.big_category_id].subcategories.append(subcategory)
        return categories

    def create_subcategory(self, big_category_id: int, name: str, description: Optional[str] = None) -> SubCategory:
        self.get_big_category(big_category_id)
        with get_connection(self.database_path) as conn:
            cursor = conn.execute(
                "INSERT INTO sub_categories (big_category_id, name, description) VALUES (?, ?, ?)",
                (big_category_id, name, description),
            )
            conn.commit()
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM sub_categories WHERE id = ?", (new_id,)).fetchone()
        return SubCategory.from_row(row)

    def update_subcategory(
        self, subcategory_id: int, *, name: Optional[str] = None, description: Optional[str] = None
    ) -> SubCategory:
        updates = {}
        params: list[object] = []
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if not updates:
            return self.get_subcategory(subcategory_id)
        assignments = ", ".join(f"{key} = ?" for key in updates)
        params.extend(updates.values())
        params.append(subcategory_id)
        with get_connection(self.database_path) as conn:
            conn.execute(f"UPDATE sub_categories SET {assignments} WHERE id = ?", params)
            conn.commit()
            row = conn.execute("SELECT * FROM sub_categories WHERE id = ?", (subcategory_id,)).fetchone()
            if row is None:
                raise ValueError("Subcategory not found")
        return SubCategory.from_row(row)

    def delete_subcategory(self, subcategory_id: int) -> None:
        with get_connection(self.database_path) as conn:
            conn.execute("DELETE FROM sub_categories WHERE id = ?", (subcategory_id,))
            conn.commit()

    def get_subcategory(self, subcategory_id: int) -> SubCategory:
        with get_connection(self.database_path) as conn:
            row = conn.execute("SELECT * FROM sub_categories WHERE id = ?", (subcategory_id,)).fetchone()
            if row is None:
                raise ValueError("Subcategory not found")
        return SubCategory.from_row(row)

    def list_subcategories(self, big_category_id: int) -> list[SubCategory]:
        with get_connection(self.database_path) as conn:
            rows = conn.execute(
                "SELECT * FROM sub_categories WHERE big_category_id = ? ORDER BY id",
                (big_category_id,),
            ).fetchall()
        return [SubCategory.from_row(row) for row in rows]

    # ------------------------------------------------------------------
    # Item operations
    # ------------------------------------------------------------------
    def create_item(self, data: ItemData) -> Item:
        self._validate_item_data(data)
        now = datetime.utcnow()
        with get_connection(self.database_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO items (
                    name, description, purchase_date, has_warranty, warranty_expiry_date,
                    location, status, price_amount, price_currency, purchase_source_name,
                    purchase_source_url, manual_url, manual_file_path, notes,
                    big_category_id, sub_category_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.name,
                    data.description,
                    serialize_date(data.purchase_date),
                    int(data.has_warranty),
                    serialize_date(data.warranty_expiry_date),
                    data.location,
                    data.status,
                    serialize_decimal(data.price_amount),
                    self._normalize_currency(data.price_currency),
                    data.purchase_source_name,
                    data.purchase_source_url,
                    data.manual_url,
                    None,
                    data.notes,
                    data.big_category_id,
                    data.sub_category_id,
                    serialize_datetime(now),
                    serialize_datetime(now),
                ),
            )
            conn.commit()
            item_id = cursor.lastrowid
        return self.get_item(item_id)

    def update_item(self, item_id: int, changes: ItemUpdateData) -> Item:
        existing = self.get_item(item_id)
        update_values = self._prepare_update_payload(existing, changes)
        if not update_values:
            return existing
        update_values["updated_at"] = serialize_datetime(datetime.utcnow())
        assignments = ", ".join(f"{key} = ?" for key in update_values.keys())
        params = list(update_values.values()) + [item_id]
        with get_connection(self.database_path) as conn:
            conn.execute(f"UPDATE items SET {assignments} WHERE id = ?", params)
            conn.commit()
        return self.get_item(item_id)

    def get_item(self, item_id: int) -> Item:
        with get_connection(self.database_path) as conn:
            row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
            if row is None:
                raise ValueError("Item not found")
            item = Item.from_row(row)
            image_rows = conn.execute(
                "SELECT * FROM item_images WHERE item_id = ? ORDER BY id",
                (item_id,),
            ).fetchall()
            item.images = [ItemImage.from_row(image_row) for image_row in image_rows]
        return item

    def list_items(
        self,
        *,
        big_category_id: Optional[int] = None,
        sub_category_id: Optional[int] = None,
        status: Optional[str] = None,
        has_warranty: Optional[bool] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Item]:
        clauses = ["1 = 1"]
        params: list[object] = []
        if big_category_id is not None:
            clauses.append("big_category_id = ?")
            params.append(big_category_id)
        if sub_category_id is not None:
            clauses.append("sub_category_id = ?")
            params.append(sub_category_id)
        if status is not None:
            if status not in ALLOWED_STATUSES:
                raise ValueError("Invalid status filter")
            clauses.append("status = ?")
            params.append(status)
        if has_warranty is not None:
            clauses.append("has_warranty = ?")
            params.append(int(has_warranty))
        if location is not None:
            clauses.append("location = ?")
            params.append(location)
        if search:
            clauses.append("(name LIKE ? OR notes LIKE ? OR purchase_source_name LIKE ?)")
            pattern = f"%{search}%"
            params.extend([pattern, pattern, pattern])
        where_clause = " AND ".join(clauses)
        with get_connection(self.database_path) as conn:
            rows = conn.execute(f"SELECT * FROM items WHERE {where_clause} ORDER BY id", params).fetchall()
            items = [Item.from_row(row) for row in rows]
            if items:
                image_rows = conn.execute(
                    "SELECT * FROM item_images WHERE item_id IN (%s) ORDER BY id"
                    % ",".join("?" for _ in items),
                    [item.id for item in items],
                ).fetchall()
                images_by_item: dict[int, list[ItemImage]] = {}
                for image_row in image_rows:
                    image = ItemImage.from_row(image_row)
                    images_by_item.setdefault(image.item_id, []).append(image)
                for item in items:
                    item.images = images_by_item.get(item.id, [])
        return items

    def delete_item(self, item_id: int) -> None:
        self.get_item(item_id)
        with get_connection(self.database_path) as conn:
            conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
            conn.commit()
        self.storage.delete_item_files(item_id)

    # ------------------------------------------------------------------
    # Asset management
    # ------------------------------------------------------------------
    def add_item_image(
        self,
        item_id: int,
        *,
        filename: str,
        data: bytes,
        content_type: Optional[str] = None,
        set_as_cover: bool = False,
    ) -> ItemImage:
        self.get_item(item_id)
        stored_path = self.storage.store_image(item_id, filename, data)
        now = serialize_datetime(datetime.utcnow())
        with get_connection(self.database_path) as conn:
            existing_cover = conn.execute(
                "SELECT id FROM item_images WHERE item_id = ? AND is_cover = 1", (item_id,)
            ).fetchone()
            make_cover = set_as_cover or existing_cover is None
            cursor = conn.execute(
                """
                INSERT INTO item_images (item_id, filename, stored_path, content_type, is_cover, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (item_id, Path(filename).name, str(stored_path), content_type, int(make_cover), now),
            )
            image_id = cursor.lastrowid
            if make_cover and existing_cover is not None:
                conn.execute(
                    "UPDATE item_images SET is_cover = 0 WHERE item_id = ? AND id != ?",
                    (item_id, image_id),
                )
            conn.commit()
            row = conn.execute("SELECT * FROM item_images WHERE id = ?", (image_id,)).fetchone()
        return ItemImage.from_row(row)

    def set_cover_image(self, item_id: int, image_id: int) -> None:
        self.get_item(item_id)
        with get_connection(self.database_path) as conn:
            updated = conn.execute(
                "UPDATE item_images SET is_cover = CASE WHEN id = ? THEN 1 ELSE 0 END WHERE item_id = ?",
                (image_id, item_id),
            )
            if updated.rowcount == 0:
                raise ValueError("Image not found")
            conn.commit()

    def remove_item_image(self, item_id: int, image_id: int) -> None:
        with get_connection(self.database_path) as conn:
            row = conn.execute(
                "SELECT stored_path FROM item_images WHERE id = ? AND item_id = ?",
                (image_id, item_id),
            ).fetchone()
            if row is None:
                raise ValueError("Image not found")
            conn.execute("DELETE FROM item_images WHERE id = ?", (image_id,))
            conn.commit()
        path = Path(row["stored_path"])
        if path.exists():
            path.unlink()

    def add_manual(self, item_id: int, *, filename: str, data: bytes) -> Item:
        self.get_item(item_id)
        stored_path = self.storage.store_manual(item_id, filename, data)
        now = serialize_datetime(datetime.utcnow())
        with get_connection(self.database_path) as conn:
            conn.execute(
                "UPDATE items SET manual_file_path = ?, manual_url = NULL, updated_at = ? WHERE id = ?",
                (str(stored_path), now, item_id),
            )
            conn.commit()
        return self.get_item(item_id)

    def remove_manual(self, item_id: int) -> None:
        item = self.get_item(item_id)
        if item.manual_file_path and item.manual_file_path.exists():
            item.manual_file_path.unlink()
        with get_connection(self.database_path) as conn:
            conn.execute(
                "UPDATE items SET manual_file_path = NULL, updated_at = ? WHERE id = ?",
                (serialize_datetime(datetime.utcnow()), item_id),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _normalize_currency(self, currency: Optional[str]) -> Optional[str]:
        if currency is None:
            return None
        return currency.upper()

    def _validate_item_data(self, data: ItemData) -> None:
        self.get_big_category(data.big_category_id)
        if data.sub_category_id is not None:
            subcategory = self.get_subcategory(data.sub_category_id)
            if subcategory.big_category_id != data.big_category_id:
                raise ValueError("Subcategory does not belong to the selected big category")
        if data.status not in ALLOWED_STATUSES:
            raise ValueError("Invalid item status")
        if data.has_warranty and data.warranty_expiry_date is None:
            raise ValueError("Warranty expiry date required when warranty is active")
        if not data.has_warranty:
            data.warranty_expiry_date = None

    def _prepare_update_payload(self, item: Item, changes: ItemUpdateData) -> dict[str, object]:
        payload: dict[str, object] = {}
        if changes.name is not UNSET:
            payload["name"] = changes.name
        if changes.description is not UNSET:
            payload["description"] = changes.description
        if changes.purchase_date is not UNSET:
            payload["purchase_date"] = serialize_date(changes.purchase_date)
        if changes.has_warranty is not UNSET:
            payload["has_warranty"] = int(changes.has_warranty)
            if changes.has_warranty and (changes.warranty_expiry_date in (UNSET, None)):
                raise ValueError("Warranty expiry date required when enabling warranty")
            payload["warranty_expiry_date"] = serialize_date(
                None if changes.warranty_expiry_date is UNSET else changes.warranty_expiry_date
            )
        elif changes.warranty_expiry_date is not UNSET:
            payload["warranty_expiry_date"] = serialize_date(changes.warranty_expiry_date)
        if changes.location is not UNSET:
            payload["location"] = changes.location
        if changes.status is not UNSET:
            if changes.status not in ALLOWED_STATUSES:
                raise ValueError("Invalid item status")
            payload["status"] = changes.status
        if changes.price_amount is not UNSET:
            payload["price_amount"] = serialize_decimal(changes.price_amount)
        if changes.price_currency is not UNSET:
            payload["price_currency"] = self._normalize_currency(changes.price_currency)
        if changes.purchase_source_name is not UNSET:
            payload["purchase_source_name"] = changes.purchase_source_name
        if changes.purchase_source_url is not UNSET:
            payload["purchase_source_url"] = changes.purchase_source_url
        if changes.manual_url is not UNSET:
            payload["manual_url"] = changes.manual_url
            payload["manual_file_path"] = None
        if changes.notes is not UNSET:
            payload["notes"] = changes.notes
        if changes.big_category_id is not UNSET:
            self.get_big_category(changes.big_category_id)
            payload["big_category_id"] = changes.big_category_id
        if changes.sub_category_id is not UNSET:
            if changes.sub_category_id is None:
                payload["sub_category_id"] = None
            else:
                subcategory = self.get_subcategory(changes.sub_category_id)
                big_id = payload.get("big_category_id", item.big_category_id)
                if subcategory.big_category_id != big_id:
                    raise ValueError("Subcategory does not belong to the selected big category")
                payload["sub_category_id"] = changes.sub_category_id
        return payload

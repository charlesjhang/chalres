"""Dataclasses representing equipment entities."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from sqlite3 import Row

from .utils import parse_date, parse_datetime, parse_decimal, serialize_date, serialize_decimal


@dataclass(slots=True)
class SubCategory:
    id: int
    big_category_id: int
    name: str
    description: Optional[str] = None

    @classmethod
    def from_row(cls, row: Row) -> "SubCategory":
        return cls(
            id=row["id"],
            big_category_id=row["big_category_id"],
            name=row["name"],
            description=row["description"],
        )


@dataclass(slots=True)
class BigCategory:
    id: int
    name: str
    description: Optional[str] = None
    subcategories: list[SubCategory] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: Row) -> "BigCategory":
        return cls(id=row["id"], name=row["name"], description=row["description"])


@dataclass(slots=True)
class ItemImage:
    id: int
    item_id: int
    filename: str
    stored_path: Path
    content_type: Optional[str]
    is_cover: bool
    uploaded_at: datetime

    @classmethod
    def from_row(cls, row: Row) -> "ItemImage":
        return cls(
            id=row["id"],
            item_id=row["item_id"],
            filename=row["filename"],
            stored_path=Path(row["stored_path"]),
            content_type=row["content_type"],
            is_cover=bool(row["is_cover"]),
            uploaded_at=parse_datetime(row["uploaded_at"]),
        )


@dataclass(slots=True)
class Item:
    id: int
    name: str
    big_category_id: int
    sub_category_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
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
    manual_file_path: Optional[Path] = None
    notes: Optional[str] = None
    images: list[ItemImage] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: Row) -> "Item":
        return cls(
            id=row["id"],
            name=row["name"],
            big_category_id=row["big_category_id"],
            sub_category_id=row["sub_category_id"],
            status=row["status"],
            created_at=parse_datetime(row["created_at"]),
            updated_at=parse_datetime(row["updated_at"]),
            description=row["description"],
            purchase_date=parse_date(row["purchase_date"]),
            has_warranty=bool(row["has_warranty"]),
            warranty_expiry_date=parse_date(row["warranty_expiry_date"]),
            location=row["location"],
            price_amount=parse_decimal(row["price_amount"]),
            price_currency=row["price_currency"],
            purchase_source_name=row["purchase_source_name"],
            purchase_source_url=row["purchase_source_url"],
            manual_url=row["manual_url"],
            manual_file_path=Path(row["manual_file_path"]) if row["manual_file_path"] else None,
            notes=row["notes"],
        )

    def serialize(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "purchase_date": serialize_date(self.purchase_date),
            "has_warranty": int(self.has_warranty),
            "warranty_expiry_date": serialize_date(self.warranty_expiry_date),
            "location": self.location,
            "status": self.status,
            "price_amount": serialize_decimal(self.price_amount),
            "price_currency": self.price_currency,
            "purchase_source_name": self.purchase_source_name,
            "purchase_source_url": self.purchase_source_url,
            "manual_url": self.manual_url,
            "manual_file_path": str(self.manual_file_path) if self.manual_file_path else None,
            "notes": self.notes,
            "big_category_id": self.big_category_id,
            "sub_category_id": self.sub_category_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

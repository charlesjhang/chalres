"""Utility helpers for parsing and formatting values."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional


def parse_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    return date.fromisoformat(value)


def serialize_date(value: Optional[date]) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def parse_datetime(value: Optional[str]) -> datetime:
    if value is None:
        raise ValueError("Datetime value cannot be None")
    return datetime.fromisoformat(value)


def serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(value)


def serialize_decimal(value: Optional[Decimal]) -> Optional[str]:
    if value is None:
        return None
    return format(value, "f")

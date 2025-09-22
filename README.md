# Equipment Management Toolkit

This repository contains a pure-Python implementation of an equipment management toolkit based on
the planning document in `docs/equipment_management_plan.md`. The service manages big categories,
subcategories, item metadata, image assets, and manual files while using only the Python standard
library for portability.

## Features

- Create and list big categories with nested subcategories that can be extended at runtime.
- Register equipment items with detailed fields such as purchase information, warranty details, and
  storage locations.
- Persist data to SQLite and attach multiple images per item, including a designated cover image.
- Store usage manuals alongside each item and clear or replace them when needed.
- Search for items by category, status, warranty availability, location, or free-text keywords.

## Project Structure

- `app/config.py` – Reads environment configuration for database and storage paths.
- `app/database.py` – Initializes and manages the SQLite schema.
- `app/models.py` – Dataclasses for categories, items, and item images.
- `app/service.py` – High-level operations for managing categories, items, images, and manuals.
- `app/storage.py` – Handles filesystem persistence for uploaded assets.
- `app/utils.py` – Helpers for parsing and serializing typed values.

## Usage

Instantiate `EquipmentService` to work with the toolkit. By default it stores data in
`./equipment.db` and files under `./storage`, but both paths can be overridden.

```python
from datetime import date
from pathlib import Path

from app import EquipmentService, ItemData

service = EquipmentService(database_path=Path("my-data/equipment.db"), storage_root=Path("my-data/storage"))
category = service.create_big_category("攝影工作室")
subcategory = service.create_subcategory(category.id, "相機")
item = service.create_item(
    ItemData(
        name="主力相機",
        big_category_id=category.id,
        sub_category_id=subcategory.id,
        has_warranty=True,
        warranty_expiry_date=date(2026, 5, 1),
        location="器材櫃",
    )
)
```

Uploaded images and manuals are stored beneath the configured storage directory in
`items/<item_id>/images` and `items/<item_id>/manuals` respectively.

## Running Tests

The repository ships with a pytest suite that exercises the core workflows:

```bash
pytest
```

No external dependencies are required; the project relies solely on Python's standard library.

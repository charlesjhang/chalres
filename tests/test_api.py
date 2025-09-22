from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app import EquipmentService, ItemData, ItemUpdateData


@pytest.fixture
def service(tmp_path: Path) -> EquipmentService:
    database_path = tmp_path / "equipment.db"
    storage_root = tmp_path / "storage"
    return EquipmentService(database_path=database_path, storage_root=storage_root)


def test_category_and_subcategory_workflow(service: EquipmentService) -> None:
    category = service.create_big_category("個人器材", description="個人用")
    subcategory = service.create_subcategory(category.id, "相機")

    categories = service.list_big_categories(include_subcategories=True)
    assert len(categories) == 1
    assert categories[0].name == "個人器材"
    assert categories[0].subcategories[0].name == "相機"

    fetched_subcategories = service.list_subcategories(category.id)
    assert fetched_subcategories[0].id == subcategory.id


def test_item_lifecycle(service: EquipmentService, tmp_path: Path) -> None:
    category = service.create_big_category("攝影工作室")
    subcategory = service.create_subcategory(category.id, "鏡頭")

    item = service.create_item(
        ItemData(
            name="標準鏡頭",
            big_category_id=category.id,
            sub_category_id=subcategory.id,
            has_warranty=True,
            warranty_expiry_date=date(2025, 1, 1),
            location="器材櫃",
            purchase_source_name="攝影器材行",
        )
    )

    assert item.name == "標準鏡頭"
    assert item.has_warranty is True
    assert item.warranty_expiry_date == date(2025, 1, 1)

    updated = service.update_item(
        item.id,
        ItemUpdateData(status="checked_out", location="外借"),
    )
    assert updated.status == "checked_out"
    assert updated.location == "外借"

    image = service.add_item_image(
        item.id,
        filename="lens.jpg",
        data=b"fake-image-bytes",
        content_type="image/jpeg",
    )
    assert image.is_cover is True

    manual_item = service.add_manual(
        item.id, filename="manual.pdf", data=b"manual-data"
    )
    assert manual_item.manual_file_path is not None
    assert manual_item.manual_file_path.exists()
    assert manual_item.manual_file_path.read_bytes() == b"manual-data"

    filtered_items = service.list_items(status="checked_out")
    assert len(filtered_items) == 1
    assert filtered_items[0].id == item.id

    service.remove_manual(item.id)
    cleared = service.get_item(item.id)
    assert cleared.manual_file_path is None

    service.remove_item_image(item.id, image.id)
    remaining = service.get_item(item.id)
    assert remaining.images == []

    service.delete_item(item.id)
    assert service.list_items() == []

    # Ensure storage directory was cleaned up
    item_storage = service.storage.root / "items" / str(item.id)
    assert not item_storage.exists()

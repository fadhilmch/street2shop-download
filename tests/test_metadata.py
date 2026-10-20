import json

import pytest

from downloader.metadata import (
    CATEGORIES,
    MetadataCollector,
    row_to_gallery_entry,
    row_to_pair,
    safe_join,
    write_json,
)


def hf_row(**overrides):
    row = {
        "type": "train",
        "category": "pants",
        "street_photo_id": 2470,
        "product_id": 804,
        "width": 1037.0,
        "top": 3091.0,
        "left": 1267.0,
        "height": 2132.0,
        "shop_photo_id": 555,
    }
    row.update(overrides)
    return row


def test_categories_match_original_protocol():
    assert CATEGORIES == [
        "bags", "belts", "dresses", "eyewear", "footwear", "hats",
        "leggings", "outerwear", "pants", "skirts", "tops",
    ]


def test_row_to_pair_matches_original_format():
    pair = row_to_pair(hf_row())
    assert pair == {
        "photo": 2470,
        "product": 804,
        "bbox": {"width": 1037, "top": 3091, "left": 1267, "height": 2132},
    }


def test_row_to_gallery_entry_matches_original_format():
    assert row_to_gallery_entry(hf_row()) == {"photo": 555, "product": 804}


def test_row_to_pair_rejects_missing_bbox_field():
    row = hf_row()
    del row["width"]
    with pytest.raises(ValueError):
        row_to_pair(row)


def test_collector_dedupes_pairs_and_gallery():
    collector = MetadataCollector()
    assert collector.add_row(hf_row()) is not None
    assert collector.add_row(hf_row(shop_photo_id=556)) is not None  # same pair, other shop image
    assert collector.counters["pairs_duplicate"] == 1
    assert len(collector.pairs[("train", "pants")]) == 1
    assert len(collector.gallery["pants"]) == 2


def test_collector_counts_invalid_rows():
    collector = MetadataCollector()
    assert collector.add_row(hf_row(type="weird")) is None
    assert collector.add_row(hf_row(category="shoes")) is None
    assert collector.counters["rows_invalid"] == 2


def test_remove_pair_and_gallery_entry():
    collector = MetadataCollector()
    _, category, pair = collector.add_row(hf_row())
    collector.remove_pair("train", category, pair)
    collector.remove_gallery_entry(category, 555)
    assert collector.pairs[("train", "pants")] == {}
    assert collector.gallery["pants"] == {}


def test_safe_join_rejects_traversal():
    with pytest.raises(ValueError):
        safe_join("/tmp/root", "..", "escape.txt")


def test_write_files_uses_original_naming(tmp_path):
    collector = MetadataCollector()
    collector.add_row(hf_row())
    collector.add_row(hf_row(type="test", street_photo_id=1, product_id=2, shop_photo_id=9))
    written = collector.write_files(str(tmp_path))
    names = sorted(p.rsplit("/", 1)[-1] for p in written)
    assert names == ["retrieval_pants.json", "test_pairs_pants.json", "train_pairs_pants.json"]
    payload = json.loads((tmp_path / "train_pairs_pants.json").read_text())
    assert payload[0]["bbox"]["width"] == 1037

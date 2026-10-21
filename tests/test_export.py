import json
import os

from PIL import Image

from downloader import export_dataset


def fake_row(split="train", category="pants", street=2470, product=804, shop=555):
    return {
        "type": split,
        "category": category,
        "street_photo_id": street,
        "product_id": product,
        "width": 10.0,
        "top": 5.0,
        "left": 5.0,
        "height": 20.0,
        "shop_photo_id": shop,
        "street_photo_image": Image.new("RGB", (30, 40), (200, 0, 0)),
        "shop_photo_image": Image.new("RGB", (50, 60), (0, 0, 200)),
    }


def loader_from(rows):
    def load(split):
        return [r for r in rows if r["type"] == split]
    return load


def run_export(tmp_path, rows, **kwargs):
    return export_dataset(
        image_dir=str(tmp_path / "images"),
        meta_dir=str(tmp_path / "meta"),
        report_path=str(tmp_path / "report.json"),
        row_loader=loader_from(rows),
        **kwargs,
    )


def test_export_writes_legacy_layout_and_metadata(tmp_path):
    report = run_export(tmp_path, [fake_row(), fake_row(split="test", street=1, product=2, shop=9)])
    assert (tmp_path / "images" / "pants" / "2470.jpg").exists()
    assert (tmp_path / "images" / "pants" / "555.jpg").exists()
    train = json.loads((tmp_path / "meta" / "train_pairs_pants.json").read_text())
    assert train == [{"photo": 2470, "product": 804,
                      "bbox": {"width": 10, "top": 5, "left": 5, "height": 20}}]
    retrieval = json.loads((tmp_path / "meta" / "retrieval_pants.json").read_text())
    assert {e["photo"] for e in retrieval} == {555, 9}
    assert report["images"]["saved"] == 4
    assert report["images"]["failed_or_missing"] == 0


def test_export_is_idempotent(tmp_path):
    rows = [fake_row()]
    first = run_export(tmp_path, rows)
    second = run_export(tmp_path, rows)
    assert first["images"]["saved"] == 2
    assert second["images"]["saved"] == 0
    assert second["images"]["skipped_existing"] == 2


def test_export_respects_max_num_samples_per_class_per_split(tmp_path):
    rows = [fake_row(street=s, product=800 + s, shop=900 + s) for s in range(5)]
    rows += [fake_row(split="test", street=100 + s, product=800 + s, shop=910 + s) for s in range(3)]
    report = run_export(tmp_path, rows, max_num_samples=2)
    assert report["splits"]["train"]["pairs_exported_per_class"] == {"pants": 2}
    assert report["splits"]["test"]["pairs_exported_per_class"] == {"pants": 2}


def test_export_filters_classes(tmp_path):
    rows = [fake_row(), fake_row(category="hats", street=7, product=8, shop=77)]
    run_export(tmp_path, rows, classes=["hats"])
    assert not (tmp_path / "images" / "pants").exists()
    assert (tmp_path / "images" / "hats" / "7.jpg").exists()


def test_missing_street_image_excludes_pair_from_metadata(tmp_path):
    row = fake_row()
    row["street_photo_image"] = None
    report = run_export(tmp_path, [row])
    assert report["images"]["failed_or_missing"] == 1
    assert not (tmp_path / "meta" / "train_pairs_pants.json").exists() or \
        json.loads((tmp_path / "meta" / "train_pairs_pants.json").read_text()) == []


def test_crop_applied_to_street_photo(tmp_path):
    run_export(tmp_path, [fake_row()], crop=True)
    from PIL import Image as PILImage
    with PILImage.open(tmp_path / "images" / "pants" / "2470.jpg") as img:
        assert img.size == (10, 20)


def test_invalid_rows_are_counted_not_fatal(tmp_path):
    bad = fake_row(street=42, product=43, shop=44)
    del bad["width"]
    report = run_export(tmp_path, [bad, fake_row()])
    assert report["metadata"]["rows_invalid"] == 1
    assert (tmp_path / "images" / "pants" / "2470.jpg").exists()


def test_unknown_category_rejected(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        run_export(tmp_path, [], classes=["shoes"])

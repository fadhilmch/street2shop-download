"""Metadata handling for the Street2Shop exporter.

Converts rows from the Hugging Face copy (petr7555/street2shop) into the
original Street2Shop metadata format and collects export statistics:

- train_pairs_<category>.json / test_pairs_<category>.json:
  [{"photo": street_photo_id, "product": product_id,
    "bbox": {"width": w, "top": y, "left": x, "height": h}}, ...]
- retrieval_<category>.json (subset gallery, exported shop photos only):
  [{"photo": shop_photo_id, "product": product_id}, ...]
"""

import json
import os

from .image_processing import validate_bbox

CATEGORIES = [
    "bags",
    "belts",
    "dresses",
    "eyewear",
    "footwear",
    "hats",
    "leggings",
    "outerwear",
    "pants",
    "skirts",
    "tops",
]

REQUIRED_ROW_KEYS = (
    "type",
    "category",
    "street_photo_id",
    "product_id",
    "shop_photo_id",
)


def row_split(row):
    """Original protocol split for a row: 'train' or 'test'."""
    split = row.get("type")
    if split not in ("train", "test"):
        raise ValueError(f"unexpected row type: {split!r}")
    return split


def row_to_pair(row):
    """Convert one HF row to the original train/test pair format."""
    missing = [k for k in REQUIRED_ROW_KEYS if k not in row or row[k] is None]
    if missing:
        raise ValueError(f"row missing fields: {', '.join(missing)}")
    bbox = validate_bbox(
        {k: row.get(k) for k in ("width", "top", "left", "height")}
    )
    return {
        "photo": int(row["street_photo_id"]),
        "product": int(row["product_id"]),
        "bbox": bbox,
    }


def row_to_gallery_entry(row):
    """Convert one HF row to the original retrieval-list format."""
    if row.get("shop_photo_id") is None or row.get("product_id") is None:
        raise ValueError("row missing shop_photo_id or product_id")
    return {
        "photo": int(row["shop_photo_id"]),
        "product": int(row["product_id"]),
    }


def safe_join(root, *parts):
    """Join path parts and verify the result stays inside root."""
    root_abs = os.path.abspath(root)
    path = os.path.abspath(os.path.join(root_abs, *parts))
    if path != root_abs and not path.startswith(root_abs + os.sep):
        raise ValueError(f"unsafe export path outside {root_abs}: {path}")
    return path


def write_json(root, filename, payload):
    """Write payload as JSON inside root, creating directories."""
    path = safe_join(root, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f)
    return path


class MetadataCollector:
    """Accumulates validated, deduplicated metadata and export counters."""

    def __init__(self):
        self.pairs = {}       # (split, category) -> {(photo, product): pair}
        self.gallery = {}     # category -> {shop_photo_id: entry}
        self.counters = {
            "rows_seen": 0,
            "rows_invalid": 0,
            "pairs_duplicate": 0,
            "gallery_duplicate": 0,
        }

    def add_row(self, row):
        """Register one row. Returns (split, category, pair) or None."""
        self.counters["rows_seen"] += 1
        try:
            category = row["category"]
            if category not in CATEGORIES:
                raise ValueError(f"unknown category: {category!r}")
            split = row_split(row)
            pair = row_to_pair(row)
            entry = row_to_gallery_entry(row)
        except (KeyError, ValueError):
            self.counters["rows_invalid"] += 1
            return None

        pair_key = (pair["photo"], pair["product"])
        bucket = self.pairs.setdefault((split, category), {})
        if pair_key in bucket:
            self.counters["pairs_duplicate"] += 1
        else:
            bucket[pair_key] = pair

        gallery = self.gallery.setdefault(category, {})
        if entry["photo"] in gallery:
            self.counters["gallery_duplicate"] += 1
        else:
            gallery[entry["photo"]] = entry
        return split, category, pair

    def remove_pair(self, split, category, pair):
        """Drop a pair (e.g. its images failed to export)."""
        bucket = self.pairs.get((split, category), {})
        bucket.pop((pair["photo"], pair["product"]), None)

    def remove_gallery_entry(self, category, entry_photo):
        self.gallery.get(category, {}).pop(entry_photo, None)

    def write_files(self, meta_dir):
        """Write all metadata files in the original naming scheme."""
        written = []
        for (split, category), bucket in sorted(self.pairs.items()):
            path = write_json(
                meta_dir, f"{split}_pairs_{category}.json", list(bucket.values())
            )
            written.append(path)
        for category, gallery in sorted(self.gallery.items()):
            path = write_json(
                meta_dir, f"retrieval_{category}.json", list(gallery.values())
            )
            written.append(path)
        return written

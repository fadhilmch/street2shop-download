"""Streaming export of the Street2Shop dataset from Hugging Face.

Loads the community copy (petr7555/street2shop) with the `datasets`
library in streaming mode and writes the legacy on-disk layout:

    <image_dir>/<category>/<street_photo_id>.jpg   (street photos)
    <image_dir>/<category>/<shop_photo_id>.jpg     (shop photos)
    <meta_dir>/{train,test}_pairs_<category>.json  (pair metadata)
    <meta_dir>/retrieval_<category>.json           (exported shop photos only)

Memory stays bounded: rows are streamed and images are written one at a
time; only compact metadata accumulates. Re-running an export skips
images that are already on disk, so interrupted runs resume cheaply.
"""

import json
import os
import sys

from .image_processing import crop_to_bbox
from .metadata import CATEGORIES, MetadataCollector, safe_join, write_json

DATASET_ID = "petr7555/street2shop"


def iter_hf_rows(split):
    """Yield rows of the Hugging Face copy for one split (streaming).

    Imported lazily so the rest of the package works without `datasets`
    installed (e.g. in tests).
    """
    from datasets import load_dataset

    dataset = load_dataset(DATASET_ID, split=split, streaming=True)
    yield from dataset


def _save_image(image, path):
    """Save a PIL image as JPEG. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image.convert("RGB").save(path, "JPEG")
        return True
    except Exception:
        return False


def export_dataset(
    classes=None,
    split="all",
    image_dir="images/",
    meta_dir="meta/json/",
    crop=False,
    max_num_samples=None,
    report_path="export_report.json",
    row_loader=None,
    progress=None,
):
    """Export Street2Shop images and metadata from the Hugging Face copy.

    Args:
        classes: categories to export (default: all 11).
        split: "train", "test" or "all".
        image_dir: root directory for exported images.
        meta_dir: directory for the generated metadata JSON files.
        crop: crop street photos to their bounding box before saving.
        max_num_samples: maximum pairs exported per category per split.
        report_path: where to write the JSON export report.
        row_loader: optional callable(split) -> iterable of rows, used to
            substitute the Hugging Face source (e.g. in tests).
        progress: optional rich.progress.Progress for terminal feedback.

    Returns:
        The export report as a dict. Counts reflect only what actually
        landed on disk; sampling-based completeness claims about the
        upstream copy are out of scope here.
    """
    load_rows = row_loader or iter_hf_rows
    classes = classes or CATEGORIES
    unknown = [c for c in classes if c not in CATEGORIES]
    if unknown:
        raise ValueError(f"unknown categories: {', '.join(unknown)}")
    splits = ["train", "test"] if split == "all" else [split]

    collector = MetadataCollector()
    images_saved = 0
    images_skipped_existing = 0
    images_failed = 0
    crops_applied = 0
    crops_failed = 0
    per_split = {}

    task_ids = {}
    for current_split in splits:
        if progress is not None:
            task_ids[current_split] = progress.add_task(
                f"[cyan]{current_split}[/cyan] rows", total=None
            )
        exported_per_class = {c: 0 for c in classes}
        rows_in_split = 0

        for row in load_rows(current_split):
            rows_in_split += 1
            if progress is not None:
                progress.advance(task_ids[current_split])
            category = row.get("category")
            if category not in classes:
                continue
            registered = collector.add_row(row)
            if registered is None:
                continue
            row_split_name, _, pair = registered
            if exported_per_class[category] >= (
                max_num_samples or float("inf")
            ):
                collector.remove_pair(row_split_name, category, pair)
                continue

            street_path = safe_join(
                image_dir, category, f"{pair['photo']}.jpg"
            )
            shop_id = row.get("shop_photo_id")
            shop_path = safe_join(image_dir, category, f"{shop_id}.jpg")

            street_ok = True
            street_written = False
            if os.path.exists(street_path):
                images_skipped_existing += 1
            else:
                street_image = row.get("street_photo_image")
                if street_image is None:
                    street_ok = False
                elif crop:
                    try:
                        street_image = crop_to_bbox(street_image, pair["bbox"])
                        crops_applied += 1
                    except ValueError:
                        crops_failed += 1
                if street_ok:
                    street_ok = _save_image(street_image, street_path)
                    street_written = street_ok

            shop_ok = True
            shop_written = False
            if os.path.exists(shop_path):
                images_skipped_existing += 1
            else:
                shop_image = row.get("shop_photo_image")
                if shop_image is not None:
                    shop_ok = _save_image(shop_image, shop_path)
                    shop_written = shop_ok
                else:
                    shop_ok = False

            # Metadata only covers what actually landed on disk, so the
            # export stays self-consistent for downstream training code.
            if not street_ok:
                images_failed += 1
                collector.remove_pair(row_split_name, category, pair)
                continue
            if not shop_ok:
                images_failed += 1
                collector.remove_gallery_entry(category, shop_id)
            images_saved += int(street_written) + int(shop_written)
            exported_per_class[category] += 1

        per_split[current_split] = {
            "rows_seen": rows_in_split,
            "pairs_exported_per_class": {
                c: n for c, n in exported_per_class.items() if n
            },
        }
        if progress is not None:
            progress.update(
                task_ids[current_split],
                description=f"[green]{current_split}[/green] done "
                f"({rows_in_split} rows)",
            )

    meta_files = collector.write_files(meta_dir)
    report = {
        "dataset": DATASET_ID,
        "splits": per_split,
        "images": {
            "saved": images_saved,
            "skipped_existing": images_skipped_existing,
            "failed_or_missing": images_failed,
        },
        "crops": {"applied": crops_applied, "failed": crops_failed},
        "metadata": {
            **collector.counters,
            "files_written": len(meta_files),
            "directory": os.path.abspath(meta_dir),
        },
        "image_directory": os.path.abspath(image_dir),
    }
    with open(os.path.abspath(report_path), "w") as f:
        json.dump(report, f, indent=2)
    return report

"""Image helpers for the Street2Shop exporter.

Only Pillow is required. The bounding-box format matches the original
Street2Shop metadata: {"width": w, "top": y, "left": x, "height": h}.
"""

BBOX_KEYS = ("width", "top", "left", "height")


def validate_bbox(bbox):
    """Return a bbox as plain ints, or raise ValueError.

    The Hugging Face copy stores bbox fields as float32; the original
    JSON files use ints, so values are rounded to the nearest int.
    """
    if not isinstance(bbox, dict):
        raise ValueError(f"bbox must be a mapping, got {type(bbox).__name__}")
    missing = [k for k in BBOX_KEYS if k not in bbox]
    if missing:
        raise ValueError(f"bbox missing keys: {', '.join(missing)}")
    try:
        normalized = {k: int(round(float(bbox[k]))) for k in BBOX_KEYS}
    except (TypeError, ValueError) as exc:
        raise ValueError(f"bbox values must be numeric: {exc}") from exc
    if normalized["width"] <= 0 or normalized["height"] <= 0:
        raise ValueError(
            f"bbox width/height must be positive, got "
            f"{normalized['width']}x{normalized['height']}"
        )
    return normalized


def crop_to_bbox(image, bbox):
    """Crop a PIL image to the bbox, clamped to the image bounds.

    Returns a new image. Raises ValueError when the bbox is invalid or
    lies fully outside the image.
    """
    box = validate_bbox(bbox)
    left = max(0, box["left"])
    top = max(0, box["top"])
    right = min(image.width, box["left"] + box["width"])
    bottom = min(image.height, box["top"] + box["height"])
    if right <= left or bottom <= top:
        raise ValueError(
            f"bbox {box} does not intersect image of size {image.size}"
        )
    return image.crop((left, top, right, bottom))

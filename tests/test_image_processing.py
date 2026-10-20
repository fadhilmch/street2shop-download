import pytest
from PIL import Image

from downloader.image_processing import crop_to_bbox, validate_bbox


def make_image(width=100, height=80):
    return Image.new("RGB", (width, height), color=(10, 20, 30))


def test_validate_bbox_rounds_hf_floats():
    bbox = validate_bbox({"width": 1037.4, "top": 3091.6, "left": 1267.0, "height": 2132.0})
    assert bbox == {"width": 1037, "top": 3092, "left": 1267, "height": 2132}


@pytest.mark.parametrize(
    "bbox",
    [
        {"width": 0, "top": 0, "left": 0, "height": 10},
        {"width": 10, "top": 0, "left": 0, "height": -3},
        {"width": 10, "top": 0, "left": 0},
        "not-a-dict",
        {"width": "x", "top": 0, "left": 0, "height": 5},
    ],
)
def test_validate_bbox_rejects_bad_input(bbox):
    with pytest.raises(ValueError):
        validate_bbox(bbox)


def test_crop_exact_region():
    image = make_image()
    cropped = crop_to_bbox(image, {"width": 30, "top": 10, "left": 20, "height": 40})
    assert cropped.size == (30, 40)


def test_crop_clamps_to_image_bounds():
    image = make_image()
    cropped = crop_to_bbox(image, {"width": 500, "top": -20, "left": 90, "height": 500})
    assert cropped.size == (10, 80)


def test_crop_outside_image_raises():
    image = make_image()
    with pytest.raises(ValueError):
        crop_to_bbox(image, {"width": 10, "top": 500, "left": 500, "height": 10})

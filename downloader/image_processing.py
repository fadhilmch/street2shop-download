import logging
import os
import urllib.request

import cv2
from PIL import Image


def create_dir(directory: str) -> None:
    """
    Create a directory if it does not exist

    Args:
        directory: str, path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_image(url: str, output_path: str) -> None:
    """
    Downloads an image from the specified URL and saves it to the given output path.
    Args:
        url (str): The URL of the image to download.
        output_path (str): The local file path where the downloaded image will be saved.
    Raises:
        Exception: If there is an error during the download process, it will be logged.
    """

    try:
        urllib.request.urlretrieve(url, output_path)
    except Exception as e:
        logging.error(f"Error downloading image from {url}: {e}")


def verify_image(image_file: str) -> bool:
    """
    Verifies if the given image file is a valid image.

    This function attempts to open and verify the image file using the PIL library.
    If the image is valid, the function returns True. If an error occurs during
    verification, the function logs the error and returns False.

    Args:
        image_file (str): The path to the image file to be verified.

    Returns:
        bool: True if the image is valid, False otherwise.
    """
    try:
        img = Image.open(image_file)
        img.verify()
    except Exception as e:
        logging.error(f"Error verifying image {image_file}: {e}")
        return False
    return True


def crop_image(image_file: str, bbox: dict) -> None:
    """
    Crops an image based on the provided bounding box coordinates.

    This function reads the image file using OpenCV, crops the image based on the
    bounding box coordinates, and overwrites the original image file with the cropped version.

    Args:
        image_file (str): The path to the image file to be cropped.
        bbox (dict): A dictionary containing the bounding box coordinates with keys 'top', 'left', 'height', and 'width'.
    """
    image = cv2.imread(image_file)
    cropped = image[
        bbox["top"] : bbox["top"] + bbox["height"],
        bbox["left"] : bbox["left"] + bbox["width"],
    ]
    cv2.imwrite(image_file, cropped)


def verify_image_and_crop(file_path: str, bbox: dict, crop: bool) -> None:
    """
    Verifies the integrity of an image file and optionally crops it based on the provided bounding box.

    Args:
        file_path (str): The path to the image file to be verified and potentially cropped.
        bbox (dict): A dictionary containing the bounding box coordinates with keys 'top', 'left', 'height', and 'width'.
        crop (bool): A flag indicating whether to crop the image if it is verified successfully.

    Side Effects:
        - Removes the image file if it fails verification.
        - Logs an error message if the image file is removed.
        - Overwrites the image file with the cropped version if cropping is enabled.
    """
    if not verify_image(file_path):
        os.remove(file_path)
        logging.error(f"Removed {file_path}")
    else:
        if crop:
            crop_image(file_path, bbox)

import logging
import os
import urllib
from concurrent.futures.thread import ThreadPoolExecutor

from progress.bar import Bar

from .image_processing import create_dir, download_image, verify_image_and_crop
from .metadata import create_images_list, loa


def download_process(item_id: int, url: str, images_dir: str, bbox: dict, crop: bool):
    """
    Downloads an image from a given URL, saves it to a specified directory, and optionally crops it.
    Args:
        item_id (int): The unique identifier for the item.
        url (str): The URL of the image to download.
        images_dir (str): The directory where the image will be saved.
        bbox (dict): The bounding box coordinates for cropping the image.
        crop (bool): A flag indicating whether to crop the image based on the bounding box.
    Raises:
        urllib.error.HTTPError: If an HTTP error occurs during the download.
        urllib.error.URLError: If a URL error occurs during the download.
        OSError: If an OS-related error occurs during file operations.
        Exception: For any other unexpected errors.
    """

    create_dir(images_dir)
    file_output = os.path.join(images_dir, str(item_id) + "." + "JPEG")

    try:
        download_image(url, file_output)
        verify_image_and_crop(file_output, bbox, crop)
    except urllib.error.HTTPError as e:
        logging.error(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        logging.error(f"URL Error: {e.reason}")
    except OSError as e:
        logging.error(f"OS Error: {e.strerror}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


def download_images(images_list: list, threads: int, crop: bool) -> None:
    """
    Downloads images concurrently using a thread pool.
    Args:
        images_list (list): A list of dictionaries, each containing:
            - item_id (str): The ID of the item.
            - url (str): The URL of the image to download.
            - images_dir (str): The directory where the image should be saved.
            - bbox (tuple): The bounding box coordinates for cropping the image.
        threads (int): The number of threads to use for downloading images.
        crop (bool): Whether to crop the images based on the bounding box.
    Returns:
        None
    """
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for x in images_list:
            executor.submit(
                download_process,
                x["item_id"],
                x["url"],
                x["images_dir"],
                x["bbox"],
                crop,
            )


def read_class(
    class_name: str,
    max_num_samples: int,
    url_dict: dict,
    images_dir: str,
    threads: int,
    crop: bool,
) -> None:
    """
    Downloads images for a specified class from a given URL dictionary.
    Args:
        class_name (str): The name of the class for which images are to be downloaded.
        max_num_samples (int): The maximum number of images to download.
        url_dict (dict): A dictionary containing URLs of images.
        images_dir (str): The directory where the downloaded images will be stored.
        threads (int): The number of threads to use for downloading images.
        crop (bool): Whether to crop the images after downloading.
    Returns:
        None
    """
    file_loc = f"meta/json/train_pairs_{class_name}.json"
    meta_data = load_metadata(file_loc)
    images_list = create_images_list(meta_data, max_num_samples, url_dict)

    bar = Bar(
        "Downloading",
        max=len(images_list),
        suffix="%(percent)d%%",
    )

    for i in range(0, len(images_list), threads):
        download_images(images_list[i : i + threads], threads, crop)
        bar.next(n=threads)

    bar.finish()

    output_dir = os.path.join(images_dir, class_name)
    downloaded_images_count = len(next(os.walk(output_dir))[2])
    print(f"Downloaded {downloaded_images_count} images for class {class_name}")

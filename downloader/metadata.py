import json


def load_metadata(file_loc: str) -> dict:
    """
    Load metadata from a JSON file.
    Args:
        file_loc (str): The location of the JSON file to be loaded.
    Returns:
        dict: The metadata loaded from the JSON file.
    """

    with open(file_loc, "r") as file_json:
        return json.load(file_json)


def create_images_list(meta_data: dict, max_num_samples: int, url_dict: dict) -> list:
    """
    Creates a list of image metadata dictionaries from the provided metadata and URL dictionary.
    Args:
        meta_data (dict): A dictionary containing metadata for images.
        max_num_samples (int): The maximum number of samples to include in the list. If None, all samples are included.
        url_dict (dict): A dictionary mapping photo IDs to their corresponding URLs.
    Returns:
        list: A list of dictionaries, each containing 'item_id', 'url', and 'bbox' keys.
    """

    images_list = []
    for i, data in enumerate(meta_data):
        if max_num_samples is not None and i >= max_num_samples:
            break
        photo_id = int(data["photo"])
        url = url_dict[photo_id]
        bbox = data["bbox"]
        images_list.append({"item_id": photo_id, "url": url, "bbox": bbox})
    return images_list

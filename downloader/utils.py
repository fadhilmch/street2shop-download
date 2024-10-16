import argparse

from config import DEFAULT_CLASSES, DEFAULT_IMAGE_DIR, DEFAULT_THREADS


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Download images from Street2Shop dataset"
    )

    parser.add_argument(
        "--urls", dest="urls", type=str, required=True, help="URLs file"
    )
    parser.add_argument(
        "--image_dir",
        dest="images_dir",
        type=str,
        default=DEFAULT_IMAGE_DIR,
        help="Image directory",
    )
    parser.add_argument("--log", dest="log", type=str, help="Log errors")
    parser.add_argument(
        "--threads",
        dest="threads",
        type=int,
        default=DEFAULT_THREADS,
        help="Number of threads",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        dest="classes",
        type=str,
        default=DEFAULT_CLASSES,
        help="Specific fashion classes to download",
    )
    parser.add_argument(
        "--max_num_samples",
        dest="max_num_samples",
        type=int,
        help="Maximum number of samples",
    )
    parser.add_argument(
        "--crop",
        dest="crop",
        action="store_true",
        help="Crop image based on given bounding box",
    )

    return parser.parse_args()

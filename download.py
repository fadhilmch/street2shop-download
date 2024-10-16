import logging

from downloader import parse_arguments, read_class


def main(args):
    print("Start downloading images from Street2Shop dataset...")

    # Set up logging
    if args.log is not None:
        logging.basicConfig(
            filename=args.log, format="%(message)s", level=logging.ERROR
        )

    with open(args.urls, "r") as f:
        url_list = f.read().split("\n")
        url_dict = dict(
            [(int(line.split(",")[0]), line.split(",")[1]) for line in url_list]
        )

    for class_name in args.classes:
        read_class(
            class_name,
            args.max_num_samples,
            url_dict,
            args.images_dir,
            args.threads,
            args.crop,
        )


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
    print("Finished")
    exit(0)

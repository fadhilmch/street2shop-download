# Street2Shop Dataset Downloader

Downloader for the [Street2Shop](https://tamaraberg.com/papers/street2shop.pdf) dataset (*Where to Buy It: Matching Street Clothing Photos in Online Shops*, ICCV 2015).

<img src="/assets/street2shop.jpg" width="480">

The original download sources (`tamaraberg.com/street2shop/`, `wheretobuyit/photos.tar`, `wheretobuyit/meta.zip`) went offline, so this tool now loads the community copy on Hugging Face - [petr7555/street2shop](https://huggingface.co/datasets/petr7555/street2shop) - and exports the same on-disk layout the original tooling produced: per-category images plus `train_pairs_*`, `test_pairs_*` and `retrieval_*` metadata JSONs. The dataset itself is never committed to this repository.

# Requirements

```sh
$ pip install -r requirements.txt
```

# Usage

<img src="/assets/screenrecords.gif" width="480">

* Option 1: Export the full dataset (all categories, both splits)

```sh
$ python download.py
```

* Option 2: Export per class, cropped to the bounding boxes

```sh
$ python download.py --classes bags pants tops --crop
```

* Extra: Running Options

```sh
  --classes               Categories to export [default: all 11]
  --split                 train, test or all [default: all]
  --image_dir             Output images directory [default: images/]
  --meta_dir              Output metadata directory [default: meta/json/]
  --max_num_samples       Maximum pairs exported per category per split
  --crop                  Crop each street photo using the bounding box data
  --report                Path for the JSON export report [default: export_report.json]
```

Images land in `images/<category>/<photo_id>.jpg` (street photos by street photo id, shop photos by shop photo id) and metadata in `meta/json/` using the original file naming, so downstream code written for the 2015 dataset layout keeps working. Re-running an export skips images already on disk. The export report lists rows seen, invalid rows, images saved/skipped/failed, crops applied and metadata files written.

# Development

```sh
$ pip install -r requirements-dev.txt
$ python -m pytest tests/
```

# Data notes and provenance

- The Hugging Face copy is **community-provided, not an official release**. Spot checks against the archived original metadata (see below) matched on pair ids, categories, bounding boxes and train/test assignment, but that is sampling, not a completeness guarantee.
- Rows are stored per shop image, so one original street-to-product pair yields several rows. Some shop-image rows are missing upstream (dead image URLs already when the copy was made), so per-pair shop-photo coverage varies.
- The copy covers the train/test pair data. The full original retrieval-benchmark gallery (~205k products) is **not** included; generated `retrieval_*.json` files therefore describe only the exported shop photos (a subset gallery).
- Images are exported as decoded by the Hugging Face copy. Shop photos are capped around 913px wide upstream; street photos may be full resolution.
- The original metadata and URL lists are archived at the Wayback Machine ([meta.zip, Feb 2019](https://web.archive.org/web/20190223052128id_/http://tamaraberg.com/street2shop/wheretobuyit/meta.zip), [photos.tar, Feb 2019](https://web.archive.org/web/20190223045729id_/http://tamaraberg.com/street2shop/wheretobuyit/photos.tar)) and were used to validate this exporter's output format.
- The dataset remains subject to the original Street2Shop terms: research use, and cite the ICCV 2015 paper.

# Changes from the URL-scraping version

The previous release scraped image URLs from the (now offline) tamaraberg.com files. That code was removed: `--urls`, `--log` and `--threads` no longer exist, and OpenCV/progress were replaced by `datasets` + `Pillow` (+ `rich` for the terminal UI). The old `--image_dir`, `--classes`, `--max_num_samples` and `--crop` options are preserved with the same meaning. The last URL-scraping revision remains available in the Git history.

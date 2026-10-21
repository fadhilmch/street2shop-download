# Street2Shop Dataset Downloader

Command-line exporter for the Street2Shop dataset (*Where to Buy It: Matching Street Clothing Photos in Online Shops*, ICCV 2015). It writes street and shop photos plus pair metadata in the same on-disk layout as the original tooling, so code written against the 2015 release keeps working.

![Street2Shop sample](/assets/street2shop.jpg)

## Data source

The original hosts (`tamaraberg.com/street2shop/`) are offline. The exporter loads the community copy on Hugging Face, [petr7555/street2shop](https://huggingface.co/datasets/petr7555/street2shop). The dataset is never committed to this repository.

## Requirements

- Python 3
- Dependencies: `datasets`, `pillow`, `rich`

```sh
pip install -r requirements.txt
```

## Usage

Export everything (all 11 categories, train and test):

```sh
python download.py
```

Export selected categories, cropping street photos to their bounding boxes:

```sh
python download.py --classes bags pants tops --crop
```

Quick trial with a few pairs:

```sh
python download.py --classes bags --split test --max_num_samples 10
```

### Options

| Option | Description | Default |
| --- | --- | --- |
| `--classes` | Categories to export: `bags`, `belts`, `dresses`, `eyewear`, `footwear`, `hats`, `leggings`, `outerwear`, `pants`, `skirts`, `tops` | all 11 |
| `--split` | `train`, `test` or `all` | `all` |
| `--image_dir` | Output directory for images | `images/` |
| `--meta_dir` | Output directory for metadata | `meta/json/` |
| `--max_num_samples` | Maximum pairs exported per category per split | no limit |
| `--crop` | Crop each street photo to its bounding box | off |
| `--report` | Path of the JSON export report | `export_report.json` |

Re-running an export skips images already on disk, so interrupted runs can be resumed.

## Output

```text
images/<category>/<street_photo_id>.jpg    street photos
images/<category>/<shop_photo_id>.jpg      shop photos
meta/json/train_pairs_<category>.json      training pairs
meta/json/test_pairs_<category>.json       test pairs
meta/json/retrieval_<category>.json        retrieval list (subset, see limitations)
export_report.json                         export summary
```

Pair files contain entries of the form:

```json
{"photo": 123, "product": 456, "bbox": {"width": 10, "top": 20, "left": 30, "height": 40}}
```

Retrieval files contain `{"photo": <shop_photo_id>, "product": <product_id>}`.

`export_report.json` counts rows seen, invalid rows, images saved, skipped and failed, crops applied and failed, and metadata files written.

## Limitations

- **Community copy.** The Hugging Face dataset is not an official release. Spot checks against the archived original metadata matched on pair ids, categories, bounding boxes and train/test assignment. This is sampling, not a guarantee of completeness.
- **Incomplete retrieval gallery.** The copy has the train/test pair data only. The original retrieval benchmark gallery (about 205k products) is not included, so the generated `retrieval_*.json` files describe only the exported shop photos.
- **Missing shop photos.** One street-to-product pair yields several shop-image rows. Some rows are missing upstream, so shop-photo coverage per pair varies.
- **Image size.** Images are exported as decoded from the Hugging Face copy. Shop photos are capped at about 913px wide upstream. Street photos may be full resolution.
- **Testing.** The unit tests pass locally. A live export was only run on a few pairs because of Hugging Face rate limits. A full-dataset export has not been validated end to end.

## Development

```sh
pip install -r requirements-dev.txt
python -m pytest tests/
```

## Changes from the URL-scraping version

The previous release scraped image URLs from the offline `tamaraberg.com` files. That code is removed: `--urls`, `--log` and `--threads` no longer exist, and OpenCV and progress were replaced by `datasets`, `Pillow` and `rich`. `--image_dir`, `--classes`, `--max_num_samples` and `--crop` keep their meaning. The last URL-scraping revision is in the Git history.

## License and citation

This repository only contains the exporter code. The dataset itself comes from the original authors and the Hugging Face copy, and this README does not grant any rights to it. Check the [original project page](https://web.archive.org/web/2019/http://tamaraberg.com/street2shop/) and the Hugging Face dataset page for terms of use, and cite the ICCV 2015 paper if you use the data:

> Kiapour, Han, Lazebnik, Berg, Berg. *Where to Buy It: Matching Street Clothing Photos in Online Shops.* ICCV 2015.

The original metadata and photo archives are preserved on the Wayback Machine ([meta.zip](https://web.archive.org/web/20190223052128id_/http://tamaraberg.com/street2shop/wheretobuyit/meta.zip), [photos.tar](https://web.archive.org/web/20190223045729id_/http://tamaraberg.com/street2shop/wheretobuyit/photos.tar)).

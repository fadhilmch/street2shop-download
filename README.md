# Street2Shop Dataset Downloader

Downloader for [Street2Shop](http://www.tamaraberg.com/street2shop/) Dataset

<img src="/assets/street2shop.jpg" width="480">

> **Status note (October 2026): the original download sources are gone.**
> The official Street2Shop page and the files referenced under **Requirements** below (`tamaraberg.com/street2shop/`, `wheretobuyit/photos.tar`, `wheretobuyit/meta.zip`) now return 404, so those steps no longer work as written. The URL lists are still archived on the [Wayback Machine](https://web.archive.org/web/2019*/http://www.tamaraberg.com/street2shop/wheretobuyit/photos.tar), but roughly half of a sample of the individual image URLs were dead, and the street-photo host (modcloth.net) is gone entirely - so a full end-to-end scrape is no longer possible. The downloader code is kept here for reference.

## Recommended alternative: Hugging Face

A community copy of the dataset, with images and metadata included, is available on Hugging Face: [petr7555/street2shop](https://huggingface.co/datasets/petr7555/street2shop). It provides `train` and `test` splits in parquet format, with the original fields (`type`, `category`, `street_photo_id`, `product_id`, the bounding box `top` / `left` / `width` / `height`, and `shop_photo_id`) plus the image columns `street_photo_image` and `shop_photo_image`:

```python
# pip install datasets
from datasets import load_dataset

ds = load_dataset("petr7555/street2shop")  # {'train': ..., 'test': ...}

sample = ds["train"][0]
print(sample["category"])                                    # e.g. "pants"
print(sample["top"], sample["left"],
      sample["width"], sample["height"])                   # bounding box
sample["street_photo_image"]                               # PIL.Image
sample["shop_photo_image"]                                 # PIL.Image
```

The Hugging Face copy is community-provided, not an official release. The dataset remains subject to the original Street2Shop terms - use it for research purposes and cite the paper: [Where to Buy It: Matching Street Clothing Photos in Online Shops](https://tamaraberg.com/papers/street2shop.pdf) (ICCV 2015).

# Requirements

* Install Python Packages

```
$ pip install -r requirements.txt
```

* Download and unarchieve images url list
```sh
$ curl http://www.tamaraberg.com/street2shop/wheretobuyit/photos.tar | tar x
```
* Download and unzip class list
```sh
$ curl -O http://www.tamaraberg.com/street2shop/wheretobuyit/meta.zip
$ unzip meta.zip
$ rm meta.zip
```

# Usage

<img src="/assets/screenrecords.gif" width="480">

* Option 1: Download all images from URL list

```sh
$ python download.py --urls photos/photos.txt --crop
```

* Option 2: Download images per class from URL list 

```sh
$ python download.py --urls photos/photos.txt --classes bags pants tops --crop
```

* Extra: Running Options
```sh
  --urls                  Path to urls list file [Required]
  --image_dir             Output images directory [default: /images/]
  --log                   Path to log file
  --threads               Number of threads to execute [default: 10]
  --classes               Download images per class
  --max_num_samples       Maximum number of files to download
  --crop                  Crop each image using the bounding box data
```

# Street2Shop Dataset Downloader

Downloader for [Street2Shop](http://www.tamaraberg.com/street2shop/) Dataset

<img src="/assets/street2shop.jpg" width="480">

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

* Option 3: Download only the shop images that have a matching street image
```sh
$ python download.py --urls photos/photos.txt --domains shop --match
```

* Extra: Running Options
```sh
  --urls                  Path to urls list file [Required]
  --image_dir             Output images directory [default: /images/]
  --domains               Specific one or more photo domains to download. Allowed domains are: street, shop [default: street]
  --match                 Only download the shop photos that have a matching street photo if the shop domain is specified
  --log                   Path to log file
  --threads               Number of threads to execute [default: 10]
  --classes               Download images per class
  --max_num_samples       Maximum number of files to download
  --crop                  Crop each image using the bounding box data
```

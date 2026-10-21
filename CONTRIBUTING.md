# Contributing

Thanks for helping with the Street2Shop exporter. This guide covers setup, tests and what a good pull request looks like.

## Setup

You need **Python 3.11 or newer**. The pinned `pillow` release does not install on Python 3.10. Tests pass on 3.11, 3.12 and 3.13.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/
```

## Project layout

- `download.py`: command-line entry point and terminal output.
- `downloader/download_manager.py`: streams the Hugging Face dataset and writes images and the export report.
- `downloader/metadata.py`: converts dataset rows to the legacy pair and retrieval JSON files.
- `downloader/image_processing.py`: image saving and bounding-box cropping.
- `tests/`: unit tests. They do not download the dataset.

## Running an export

Export a small sample first. Real exports use a lot of disk space and network, and Hugging Face may rate-limit you.

```sh
python download.py --classes bags --split test --max_num_samples 10
```

`images/`, `meta/` and `export_report.json` are in `.gitignore`. Never commit exported data.

## Pull requests

- Keep each pull request focused on one change.
- Add or update tests for behavior changes. Tests must pass without network access.
- Update the README if you change a command-line option or the output layout.
- Do not add dataset files, credentials or tokens to the repository.

## Dataset and licensing

This repository holds exporter code only. The data comes from the community copy [petr7555/street2shop](https://huggingface.co/datasets/petr7555/street2shop) of the original Street2Shop dataset. Check the original project and the Hugging Face page for the terms that apply to the data. The repository does not currently include a license file.

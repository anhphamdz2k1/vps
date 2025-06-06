# Douyin Bulk Downloader

This Python project downloads Douyin videos in bulk from a list of share URLs.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
1. Create a text file (e.g. `urls.txt`) containing one Douyin share URL per line.
2. Run the downloader:
```bash
python -m douyin_downloader.main urls.txt --out videos
```
Downloaded videos will appear in the specified output directory (default `downloads`).

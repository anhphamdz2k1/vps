import os
import re
import json
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}


def fetch_video_url(share_url: str) -> str:
    """Fetch direct video URL from a Douyin share link."""
    # Resolve the share link to the real video page
    resp = requests.get(share_url, headers=HEADERS, allow_redirects=True, timeout=10)
    resp.raise_for_status()
    video_page_url = resp.url

    # Fetch video page HTML
    page = requests.get(video_page_url, headers=HEADERS, timeout=10)
    page.raise_for_status()

    # The page contains JSON data inside a script tag with id="RENDER_DATA"
    soup = BeautifulSoup(page.text, "html.parser")
    render_data_script = soup.find("script", id="RENDER_DATA")
    if not render_data_script:
        raise ValueError("Cannot find RENDER_DATA in page")

    data = json.loads(requests.utils.unquote(render_data_script.string))
    # Navigate the nested structure to find play address
    for key in data:
        item = data[key].get('aweme', {}).get('detail', {})
        if 'video' in item:
            play_addr = item['video']['playAddr'][0]['src']
            return play_addr
    raise ValueError("Video URL not found")


def download_video(video_url: str, output_dir: str, filename: str):
    """Download video from direct URL to output_dir/filename"""
    resp = requests.get(video_url, headers=HEADERS, stream=True, timeout=10)
    resp.raise_for_status()
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filepath


def download_from_file(url_file: str, output_dir: str):
    """Download all Douyin videos listed in url_file."""
    with open(url_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for i, url in enumerate(urls, 1):
        try:
            print(f"Processing {url}...")
            video_url = fetch_video_url(url)
            filename = f"video_{i}.mp4"
            path = download_video(video_url, output_dir, filename)
            print(f"Saved to {path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bulk Douyin video downloader")
    parser.add_argument("url_file", help="Path to text file with Douyin share URLs")
    parser.add_argument("--out", default="downloads", help="Output directory")
    args = parser.parse_args()

    download_from_file(args.url_file, args.out)

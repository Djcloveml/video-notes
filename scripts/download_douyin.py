#!/usr/bin/env python3
"""
Download Douyin videos WITHOUT login (no browser, no cookies).
Vendored into video-notes for self-containment.

Route: short link -> iesdouyin share page HTML -> play_addr video_id
-> aweme play API (no-watermark first, watermark fallback).

Usage:
    python download_direct.py <url> [--output <dir>] [--info-only]

Examples:
    python download_direct.py https://v.douyin.com/xxx
    python download_direct.py "8.79 08/17 ... https://v.douyin.com/xxx/ 复制此链接..." --output ./videos
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests

UA_MOBILE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
HEADERS = {"User-Agent": UA_MOBILE, "Referer": "https://www.iesdouyin.com/"}


def extract_url(text: str) -> str:
    """Pull the douyin URL out of a pasted share text."""
    m = re.search(r"https?://(?:v\.douyin\.com|www\.iesdouyin\.com|www\.douyin\.com)\S+", text)
    if not m:
        sys.exit("Error: no douyin URL found in input")
    return m.group(0).rstrip("/）)。")


def get_share_page(url: str) -> str:
    """Follow redirects to the iesdouyin share page and return its HTML."""
    r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
    r.raise_for_status()
    return r.text


def parse_video(html: str) -> dict:
    """Extract video metadata from the share page HTML."""
    i = html.find('"play_addr"')
    if i == -1:
        sys.exit("Error: play_addr not found in share page (video may be deleted or region-locked)")
    blob = html[i : i + 2000]
    m = re.search(r'"uri":\s*"(v[0-9a-z]+)"', blob)
    if not m:
        sys.exit("Error: video uri not found in play_addr")
    video_uri = m.group(1)

    def grab(pattern):
        mm = re.search(pattern, html)
        return mm.group(1) if mm else None

    return {
        "video_uri": video_uri,
        "title": grab(r'"desc":\s*"((?:[^"\\]|\\.)*)"'),
        "author": grab(r'"nickname":\s*"((?:[^"\\]|\\.)*)"'),
        "duration_ms": grab(r'"duration":\s*(\d+)'),
        "aweme_id": grab(r'"itemId":\s*"(\d+)"') or grab(r"/video/(\d+)"),
    }


def play_url(video_uri: str, kind: str) -> str:
    return (
        f"https://aweme.snssdk.com/aweme/v1/{kind}/"
        f"?line=0&logo_name=aweme_diversion_search&ratio=720p&video_id={video_uri}"
    )


def download(video_uri: str, out_path: Path) -> Path:
    """Try no-watermark first, fall back to watermark."""
    for kind in ("play", "playwm"):
        r = requests.get(play_url(video_uri, kind), headers=HEADERS, timeout=120, stream=True)
        if r.status_code != 200:
            continue
        data = r.content
        if len(data) < 100_000 or not data[4:8] == b"ftyp":
            continue
        out_path.write_bytes(data)
        return out_path
    sys.exit("Error: both play and playwm download failed")


def safe_name(s: str, fallback: str) -> str:
    s = re.sub(r'[\\/:*?"<>|#]', "", (s or "").strip())[:50]
    return s or fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="douyin URL or full share text")
    ap.add_argument("--output", default=".", help="output directory")
    ap.add_argument("--info-only", action="store_true")
    args = ap.parse_args()

    url = extract_url(args.url)
    html = get_share_page(url)
    info = parse_video(html)

    if info["title"]:
        try:
            info["title"] = json.loads(f'"{info["title"]}"')
        except Exception:
            pass
    if info["author"]:
        try:
            info["author"] = json.loads(f'"{info["author"]}"')
        except Exception:
            pass

    dur = int(info["duration_ms"] or 0) / 1000
    print(f"标题: {info['title']}")
    print(f"作者: {info['author']}")
    print(f"时长: {int(dur // 60)}:{int(dur % 60):02d}")
    print(f"video_uri: {info['video_uri']}")

    if args.info_only:
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"{safe_name(info['title'], 'douyin')}_{info['aweme_id'] or info['video_uri']}.mp4"
    out_path = out_dir / name
    download(info["video_uri"], out_path)
    print(f"已下载: {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

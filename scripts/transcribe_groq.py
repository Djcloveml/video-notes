#!/usr/bin/env python3
"""
Transcribe audio/video via Groq cloud Whisper API (free tier: whisper-large-v3-turbo).

Usage:
    python transcribe_groq.py <media_file> [--language zh]

- Input: mp4/mp3/wav/m4a... Video files are auto-converted to 16kHz mono mp3 via ffmpeg.
- Output: <name>_字幕.srt and <name>_全文.txt next to the input file.
- API key: env GROQ_API_KEY, or file ~/.asr/groq_api_key
- Network: Groq is overseas; tries direct, then local proxies 7897 / 15715.

Requires: ffmpeg on PATH (only for video input), curl on PATH.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# 直连 → 本地代理常见端口。可用环境变量自定义：VIDEO_NOTES_PROXIES="http://127.0.0.1:1080,..."
PROXIES = [None] + [p.strip() for p in os.environ.get(
    "VIDEO_NOTES_PROXIES", "http://127.0.0.1:7897,http://127.0.0.1:15715"
).split(",") if p.strip()]
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".webm"}


def get_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        f = Path.home() / ".asr" / "groq_api_key"
        if f.exists():
            key = f.read_text(encoding="utf-8").strip()
    if not key:
        sys.exit("Error: no Groq API key. Set GROQ_API_KEY or write it to ~/.asr/groq_api_key")
    return key


def to_audio(media: Path) -> Path:
    if media.suffix.lower() in AUDIO_EXTS:
        return media
    out = media.with_suffix(".audio.mp3")
    print(f"extracting audio -> {out.name}")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(media),
         "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k", str(out)],
        check=True,
    )
    return out


def transcribe(audio: Path, key: str, language: str) -> dict:
    cmd_base = [
        "curl", "-s", "--max-time", "280",
        "https://api.groq.com/openai/v1/audio/transcriptions",
        "-H", f"Authorization: Bearer {key}",
        "-F", f"file=@{audio}",
        "-F", "model=whisper-large-v3-turbo",
        "-F", f"language={language}",
        "-F", "response_format=verbose_json",
        "-F", "timestamp_granularities[]=segment",
    ]
    last_err = ""
    for proxy in PROXIES:
        cmd = cmd_base + (["-x", proxy] if proxy else [])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            r = subprocess.run(cmd + ["-o", tmp_path, "-w", "%{http_code}"],
                               capture_output=True, text=True, timeout=300)
            code = r.stdout.strip()
            body = Path(tmp_path).read_text(encoding="utf-8", errors="ignore")
            if code == "200":
                return json.loads(body)
            last_err = f"http {code}: {body[:300]}"
        except Exception as e:
            last_err = str(e)[:300]
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        print(f"  retry ({'direct' if proxy is None else proxy} failed)")
    sys.exit(f"Error: Groq transcription failed. {last_err}")


def srt_ts(t: float) -> str:
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media", help="audio or video file path")
    ap.add_argument("--language", default="zh")
    args = ap.parse_args()

    media = Path(args.media)
    if not media.exists():
        sys.exit(f"Error: file not found: {media}")

    audio = to_audio(media)
    size_mb = audio.stat().st_size / 1e6
    if size_mb > 25:
        sys.exit(f"Error: audio is {size_mb:.0f}MB, over Groq free-tier 25MB limit. "
                 f"Re-encode smaller (e.g. -b:a 24k) or split the file.")

    print(f"transcribing {audio.name} ({size_mb:.1f}MB) via Groq ...")
    result = transcribe(audio, get_key(), args.language)
    segs = result.get("segments", [])
    if not segs:
        sys.exit("Error: no segments in response")

    stem = media.stem
    srt_path = media.with_name(f"{stem}_字幕.srt")
    txt_path = media.with_name(f"{stem}_全文.txt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, s in enumerate(segs, 1):
            f.write(f"{i}\n{srt_ts(s['start'])} --> {srt_ts(s['end'])}\n{s['text'].strip()}\n\n")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(s["text"].strip() for s in segs))

    dur = result.get("duration", 0)
    print(f"OK: {len(segs)} segments, duration {int(dur//60)}:{int(dur%60):02d}")
    print(f"  {srt_path}")
    print(f"  {txt_path}")


if __name__ == "__main__":
    main()

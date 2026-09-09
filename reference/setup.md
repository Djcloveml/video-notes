# Dependencies & setup

Run `scripts/setup.sh` — it checks everything and creates the venv automatically. This file explains what each dependency is for.

| Dependency | Purpose | Install |
|---|---|---|
| uv (or python 3.10+) | create the dedicated venv | `brew install uv` / https://docs.astral.sh/uv/ |
| ffmpeg | extract audio from video | `brew install ffmpeg` / apt / winget |
| curl | call the Groq API | ships with the OS |
| requests (inside the venv) | Douyin download script | installed automatically by setup.sh |
| Groq API key | cloud transcription | free at console.groq.com → write to `~/.asr/groq_api_key` |
| yt-dlp (optional) | Bilibili/YouTube etc. | `brew install yt-dlp` |

## The venv convention `$PY`

Always `~/video-notes-env` (created by setup.sh):

- macOS / Linux: `PY=~/video-notes-env/bin/python`
- Windows: `PY=~/video-notes-env/Scripts/python.exe` (**do not use the system `python`** — on Windows it often resolves to the WindowsApps stub and fails instantly)

Add packages: `uv pip install --python $PY <pkg>` (slow PyPI? `UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`).

## Network

- Chinese sites (Douyin etc.): direct connection (unset proxy vars first).
- Groq: overseas; the script retries common local proxy ports automatically; customize via `VIDEO_NOTES_PROXIES` (see `transcription.md`).

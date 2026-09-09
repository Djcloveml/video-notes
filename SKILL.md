---
name: video-notes
description: "Video knowledge-extraction pipeline for any video site (Douyin, YouTube, Bilibili, and 1000+ via yt-dlp): link / local file → captions or transcription → structured knowledge notes stored in a self-contained VideoNotes/ folder. Use when the user shares a video link or paste-text and asks to extract key points, transcribe subtitles, analyze a video, or take notes (e.g. \"提取知识点\", \"转字幕\", \"做笔记\"), or wants a local video/audio file transcribed and summarized. Transcription defaults to Groq cloud Whisper (free tier); no local GPU required."
---

# Video Notes: video → transcript → knowledge notes

Turn knowledge videos into structured Markdown notes. Full pipeline: acquire → transcribe → write.

## Workflow checklist (in order, check off as you go)

- [ ] **0. Environment check (first use / any error)**: run `scripts/setup.sh`. If it prints **FIRST_RUN**, present the fallback-strategy choice to the user (a/b/c, with pros/cons as printed), record their answer via `bash scripts/setup.sh --set-strategy <choice>` — this is asked **once**, config persists in `~/.video-notes/config.json`, later runs never ask again. Also tell the user any missing dependency with its install command and wait before continuing.
- [ ] **1. Acquire the video**: route by source per `reference/acquire.md` (caption-first for YouTube/Bilibili; Douyin direct script; yt-dlp for everything else; browser fallback only if configured)
- [ ] **2. Transcribe**: `scripts/transcribe_groq.py`, details in `reference/transcription.md`
- [ ] **3. Write the knowledge note**: the agent writes it; conventions in `reference/note-writing.md`
- [ ] **4. Store**: everything lives under a `VideoNotes/` folder at the project (or working-directory) root — one subfolder per video: `VideoNotes/YYYYMMDD-<topic>/` holding the video file, `*_字幕.srt`, `*_全文.txt`, and the note. Nothing leaves this folder; no external knowledge base is touched.

## Conventions

- Chinese sites (Douyin etc.): **direct connection, no proxy**. Groq is overseas; the script retries direct → common local proxy ports automatically (configurable via env var).
- If Groq free tier fails, **say so explicitly** — never silently fall back to a local solution. Only use faster-whisper when the user asks for local transcription (see `reference/transcription.md`).
- Notes stay faithful to the video; fix obvious ASR homophone errors in the note but never touch the SRT.

## Layout

```
video-notes/
├── SKILL.md                  # this file: router
├── reference/
│   ├── acquire.md            # per-platform acquisition (incl. Douyin anti-bot fallback)
│   ├── transcription.md      # transcription details & local fallback
│   ├── note-writing.md       # note-writing conventions
│   ├── setup.md              # dependency purposes & install
│   └── evals.md              # regression scenarios after changes
└── scripts/
    ├── setup.sh              # env check + venv creation (execute, don't read)
    ├── download_douyin.py    # no-login Douyin direct download
    └── transcribe_groq.py    # Groq cloud transcription (SRT + full text)
```

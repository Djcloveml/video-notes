# video-notes — video link in, folder of notes out

[![Version](https://img.shields.io/github/v/release/Djcloveml/video-notes?label=version&color=blue)](https://github.com/Djcloveml/video-notes/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Djcloveml/video-notes.svg?logo=github)](https://github.com/Djcloveml/video-notes/stargazers)
[![skills.sh](https://skills.sh/b/Djcloveml/video-notes)](https://skills.sh/Djcloveml/video-notes)

English | [中文](./README_CN.md)

Drop a video link in the chat. Get back a folder with the subtitles, the full text, and a note you can actually review later.

<p>
  <a href="#install"><strong>Install</strong></a> ·
  <a href="#the-pipeline"><strong>Pipeline</strong></a> ·
  <a href="#first-run"><strong>First Run</strong></a> ·
  <a href="#what-it-wont-do"><strong>Limits</strong></a>
</p>

I kept saving knowledge videos on Douyin, YouTube, and Bilibili, and never rewatched any of them. This skill turns each one into a folder of text I can search and skim. A 5-minute video becomes a page I can read in 40 seconds.

## The pipeline

```
link or local file
  → captions first (YouTube / Bilibili: official subtitles, no ASR)
  → otherwise download (Douyin direct / yt-dlp) and transcribe (Groq cloud Whisper, free tier)
  → agent writes a structured note with a timestamped outline
  → everything lands in VideoNotes/YYYYMMDD-<topic>/  (video + SRT + full text + note)
```

A real output, from a 5-minute Douyin video about monetizing a personal brand:

```
VideoNotes/20260907-personal-brand/
├── jianghushuo.mp4                    # the original video
├── jianghushuo_transcript.srt         # 201 segments, timestamped
├── jianghushuo_fulltext.txt           # plain full text
└── notes.md                           # timeline table + layered breakdown
```

## Install

One command, powered by the open [skills](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills add Djcloveml/video-notes
```

The CLI walks you through picking agents and scope interactively. To skip the prompts:

<details>
<summary><strong>Claude Code</strong></summary>

```bash
npx skills add Djcloveml/video-notes --agent claude-code -y
```

</details>

<details>
<summary><strong>Kimi Code</strong></summary>

```bash
npx skills add Djcloveml/video-notes --agent kimi-code -y
```

</details>

<details>
<summary><strong>Codex / Cursor / others</strong></summary>

```bash
npx skills add Djcloveml/video-notes --agent codex -y
npx skills add Djcloveml/video-notes --agent cursor -y
```

Full list: [75+ supported agents](https://github.com/vercel-labs/skills#supported-agents).

</details>

Useful flags:

- `-g` — install globally (~ directory), available in every project. Without it, the skill installs into the current project only.
- `--copy` — copy files instead of symlinking (pick this if you plan to hack on the skill).
- `-l` — list what's in the repo before installing.

The repo is private while in early development. Until it goes public, installs need GitHub auth on your machine (`gh auth login`, or set `GITHUB_TOKEN`) — the CLI picks it up automatically. After that, the plain command works as-is.

To verify the install, send your agent a video link and say "提取知识点" (or "take notes on this video"). First run starts with a short setup check — see below.

## First run

The skill checks your machine with `scripts/setup.sh` and tells you what to install: ffmpeg, a Python venv (it creates `~/video-notes-env` itself), a free Groq API key, and yt-dlp. Each missing item comes with the install command.

It also asks you one question, once, and remembers the answer:

- **(a) No fallback** (default): if a site blocks plain downloads, the skill reports the failure and stops.
- **(b) Browser fallback**: a CDP-capable browser controller (Playwright, or an agent-browser skill you already have) captures the real network response, which beats most anti-bot walls. You want this if your Douyin direct downloads start failing.
- **(c) API-only**: captions via APIs for YouTube/Bilibili, nothing else.

Pick (a) if you mostly use YouTube/Bilibili. Pick (b) if you live on Douyin.

## What it won't do

- Douyin changes its anti-bot measures every few months. The direct-link route has broken once already; the browser fallback exists for exactly this reason. If neither works on a given day, the skill says so instead of silently failing.
- Groq's free tier caps at about 8 hours of audio a day and 25MB per file. Long recordings need splitting or a paid key.
- ASR makes homophone errors, especially with jargon. The note step fixes the obvious ones; the SRT always keeps the raw transcript.
- Videos behind a login wall need a browser session where you're already logged in.

## Layout

```
video-notes/
├── SKILL.md                 # the pipeline contract
├── reference/               # loaded only when needed
│   ├── acquire.md           #   per-site routing, caption-first, CDP fallback
│   ├── transcription.md     #   Groq details, local faster-whisper option
│   ├── note-writing.md      #   note structure and rules
│   ├── setup.md             #   what each dependency is for
│   └── evals.md             #   regression scenarios
└── scripts/
    ├── setup.sh             #   env check + first-run onboarding
    ├── download_douyin.py   #   no-login Douyin download
    └── transcribe_groq.py   #   audio → SRT + full text
```

## License

[MIT](LICENSE).

# Transcription (Groq cloud Whisper)

## Usage

```bash
$PY scripts/transcribe_groq.py <video-or-audio-path>          # $PY: see setup.md
```

- Video is auto-converted to 16kHz mono mp3 via ffmpeg (fits Groq's 25MB free-tier limit).
- Outputs `*_transcript.srt` (timestamped) and `*_fulltext.txt` next to the input file.
- The script itself has zero Python-package dependencies — it shells out to ffmpeg + curl.
- Free tier ≈ 8 hours of audio per day; beyond that you get HTTP 429 — tell the user plainly, retry tomorrow or use the fallback below.

## API key

Env var `GROQ_API_KEY`, or one line of key text in `~/.asr/groq_api_key`. Free signup at console.groq.com.

## Network

Groq is overseas. The script retries in order: direct → common local proxy ports (7897 / 15715). To customize:

```bash
export VIDEO_NOTES_PROXIES="http://127.0.0.1:1080,http://127.0.0.1:8080"
```

## Fallback: local faster-whisper (only when the user explicitly asks)

- `uv pip install --python $PY faster-whisper`, pull the `large-v3-turbo` model from HuggingFace, run CPU int8.
- Use only when the user asks for local transcription or accepts it after repeated Groq failures; explain the speed/accuracy trade-off first.

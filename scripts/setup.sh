#!/usr/bin/env bash
# video-notes environment check + venv creation (macOS / Linux / Windows Git Bash)
# Usage: bash setup.sh
# Note: always brace-expand variables (${VAR}) — bash 3.2 (stock macOS) merges
# CJK punctuation bytes into $VAR names and errors out under set -u.
set -u

ok()   { printf "  [✓] %s\n" "$1"; }
miss() { printf "  [✗] %s\n         -> %s\n" "$1" "$2"; }

OS="$(uname -s 2>/dev/null || echo unknown)"
echo "== video-notes environment check (OS: ${OS}) =="

# ---------- ffmpeg / curl ----------
echo "[transcription deps]"
command -v ffmpeg >/dev/null 2>&1 && ok "ffmpeg: $(command -v ffmpeg)" || miss "ffmpeg" "macOS: brew install ffmpeg / Ubuntu: apt install ffmpeg / Windows: winget install ffmpeg"
command -v curl >/dev/null 2>&1 && ok "curl" || miss "curl" "ships with the OS; install via your package manager if missing"

# ---------- venv ~/video-notes-env ----------
echo "[Python venv ~/video-notes-env]"
ENV_DIR="$HOME/video-notes-env"
if [ -n "${MSYSTEM:-}" ]; then
  PY="$ENV_DIR/Scripts/python.exe"
else
  PY="$ENV_DIR/bin/python"
fi

if [ -x "$PY" ]; then
  ok "venv exists: ${PY}"
else
  echo "  ... not found, creating with uv"
  if command -v uv >/dev/null 2>&1; then
    uv venv "$ENV_DIR" && ok "created ${ENV_DIR}" || miss "venv creation failed" "run manually: uv venv ~/video-notes-env"
  else
    miss "uv (to create the venv)" "macOS: brew install uv / others: https://docs.astral.sh/uv/"
  fi
fi

if [ -x "$PY" ]; then
  "$PY" -c "import requests" 2>/dev/null && ok "requests installed" || {
    echo "  ... installing requests into the venv"
    if command -v uv >/dev/null 2>&1; then
      uv pip install --python "$PY" requests && ok "requests installed" || miss "requests install failed" "uv pip install --python ${PY} requests"
    else
      miss "requests" "re-run this script after installing uv"
    fi
  }
fi

# ---------- Groq API key ----------
echo "[Groq API key]"
if [ -n "${GROQ_API_KEY:-}" ] || [ -f "$HOME/.asr/groq_api_key" ]; then
  ok "configured (env var or ~/.asr/groq_api_key)"
else
  miss "Groq API key" "free signup at https://console.groq.com, then: mkdir -p ~/.asr && echo 'your-key' > ~/.asr/groq_api_key"
fi

# ---------- yt-dlp (optional) ----------
echo "[optional: other platforms]"
command -v yt-dlp >/dev/null 2>&1 && ok "yt-dlp" || miss "yt-dlp (only needed for Bilibili/YouTube etc.)" "brew install yt-dlp / pip install yt-dlp"

echo "== done. PY = ${PY} =="

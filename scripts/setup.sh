#!/usr/bin/env bash
# video-notes environment check + venv creation + first-run onboarding.
# Usage:
#   bash setup.sh                  # check env; on first run prints FIRST_RUN and the strategy options
#   bash setup.sh --set-strategy <a|b|c>   # record the user's first-run choice (writes config)
# Config: ~/.video-notes/config.json — once it exists, setup.sh stays silent about onboarding.
# Note: always brace-expand variables (${VAR}) — bash 3.2 (stock macOS) merges
# CJK punctuation bytes into $VAR names and errors out under set -u.
set -u

ok()   { printf "  [✓] %s\n" "$1"; }
miss() { printf "  [✗] %s\n         -> %s\n" "$1" "$2"; }

CONFIG_DIR="$HOME/.video-notes"
CONFIG="$CONFIG_DIR/config.json"

# ---------- record first-run choice ----------
if [ "${1:-}" = "--set-strategy" ]; then
  case "${2:-}" in
    a|b|c)
      mkdir -p "$CONFIG_DIR"
      printf '{\n  "fallback_strategy": "%s",\n  "configured_at": "%s"\n}\n' "$2" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$CONFIG"
      echo "recorded fallback_strategy=${2} in ${CONFIG}"
      ;;
    *) echo "usage: setup.sh --set-strategy a|b|c" >&2; exit 1 ;;
  esac
  exit 0
fi

OS="$(uname -s 2>/dev/null || echo unknown)"
echo "== video-notes environment check (OS: ${OS}) =="

# ---------- core deps ----------
echo "[core]"
command -v ffmpeg >/dev/null 2>&1 && ok "ffmpeg: $(command -v ffmpeg)" || miss "ffmpeg" "macOS: brew install ffmpeg / Ubuntu: apt install ffmpeg / Windows: winget install ffmpeg"
command -v curl >/dev/null 2>&1 && ok "curl" || miss "curl" "ships with the OS; install via your package manager if missing"
command -v yt-dlp >/dev/null 2>&1 && ok "yt-dlp (YouTube / Bilibili / 1000+ sites)" || miss "yt-dlp" "brew install yt-dlp / pip install yt-dlp"

# ---------- venv ----------
echo "[Python venv ~/video-notes-env]"
ENV_DIR="$HOME/video-notes-env"
if [ -n "${MSYSTEM:-}" ]; then PY="$ENV_DIR/Scripts/python.exe"; else PY="$ENV_DIR/bin/python"; fi
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
    command -v uv >/dev/null 2>&1 && { uv pip install --python "$PY" requests && ok "requests installed"; } || miss "requests" "install uv first, then re-run this script"
  }
fi

# ---------- Groq key ----------
echo "[Groq API key]"
if [ -n "${GROQ_API_KEY:-}" ] || [ -f "$HOME/.asr/groq_api_key" ]; then
  ok "configured (env var or ~/.asr/groq_api_key)"
else
  miss "Groq API key" "free signup at https://console.groq.com, then: mkdir -p ~/.asr && echo 'your-key' > ~/.asr/groq_api_key"
fi

# ---------- first-run onboarding ----------
if [ ! -f "$CONFIG" ]; then
  cat <<'EOF'

== FIRST_RUN ==
This is the first run. The agent MUST now present the following choice to the
user and record the answer with:  bash setup.sh --set-strategy a|b|c

Fallback strategy when a site refuses plain downloads (login walls / anti-bot):

  (a) none (default) — yt-dlp + Douyin direct script + caption-first shortcuts.
      Pros: zero extra install, fully offline-friendly.
      Cons: sites with hard anti-bot (e.g. Douyin risk-control) may fail.

  (b) browser automation — any CDP-capable controller (Playwright, or an
      agent browser skill such as ego-browser / kimi-webbridge if installed).
      Pros: can capture real network responses, beats most anti-bot.
      Cons: heavier install; requires a browser on the machine.

  (c) API-first (agent-reach style) — YouTube/Bilibili captions via pure APIs,
      no browser ever. Pros: lightest; cons: no help for sites without caption APIs.

After the user picks, re-run: bash setup.sh --set-strategy <choice>
Subsequent runs will not ask again.
EOF
else
  echo "onboarding: already configured (${CONFIG})"
  grep -o '"fallback_strategy": *"[abc]"' "$CONFIG" || true
fi

echo "== done. PY = ${PY} =="

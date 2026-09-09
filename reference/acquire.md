# Acquiring videos (route by source)

## Source routing

| Source | How |
|---|---|
| Douyin link / share text | `scripts/download_douyin.py` (no-login direct link, see below) |
| Local file | Use the user's path directly; skip to transcription |
| Bilibili / YouTube / others | `yt-dlp "<url>"` (install first, see `setup.md`), then transcribe |

## Douyin: no-login direct link (default)

```bash
$PY scripts/download_douyin.py "https://v.douyin.com/xxx"          # $PY: see setup.md (venv python)
$PY scripts/download_douyin.py "8.79 full share text https://v.douyin.com/xxx/ ..." --output ./videos
```

- Pasting the full share text works; the script extracts the link itself.
- How it works: short link → iesdouyin share-page HTML → parse `play_addr` video_id → call `aweme/v1/play` for the no-watermark stream (falls back to watermarked on failure).
- **Direct connection — unset proxy variables first** (`unset HTTPS_PROXY HTTP_PROXY ALL_PROXY` and lowercase variants).
- Only depends on `requests`.

## Douyin fallback: real response body via browser CDP

When the direct route breaks (e.g. share-page SSR stops embedding `play_addr`), use any browser-automation capability that exposes CDP:

1. Open `https://www.douyin.com/video/<video_id>` in the browser, wait 5–7s, confirm the page is alive (title appears).
2. Over CDP: `Network.enable` → `Page.reload` → wait ~7s → in `Network.responseReceived` events find the requestId whose URL contains `/aweme/v1/web/aweme/detail/` and `aweme_id=`.
3. `Network.getResponseBody(requestId)` → the JSON's `aweme_detail.video.play_addr.url_list[0]` is the no-watermark CDN URL.
4. Download with curl: browser UA + Referer `-e "https://www.douyin.com/"`, direct connection.

Hard-won pitfalls:

- **Do not replay that API with `fetch()`** — risk control returns an HTML login page. You must capture the real network response via CDP.
- `blob:` video URLs can't be curled. Don't try.
- If even the video page demands login, switch to a browser session that's already logged in (any automation tool works; nothing here is tool-specific).

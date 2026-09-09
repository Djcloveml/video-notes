# Acquiring videos (route by source)

Universal pipeline — same for every site: **captions first if the site has them (skips transcription entirely), otherwise download the media and transcribe**.

## Source routing

| Source | First try | If that fails |
|---|---|---|
| YouTube | Captions: `yt-dlp --write-auto-sub --write-sub --skip-download --sub-langs "zh.*,en.*" --convert-subs srt <url>` | Full download via yt-dlp → transcribe |
| Bilibili | Captions via `bili` CLI (`bili` subtitle commands) or yt-dlp | Full download via yt-dlp → transcribe |
| Douyin | `$PY scripts/download_douyin.py "<link or share text>"` (no-login direct link) | Browser fallback (strategy b, if configured) |
| Other video sites | `yt-dlp "<url>"` | Browser fallback (strategy b, if configured) |
| Local file | Use the path directly → transcribe | — |

**Caption-first shortcut**: when subtitles come back from the site itself, clean them into plain text and jump straight to note-writing — no ffmpeg/Groq needed, faster and more accurate than ASR.

## Douyin: no-login direct link (default)

- How it works: short link → iesdouyin share-page HTML → parse `play_addr` video_id → call `aweme/v1/play` for the no-watermark stream (watermarked fallback built in).
- **Direct connection — unset proxy variables first.**
- Only depends on `requests`.

## Browser fallback (only if the user chose strategy b at first run)

For sites that refuse plain downloads (login walls / anti-bot SSR), use the configured CDP-capable browser controller (Playwright, or an agent-browser skill if one is installed):

1. Open the video page in the browser, wait 5–7s, confirm it's alive (title appears).
2. Over CDP: `Network.enable` → `Page.reload` → wait ~7s → in `Network.responseReceived` find the request whose URL looks like the site's "detail/play" API (for Douyin: contains `/aweme/v1/web/aweme/detail/` and `aweme_id=`).
3. `Network.getResponseBody(requestId)` → extract the CDN stream URL from the JSON (Douyin: `aweme_detail.video.play_addr.url_list[0]`).
4. Download with curl: browser UA + site Referer, direct connection.

Hard-won pitfalls:

- **Do not replay those APIs with `fetch()`** — risk control returns an HTML login page. You must capture the real network response via CDP.
- `blob:` URLs can't be curled. Don't try.
- If the page itself demands login, you need an already-logged-in browser session (any automation tool works).

If the user chose strategy (a) or (c), do **not** attempt the browser fallback — report the failure and explain that strategy (b) would handle it (`bash setup.sh --set-strategy b` to switch).

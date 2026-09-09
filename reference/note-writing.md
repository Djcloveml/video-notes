# Knowledge-note conventions

Read `*_全文.txt`, consult `*_字幕.srt` for timestamps, and produce `{title}_知识点.md` next to the video.

## Structure

1. **Header**: source link, author, duration, transcription method, list of produced files.
2. **Chapter timeline**: pick anchor sentences for key sections, look up their timestamps in the SRT, present as a table — so the user can jump back into the video.
3. **Layered breakdown**: core idea → knowledge points (definition / criteria / examples) → takeaways.

## Rules

- **Stay faithful to the video** — no invented viewpoints; mark any additions clearly as "editor's note".
- **Fix obvious ASR homophone errors** (e.g. wrong homophone characters) in the note; keep the SRT untouched.
- Notes are for review: every knowledge point must stand alone and read clearly without watching the video.

## Output location

Everything lives under `VideoNotes/` at the project (or working-directory) root: one subfolder per video, `VideoNotes/YYYYMMDD-<topic>/`, containing the video file, the SRT, the full text, and the note. Self-contained by design — no external knowledge base, no user-home paths.

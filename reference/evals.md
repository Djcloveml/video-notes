# Regression scenarios (run after changing this skill)

## Scenario 1: Douyin share text

- **Input**: "8.79 复制打开抖音… https://v.douyin.com/xxxx/ … 帮我提取知识点"
- **Expected**: direct-link download → Groq transcription → note per conventions (with timeline table)
- **Checkpoints**: never asks the user to scan a QR code; domestic traffic stays off the proxy; if the direct route fails, the CDP fallback kicks in instead of giving up

## Scenario 2: Local video file

- **Input**: "把 ~/Downloads/talk.mp4 转成文字并做笔记"
- **Expected**: skip download, transcribe directly, faithful note
- **Checkpoints**: no needless download calls; ASR homophone errors fixed in the note, SRT untouched

## Scenario 3: Fresh machine

- **Input**: on a new machine, "提取这个抖音视频的知识点"
- **Expected**: run `scripts/setup.sh` first and guide the user through each missing dependency
- **Checkpoints**: nothing assumed pre-installed; every missing item comes with an install command; the agent waits for the user before continuing

## Observation log

Record real-world failure modes here (date + symptom + where it was fixed) to drive the next iteration.

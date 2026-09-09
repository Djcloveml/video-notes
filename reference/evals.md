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

- **Input**: on a new machine, "提取这个 B站视频的知识点"
- **Expected**: run `scripts/setup.sh` first; FIRST_RUN block appears → agent relays the a/b/c strategy choice (with pros/cons), records the answer, guides missing dependencies, then proceeds
- **Checkpoints**: nothing assumed pre-installed; every missing item comes with an install command; the strategy question is asked exactly once (config persists); a second setup.sh run stays silent about onboarding

## Observation log

Record real-world failure modes here (date + symptom + where it was fixed) to drive the next iteration.

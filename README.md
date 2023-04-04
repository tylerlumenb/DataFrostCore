# SwanSong Logbook

SwanSong Logbook is a lightweight CLI journal that captures late-night research micro-moments, tracks moods, and queues follow-up reminders. It is crafted as a solo after-hours tool and simulates a real developer pacing through personal notes.

## Features
- add brief entries with title, body, mood, and tags
- attach follow-up reminders that carry a due-date hint
- list history filtered by mood, tag, or date window
- emit a quick recap of what needs attention next

## Layout
- `swan_song/cli.py`: entry point with argument parsing
- `swan_song/data_store.py`: serializes entries and reminders to disk
- `data/logbook.json`: persistent record of sessions (auto-created)

## CLI samples
```
python -m swan_song add --title "Obsessive API" \
    --mood curious --body "Sketch caching idea" --tags api,caching --remind "2023-03-24"
python -m swan_song list --mood curious --tag api
python -m swan_song remind
```

## Guided entry prompt
- `python -m swan_song prompt` asks for a title, body, mood, tags, and optional reminder  
- blank inputs fall back to placeholders so the session can keep moving even if distracted

## Mood review
- `python -m swan_song review` prints a quick mood snapshot followed by reminders within the next two weeks.
- Extend or shrink that window with `--remind-days` to match the sprint/mood cycle you are currently in.
- `python -m swan_song complete --timestamp "2023-03-21T20:15:01"` retires a reminder once the experiment is logged.

## Getting started
1. Install dependencies (if any) via `pip install -r requirements.txt` (none for now).
2. Run `python -m swan_song --help` to explore commands.
3. Drop entries anytime, even between meetings, mirroring a distracted personal project rhythm.

## Next steps
- add interactive prompts for voice-of-the-day notes
- build a web dashboard for weekly summaries

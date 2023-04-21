"""Utility to drop a few sample SwanSong entries for local tinkering."""

from datetime import datetime, timedelta

from swan_song.cli import _build_entry_payload
from swan_song.data_store import append_entry


def _seed_entry(title: str, mood: str, tags: str, reminder: str, days_ago: int) -> None:
    timestamp = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    entry = _build_entry_payload(
        title=title,
        body=f"{title} notes after hours.",
        mood=mood,
        tags=tags,
        remind=reminder,
        timestamp=timestamp,
    )
    append_entry(entry)


if __name__ == "__main__":
    print("seeding three low-effort entries...")
    _seed_entry("Cache sketch", "curious", "cache,api", "2023-04-20", 7)
    _seed_entry("Nightly graphs", "bright", "charts,ai", "2023-05-02", 3)
    _seed_entry("Quiet proof", "tired", "proof,math", None, 1)
    print("seed complete")

"""Utility helpers that persist SwanSong Logbook entries to disk."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LOGBOOK_FILE = DATA_DIR / "logbook.json"

Entry = Dict[str, Any]


def _ensure_logbook() -> None:
    """Guarantee the logbook file exists before reading or writing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOGBOOK_FILE.exists():
        LOGBOOK_FILE.write_text("[]")


def load_entries() -> List[Entry]:
    """Return all entries stored in the logbook, sorted by timestamp desc."""
    _ensure_logbook()
    raw = json.loads(LOGBOOK_FILE.read_text())
    entries = sorted(raw, key=lambda e: e.get("timestamp", ""), reverse=True)
    return entries


def save_entries(entries: List[Entry]) -> None:
    """Overwrite the logbook with the given entries."""
    _ensure_logbook()
    LOGBOOK_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False))


def append_entry(entry: Entry) -> Entry:
    """Add a new entry to the logbook and return it."""
    entries = load_entries()
    entries.insert(0, entry)
    save_entries(entries)
    return entry

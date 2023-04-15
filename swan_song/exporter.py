"""Helpers to export SwanSong Logbook entries to a JSON snapshot."""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

Entry = Dict[str, Any]


def export_entries(entries: Iterable[Entry], target: Path) -> Path:
    """Write the given entries to the provided target file.

    The parent directory is created automatically.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        json.dump(list(entries), fh, indent=2, ensure_ascii=False)
    return target

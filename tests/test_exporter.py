import json

from swan_song.exporter import export_entries


def test_export_entries_creates_file(tmp_path):
    entries = [
        {"title": "Night dive", "mood": "curious"},
        {"title": "Tinker", "mood": "tired"},
    ]
    target = tmp_path / "logbook.json"
    exported = export_entries(entries, target)

    assert exported == target
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert len(payload) == 2
    assert payload[0]["title"] == "Night dive"

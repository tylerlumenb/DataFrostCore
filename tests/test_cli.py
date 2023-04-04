from swan_song.cli import _build_entry_payload, _format_entry, _normalize_tags, _summarize_moods


def test_normalize_tags_strips_whitespace():
    raw = "  research,api , , curiosity   "
    normalized = _normalize_tags(raw)
    assert normalized == ["research", "api", "curiosity"]


def test_build_entry_payload_includes_default_timestamp():
    entry = _build_entry_payload("title", "body", "moody", "tag1,tag2", None, timestamp="2022-01-02T03:04:05")
    assert entry["timestamp"] == "2022-01-02T03:04:05"
    assert entry["tags"] == ["tag1", "tag2"]
    assert entry["mood"] == "moody"


def test_summarize_moods_counts_entries():
    entries = [
        {"mood": "curious"},
        {"mood": "curious"},
        {"mood": "tired"},
        {},
    ]
    summary = _summarize_moods(entries)
    assert summary["curious"] == 2
    assert summary["tired"] == 1
    assert summary["neutral"] == 1


def test_format_entry_shows_status():
    entry = {
        "title": "Checkpoint",
        "body": "Need to rewire the cache",
        "mood": "thrilled",
        "timestamp": "2023-03-23T05:00:00",
        "tags": ["cache"],
        "reminder": "2023-04-01",
        "status": "done",
    }
    formatted = _format_entry(entry)
    assert "[done]" in formatted

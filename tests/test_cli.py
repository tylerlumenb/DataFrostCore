from swan_song.cli import _normalize_tags


def test_normalize_tags_strips_whitespace():
    raw = "  research,api , , curiosity   "
    normalized = _normalize_tags(raw)
    assert normalized == ["research", "api", "curiosity"]

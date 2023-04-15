"""Small CLI layer for the SwanSong Logbook utility."""

from argparse import ArgumentParser, Namespace
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .data_store import append_entry, DATA_DIR, load_entries, set_entry_status
from .exporter import export_entries

DATE_FORMAT = "%Y-%m-%d"


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"date must be in YYYY-MM-DD form, got {value!r}")


def _format_entry(entry: dict) -> str:
    tags = ", ".join(entry.get("tags", []))
    reminder = entry.get("reminder") or "no reminder"
    status = entry.get("status", "open")
    return (
        f"- {entry['title']} [{status}] ({entry['mood']} @ {entry['timestamp']})\n"
        f"  tags: {tags}\n"
        f"  reminder: {reminder}\n"
        f"  {entry['body']}"
    )


def _filter_entries(entries: List[dict], args: Namespace) -> List[dict]:
    filtered = entries
    if args.mood:
        filtered = [e for e in filtered if e.get("mood") == args.mood]
    if args.tag:
        filtered = [e for e in filtered if args.tag in e.get("tags", [])]
    since_date = _parse_date(args.since)
    if since_date:
        filtered = [
            e
            for e in filtered
            if e.get("timestamp") and date.fromisoformat(e["timestamp"][:10]) >= since_date
        ]
    until_date = _parse_date(args.until)
    if until_date:
        filtered = [
            e
            for e in filtered
            if e.get("timestamp") and date.fromisoformat(e["timestamp"][:10]) <= until_date
        ]
    if args.limit:
        filtered = filtered[: args.limit]
    return filtered


def _print_entries(entries: List[dict]) -> None:
    if not entries:
        print("no entries found")
        return
    for entry in entries:
        print(_format_entry(entry))
        print()


def _summarize_moods(entries: List[dict]) -> dict:
    summary = {}
    for entry in entries:
        mood = entry.get("mood", "neutral")
        summary[mood] = summary.get(mood, 0) + 1
    return summary


def _plan_reminders(entries: List[dict], days: Optional[int] = 30) -> None:
    today = date.today()
    due_window = today + timedelta(days=days) if days is not None else None
    upcoming: List[dict] = []
    overdue: List[dict] = []
    for entry in entries:
        remind = entry.get("reminder")
        if not remind:
            continue
        reminder_date = date.fromisoformat(remind)
        if reminder_date < today:
            overdue.append(entry)
            continue
        if due_window is None or reminder_date <= due_window:
            upcoming.append(entry)
    if not upcoming and not overdue:
        print("no reminders waiting")
        return
    if overdue:
        print("overdue reminders:")
        for entry in overdue:
            print(
                f"- {entry['title']} overdue {entry['reminder']} (mood {entry['mood']})"
            )
    if upcoming:
        print("upcoming reminders:")
        for entry in upcoming:
            print(
                f"- {entry['title']} due {entry['reminder']} (mood {entry['mood']})"
            )


def _print_review(entries: List[dict], remind_days: int) -> None:
    summary = _summarize_moods(entries)
    if summary:
        print("mood snapshot:")
        for mood, count in sorted(summary.items(), key=lambda pair: -pair[1]):
            print(f"- {mood}: {count} entries")
        print()
    else:
        print("no entries recorded yet")
        print()
    _plan_reminders(entries, days=remind_days)


def _gather_tag_usage(entries: List[dict]) -> dict:
    usage = {}
    for entry in entries:
        for tag in entry.get("tags", []):
            usage[tag] = usage.get(tag, 0) + 1
    return usage


def _print_tag_usage(entries: List[dict], top: int = 0) -> None:
    usage = _gather_tag_usage(entries)
    if not usage:
        print("no tags have been tracked yet")
        return
    print("tag usage:")
    sorted_tags = sorted(usage.items(), key=lambda pair: (-pair[1], pair[0]))
    for index, (tag, count) in enumerate(sorted_tags):
        if top and index >= top:
            break
        print(f"- {tag}: {count}")


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser("swan_song", description="Personal logbook CLI.")
    sub = parser.add_subparsers(dest="command")

    add_parser = sub.add_parser("add", help="Add a fast journal entry.")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--body", required=True)
    add_parser.add_argument("--mood", default="neutral")
    add_parser.add_argument("--tags", default="", help="Comma-separated tags.")
    add_parser.add_argument(
        "--remind",
        help="Optional follow-up date in YYYY-MM-DD.",
    )

    list_parser = sub.add_parser("list", help="Browse recent entries.")
    list_parser.add_argument("--mood", help="Filter by mood label.")
    list_parser.add_argument("--tag", help="Filter by single tag.")
    list_parser.add_argument("--since", help="Inclusive start date.")
    list_parser.add_argument("--until", help="Inclusive end date.")
    list_parser.add_argument("--limit", type=int, default=10)

    remind_parser = sub.add_parser("remind", help="Show outstanding reminders.")
    remind_parser.add_argument(
        "--days", type=int, default=30, help="Look ahead this many days."
    )
    sub.add_parser("prompt", help="Guided interactive entry.")
    tags_parser = sub.add_parser("tags", help="Summarize logged tags.")
    tags_parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Limit the output to the most used tags.",
    )
    review_parser = sub.add_parser("review", help="Summarize recent moods.")
    review_parser.add_argument(
        "--remind-days",
        type=int,
        default=14,
        help="How far ahead to surface reminders.",
    )
    complete_parser = sub.add_parser("complete", help="Mark an entry as done.")
    complete_parser.add_argument(
        "--timestamp",
        required=True,
        help="Timestamp identifier of the entry to mark as done.",
    )
    export_parser = sub.add_parser("export", help="Write all entries to JSON.")
    export_parser.add_argument(
        "--output",
        type=Path,
        default=DATA_DIR / "logbook_export.json",
        help="File path for the exported snapshot.",
    )
    return parser


def _normalize_tags(raw: str) -> List[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _build_entry_payload(
    title: str,
    body: str,
    mood: str,
    tags: str,
    remind: Optional[str],
    timestamp: Optional[str] = None,
) -> dict:
    return {
        "title": title,
        "body": body,
        "mood": mood,
        "timestamp": timestamp or datetime.utcnow().isoformat(),
        "tags": _normalize_tags(tags),
        "reminder": remind,
    }


def _prompt_for_entry() -> dict:
    print("starting a guided entry (leave blank to skip)")
    title = input("title: ").strip()
    body = input("body: ").strip()
    mood = input("mood (default neutral): ").strip() or "neutral"
    tags = input("tags (comma list): ").strip()
    remind = input("reminder date YYYY-MM-DD: ").strip() or None
    return _build_entry_payload(
        title=title or "untitled",
        body=body or "no body yet",
        mood=mood,
        tags=tags,
        remind=remind,
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "add":
        entry = _build_entry_payload(
            title=args.title,
            body=args.body,
            mood=args.mood,
            tags=args.tags,
            remind=args.remind,
        )
        append_entry(entry)
        print("entry recorded")
        return
    if args.command == "prompt":
        entry = _prompt_for_entry()
        append_entry(entry)
        print("guided entry logged")
        return
    entries = load_entries()
    if args.command == "list":
        _print_entries(_filter_entries(entries, args))
        return
    if args.command == "tags":
        _print_tag_usage(entries, top=args.top)
        return
    if args.command == "remind":
        _plan_reminders(entries, days=args.days)
        return
    if args.command == "review":
        _print_review(entries, remind_days=args.remind_days)
        return
    if args.command == "complete":
        updated = set_entry_status(args.timestamp, "done")
        if updated:
            print("entry marked as done")
        else:
            print("could not find an entry with that timestamp")
        return
    if args.command == "export":
        exported = export_entries(entries, args.output)
        print(f"exported {len(entries)} entries to {exported}")
        return
    parser.print_help()

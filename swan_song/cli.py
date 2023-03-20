"""Small CLI layer for the SwanSong Logbook utility."""

from argparse import ArgumentParser, Namespace
from datetime import date, datetime
from typing import List, Optional

from .data_store import append_entry, load_entries

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
    return (
        f"- {entry['title']} ({entry['mood']} @ {entry['timestamp']})\n"
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


def _plan_reminders(entries: List[dict]) -> None:
    today = date.today()
    pending = [
        e
        for e in entries
        if e.get("reminder")
        and date.fromisoformat(e["reminder"]) >= today
    ]
    if not pending:
        print("no reminders waiting")
        return
    print("reminders to follow up on:")
    for entry in pending:
        print(
            f"- {entry['title']} due {entry['reminder']} (mood {entry['mood']})"
        )


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

    sub.add_parser("remind", help="Show outstanding reminders.")
    return parser


def _normalize_tags(raw: str) -> List[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "add":
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "title": args.title,
            "body": args.body,
            "mood": args.mood,
            "timestamp": timestamp,
            "tags": _normalize_tags(args.tags),
            "reminder": args.remind,
        }
        append_entry(entry)
        print("entry recorded")
        return
    entries = load_entries()
    if args.command == "list":
        _print_entries(_filter_entries(entries, args))
        return
    if args.command == "remind":
        _plan_reminders(entries)
        return
    parser.print_help()

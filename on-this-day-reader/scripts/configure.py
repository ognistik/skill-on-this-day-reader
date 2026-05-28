#!/usr/bin/env python3
"""Edit the on-this-day-reader config file safely."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"
ACTIVE_CONFIG_PATH = Path(os.environ.get("ON_THIS_DAY_CONFIG", str(CONFIG_PATH))).expanduser()
DEFAULT_CONFIG: dict[str, Any] = {
    "dayone": {
        "db_path": "~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite",
        "exclude_journals": [],
        "exclude_tags": [],
        "sort": "asc",
    },
    "reader": {
        "delete_files_after_save": True,
        "dry_run": False,
    },
    "note": {
        "enabled": False,
        "url_template": "bear://x-callback-url/create?text={analysis}",
        "open_in_background": True,
    },
}


def load_config() -> dict[str, Any]:
    if not ACTIVE_CONFIG_PATH.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        loaded = json.loads(ACTIVE_CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config file: {ACTIVE_CONFIG_PATH}\n{exc}") from exc
    return merge_defaults(loaded)


def merge_defaults(config: dict[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    for section, values in config.items():
        if isinstance(values, dict) and isinstance(merged.get(section), dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged


def save_config(config: dict[str, Any]) -> None:
    ACTIVE_CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_config(config: dict[str, Any]) -> None:
    print(json.dumps(config, ensure_ascii=False, indent=2))


def normalized_items(items: list[str]) -> list[str]:
    values: list[str] = []
    for item in items:
        values.extend(part.strip() for part in item.split(","))
    return [value for value in values if value]


def update_list(config: dict[str, Any], key: str, action: str, items: list[str]) -> None:
    values = normalized_items(items)
    if not values:
        raise SystemExit("Provide at least one value.")

    current = config["dayone"].setdefault(key, [])
    if not isinstance(current, list):
        raise SystemExit(f"config dayone.{key} must be a list")

    if action == "add":
        for value in values:
            if value not in current:
                current.append(value)
    elif action == "remove":
        config["dayone"][key] = [value for value in current if value not in values]
    elif action == "set":
        config["dayone"][key] = values
    elif action == "clear":
        config["dayone"][key] = []
    else:
        raise SystemExit(f"Unknown action: {action}")


def set_bool(config: dict[str, Any], section: str, key: str, value: str) -> None:
    if value == "on":
        config[section][key] = True
    elif value == "off":
        config[section][key] = False
    else:
        raise SystemExit("Value must be 'on' or 'off'.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show or edit the on-this-day-reader config.json file."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("show", help="Print the current config.")
    subparsers.add_parser("reset", help="Reset config.json to the default config.")

    db_parser = subparsers.add_parser("db-path", help="Set the Day One database path.")
    db_parser.add_argument("path")

    sort_parser = subparsers.add_parser("sort", help="Set export sort order.")
    sort_parser.add_argument("order", choices=["asc", "desc"])

    dry_run_parser = subparsers.add_parser("dry-run", help="Turn Reader dry-run on or off.")
    dry_run_parser.add_argument("value", choices=["on", "off"])

    delete_parser = subparsers.add_parser(
        "delete-files",
        help="Delete temporary analysis files after successful Reader save.",
    )
    delete_parser.add_argument("value", choices=["on", "off"])

    note_parser = subparsers.add_parser("note", help="Turn optional note creation on or off.")
    note_parser.add_argument("value", choices=["on", "off"])

    note_url_parser = subparsers.add_parser("note-url", help="Set the note URL template.")
    note_url_parser.add_argument("template")

    for name, key, label in [
        ("exclude-journal", "exclude_journals", "journal"),
        ("exclude-tag", "exclude_tags", "tag"),
    ]:
        list_parser = subparsers.add_parser(name, help=f"Edit excluded Day One {label}s.")
        list_parser.add_argument("action", choices=["add", "remove", "set", "clear"])
        list_parser.add_argument(
            "items",
            nargs="*",
            help=f"{label.title()} names. Multiple values and comma-separated values are supported.",
        )
        list_parser.set_defaults(list_key=key)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "reset":
        config = json.loads(json.dumps(DEFAULT_CONFIG))
        save_config(config)
        print_config(config)
        return 0

    config = load_config()

    if args.command == "show":
        print_config(config)
        return 0
    if args.command == "db-path":
        config["dayone"]["db_path"] = args.path
    elif args.command == "sort":
        config["dayone"]["sort"] = args.order
    elif args.command == "dry-run":
        set_bool(config, "reader", "dry_run", args.value)
    elif args.command == "delete-files":
        set_bool(config, "reader", "delete_files_after_save", args.value)
    elif args.command == "note":
        set_bool(config, "note", "enabled", args.value)
    elif args.command == "note-url":
        config["note"]["url_template"] = args.template
    elif args.command in {"exclude-journal", "exclude-tag"}:
        update_list(config, args.list_key, args.action, args.items)
    else:
        parser.error(f"Unknown command: {args.command}")

    save_config(config)
    print_config(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())

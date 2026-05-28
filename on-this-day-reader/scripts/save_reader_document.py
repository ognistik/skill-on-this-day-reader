#!/usr/bin/env python3
"""Save a Markdown file to Readwise Reader via the Readwise CLI."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"
DEFAULT_URL_PREFIX = "https://local.dayone/on-this-day"
DEFAULT_AUTHOR = "Day One On This Day"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config file: {CONFIG_PATH}\n{exc}") from exc


def normalize_day(value: str | None) -> str:
    if not value:
        today = dt.date.today()
        return f"{today.month:02d}-{today.day:02d}"

    if len(value) == 10:
        try:
            parsed = dt.date.fromisoformat(value)
        except ValueError as exc:
            raise SystemExit("date must use MM-DD, for example 05-26") from exc
        return f"{parsed.month:02d}-{parsed.day:02d}"

    try:
        month_text, day_text = value.split("-", 1)
        month = int(month_text)
        day = int(day_text)
        dt.date(2000, month, day)
    except ValueError as exc:
        raise SystemExit("date must use MM-DD, for example 05-26") from exc
    return f"{month:02d}-{day:02d}"


def run_readwise(readwise_bin: str, args: list[str], dry_run: bool) -> str:
    cmd = [readwise_bin, "--json", *args]
    if dry_run:
        print("DRY RUN:", " ".join(cmd[:4] + ["..."]))
        return "{}"
    completed = subprocess.run(
        cmd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"Readwise CLI failed ({completed.returncode}).\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return completed.stdout.strip()


def find_document_id(value: Any) -> str | None:
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            return value["id"]
        for key in ("document", "result", "data"):
            found = find_document_id(value.get(key))
            if found:
                return found
        for nested in value.values():
            found = find_document_id(nested)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = find_document_id(item)
            if found:
                return found
    return None


def create_note(
    markdown: str,
    title: str,
    date_label: str,
    config: dict[str, Any],
    dry_run: bool,
) -> str | None:
    note_config = config.get("note", {})
    if not note_config.get("enabled", False):
        return None

    template = note_config.get("url_template")
    if not template:
        raise SystemExit("config note.url_template is required when note.enabled is true")

    replacements = {
        "analysis": urllib.parse.quote(markdown, safe=""),
        "title": urllib.parse.quote(title, safe=""),
        "date": urllib.parse.quote(date_label, safe=""),
    }
    try:
        url = str(template).format(**replacements)
    except KeyError as exc:
        raise SystemExit(f"Unsupported placeholder in note.url_template: {exc}") from exc

    if dry_run:
        return "dry-run"

    completed = subprocess.run(
        ["open", url],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(f"Could not open note URL.\nSTDERR:\n{completed.stderr}")
    return "opened"


def delete_files(paths: list[str]) -> list[str]:
    deleted: list[str] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if not path.exists():
            continue
        if not path.is_file():
            raise SystemExit(f"Cleanup path is not a file: {path}")
        path.unlink()
        deleted.append(str(path))
    return deleted


def delete_empty_directories(paths: list[str]) -> list[str]:
    deleted: list[str] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if not path.exists():
            continue
        if not path.is_dir():
            raise SystemExit(f"Cleanup path is not a directory: {path}")
        try:
            path.rmdir()
        except OSError:
            continue
        deleted.append(str(path))
    return deleted


def common_parent(paths: list[str]) -> Path | None:
    parents = {Path(raw_path).expanduser().parent for raw_path in paths}
    if len(parents) != 1:
        return None
    return next(iter(parents))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a Reader document from Markdown and move it to a location."
    )
    parser.add_argument("markdown_file", help="Markdown analysis file to upload.")
    parser.add_argument(
        "date",
        nargs="?",
        help="Optional calendar date as MM-DD. Defaults to today.",
    )
    args = parser.parse_args()

    config = load_config()
    reader_config = config.get("reader", {})
    dry_run = bool(reader_config.get("dry_run", False))
    if str(os.environ.get("ON_THIS_DAY_DRY_RUN", "")).lower() in {"1", "true", "yes"}:
        dry_run = True

    readwise_bin_name = "readwise"
    readwise_bin = shutil.which(readwise_bin_name)
    if not readwise_bin:
        if dry_run:
            readwise_bin = readwise_bin_name
        else:
            raise SystemExit(
                "Readwise CLI not found. Install with: npm install -g @readwise/cli"
            )

    markdown = Path(args.markdown_file).expanduser().read_text(encoding="utf-8")
    date_label = normalize_day(args.date)
    title = f"{date_label} On This Day Analysis"
    url = f"{DEFAULT_URL_PREFIX.rstrip('/')}/{date_label}"
    summary = f"Day One On This Day journal analysis for {date_label}."
    create_args = [
        "reader-create-document",
        "--url",
        url,
        "--markdown",
        markdown,
        "--title",
        title,
        "--author",
        DEFAULT_AUTHOR,
        "--summary",
        summary,
    ]

    create_output = run_readwise(
        readwise_bin,
        create_args,
        dry_run,
    )

    document_id = None
    if create_output:
        try:
            document_id = find_document_id(json.loads(create_output))
        except json.JSONDecodeError:
            document_id = None

    if not document_id and not dry_run:
        raise SystemExit(f"Could not find document id in Readwise output:\n{create_output}")

    if document_id:
        run_readwise(
            readwise_bin,
            [
                "reader-move-documents",
                "--document-ids",
                document_id,
                "--location",
                "shortlist",
            ],
            dry_run,
        )

    note_status = (
        create_note(markdown, title, date_label, config, dry_run)
        if (document_id or dry_run)
        else None
    )

    deleted_files: list[str] = []
    deleted_dirs: list[str] = []
    if document_id and reader_config.get("delete_files_after_save", True) and not dry_run:
        cleanup_paths = [args.markdown_file]
        deleted_files = delete_files(cleanup_paths)
        parent = common_parent(cleanup_paths)
        if parent:
            deleted_dirs = delete_empty_directories([str(parent)])

    print(
        json.dumps(
            {
                "document_id": document_id,
                "title": title,
                "url": url,
                "location": "shortlist",
                "note_status": note_status,
                "deleted_files": deleted_files,
                "deleted_dirs": deleted_dirs,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

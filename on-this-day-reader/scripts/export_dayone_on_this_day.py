#!/usr/bin/env python3
"""Export Day One entries for a calendar day from the local macOS database."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


DEFAULT_DB = (
    "~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite"
)
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"


def parse_day(value: str | None) -> tuple[int, int]:
    if not value:
        today = dt.date.today()
        return today.month, today.day

    try:
        month_text, day_text = value.split("-", 1)
        month = int(month_text)
        day = int(day_text)
        dt.date(2000, month, day)
    except ValueError as exc:
        raise SystemExit("date must use MM-DD, for example 05-26") from exc
    return month, day


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config file: {CONFIG_PATH}\n{exc}") from exc


def config_list(config: dict[str, Any], section: str, key: str) -> list[str]:
    value = config.get(section, {}).get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise SystemExit(f"config {section}.{key} must be a list")
    return [str(item).strip() for item in value if str(item).strip()]


def default_db_path(config: dict[str, Any]) -> Path:
    configured = config.get("dayone", {}).get("db_path") or DEFAULT_DB
    return Path(os.environ.get("DAYONE_DB", configured)).expanduser()


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise SystemExit(f"Day One database not found: {db_path}")
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def split_values(values: list[str] | None, env_name: str | None = None) -> list[str]:
    raw_values: list[str] = []
    if env_name and os.environ.get(env_name):
        raw_values.extend(os.environ[env_name].split(","))
    if values:
        for value in values:
            raw_values.extend(value.split(","))
    return [value.strip() for value in raw_values if value.strip()]


def quote_identifier(identifier: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise RuntimeError(f"unexpected SQLite identifier: {identifier}")
    return f'"{identifier}"'


def get_tag_join_column(conn: sqlite3.Connection) -> str:
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(Z_17TAGS)")]
    tag_columns = [
        column
        for column in columns
        if column != "Z_17ENTRIES" and re.fullmatch(r"Z_\d+TAGS1", column)
    ]
    if len(tag_columns) != 1:
        raise RuntimeError(
            f"could not find Day One tag join column in Z_17TAGS: {columns}"
        )
    return quote_identifier(tag_columns[0])


def build_in_clause(column: str, values: list[str], negate: bool = False) -> tuple[str, list[str]]:
    if not values:
        return "", []
    placeholders = ",".join("?" for _ in values)
    operator = "NOT IN" if negate else "IN"
    return f"AND {column} {operator} ({placeholders})", values


def clean_body(text: str | None) -> str:
    if not text:
        return ""
    text = text.strip()
    # Day One markdown often stores punctuation escaped for Markdown safety.
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", text)
    return text


def fetch_tags(conn: sqlite3.Connection, entry_pk: int, tag_join_column: str) -> list[str]:
    rows = conn.execute(
        f"""
        SELECT t.ZNAME
        FROM Z_17TAGS et
        JOIN ZTAG t ON t.Z_PK = et.{tag_join_column}
        WHERE et.Z_17ENTRIES = ?
        ORDER BY lower(t.ZNAME)
        """,
        (entry_pk,),
    ).fetchall()
    return [row["ZNAME"] for row in rows if row["ZNAME"]]


def fetch_attachments(conn: sqlite3.Connection, entry_pk: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT ZTYPE, ZFILENAME, ZTITLE, ZCAPTION, ZDATE, ZDURATION, ZFILESIZE
        FROM ZATTACHMENT
        WHERE ZENTRY = ?
        ORDER BY coalesce(ZORDERINENTRY, 0), Z_PK
        """,
        (entry_pk,),
    ).fetchall()
    attachments: list[dict[str, Any]] = []
    for row in rows:
        attachments.append(
            {
                "type": row["ZTYPE"],
                "filename": row["ZFILENAME"],
                "title": row["ZTITLE"],
                "caption": row["ZCAPTION"],
                "date": row["ZDATE"],
                "duration": row["ZDURATION"],
                "file_size": row["ZFILESIZE"],
            }
        )
    return attachments


def fetch_entries(
    conn: sqlite3.Connection,
    month: int,
    day: int,
    include_current_year: bool,
    include_journals: list[str],
    exclude_journals: list[str],
    include_tags: list[str],
    exclude_tags: list[str],
    tag_match: str,
    sort: str,
) -> list[dict[str, Any]]:
    params: list[Any] = [month, day]
    tag_join_column = get_tag_join_column(conn)
    include_journal_sql, include_journal_params = build_in_clause("j.ZNAME", include_journals)
    exclude_journal_sql, exclude_journal_params = build_in_clause(
        "j.ZNAME", exclude_journals, negate=True
    )
    params.extend(include_journal_params)
    params.extend(exclude_journal_params)

    tag_filter_sql = ""
    if exclude_tags:
        excluded_tag_placeholders = ",".join("?" for _ in exclude_tags)
        tag_filter_sql += f"""
          AND NOT EXISTS (
            SELECT 1
            FROM Z_17TAGS xt
            JOIN ZTAG x ON x.Z_PK = xt.{tag_join_column}
            WHERE xt.Z_17ENTRIES = e.Z_PK
              AND x.ZNAME IN ({excluded_tag_placeholders})
          )
        """
        params.extend(exclude_tags)

    if include_tags:
        included_tag_placeholders = ",".join("?" for _ in include_tags)
        comparator = ">=" if tag_match == "all" else ">="
        required_count = len(set(include_tags)) if tag_match == "all" else 1
        tag_filter_sql += f"""
          AND (
            SELECT count(DISTINCT it.ZNAME)
            FROM Z_17TAGS ixt
            JOIN ZTAG it ON it.Z_PK = ixt.{tag_join_column}
            WHERE ixt.Z_17ENTRIES = e.Z_PK
              AND it.ZNAME IN ({included_tag_placeholders})
          ) {comparator} ?
        """
        params.extend(include_tags)
        params.append(required_count)

    sort_direction = "DESC" if sort == "desc" else "ASC"

    rows = conn.execute(
        f"""
        SELECT
          e.Z_PK AS entry_pk,
          e.ZUUID AS uuid,
          e.ZGREGORIANYEAR AS year,
          e.ZGREGORIANMONTH AS month,
          e.ZGREGORIANDAY AS day,
          e.ZCREATIONDATE AS creation_date,
          e.ZMODIFIEDDATE AS modified_date,
          e.ZMARKDOWNTEXT AS markdown,
          e.ZRICHTEXTJSON AS rich_text_json,
          e.ZISDRAFT AS is_draft,
          j.ZNAME AS journal_name,
          j.ZSHOULDBEINCLUDEDINONTHISDAY AS include_on_this_day,
          j.ZISTRASHJOURNAL AS is_trash_journal
        FROM ZENTRY e
        LEFT JOIN ZJOURNAL j ON j.Z_PK = e.ZJOURNAL
        WHERE e.ZGREGORIANMONTH = ?
          AND e.ZGREGORIANDAY = ?
          AND coalesce(e.ZISDRAFT, 0) = 0
          AND coalesce(j.ZISTRASHJOURNAL, 0) = 0
          AND coalesce(j.ZSHOULDBEINCLUDEDINONTHISDAY, 1) != 0
          {include_journal_sql}
          {exclude_journal_sql}
          {tag_filter_sql}
        ORDER BY e.ZGREGORIANYEAR {sort_direction}, coalesce(e.ZCREATIONDATE, 0) {sort_direction}, e.Z_PK {sort_direction}
        """,
        params,
    ).fetchall()

    current_year = dt.date.today().year
    entries: list[dict[str, Any]] = []
    for row in rows:
        year = int(row["year"])
        if not include_current_year and year == current_year:
            continue

        text = clean_body(row["markdown"])
        entry_id = row["uuid"]
        entries.append(
            {
                "entry_id": entry_id,
                "entry_pk": row["entry_pk"],
                "date": f"{year:04d}-{int(row['month']):02d}-{int(row['day']):02d}",
                "year": year,
                "journal": row["journal_name"],
                "text": text,
                "rich_text_json_empty": not bool(row["rich_text_json"]),
                "tags": fetch_tags(conn, row["entry_pk"], tag_join_column),
                "attachments": fetch_attachments(conn, row["entry_pk"]),
                "day_one_url": f"dayone://view?entryId={entry_id}",
            }
        )
    return entries


def attachment_label(attachment: dict[str, Any]) -> str:
    parts = [
        attachment.get("type") or "attachment",
        attachment.get("filename"),
        attachment.get("title"),
        attachment.get("caption"),
    ]
    return " - ".join(str(part) for part in parts if part)


def render_markdown(entries: list[dict[str, Any]], month: int, day: int) -> str:
    lines = [f"# Day One On This Day Export: {month:02d}-{day:02d}", ""]
    lines.append(f"Entry count: {len(entries)}")
    lines.append("")

    if not entries:
        lines.append("No Day One entries were found for this calendar date.")
        lines.append("")
        return "\n".join(lines)

    for entry in entries:
        lines.append(f"## {entry['date']} ({entry['journal'] or 'Untitled Journal'})")
        lines.append("")
        if entry["tags"]:
            lines.append("Tags: " + ", ".join(entry["tags"]))
            lines.append("")
        if entry["attachments"]:
            lines.append("Attachments:")
            for attachment in entry["attachments"]:
                lines.append(f"- {attachment_label(attachment)}")
            lines.append("")
        lines.append(entry["text"].strip() or "[No plain-text entry body found.]")
        lines.append("")
        lines.append(f"[Open this Day One entry]({entry['day_one_url']})")
        lines.append("")

    return "\n".join(lines)


def append_ai_guidance(markdown: str) -> str:
    guidance = """
---

## Continue the Skill Workflow

Use the Day One entries above as the complete source material for the analysis. Next:

1. Read `references/analysis_instructions.md`.
2. Write the final Markdown analysis using those instructions exactly.
3. Save that analysis to a temporary Markdown file.
4. Run `save_reader_document.py` with that analysis file.

Do not summarize these entries in chat during the normal workflow.
"""
    return markdown.rstrip() + "\n\n" + guidance.strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Day One entries written on a given MM-DD across years."
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="Optional calendar date as MM-DD. Defaults to today.",
    )
    args = parser.parse_args()

    config = load_config()
    month, day = parse_day(args.date)
    sort = config.get("dayone", {}).get("sort", "asc")
    if sort not in {"asc", "desc"}:
        raise SystemExit('config dayone.sort must be "asc" or "desc"')

    conn = connect_readonly(default_db_path(config))
    entries = fetch_entries(
        conn,
        month,
        day,
        True,
        [],
        split_values(
            config_list(config, "dayone", "exclude_journals"),
            "DAYONE_EXCLUDE_JOURNALS",
        ),
        [],
        split_values(
            config_list(config, "dayone", "exclude_tags"),
            "DAYONE_EXCLUDE_TAGS",
        ),
        "any",
        sort,
    )

    print(append_ai_guidance(render_markdown(entries, month, day)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

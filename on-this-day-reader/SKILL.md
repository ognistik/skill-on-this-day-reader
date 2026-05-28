---
name: on-this-day-reader
description: Export Day One On This Day entries from the local macOS Day One database, analyze them as a personal-history journal review, and save the result to Readwise Reader using the Readwise CLI. Use when the user asks to run, package, automate, or share a Day One On This Day to Reader workflow without relying on MCP tools.
---

# On This Day Reader

Use the bundled scripts. Do not use Day One MCP or Readwise MCP for the normal workflow.

## Prerequisites

- macOS with Day One installed and synced locally.
- Readwise CLI installed and authenticated: `npm install -g @readwise/cli`, then `readwise login` or `readwise login-with-token`.
- Python 3 with the standard library.

## Workflow

1. Create a temporary working directory for the run. Prefer `mktemp -d` so the run folder is disposable.
2. Export entries for the target date. For a normal "today" run:

```bash
python3 "$SKILL_DIR/scripts/export_dayone_on_this_day.py"
```

Do not redirect this command to a Markdown file and do not create a separate
export/capture file for its output. Read the exporter output directly from
stdout/tool output. The exporter already prints the complete Markdown source
material the AI needs for analysis, and saving it separately causes duplicate
reading and leaves unnecessary files behind.

If the user asks for a different calendar date, pass only that date as `MM-DD`:

```bash
python3 "$SKILL_DIR/scripts/export_dayone_on_this_day.py" "05-26"
```

3. Use the exporter output as the complete Day One source material. It is Markdown meant to be read directly by the AI and includes entry dates, journals, tags, attachments, entry text, Day One links, and a short workflow reminder.
4. Read `references/analysis_instructions.md`.
5. Write the final analysis to `$WORKDIR/on-this-day-analysis.md`.
6. Save the analysis to Reader shortlist. For a normal "today" run:

```bash
python3 "$SKILL_DIR/scripts/save_reader_document.py" "$WORKDIR/on-this-day-analysis.md"
```

If the user asked for a different calendar date, pass the same `MM-DD` used for export so the Reader title, summary, and stable URL match that date:

```bash
python3 "$SKILL_DIR/scripts/save_reader_document.py" "$WORKDIR/on-this-day-analysis.md" "05-26"
```

Omit dates for a normal "today" run. Use a requested date only when the user asks for one.

## Configuration

User customization lives in `config.json`. Do not add command-line options for normal runs.

If the user asks how to configure the skill, read `references/configuration.md` and use `scripts/configure.py`.

## Script Notes

- If a date is omitted, both scripts use today's local system month/day.
- The exporter output is the only Day One source material needed for analysis.
- Do not persist the raw exporter output as `*.md`, `export.md`, `on-this-day.md`,
  or any other handoff file. If a temporary capture file is accidentally created
  for the raw export, delete it before finishing the run.
- The save script handles Reader upload, cleanup, and any configured note export.

## Output Rules

- Save the analysis to Reader unless the user explicitly asks to preview it in chat.
- Do not paste the full analysis into the conversation during the normal workflow.
- In the normal workflow, the file written to `$WORKDIR/on-this-day-analysis.md` is the deliverable. Chat is only for a brief status update after Reader upload succeeds or for reporting an error.
- `$WORKDIR/on-this-day-analysis.md` should be the only Markdown file intentionally
  created during the normal workflow.
- If no entries are found, still create a short Markdown analysis file that says no Day One entries were found for that date, then save it to Reader.
- If a script fails, report the exact command that failed and the relevant error. Do not silently fall back to MCP tools.

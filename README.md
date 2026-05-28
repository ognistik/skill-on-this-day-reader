# On This Day Reader Skill

A Codex skill for turning Day One's "On This Day" memories into a thoughtful Markdown analysis and saving that analysis to Readwise Reader.

This repo is intentionally shaped as a wrapper around the installable skill. The folder you install is:

```text
on-this-day-reader/
```

Do not copy the whole repository into your skills folder. Copy only the `on-this-day-reader` folder.

## What It Does

The skill reads entries for today's calendar date across previous years from your local Day One database, asks the AI to analyze those entries as a personal-history review, writes the result as Markdown, and saves it to Reader.

The workflow is designed to avoid the MCP route. Instead of relying on Day One MCP or Readwise MCP tools, it uses small local scripts:

- `scripts/export_dayone_on_this_day.py` reads Day One entries directly from the local SQLite database.
- `references/analysis_instructions.md` tells the AI how to write the analysis.
- `scripts/save_reader_document.py` sends the finished Markdown to Readwise Reader with the Readwise CLI.
- `scripts/configure.py` edits `config.json` safely.

This makes the workflow simpler, more portable, and easier for smaller or less tool-aware models to run correctly: export the entries, analyze the exported Markdown, then save the result.

## Safety

The Day One export script opens the database in read-only mode. It does not edit your Day One database, journal entries, attachments, or local files.

The Reader save script creates a new Reader document through the Readwise CLI and moves it to your Reader shortlist. By default, it deletes the temporary analysis Markdown file after a successful upload.

## Requirements

- macOS
- Day One installed and synced locally
- Python 3
- Readwise CLI installed and authenticated

Install and authenticate the Readwise CLI:

```bash
npm install -g @readwise/cli
readwise login
```

You can also authenticate with:

```bash
readwise login-with-token
```

## Install In Codex

Clone or download this repository, then copy only the skill folder:

```bash
mkdir -p ~/.codex/skills
cp -R on-this-day-reader ~/.codex/skills/
```

After installation, the skill should live here:

```text
~/.codex/skills/on-this-day-reader/SKILL.md
```

Then ask Codex:

```text
Use $on-this-day-reader to analyze today's Day One On This Day entries and save the result to Reader.
```

For a specific calendar date:

```text
Use $on-this-day-reader for 05-26 and save it to Reader.
```

## Using With Other AI Apps

This was built as a Codex skill, but the core workflow is plain files and scripts. In another local AI app, point the assistant at `on-this-day-reader/SKILL.md` and ask it to follow the instructions.

The important rule is the same: install or reference the `on-this-day-reader` folder itself, not this entire repository.

## Configuration

Configuration lives in:

```text
on-this-day-reader/config.json
```

Use the configure script from inside the skill folder:

```bash
python3 scripts/configure.py show
```

Common examples:

```bash
python3 scripts/configure.py exclude-journal add "Work Journal"
python3 scripts/configure.py exclude-tag add ".private"
python3 scripts/configure.py sort asc
python3 scripts/configure.py dry-run on
python3 scripts/configure.py dry-run off
```

More configuration details are in:

```text
on-this-day-reader/references/configuration.md
```

## Dry Run

To test without writing to Reader:

```bash
python3 scripts/configure.py dry-run on
```

You can also use a one-off environment override:

```bash
ON_THIS_DAY_DRY_RUN=1 python3 scripts/save_reader_document.py /path/to/on-this-day-analysis.md
```

## Privacy Notes

This skill runs locally, reads your local Day One database, and sends only the final generated analysis to Readwise Reader when saving is enabled.

Your raw Day One export is intended to be read directly by the AI during the run, not saved as a separate handoff file. The skill instructions explicitly avoid persisting duplicate raw export Markdown files.

## Repository Layout

```text
.
├── README.md
├── .gitignore
└── on-this-day-reader/
    ├── SKILL.md
    ├── agents/
    ├── config.json
    ├── references/
    └── scripts/
```

## License

No license has been added yet. Add one before publishing if you want others to reuse, modify, or redistribute this skill under explicit terms.

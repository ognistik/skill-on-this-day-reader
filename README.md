# On This Day Reader

A portable local workflow for turning Day One's "On This Day" memories into a thoughtful Markdown analysis and saving that analysis to Readwise Reader.

This repo is intentionally shaped as a wrapper around the portable workflow folder. The folder you use is:

```text
on-this-day-reader/
```

Do not treat the whole repository as the workflow folder. Use only the `on-this-day-reader` folder.

## What It Does

The workflow reads entries for today's calendar date across previous years from your local Day One database, asks the AI to analyze those entries as a personal-history review, writes the result as Markdown, and saves it to Reader.

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

## Use It With An AI Assistant

Clone or download this repository, then give your AI assistant access to the workflow folder:

```text
on-this-day-reader/
```

Point the assistant at:

```text
on-this-day-reader/SKILL.md
```

Then ask:

```text
Use the on-this-day-reader workflow to analyze today's Day One On This Day entries and save the result to Reader.
```

For a specific calendar date:

```text
Use the on-this-day-reader workflow for 05-26 and save it to Reader.
```

## Installing Into Tool-Specific Skill Folders

Some AI tools support reusable local instruction folders, often called skills, agents, or workflows. If your tool has that kind of feature, install only this folder:

```text
on-this-day-reader/
```

Do not install the repository root unless your tool explicitly expects the README and workflow folder together.

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

## Optional Note URL

The workflow can also open a note URL after the Reader document is created. This is optional and disabled by default.

The default `url_template` is meant for Bear:

```json
"url_template": "bear://x-callback-url/create?title={title}&text={analysis}"
```

The feature is not Bear-specific, though. You can use any app URL or callback URL that accepts text in the URL, as long as the receiving app can handle the amount of text being sent.

Available placeholders:

- `{analysis}`: full Markdown analysis
- `{title}`: generated Reader title
- `{date}`: `MM-DD` date label

The script URL-encodes those values before opening the URL.

Enable note creation:

```bash
python3 scripts/configure.py note on
```

Set a custom URL template:

```bash
python3 scripts/configure.py note-url "bear://x-callback-url/create?title={title}&text={analysis}&tags=on-this-day"
```

## Privacy Notes

This workflow runs locally, reads your local Day One database, and sends only the final generated analysis to Readwise Reader when saving is enabled.

Your raw Day One export is intended to be read directly by the AI during the run, not saved as a separate handoff file. The workflow instructions explicitly avoid persisting duplicate raw export Markdown files.

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

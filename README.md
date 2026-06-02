# On This Day Reader

A portable local workflow packaged as a skill, for turning Day One's "On This Day" memories into a thoughtful Markdown analysis and saving that analysis to Readwise Reader.

The workflow folder you give to your AI assistant is:

```text
on-this-day-reader/
```

The easiest way to get it is the latest release zip:

[Download on-this-day-reader.zip](https://github.com/ognistik/skill-on-this-day-reader/releases/latest/download/on-this-day-reader.zip)

After downloading, unzip it. You should have a folder named `on-this-day-reader`.

## Quick Start

If you already have Day One, Python 3, and the Readwise CLI set up:

1. Download the latest `on-this-day-reader.zip`.
2. Unzip it.
3. Give your AI assistant access to the `on-this-day-reader/` folder.
4. Point the assistant at `on-this-day-reader/SKILL.md`.
5. Ask:

```text
Use the On This Day to Reader workflow to analyze today's Day One On This Day entries and save the result to Reader.
```

For a specific calendar date:

```text
Use the On This Day to Reader workflow for 05-26 and save it to Reader.
```

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
- Day One installed, opened at least once, and synced locally
- Python 3
- Node.js and npm, used to install the Readwise CLI
- Readwise CLI installed and authenticated

If you are comfortable with the command line, the short version is:

```bash
brew install python node
npm install -g @readwise/cli
readwise login
```

If those commands are unfamiliar, the next section walks through them more slowly.

## Beginner Setup

This workflow is local, but it does need a few command-line tools. On a Mac, the simplest way to install them is usually [Homebrew](https://brew.sh/), a package manager for macOS.

### 1. Install Homebrew

Open Terminal on your Mac. Then follow the install instructions on the [Homebrew homepage](https://brew.sh/). Homebrew provides a one-line command you can copy and paste into Terminal.

When Homebrew finishes, close and reopen Terminal. Then check that it works:

```bash
brew --version
```

### 2. Install Python 3

Install Python with Homebrew:

```bash
brew install python
```

Check that Python is available:

```bash
python3 --version
```

This workflow only uses Python's standard library. You do not need to install extra Python packages.

### 3. Install Node.js and npm

The Readwise CLI is installed with npm, which comes with Node.js.

```bash
brew install node
```

Check that npm is available:

```bash
npm --version
```

### 4. Install and authenticate the Readwise CLI

Install the Readwise CLI:

```bash
npm install -g @readwise/cli
```

Then connect it to your Readwise account:

```bash
readwise login
```

The official Readwise CLI page is here: [readwise.io/cli](https://readwise.io/cli).

### 5. Make sure Day One is synced locally

Open the Day One Mac app and make sure the journal entries you want are available on this Mac. The exporter reads from Day One's local database, so entries that have not synced to this computer will not appear.

## Download the Skill

For most people, use the latest release zip

[Download on-this-day-reader.zip](https://github.com/ognistik/skill-on-this-day-reader/releases/latest/download/on-this-day-reader.zip)

Otherwise, you can directly [get the folder from this repo](https://github.com/ognistik/skill-on-this-day-reader/tree/main/on-this-day-reader).

## MCP Alternative

This workflow intentionally does not use MCP during the normal run. It uses local scripts plus the Readwise CLI because that keeps the steps explicit and portable.

There is another way to build a similar workflow: use the official MCP servers and instruct your AI assistant to connect Day One and Readwise directly.

Useful links:

- Day One MCP server guide: [dayoneapp.com/guides/day-one-for-mac/day-one-mcp-server](https://dayoneapp.com/guides/day-one-for-mac/day-one-mcp-server/)
- Readwise MCP: [readwise.io/mcp](https://readwise.io/mcp)
- Readwise CLI: [readwise.io/cli](https://readwise.io/cli)

If you go the MCP route, you can ask Codex, Claude, or another MCP-capable assistant something like:

```text
Use the Day One MCP server to find my On This Day entries for today, write a reflective personal-history analysis, and save the finished analysis to Readwise Reader using the Readwise MCP server.
```

The MCP route may be more natural if your assistant already has both MCP servers configured. This skill is useful when you want a reusable local workflow that does not depend on the assistant choosing the right MCP calls every time.

## Configuration

Configuration lives in:

```text
on-this-day-reader/config.json
```

You do not have to edit this file by hand. Once your AI assistant has access to the skill folder, you can ask it to read the configuration instructions and make the change for you.

For example:

```text
Use the On This Day to Reader skill configuration instructions to exclude my Work Journal.
```

```text
Use the On This Day to Reader skill configuration instructions to turn on dry run.
```

The instructions the assistant should read are here:

```text
on-this-day-reader/references/configuration.md
```

If you prefer to configure it yourself, use the configure script from inside the skill folder:

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
    ├── config.json
    ├── references/
    └── scripts/
```

## License

MIT. Day One and Readwise are trademarks of their respective owners. This project is unofficial and not affiliated with Day One or Readwise.

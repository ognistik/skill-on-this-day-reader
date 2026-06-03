# On This Day Reader

A portable local skill for turning Day One's "On This Day" memories into a thoughtful Markdown analysis and saving that analysis to [Readwise Reader](https://readwise.io/aft/).

## Quick Start

If you already have Day One, Python 3, and the Readwise CLI set up:

1. Download [the latest version of the skill.](https://github.com/ognistik/skill-on-this-day-reader/releases/latest/download/on-this-day-reader.zip)
2. Unzip it.
3. Give your AI assistant access to the `on-this-day-reader/` skill folder.
4. Ask:

```text
Use the On This Day to Reader workflow to analyze today's Day One On This Day entries and save the result to Reader.
```

For a specific calendar date:

```text
Use the On This Day to Reader workflow for 05-26 and save it to Reader.
```

New to the command line? Use the step-by-step walkthrough: [Beginner Setup](docs/beginner-setup.md).

## Requirements

- macOS
- Day One installed, opened at least once, and synced locally
- Python 3
- Node.js and npm
- Readwise CLI installed and authenticated

Short command-line setup:

```bash
brew install python node
npm install -g @readwise/cli
readwise login
```

Need those steps explained one at a time? See [Beginner Setup](docs/beginner-setup.md).

## What It Does

The skill reads entries for today's calendar date across previous years from your local Day One database, asks the AI to analyze those entries as a personal-history review, writes the result as Markdown, and saves it to Reader.

It intentionally avoids the normal MCP route. Instead, it uses small local scripts so the workflow stays explicit and portable:

- `scripts/export_dayone_on_this_day.py` reads Day One entries directly from the local SQLite database.
- `references/analysis_instructions.md` tells the AI how to write the analysis.
- `scripts/save_reader_document.py` sends the finished Markdown to Readwise Reader with the Readwise CLI.
- `scripts/configure.py` edits `config.json` safely.

## Configuration

Configuration lives in:

```text
on-this-day-reader/config.json
```

You can ask your AI assistant to configure the skill for you:

```text
Use the On This Day to Reader skill configuration instructions to exclude my Work Journal.
```

```text
Use the On This Day to Reader skill configuration instructions to turn on dry run.
```

The assistant should read:

```text
on-this-day-reader/references/configuration.md
```

If you prefer to configure it yourself, run commands from inside the skill folder:

```bash
python3 scripts/configure.py show
python3 scripts/configure.py exclude-journal add "Work Journal"
python3 scripts/configure.py exclude-tag add ".private"
python3 scripts/configure.py sort asc
python3 scripts/configure.py dry-run on
python3 scripts/configure.py dry-run off
```

More configuration details, including optional note URL creation, are in [configuration.md](on-this-day-reader/references/configuration.md).

## Safety

The Day One export script opens the database in read-only mode. It does not edit your Day One database, journal entries, attachments, or local files.

This workflow runs locally, reads your local Day One database, and sends only the final generated analysis to Readwise Reader when saving is enabled.

## MCP Alternative

This skill is useful when you want a reusable local workflow that does not depend on the assistant choosing the right MCP calls every time. If your assistant already has both MCP servers configured, these links may be useful:

- Day One MCP server guide: [dayoneapp.com/guides/day-one-for-mac/day-one-mcp-server](https://dayoneapp.com/guides/day-one-for-mac/day-one-mcp-server/)
- Readwise MCP: [readwise.io/mcp](https://readwise.io/mcp)
- Readwise CLI: [readwise.io/cli](https://readwise.io/cli)

## Support

If this workflow is useful in your journal or reading practice, I'd be grateful if you [Buy me a coffee](https://buymeacoffee.com/afadingthought/) or support the project through [PayPal](https://paypal.me/obergfilms).

## License

MIT. Day One and Readwise are trademarks of their respective owners. This project is unofficial and not affiliated with Day One or Readwise.

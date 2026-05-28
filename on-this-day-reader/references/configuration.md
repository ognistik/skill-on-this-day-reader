# Configuration

User customization lives in `config.json` at the root of this skill. The easiest and safest way to edit it is with `scripts/configure.py`.

The normal skill workflow should not add command-line options for filtering, cleanup, dry-run behavior, Reader location, or note creation. Edit `config.json` with `configure.py` instead.

## Configure Script

From the skill folder, run:

```bash
python3 scripts/configure.py show
```

Every command prints the updated configuration after it runs.

### Common Commands

Show the current config:

```bash
python3 scripts/configure.py show
```

Exclude one or more journals:

```bash
python3 scripts/configure.py exclude-journal add "Instagram" "Work Journal"
```

Exclude one or more tags:

```bash
python3 scripts/configure.py exclude-tag add ".g tracker" ".a filmreviews"
```

Comma-separated values also work:

```bash
python3 scripts/configure.py exclude-tag add ".g tracker,.a filmreviews"
```

Remove exclusions:

```bash
python3 scripts/configure.py exclude-journal remove "Instagram"
python3 scripts/configure.py exclude-tag remove ".g tracker" ".a filmreviews"
```

Replace the full exclusion list:

```bash
python3 scripts/configure.py exclude-journal set "Instagram" "Work Journal"
python3 scripts/configure.py exclude-tag set ".g tracker" ".a filmreviews"
```

Clear exclusions:

```bash
python3 scripts/configure.py exclude-journal clear
python3 scripts/configure.py exclude-tag clear
```

Set sort order:

```bash
python3 scripts/configure.py sort asc
python3 scripts/configure.py sort desc
```

Turn Reader dry-run on or off:

```bash
python3 scripts/configure.py dry-run on
python3 scripts/configure.py dry-run off
```

Keep or delete the temporary analysis file after Reader save:

```bash
python3 scripts/configure.py delete-files on
python3 scripts/configure.py delete-files off
```

Set a custom Day One database path:

```bash
python3 scripts/configure.py db-path "~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite"
```

Enable or disable optional note creation:

```bash
python3 scripts/configure.py note on
python3 scripts/configure.py note off
```

Set the note URL template:

```bash
python3 scripts/configure.py note-url "bear://x-callback-url/create?title={title}&text={analysis}&tags=on-this-day"
```

Reset the entire config to defaults:

```bash
python3 scripts/configure.py reset
```

Config path:

```text
on-this-day-reader/config.json
```

## Editing With AI

You can ask an AI assistant to edit the configuration for you. Use direct requests like:

- "Use the on-this-day-reader configure script to exclude the Instagram journal."
- "Use the configure script to add `.g tracker` and `.a filmreviews` to the excluded Day One tags."
- "Use the configure script to turn on dry run for the on-this-day-reader skill."
- "Use the configure script to turn off dry run for the on-this-day-reader skill."
- "Use the configure script to enable Bear note creation for the on-this-day analysis."
- "Use the configure script to set the Bear note URL to create notes tagged `on-this-day`."
- "Use the configure script to change the export sort order to newest first."
- "Use the configure script to show me the current on-this-day-reader configuration."

The assistant should use `scripts/configure.py` for these changes. It should not change `SKILL.md`, `analysis_instructions.md`, or the scripts unless you explicitly ask for a behavior change.

## Example

```json
{
  "dayone": {
    "db_path": "~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite",
    "exclude_journals": ["Instagram"],
    "exclude_tags": [".a filmreviews", ".g tracker"],
    "sort": "asc"
  },
  "reader": {
    "delete_files_after_save": true,
    "dry_run": false
  },
  "note": {
    "enabled": false,
    "url_template": "bear://x-callback-url/create?title={title}&text={analysis}",
    "open_in_background": true
  }
}
```

## Day One

- `db_path`: Day One SQLite database path. The script can also use `DAYONE_DB` as an environment override.
- `exclude_journals`: journal names to omit from the export.
- `exclude_tags`: tag names to omit from the export.
- `sort`: `asc` for oldest-first or `desc` for newest-first. The analysis instructions expect `asc`.

The exporter always includes current-year entries.

## Reader

- `delete_files_after_save`: delete the temporary analysis Markdown file after a successful Reader upload.
- `dry_run`: test the save script without writing to Reader.

The script always saves to Reader `shortlist`. Reader title, summary, and stable URL are generated automatically from the `MM-DD` date.

For one-off debugging, `ON_THIS_DAY_DRY_RUN=1` overrides `reader.dry_run` without editing the config file.

Advanced: `ON_THIS_DAY_CONFIG=/path/to/config.json` makes `configure.py` edit a different config file. Normal users should not need this.

## Optional Note URL

If `note.enabled` is true, the save script opens `note.url_template` after a successful Reader upload.

The template is app-agnostic. These placeholders are URL-encoded before substitution:

- `{analysis}`: full Markdown analysis
- `{title}`: Reader title
- `{date}`: `MM-DD` date label

Bear example:

```json
"url_template": "bear://x-callback-url/create?title={title}&text={analysis}&tags=on-this-day"
```

Apps that do not support tags can omit tag-related URL parameters entirely.

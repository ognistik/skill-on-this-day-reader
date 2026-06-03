# Beginner Setup

This guide is for people who want to use On This Day Reader but are new to command-line setup on a Mac.

If you are already comfortable with Terminal, the short version is:

```bash
brew install python node
npm install -g @readwise/cli
readwise login
```

Then download the latest skill zip:

[Download on-this-day-reader.zip](https://github.com/ognistik/skill-on-this-day-reader/releases/latest/download/on-this-day-reader.zip)

## 1. Install Homebrew

Homebrew is a package manager for macOS. It helps install tools like Python and Node.js.

Open Terminal on your Mac. Then follow the install instructions on the [Homebrew homepage](https://brew.sh/). Homebrew provides a one-line command you can copy and paste into Terminal.

When Homebrew finishes, close and reopen Terminal. Then check that it works:

```bash
brew --version
```

If Terminal prints a version number, Homebrew is ready.

## 2. Install Python 3

Install Python with Homebrew:

```bash
brew install python
```

Check that Python is available:

```bash
python3 --version
```

This workflow only uses Python's standard library. You do not need to install extra Python packages.

## 3. Install Node.js and npm

The Readwise CLI is installed with npm, which comes with Node.js.

```bash
brew install node
```

Check that npm is available:

```bash
npm --version
```

## 4. Install and Authenticate the Readwise CLI

Install the Readwise CLI:

```bash
npm install -g @readwise/cli
```

Then connect it to your Readwise account:

```bash
readwise login
```

The official Readwise CLI page is here: [readwise.io/cli](https://readwise.io/cli).

## 5. Make Sure Day One Is Synced Locally

Open the Day One Mac app and make sure the journal entries you want are available on this Mac.

The exporter reads from Day One's local database, so entries that have not synced to this computer will not appear.

## 6. Download the Skill

Download the latest release zip:

[Download on-this-day-reader.zip](https://github.com/ognistik/skill-on-this-day-reader/releases/latest/download/on-this-day-reader.zip)

Unzip it. You should have a folder named:

```text
on-this-day-reader
```

Give your AI assistant access to that folder, then ask:

```text
Use the On This Day to Reader workflow to analyze today's Day One On This Day entries and save the result to Reader.
```

For a specific calendar date, ask:

```text
Use the On This Day to Reader workflow for 05-26 and save it to Reader.
```

## Optional Configuration

You do not need to configure anything for a normal first run.

If you later want to exclude a journal, exclude a tag, turn on dry run, or enable optional note creation, ask your AI to set that up for you.
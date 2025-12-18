# Configuration

YTC stores your transcript library (metadata, transcripts, and logs) in a configurable location. This guide explains how to set up and manage your data storage.

---

## How Configuration Works

YTC determines where to store data using this priority order:

1. **Environment variable** `YTC_DATA_PATH` (highest priority)
2. **User config file** `~/.ytc/config.yaml`
3. **Repository config** `./config/settings.yaml` (for git clone users)
4. **Setup wizard** (runs automatically if nothing is configured)

---

## First-Time Setup

### PyPI Installation (`pip install`)

When you run any YTC command for the first time, you'll see the setup wizard:

```
Welcome to YouTube Transcript Curator (YTC)!

YTC stores YouTube transcripts locally for fast searching and reference.
You need to choose where to store your transcript library.

Recommended: /Users/you/Documents/YTC-Library

[1] Use recommended location
[2] Enter custom path
[3] Use current directory (./ytc-data)

Your choice [1]:
```

Choose an option and YTC will:
- Create the directory structure (`metadata/`, `transcripts/`, `logs/`)
- Save your choice to `~/.ytc/config.yaml`

### Repository Installation (git clone)

If you cloned the repository, YTC uses the built-in `data/output/` directory by default. However, you can still run the setup wizard if you prefer a different location:

```bash
ytc config init
```

---

## The `ytc config` Command

Manage your configuration from the command line.

### View Current Configuration

```bash
ytc config show
```

Output:
```
Config file: ~/.ytc/config.yaml

version: 1
data:
  path: ~/Documents/YTC-Library
```

### Show Data Path

```bash
ytc config path
```

Shows the current data storage path and library statistics.

### Run Setup Wizard

```bash
ytc config init
```

Re-run the interactive setup to change your data location.

### Set Data Path Directly

```bash
ytc config set data.path ~/my-transcripts
```

This creates the directory structure and updates your config.

**Important:** This only changes where YTC looks for data. It does NOT move your existing files. If you want to relocate your library, use `ytc config move` instead.

### Move Library to New Location

```bash
ytc config move ~/Dropbox/YTC-Library
```

This safely relocates your entire library:

1. Copies all files to the new location
2. Verifies the copy is complete and not corrupted
3. Updates your configuration
4. Only then removes the original files

Your data is never at risk - if anything fails, your original library remains intact.

### Reset Configuration

```bash
ytc config reset
```

Removes `~/.ytc/config.yaml`. You'll see a confirmation prompt explaining:

- Your transcript library data is NOT deleted
- Next YTC command will trigger the setup wizard
- You'll need to reconfigure your data path

Use `--force` to skip the confirmation.

### Edit Config File

```bash
ytc config edit
```

Opens the config file in your default editor.

### Show All Config Locations

```bash
ytc config where
```

Shows paths to user config, repo config, and environment variable status.

---

## Configuration File

The user config file is stored at `~/.ytc/config.yaml`:

```yaml
version: 1
data:
  path: ~/Documents/YTC-Library
```

### Fields

| Field | Description |
|-------|-------------|
| `version` | Config format version (for future migrations) |
| `data.path` | Path to your transcript library |

The path supports:
- Home directory shorthand: `~/Documents/YTC-Library`
- Environment variables: `$HOME/transcripts`
- Absolute paths: `/Volumes/External/YTC-Library`

---

## Environment Variable Override

Set `YTC_DATA_PATH` to override all other configuration:

```bash
# Temporary override for one command
YTC_DATA_PATH=/tmp/test-library ytc list

# Permanent override (add to ~/.zshrc or ~/.bash_profile)
export YTC_DATA_PATH=~/Documents/YTC-Library
```

This is useful for:
- Testing with different libraries
- CI/CD pipelines
- Docker containers

---

## Data Directory Structure

Wherever you configure YTC to store data, it creates this structure:

```
YTC-Library/
├── metadata/      # Video metadata (JSON files)
├── transcripts/   # Raw transcript files (TXT)
└── logs/          # Library change history
```

---

## Platform Defaults

When using the setup wizard's "recommended location":

| Platform | Default Path |
|----------|-------------|
| macOS | `~/Documents/YTC-Library` |
| Windows | `~/Documents/YTC-Library` |
| Linux | `~/YTC-Library` |

---

## Common Scenarios

### Moving Your Library

Use `ytc config move` for safe relocation with verification:

```bash
ytc config move /new/location/YTC-Library
```

This is the recommended way to relocate your library. The process:

1. Copies all files
2. Verifies integrity
3. Updates config
4. Removes originals only after success

### Pointing to an Existing Library

If you already have a YTC library (e.g., from another machine or backup), use `set`:

```bash
ytc config set data.path /path/to/existing/YTC-Library
```

This only changes the config - it doesn't move or copy any files.

### Using External Storage

```bash
ytc config move /Volumes/External/YTC-Library
```

### Multiple Libraries

Use environment variables to switch between libraries:

```bash
# Work library
YTC_DATA_PATH=~/work-transcripts ytc list

# Personal library
YTC_DATA_PATH=~/personal-transcripts ytc list
```

Or create shell aliases:

```bash
# Add to ~/.zshrc
alias ytc-work='YTC_DATA_PATH=~/work-transcripts ytc'
alias ytc-personal='YTC_DATA_PATH=~/personal-transcripts ytc'
```

---

## Command Reference

| Command | Description |
|---------|-------------|
| `ytc config show` | Display current configuration |
| `ytc config path` | Show data path and library stats |
| `ytc config init` | Run setup wizard |
| `ytc config set KEY VALUE` | Set a config value |
| `ytc config get KEY` | Get a config value |
| `ytc config edit` | Open config in editor |
| `ytc config move DEST` | Safely move library to new location |
| `ytc config reset` | Remove config file |
| `ytc config where` | Show all config file locations |

---

## Troubleshooting

### "Data directory not found"

Your configured path doesn't exist. Options:

- Run setup wizard: `ytc config init`
- Point to existing data: `ytc config set data.path /path/to/data`

### Config file is corrupted

Reset and reconfigure:

```bash
ytc config reset
ytc config init
```

### Permission denied

Ensure you have write access to the configured directory:

```bash
ls -la ~/Documents/YTC-Library
```

### Move failed partway through

If `ytc config move` fails:

- Your original library is intact (no data loss)
- An incomplete copy may exist at the destination
- Remove the incomplete copy manually if needed
- Retry with `ytc config move`

---

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Complete command reference
- [FETCH.md](./FETCH.md) - Fetching transcripts

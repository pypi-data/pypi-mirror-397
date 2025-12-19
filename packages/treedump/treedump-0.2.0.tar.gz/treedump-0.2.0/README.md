# treedump v0.2.0

`treedump` walks a directory tree and produces a single text dump containing:

1. The directory tree structure (first)
2. The contents of all **text files** in that tree (second)

Binary files are never dumped.  
The output file itself is never re-ingested.

By default, hidden files and directories are excluded.

This tool is designed for:
- code review and audits
- LLM context ingestion
- archiving project snapshots
- inspecting unfamiliar repositories

---

## Installation

Install from PyPI:

    pip install treedump

For development or local testing:

    pip install -e .

---

## Basic usage

Run in any directory:

    treedump

This creates `dump.txt` in the current directory.

---

## Output format

The output is structured and deterministic.

Tree structure is always written first, followed by file contents.

Example:

    ===== TREE STRUCTURE =====
    .
    ./src
    ./src/main.py
    ./README.md
    ===== END TREE STRUCTURE =====

    ===== FILE: src/main.py =====
    <file contents>
    ===== END FILE: src/main.py =====

    ===== FILE: README.md =====
    <file contents>
    ===== END FILE: README.md =====

---

## Ignore behavior (important)

### Default behavior

Ignore rules are determined as follows:

1. If a `.gitignore` file exists in the current directory:
   - Only `.gitignore` rules are used
   - Built-in defaults are NOT applied

2. If no `.gitignore` exists:
   - A safe built-in ignore list is used

The built-in ignore list includes:

- version control and tooling directories  
  `.git/`, `__pycache__/`, `venv/`, `.venv/`, `node_modules/`,  
  `.mypy_cache/`, `.pytest_cache/`, `.idea/`, `.vscode/`

- compiled and noisy artifacts  
  `*.pyc`, `*.log`

- secret-bearing files  
  `.env`, `.env.*`, `*.env`  
  `.secrets`, `.secrets.*`  
  `*.key`, `*.pem`, `*.crt`, `*.p12`, `*.keystore`  
  `id_rsa`, `id_ed25519`, `*.pub`  
  `credentials`, `credentials.*`  
  `.aws/`, `.ssh/`

Hidden files are excluded by default at the directory traversal level.

---

## Ignore options

### Disable all ignore rules

    treedump --ignore-off

When this flag is used:
- all ignore rules are disabled
- binary files are still skipped
- the output file is still excluded

Use with care.

---

### Add ignore files

    treedump --ignore .gitignore custom.ignore

Ignore files use simple glob-style patterns.  
Empty lines and comments (`#`) are ignored.

---

### Add ignore patterns inline

    treedump --ignore-pattern "*.sql" "*.db"

Ignore files and inline patterns are additive unless `--ignore-off` is specified.

---

## Other options

### Change output file name

    treedump --output project_dump.txt

---

### Omit tree structure

    treedump --no-tree

Only file contents will be written.

---

### Include hidden files and directories

    treedump --include-hidden

Includes dotfiles and dot-directories (such as `.env`, `.git/`, `.github/`),
subject to ignore rules.

---

### Show version

    treedump --version

---

## Requirements

- Python 3.9 or newer
- External commands available in PATH:
  - `tree`
  - `file`

These are standard on most Unix-like systems.

---

## Philosophy

`treedump` follows classic Unix principles:

- structure before content
- text-only by default
- hidden files excluded unless explicitly requested
- explicit behavior over clever inference
- safe defaults with deliberate escape hatches
- boring, predictable output

It intentionally does less than a full indexing or archival system.

---

## License

MIT

#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import fnmatch

from treedump import __version__

DEFAULT_IGNORE_PATTERNS = [
    ".git/*",
    "__pycache__/*",
    "venv/*",
    ".venv/*",
    "node_modules/*",
    ".mypy_cache/*",
    ".pytest_cache/*",
    ".idea/*",
    ".vscode/*",
    "*.pyc",
    "*.log",
    ".env",
    ".env.*",
    "*.env",
    ".secrets",
    ".secrets.*",
    "*.key",
    "*.pem",
    "*.crt",
    "*.p12",
    "*.keystore",
    "id_rsa",
    "id_ed25519",
    "*.pub",
    "credentials",
    "credentials.*",
    ".aws/*",
    ".ssh/*",
]

def run(cmd):
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

def is_text_file(path: Path) -> bool:
    try:
        mime = run(["file", "--mime-type", "-b", str(path)]).strip()
        return mime.startswith("text/")
    except Exception:
        return False

def load_ignore_file(path: Path):
    patterns = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
    except Exception:
        pass
    return patterns

def is_ignored(path: Path, patterns):
    posix_path = path.as_posix()
    for pattern in patterns:
        if fnmatch.fnmatch(posix_path, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
    return False

def main():
    parser = argparse.ArgumentParser(
        prog="treedump",
        description="Dump all text files in a directory tree into a single file.",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"treedump {__version__}",
    )
    parser.add_argument(
        "--output",
        default="dump.txt",
        help="output file name (default: dump.txt)",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="do not include tree structure at the top of the dump",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="include hidden files and directories",
    )
    parser.add_argument(
        "--ignore-off",
        action="store_true",
        help="disable all ignore rules (except binary files and output file)",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        help="path(s) to ignore pattern files",
    )
    parser.add_argument(
        "--ignore-pattern",
        nargs="*",
        default=[],
        help="additional ignore patterns (glob syntax)",
    )

    args = parser.parse_args()

    root = Path(".").resolve()
    output_path = root / args.output
    gitignore_path = root / ".gitignore"

    ignore_patterns = []

    if not args.ignore_off:
        if gitignore_path.exists():
            ignore_patterns.extend(load_ignore_file(gitignore_path))
        else:
            ignore_patterns.extend(DEFAULT_IGNORE_PATTERNS)

        for ignore_file in args.ignore:
            ignore_patterns.extend(load_ignore_file(Path(ignore_file)))

        ignore_patterns.extend(args.ignore_pattern)

    output_path.write_text("")

    tree_cmd = ["tree", "-if", "--noreport", "."]
    if args.include_hidden:
        tree_cmd.insert(1, "-a")

    tree_output = run(tree_cmd)

    if not args.no_tree:
        with output_path.open("a") as out:
            out.write("===== TREE STRUCTURE =====\n")
            out.write(tree_output)
            out.write("\n===== END TREE STRUCTURE =====\n\n")

    for line in tree_output.splitlines():
        path = Path(line)

        if not path.is_file():
            continue

        if path.resolve() == output_path.resolve():
            continue

        if not args.ignore_off and is_ignored(path, ignore_patterns):
            continue

        if not is_text_file(path):
            continue

        with output_path.open("a") as out:
            out.write(f"===== FILE: {path} =====\n")
            out.write(path.read_text(errors="ignore"))
            out.write(f"\n===== END FILE: {path} =====\n\n")

if __name__ == "__main__":
    main()

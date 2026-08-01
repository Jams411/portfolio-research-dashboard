#!/usr/bin/env python3
"""Validate repository-local targets in tracked Markdown files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


LINK_PATTERN = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")


def tracked_markdown_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "*.md"], text=True)
    return [Path(line) for line in output.splitlines() if line]


def local_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return None
    return unquote(parsed.path)


def main() -> int:
    failures: list[tuple[Path, str]] = []
    files = tracked_markdown_files()
    for markdown_file in files:
        for raw_target in LINK_PATTERN.findall(markdown_file.read_text(encoding="utf-8")):
            target = local_target(raw_target)
            if target and not (markdown_file.parent / target).resolve().exists():
                failures.append((markdown_file, raw_target))

    print(f"Validated {len(files)} tracked Markdown files.")
    if not failures:
        print("All repository-local Markdown link targets exist.")
        return 0
    for source, target in failures:
        print(f"{source}: missing target {target}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

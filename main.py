#!/usr/bin/env python3
"""Entrypoint: copy the rendered poster into the grader's output folder.

The poster itself is drawn by draw.py and stored in this repository as
entry.png. This program only moves those bytes to $MAKEFUN_OUTPUT_DIR
(default /output) under the name entry.png, so the two grader runs
produce identical output.
"""

import os
import shutil
import sys

SOURCE = "entry.png"
TARGET = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def check_png(path):
    """Refuse to ship anything that is not a small, well-formed PNG."""
    with open(path, "rb") as f:
        head = f.read(len(PNG_MAGIC))
        if head != PNG_MAGIC:
            raise ValueError(f"{path}: not a PNG (bad magic bytes)")
        f.seek(0, os.SEEK_END)
        size = f.tell()
    if size > MAX_BYTES:
        raise ValueError(f"{path}: {size} bytes exceeds the 1 MiB limit")
    if size == 0:
        raise ValueError(f"{path}: empty file")
    return size


def main():
    try:
        size = check_png(SOURCE)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    dest_dir = output_dir()
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copyfile(SOURCE, os.path.join(dest_dir, TARGET))
    print(f"wrote {os.path.join(dest_dir, TARGET)} ({size} bytes)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Entrypoint for the news-image-20261123 entry (Python 3.13, stdlib only).

The poster is drawn at build time by draw.py and shipped in this repo as
entry.png; this program simply copies it to the grader's output directory.
The copy is byte-for-byte, so two runs always write identical bytes.
No drawing happens here, so this entrypoint needs no fonts, no Pillow
and no network at run time.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()

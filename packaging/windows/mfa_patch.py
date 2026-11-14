"""Prepare a minimal, checked source patch for MFA 3.3.8's SQLite imports."""
import argparse
from pathlib import Path


def prepare(prefix, destination):
    source = prefix / "Lib/site-packages/montreal_forced_aligner/alignment/base.py"
    text = source.read_text(encoding="utf-8")
    for kind in ["word", "phone"]:
        old = f'f".import {{{kind}_csv_path.as_posix()}} {kind}_interval_temp"'
        new = f'f\'.import "{{{kind}_csv_path.as_posix()}}" {kind}_interval_temp\''
        if text.count(old) != 1:
            raise ValueError("MFA SQLite patch no longer matches; review the dependency update.")
        text = text.replace(old, new)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("# VocaListener Windows packaging: quote SQLite CSV paths containing spaces.\n" + text, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.prefix, args.destination)

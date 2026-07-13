#!/usr/bin/env python3
"""Validate and save an IdeaHub dataset without ever replacing an existing file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_dataset import errors_for


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True, help="normalized dataset JSON")
    parser.add_argument("--out", type=Path, required=True, help="new dataset destination")
    args = parser.parse_args()
    try:
        payload = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read dataset: {error}", file=sys.stderr)
        return 1

    errors = errors_for(payload)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as saved:
            json.dump(payload, saved, ensure_ascii=False, indent=2)
            saved.write("\n")
    except FileExistsError:
        print(f"dataset already exists: {args.out}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"cannot save dataset: {error}", file=sys.stderr)
        return 1
    print(f"saved immutable IdeaHub dataset: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

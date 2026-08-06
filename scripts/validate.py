#!/usr/bin/env python3
"""Validate catalog, board meta, and existing snapshots against JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    meta_schema = load(ROOT / "schemas" / "board-meta.schema.json")
    snap_schema = load(ROOT / "schemas" / "board-snapshot.schema.json")
    catalog_schema = load(ROOT / "schemas" / "catalog.schema.json")

    meta_v = Draft202012Validator(meta_schema)
    snap_v = Draft202012Validator(snap_schema)
    cat_v = Draft202012Validator(catalog_schema)

    errors: list[str] = []

    catalog_path = ROOT / "catalogs" / "index.json"
    for err in sorted(cat_v.iter_errors(load(catalog_path)), key=lambda e: e.path):
        errors.append(f"{catalog_path}: {err.message}")

    boards_dir = ROOT / "boards"
    for meta_path in sorted(boards_dir.glob("*/meta.json")):
        data = load(meta_path)
        for err in sorted(meta_v.iter_errors(data), key=lambda e: e.path):
            errors.append(f"{meta_path}: {err.message}")

        latest = meta_path.parent / "latest.json"
        if latest.exists():
            for err in sorted(snap_v.iter_errors(load(latest)), key=lambda e: e.path):
                errors.append(f"{latest}: {err.message}")

        for hist in sorted((meta_path.parent / "history").glob("*.json")):
            for err in sorted(snap_v.iter_errors(load(hist)), key=lambda e: e.path):
                errors.append(f"{hist}: {err.message}")

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK: catalog, meta, and snapshots validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

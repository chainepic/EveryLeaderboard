#!/usr/bin/env python3
"""Run connectors for boards that are due under their own schedule."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.schedule_lib import (  # noqa: E402
    history_dir,
    is_due,
    iter_board_slugs,
    latest_path,
    load_meta,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Only print due boards")
    parser.add_argument("--slug", action="append", help="Limit to one or more slugs")
    parser.add_argument("--force", action="store_true", help="Ignore schedule gate")
    parser.add_argument(
        "--only-enabled",
        action="store_true",
        default=True,
        help="Skip connectors with enabled=false (default)",
    )
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="Also attempt boards whose connector.enabled is false",
    )
    args = parser.parse_args()

    slugs = args.slug or iter_board_slugs()
    now = datetime.now(timezone.utc)
    due: list[str] = []

    for slug in slugs:
        meta = load_meta(slug)
        enabled = meta.get("connector", {}).get("enabled", False)
        if not args.include_disabled and not enabled:
            continue
        if args.force or is_due(meta, now):
            due.append(slug)

    if args.dry_run:
        print(json.dumps({"now": now.isoformat(), "due": due}, indent=2))
        return 0

    if not due:
        print("No due boards.")
        return 0

    failures = 0
    for slug in due:
        meta = load_meta(slug)
        module_name = meta["connector"]["module"]
        print(f"→ running {slug} ({module_name})")
        try:
            mod = importlib.import_module(f"connectors.{module_name}")
            snapshot = mod.fetch(meta)
            out = latest_path(slug)
            out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            # also archive by as_of date when possible
            as_of = str(snapshot.get("as_of", now.date().isoformat()))[:10]
            hist = history_dir(slug)
            hist.mkdir(parents=True, exist_ok=True)
            (hist / f"{as_of}.json").write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"  wrote {out.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001 — surface per-board errors in CI logs
            failures += 1
            print(f"  ERROR {slug}: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Rebuild catalogs/index.json from boards/*/meta.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "boards"


def main() -> None:
    boards = []
    for meta_path in sorted(BOARDS.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        boards.append(
            {
                "slug": meta["slug"],
                "title": meta["title"],
                "title_zh": meta.get("title_zh"),
                "status": meta["status"],
                "category": meta["category"],
                "cadence": meta["schedule"]["cadence"],
                "metric_id": meta["metric"]["id"],
                "tags": meta.get("tags", []),
                "meta_path": f"boards/{meta['slug']}/meta.json",
                "latest_path": f"boards/{meta['slug']}/latest.json",
            }
        )

    catalog = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": "https://github.com/chainepic/EveryLeaderboard",
        "boards": boards,
    }
    out = ROOT / "catalogs" / "index.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(boards)} boards)")


if __name__ == "__main__":
    main()

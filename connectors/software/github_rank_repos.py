"""jaywcjlove/github-rank repos → github-repos-stars."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 100)))
    url = cfg.get("url") or "https://unpkg.com/@wcj/github-rank/dist/repos.json"
    resp = get(url)
    rows = resp.json()
    items = []
    for i, row in enumerate(rows[:top_n], start=1):
        full = row.get("full_name") or row.get("name")
        items.append(
            {
                "rank": int(row.get("rank") or i),
                "id": full,
                "name": full,
                "value": float(row.get("stargazers_count") or row.get("stars") or 0),
                "unit": "stars",
                "meta": {
                    "language": row.get("language"),
                    "forks": row.get("forks_count"),
                    "html_url": row.get("html_url"),
                    "description": (row.get("description") or "")[:200],
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label="stars",
        items=items,
        sources=[
            {
                "name": "jaywcjlove/github-rank",
                "url": url,
                "fetched_at": as_of,
                "http_status": resp.status_code,
            }
        ],
    )

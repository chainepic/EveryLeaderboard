"""jaywcjlove/github-rank users → github-users-followers."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 100)))
    url = cfg.get("url") or "https://unpkg.com/@wcj/github-rank/dist/users.json"
    resp = get(url)
    rows = resp.json()
    items = []
    for i, row in enumerate(rows[:top_n], start=1):
        items.append(
            {
                "rank": int(row.get("rank") or i),
                "id": str(row.get("login") or row.get("id")),
                "name": row.get("name") or row.get("login"),
                "value": float(row.get("followers") or 0),
                "unit": "followers",
                "meta": {
                    "login": row.get("login"),
                    "public_repos": row.get("public_repos"),
                    "html_url": row.get("html_url"),
                    "location": row.get("location"),
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label="followers",
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

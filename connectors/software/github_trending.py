"""GitHub Trending mirror (isboyjc/github-trending-api)."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    since = cfg.get("since", "daily")  # daily|weekly|monthly
    language = cfg.get("language", "all")
    url = (
        "https://raw.githubusercontent.com/isboyjc/github-trending-api/"
        f"main/data/{since}/{language}.json"
    )
    resp = get(url)
    data = resp.json()
    rows = data.get("items") or []
    items = []
    for i, row in enumerate(rows, start=1):
        def _num(v) -> float:
            if isinstance(v, (int, float)):
                return float(v)
            if isinstance(v, str):
                digits = "".join(ch for ch in v if ch.isdigit())
                return float(digits) if digits else 0.0
            return 0.0

        stars_period = _num(row.get("addStars") or row.get("stars_period") or row.get("currentPeriodStars"))
        full = row.get("title") or row.get("full_name") or row.get("name") or ""
        items.append(
            {
                "rank": i,
                "id": full,
                "name": full,
                "value": stars_period,
                "unit": "stars",
                "meta": {
                    "description": row.get("description"),
                    "language": row.get("language"),
                    "url": row.get("url") or row.get("link"),
                    "total_stars": _num(row.get("stars")),
                    "forks": _num(row.get("forks")),
                    "since": since,
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label=since,
        items=items,
        sources=[
            {
                "name": "isboyjc/github-trending-api",
                "url": url,
                "fetched_at": as_of,
                "http_status": resp.status_code,
            }
        ],
    )

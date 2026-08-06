"""open-source-star-rank daily net growth → github-star-delta-daily."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 100)))
    index_url = (
        cfg.get("index_url")
        or "https://728792899-create.github.io/open-source-star-rank/data/index.json"
    )
    idx = get(index_url).json()
    date = cfg.get("date") or idx.get("latest_date")
    if not date:
        raise RuntimeError("star-rank index missing latest_date")
    data_url = (
        "https://728792899-create.github.io/open-source-star-rank/"
        f"data/explore/daily/{date}.json"
    )
    resp = get(data_url)
    rows = (resp.json().get("entries") or [])[:top_n]
    items = []
    for i, row in enumerate(rows, start=1):
        gained = float(row.get("stars_gained") or 0)
        items.append(
            {
                "rank": int(row.get("rank") or i),
                "id": row.get("full_name"),
                "name": row.get("full_name"),
                "value": gained,
                "unit": "stars",
                "meta": {
                    "stars_total": row.get("stars_total"),
                    "language": row.get("language"),
                    "html_url": row.get("html_url"),
                    "rank_change": row.get("rank_change"),
                    "date": date,
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=str(date),
        period_label=f"daily:{date}",
        items=items,
        sources=[
            {
                "name": "open-source-star-rank",
                "url": data_url,
                "fetched_at": as_of,
                "http_status": resp.status_code,
            }
        ],
        notes=f"upstream index updated_at={idx.get('updated_at')}",
    )

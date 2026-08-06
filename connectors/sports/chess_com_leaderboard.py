"""Chess.com public leaderboards → chess-com-* boards."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    category = cfg.get("category", "live_blitz")
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 50)))
    url = "https://api.chess.com/pub/leaderboards"
    resp = get(url)
    data = resp.json()
    rows = data.get(category) or []
    items = []
    for row in rows[:top_n]:
        items.append(
            {
                "rank": int(row.get("rank") or len(items) + 1),
                "id": str(row.get("username") or row.get("player_id")),
                "name": row.get("name") or row.get("username"),
                "value": float(row.get("score") or 0),
                "unit": "rating",
                "meta": {
                    "username": row.get("username"),
                    "title": row.get("title"),
                    "country_url": row.get("country"),
                    "category": category,
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label=category,
        items=items,
        sources=[{"name": "Chess.com", "url": url, "fetched_at": as_of, "http_status": resp.status_code}],
    )

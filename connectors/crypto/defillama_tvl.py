"""DeFiLlama protocols TVL → defillama-tvl-top."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 50)))
    url = "https://api.llama.fi/protocols"
    resp = get(url)
    rows = resp.json()
    ranked = sorted(
        (r for r in rows if isinstance(r.get("tvl"), (int, float)) and r["tvl"] > 0),
        key=lambda r: float(r["tvl"]),
        reverse=True,
    )[:top_n]

    items = []
    for i, row in enumerate(ranked, start=1):
        items.append(
            {
                "rank": i,
                "id": str(row.get("slug") or row.get("name")),
                "name": row.get("name"),
                "value": float(row["tvl"]),
                "unit": "USD",
                "meta": {
                    "category": row.get("category"),
                    "chain": row.get("chain"),
                    "symbol": row.get("symbol"),
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label="live",
        items=items,
        sources=[{"name": "DeFiLlama", "url": url, "fetched_at": as_of, "http_status": resp.status_code}],
    )

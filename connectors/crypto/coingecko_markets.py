"""CoinGecko markets → crypto-marketcap-top100."""

from __future__ import annotations

import os
from typing import Any

import requests

from connectors._common import base_snapshot, utc_now


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    vs = cfg.get("vs_currency", "usd")
    per_page = int(cfg.get("per_page", 100))
    url = "https://api.coingecko.com/api/v3/coins/markets"
    headers = {"accept": "application/json"}
    api_key = os.getenv("COINGECKO_API_KEY")
    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    params = {
        "vs_currency": vs,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=60)
    resp.raise_for_status()
    rows = resp.json()

    items = []
    for i, row in enumerate(rows, start=1):
        items.append(
            {
                "rank": i,
                "id": row.get("id") or row.get("symbol"),
                "name": row.get("name"),
                "value": float(row.get("market_cap") or 0),
                "unit": "USD",
                "meta": {
                    "symbol": row.get("symbol"),
                    "price": row.get("current_price"),
                    "market_cap_rank": row.get("market_cap_rank"),
                },
            }
        )

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label="live",
        items=items,
        sources=[
            {
                "name": "CoinGecko",
                "url": resp.url,
                "fetched_at": as_of,
                "http_status": resp.status_code,
            }
        ],
    )

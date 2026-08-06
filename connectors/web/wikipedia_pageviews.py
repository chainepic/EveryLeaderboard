"""Wikimedia pageviews top → wikipedia-pageviews-top."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    project = cfg.get("project", "en.wikipedia")
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 100)))
    access = cfg.get("access", "all-access")

    last_err: Exception | None = None
    payload = None
    used_url = ""
    status = 0
    as_of_date = ""
    for days_back in range(1, 8):
        day = datetime.now(timezone.utc) - timedelta(days=days_back)
        as_of_date = day.strftime("%Y-%m-%d")
        url = (
            "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
            f"{project}/{access}/{day:%Y}/{day:%m}/{day:%d}"
        )
        try:
            resp = get(url)
            payload = resp.json()
            used_url = url
            status = resp.status_code
            break
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    if payload is None:
        raise RuntimeError(f"pageviews unavailable: {last_err}")

    articles = payload["items"][0]["articles"]
    skip = {"Main_Page", "Special:Search", "-"}
    items = []
    rank = 0
    for row in articles:
        article = row.get("article") or ""
        if article in skip or article.startswith("Special:"):
            continue
        rank += 1
        items.append(
            {
                "rank": rank,
                "id": article,
                "name": article.replace("_", " "),
                "value": int(row.get("views") or 0),
                "unit": "views",
                "meta": {"ns": row.get("ns")},
            }
        )
        if rank >= top_n:
            break

    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=as_of_date,
        period_label=f"day:{as_of_date}",
        items=items,
        sources=[
            {
                "name": "Wikimedia Pageviews API",
                "url": used_url,
                "fetched_at": as_of,
                "http_status": status,
            }
        ],
    )

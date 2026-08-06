"""Steam concurrent players → steam-top-played."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def _app_name(appid: int) -> str:
    url = "https://store.steampowered.com/api/appdetails"
    try:
        resp = get(url, params={"appids": appid, "filters": "basic"}, timeout=30)
        payload = resp.json().get(str(appid)) or {}
        if payload.get("success") and payload.get("data"):
            return payload["data"].get("name") or str(appid)
    except Exception:  # noqa: BLE001
        pass
    return str(appid)


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    top_n = int(cfg.get("top_n", meta.get("limits", {}).get("top_n", 50)))
    url = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    resp = get(url)
    ranks = (resp.json().get("response") or {}).get("ranks") or []
    items = []
    for row in ranks[:top_n]:
        appid = int(row["appid"])
        items.append(
            {
                "rank": int(row.get("rank") or len(items) + 1),
                "id": str(appid),
                "name": _app_name(appid),
                "value": int(row.get("concurrent_in_game") or 0),
                "unit": "players",
                "meta": {
                    "peak_in_game": row.get("peak_in_game"),
                    "appid": appid,
                },
            }
        )

    as_of = utc_now()
    last_update = (resp.json().get("response") or {}).get("last_update")
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label="live",
        items=items,
        sources=[
            {
                "name": "Steam Web API",
                "url": url,
                "fetched_at": as_of,
                "http_status": resp.status_code,
            }
        ],
        notes=f"steam last_update={last_update}" if last_update else None,
    )

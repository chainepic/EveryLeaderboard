"""Shared HTTP helpers for connectors."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_HEADERS = {
    "User-Agent": "EveryLeaderboard/1.0 (+https://github.com/chainepic/EveryLeaderboard)",
    "Accept": "application/json,text/csv,*/*",
}


def get(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 60,
) -> requests.Response:
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    resp = requests.get(url, params=params, headers=h, timeout=timeout)
    resp.raise_for_status()
    return resp


def espn_stat(entry: dict[str, Any], name: str, default: float = 0.0) -> float:
    for s in entry.get("stats") or []:
        if s.get("name") == name:
            try:
                return float(s.get("value"))
            except (TypeError, ValueError):
                return default
    return default

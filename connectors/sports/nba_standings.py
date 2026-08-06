"""NBA standings via ESPN web API → nba-standings."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import espn_stat, get


def fetch(meta: dict[str, Any]) -> dict:
    url = "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings"
    resp = get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = resp.json()

    items = []
    for child in data.get("children") or []:
        conference = child.get("name") or ""
        entries = sorted(
            child.get("standings", {}).get("entries") or [],
            key=lambda e: (
                espn_stat(e, "winPercent"),
                espn_stat(e, "wins"),
            ),
            reverse=True,
        )
        for i, entry in enumerate(entries, start=1):
            team = entry.get("team") or {}
            items.append(
                {
                    "rank": i,  # within conference; overall reassigned below
                    "id": str(team.get("id") or team.get("abbreviation")),
                    "name": team.get("displayName") or team.get("name"),
                    "value": round(espn_stat(entry, "winPercent"), 4),
                    "unit": "ratio",
                    "meta": {
                        "conference": conference,
                        "conference_rank": i,
                        "wins": espn_stat(entry, "wins"),
                        "losses": espn_stat(entry, "losses"),
                        "games_behind": espn_stat(entry, "gamesBehind"),
                        "playoff_seed": espn_stat(entry, "playoffSeed"),
                    },
                }
            )

    # Global order by win% for leaderboard consumers
    items.sort(key=lambda it: (it["value"], it["meta"].get("wins", 0)), reverse=True)
    for i, it in enumerate(items, start=1):
        it["rank"] = i

    as_of = utc_now()
    season = (data.get("season") or {}).get("displayName") or "NBA"
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label=str(season),
        items=items,
        sources=[{"name": "ESPN", "url": url, "fetched_at": as_of, "http_status": resp.status_code}],
    )

"""ESPN soccer standings → soccer-pl-table / soccer-ucl-table."""

from __future__ import annotations

from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import espn_stat, get

ESPN_UA = {"User-Agent": "Mozilla/5.0"}


def _standings_url(league: str) -> str:
    return f"https://site.web.api.espn.com/apis/v2/sports/soccer/{league}/standings"


def _load(league: str, season: int | None = None) -> tuple[dict, Any]:
    params = {"season": season} if season else None
    resp = get(_standings_url(league), params=params, headers=ESPN_UA)
    data = resp.json()
    if not data.get("children"):
        raise RuntimeError(f"ESPN standings empty for {league} season={season}")
    return data, resp


def _pick_season_year(league: str, prefer: int | None = None) -> int | None:
    if prefer:
        return prefer
    now_year = int(utc_now()[:4])
    for year in (None, now_year, now_year - 1, now_year - 2):
        try:
            data, _ = _load(league, year)
            entries = data["children"][0]["standings"]["entries"]
            if any(espn_stat(e, "gamesPlayed") > 0 for e in entries):
                return year
        except Exception:
            continue
    return None


def fetch(meta: dict[str, Any]) -> dict:
    cfg = meta.get("connector", {}).get("config", {})
    league = cfg.get("espn_league") or cfg.get("competition") or "eng.1"
    if league == "PL":
        league = "eng.1"
    if league == "CL":
        league = "uefa.champions"
    season = cfg.get("season")
    season_year = _pick_season_year(league, int(season) if season else None)
    data, resp = _load(league, season_year)

    items = []
    for child in data.get("children") or []:
        group = child.get("name") or child.get("abbreviation") or ""
        for entry in child.get("standings", {}).get("entries") or []:
            team = entry.get("team") or {}
            items.append(
                {
                    "rank": 0,
                    "id": str(team.get("id") or team.get("abbreviation") or team.get("displayName")),
                    "name": team.get("displayName") or team.get("name"),
                    "value": espn_stat(entry, "points"),
                    "unit": "pts",
                    "meta": {
                        "group": group,
                        "wins": espn_stat(entry, "wins"),
                        "losses": espn_stat(entry, "losses"),
                        "ties": espn_stat(entry, "ties"),
                        "games_played": espn_stat(entry, "gamesPlayed"),
                        "goal_diff": espn_stat(entry, "pointDifferential"),
                        "season": child.get("standings", {}).get("seasonDisplayName"),
                    },
                }
            )

    # Single table: sort by points / GD / wins. Multi-group (rare): keep ESPN order within groups then global by points.
    items.sort(
        key=lambda it: (it["value"], it["meta"].get("goal_diff", 0), it["meta"].get("wins", 0)),
        reverse=True,
    )
    for i, it in enumerate(items, start=1):
        it["rank"] = i

    as_of = utc_now()
    season_label = (
        (data.get("children") or [{}])[0]
        .get("standings", {})
        .get("seasonDisplayName", str(season_year or "current"))
    )
    return base_snapshot(
        meta,
        as_of=as_of,
        period_label=season_label,
        items=items,
        sources=[
            {
                "name": "ESPN",
                "url": resp.url,
                "fetched_at": as_of,
                "http_status": resp.status_code,
            }
        ],
    )

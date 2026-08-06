"""Shared schedule helpers for EveryLeaderboard runners."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BOARDS_DIR = ROOT / "boards"


def load_meta(slug: str) -> dict[str, Any]:
    path = BOARDS_DIR / slug / "meta.json"
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def iter_board_slugs() -> list[str]:
    return sorted(p.name for p in BOARDS_DIR.iterdir() if (p / "meta.json").is_file())


def _local_now(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def is_due(meta: dict[str, Any], now_utc: datetime | None = None) -> bool:
    """Return True if this board should run at the given UTC time.

    Rules are intentionally simple for v1:
    - hourly: always due when the workflow wakes (caller should still throttle writes)
    - every_n_hours: due when UTC hour % n == 0 (minute ignored; workflow should run hourly)
    - daily: due once per local calendar day (hour window 0-1 matching cron_hint is NOT enforced;
      rely on workflow calling once/day OR check last run stamp later)
    - weekly: due on configured weekday (Mon=0) in board timezone
    - monthly: due on/after day_of_month_after in board timezone
    - on_release: never auto-due (manual / specialized connector)
    """
    schedule = meta["schedule"]
    cadence = schedule["cadence"]
    tz = schedule.get("timezone", "UTC")
    local = _local_now(tz)
    now_utc = now_utc or datetime.now(timezone.utc)

    active_months = schedule.get("active_months")
    if active_months and local.month not in active_months:
        return False

    if cadence == "hourly":
        return True

    if cadence == "every_n_hours":
        n = int(schedule["every_n_hours"])
        return now_utc.hour % n == 0

    if cadence == "daily":
        return True

    if cadence == "weekly":
        weekday = int(schedule.get("weekday", 0))
        # Python: Monday=0
        return local.weekday() == weekday

    if cadence == "monthly":
        after = int(schedule.get("day_of_month_after", 1))
        return local.day >= after

    if cadence == "on_release":
        return False

    return False


def latest_path(slug: str) -> Path:
    return BOARDS_DIR / slug / "latest.json"


def history_dir(slug: str) -> Path:
    return BOARDS_DIR / slug / "history"

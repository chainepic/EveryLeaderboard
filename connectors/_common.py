from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def base_snapshot(meta: dict[str, Any], *, as_of: str, period_label: str, items: list[dict], sources: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "slug": meta["slug"],
        "generated_at": utc_now(),
        "as_of": as_of,
        "period": {"label": period_label},
        "metric": {"id": meta["metric"]["id"], "unit": meta["metric"]["unit"]},
        "items": items,
        "source_fetched": sources,
    }

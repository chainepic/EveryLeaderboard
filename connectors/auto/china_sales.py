"""China auto sales via chinese-car-watch open CSVs."""

from __future__ import annotations

import csv
import io
from typing import Any

from connectors._common import base_snapshot, utc_now
from connectors._http import get

API = "https://api.github.com/repos/ChenyuHeee/chinese-car-watch/contents"


def _latest_csv(path: str, prefix: str | None = None, suffix: str = ".csv") -> tuple[str, str]:
    """Return (download_url, filename) for newest matching file under path."""
    resp = get(f"{API}/{path}")
    files = [f for f in resp.json() if f.get("type") == "file" and f["name"].endswith(suffix)]
    if prefix:
        files = [f for f in files if f["name"].startswith(prefix) or prefix in f["name"]]
    if not files:
        # try year subdirs
        listing = resp.json()
        dirs = [d for d in listing if d.get("type") == "dir"]
        dirs.sort(key=lambda d: d["name"], reverse=True)
        for d in dirs:
            sub = get(f"{API}/{path}/{d['name']}").json()
            files = [f for f in sub if f.get("type") == "file" and f["name"].endswith(suffix)]
            if prefix:
                files = [f for f in files if prefix in f["name"]]
            if files:
                break
    if not files:
        raise RuntimeError(f"no CSV under {path}")
    files.sort(key=lambda f: f["name"], reverse=True)
    f = files[0]
    return f["download_url"], f["name"]


def _parse_sales_csv(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        name = (row.get("name") or "").strip()
        sales = row.get("sales") or "0"
        try:
            value = float(str(sales).replace(",", ""))
        except ValueError:
            continue
        if not name:
            continue
        rows.append(
            {
                "rank": int(row.get("rank") or len(rows) + 1),
                "id": name,
                "name": name,
                "value": value,
                "unit": "vehicles",
                "meta": {
                    "month": row.get("month"),
                    "type": row.get("type"),
                    "price_range": row.get("price_range"),
                },
            }
        )
    rows.sort(key=lambda r: r["value"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows


def fetch_brand(meta: dict[str, Any]) -> dict:
    url, fname = _latest_csv("data/brands", prefix="brand")
    # prefer *_brand.csv over factory
    resp = get(f"{API}/data/brands")
    years = sorted([d["name"] for d in resp.json() if d.get("type") == "dir"], reverse=True)
    chosen = None
    for y in years:
        files = get(f"{API}/data/brands/{y}").json()
        brand_files = [f for f in files if f["name"].endswith("_brand.csv")]
        if brand_files:
            brand_files.sort(key=lambda f: f["name"], reverse=True)
            chosen = brand_files[0]
            break
    if not chosen:
        url, fname = _latest_csv("data/brands")
    else:
        url, fname = chosen["download_url"], chosen["name"]
    text = get(url).text
    items = _parse_sales_csv(text)
    as_of = utc_now()
    month = items[0]["meta"].get("month") if items else fname
    return base_snapshot(
        meta,
        as_of=str(month),
        period_label=f"month:{month}",
        items=items,
        sources=[
            {
                "name": "chinese-car-watch",
                "url": url,
                "fetched_at": as_of,
                "http_status": 200,
            }
        ],
        notes="Derived from ChenyuHeee/chinese-car-watch CC BY 4.0 CSVs",
    )


def fetch_models(meta: dict[str, Any]) -> dict:
    # prefer style (passenger models) then ev
    resp = get(f"{API}/data/sales")
    years = sorted([d["name"] for d in resp.json() if d.get("type") == "dir"], reverse=True)
    chosen = None
    for y in years:
        files = get(f"{API}/data/sales/{y}").json()
        preferred = [f for f in files if f["name"].endswith("_style.csv")]
        if not preferred:
            preferred = [f for f in files if f["name"].endswith("_ev.csv")]
        if preferred:
            preferred.sort(key=lambda f: f["name"], reverse=True)
            chosen = preferred[0]
            break
    if not chosen:
        raise RuntimeError("no model sales CSV found")
    url, fname = chosen["download_url"], chosen["name"]
    text = get(url).text
    items = _parse_sales_csv(text)
    as_of = utc_now()
    month = items[0]["meta"].get("month") if items else fname
    return base_snapshot(
        meta,
        as_of=str(month),
        period_label=f"month:{month}",
        items=items,
        sources=[
            {
                "name": "chinese-car-watch",
                "url": url,
                "fetched_at": as_of,
                "http_status": 200,
            }
        ],
        notes="Derived from ChenyuHeee/chinese-car-watch CC BY 4.0 CSVs",
    )

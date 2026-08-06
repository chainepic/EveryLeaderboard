"""US weekend box office via Box Office Mojo HTML."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from connectors._common import base_snapshot, utc_now
from connectors._http import get


def _parse_money(text: str) -> float:
    t = (text or "").strip().replace(",", "").replace("$", "")
    if not t or t == "-":
        return 0.0
    return float(t)


def _weekend_candidates(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    hrefs = []
    for a in soup.select("a[href*='/weekend/']"):
        href = a.get("href") or ""
        if re.search(r"/weekend/\d{4}W\d{2}/", href):
            hrefs.append(href.split("?")[0])
    # unique preserve order
    out = []
    seen = set()
    for h in hrefs:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def _parse_weekend(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return []
    items = []
    for tr in table.select("tr")[1:]:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 4:
            continue
        # typical: rank, rw, title, weekend, ...
        title = None
        weekend = 0.0
        rank = None
        a = tr.find("a")
        if a:
            title = a.get_text(strip=True)
        for i, c in enumerate(cells):
            if c.startswith("$") and weekend == 0:
                weekend = _parse_money(c)
                break
        try:
            rank = int(re.match(r"\d+", cells[0]).group()) if re.match(r"\d+", cells[0] or "") else None
        except Exception:
            rank = None
        if not title or weekend <= 0:
            continue
        items.append(
            {
                "rank": rank or len(items) + 1,
                "id": title,
                "name": title,
                "value": weekend,
                "unit": "USD",
                "meta": {"raw_cells": cells[:8]},
            }
        )
    items.sort(key=lambda x: x["value"], reverse=True)
    for i, it in enumerate(items, start=1):
        it["rank"] = i
        it.pop("meta", None)
        it["meta"] = {}
    return items


def fetch(meta: dict[str, Any]) -> dict:
    index_url = "https://www.boxofficemojo.com/weekend/"
    index = get(index_url, headers={"User-Agent": "Mozilla/5.0"})
    candidates = _weekend_candidates(index.text)
    if not candidates:
        raise RuntimeError("no weekend links found")

    chosen_url = None
    items = []
    status = 0
    for rel in candidates[:12]:
        url = urljoin("https://www.boxofficemojo.com", rel)
        resp = get(url, headers={"User-Agent": "Mozilla/5.0"})
        parsed = _parse_weekend(resp.text)
        if parsed:
            chosen_url = url
            items = parsed
            status = resp.status_code
            break
    if not items or not chosen_url:
        raise RuntimeError("no weekend chart with revenue found")

    m = re.search(r"/weekend/(\d{4}W\d{2})/", chosen_url)
    period = m.group(1) if m else "weekend"
    as_of = utc_now()
    return base_snapshot(
        meta,
        as_of=period,
        period_label=period,
        items=items[: int(meta.get("limits", {}).get("top_n", 25))],
        sources=[
            {
                "name": "Box Office Mojo",
                "url": chosen_url,
                "fetched_at": as_of,
                "http_status": status,
            }
        ],
    )

#!/usr/bin/env python3
"""Render shareable leaderboard preview PNGs from board snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"


def _font(
    size: int,
    bold: bool = False,
    *,
    cjk: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: list[str] = []
    if cjk:
        candidates += [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
    if bold:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def _fmt_value(value: float, unit: str) -> str:
    u = (unit or "").upper()
    if u == "USD":
        if value >= 1e12:
            return f"${value / 1e12:.2f}T"
        if value >= 1e9:
            return f"${value / 1e9:.2f}B"
        if value >= 1e6:
            return f"${value / 1e6:.2f}M"
        return f"${value:,.0f}"
    if abs(value) >= 1e9:
        return f"{value / 1e9:.2f}B"
    if abs(value) >= 1e6:
        return f"{value / 1e6:.2f}M"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


def render_top_n(
    snapshot: dict,
    *,
    title: str,
    subtitle: str,
    out: Path,
    top_n: int = 10,
    width: int = 1200,
    cjk: bool = False,
    brand_label: str = "EveryLeaderboard",
    as_of_label: str = "as of",
    footer: str | None = None,
) -> Path:
    items = snapshot.get("items", [])[:top_n]
    if not items:
        raise ValueError("snapshot has no items")

    metric = snapshot.get("metric", {})
    unit = metric.get("unit", "")
    as_of = str(snapshot.get("as_of", ""))[:10]

    # layout
    pad_x = 48
    header_h = 150
    row_h = 64
    footer_h = 56
    height = header_h + row_h * len(items) + footer_h + 24

    img = Image.new("RGB", (width, height), "#0B1220")
    draw = ImageDraw.Draw(img)

    # accent bar
    draw.rectangle((0, 0, 10, height), fill="#0EA5E9")

    title_font = _font(42, bold=True, cjk=cjk)
    sub_font = _font(22, cjk=cjk)
    row_font = _font(26, bold=True, cjk=cjk)
    meta_font = _font(20, cjk=cjk)
    small_font = _font(18, cjk=cjk)

    draw.text((pad_x, 36), title, fill="#F8FAFC", font=title_font)
    draw.text((pad_x, 92), subtitle, fill="#94A3B8", font=sub_font)
    draw.text((width - pad_x - 240, 44), brand_label, fill="#38BDF8", font=meta_font)
    draw.text(
        (width - pad_x - 240, 78),
        f"{as_of_label} {as_of}",
        fill="#64748B",
        font=small_font,
    )
    max_val = max(float(it["value"]) for it in items) or 1.0
    bar_left = 320
    bar_right = width - pad_x - 160
    bar_max_w = bar_right - bar_left

    medals = {1: "#FBBF24", 2: "#CBD5E1", 3: "#F59E0B"}

    y = header_h
    for it in items:
        rank = int(it["rank"])
        name = str(it["name"])
        value = float(it["value"])
        bar_w = int(bar_max_w * (value / max_val))

        # row background
        draw.rounded_rectangle(
            (pad_x - 8, y, width - pad_x + 8, y + row_h - 8),
            radius=12,
            fill="#111827",
        )

        # rank
        rank_color = medals.get(rank, "#64748B")
        draw.ellipse((pad_x + 8, y + 12, pad_x + 44, y + 48), fill=rank_color)
        rank_text = str(rank)
        bbox = draw.textbbox((0, 0), rank_text, font=meta_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (pad_x + 26 - tw / 2, y + 30 - th / 2),
            rank_text,
            fill="#0B1220" if rank <= 3 else "#F8FAFC",
            font=meta_font,
        )

        draw.text((pad_x + 60, y + 16), name, fill="#F1F5F9", font=row_font)

        # bar
        draw.rounded_rectangle(
            (bar_left, y + 20, bar_left + max(bar_w, 8), y + 40),
            radius=8,
            fill="#0284C7",
        )
        # soft highlight
        draw.rounded_rectangle(
            (bar_left, y + 20, bar_left + max(int(bar_w * 0.35), 4), y + 28),
            radius=4,
            fill="#38BDF8",
        )

        val_text = _fmt_value(value, unit)
        draw.text((bar_right + 16, y + 16), val_text, fill="#E2E8F0", font=meta_font)
        y += row_h

    footer_text = footer or (
        "Objective rankings · JSON API · github.com/chainepic/EveryLeaderboard"
    )
    draw.text((pad_x, height - 40), footer_text, fill="#64748B", font=small_font)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    return out


def render_hero_banner(
    out: Path,
    *,
    width: int = 1280,
    height: int = 420,
    cjk: bool = False,
    title: str = "EveryLeaderboard",
    subtitle: str = "Open catalog of objective, quantifiable rankings",
    tags: str = "Sales · Standings · Market caps · Downloads",
    cta: str = "JSON API ready",
) -> Path:
    img = Image.new("RGB", (width, height), "#0B1220")
    draw = ImageDraw.Draw(img)

    # gradient-ish blocks
    for i in range(8):
        x0 = 80 + i * 140
        h = 80 + (7 - i) * 28
        y0 = height - 70 - h
        color = ["#0369A1", "#0284C7", "#0EA5E9", "#38BDF8"][i % 4]
        draw.rounded_rectangle((x0, y0, x0 + 88, height - 70), radius=14, fill=color)

    draw.rectangle((0, 0, 14, height), fill="#0EA5E9")
    title_font = _font(56, bold=True, cjk=cjk)
    sub_font = _font(26, cjk=cjk)
    draw.text((64, 70), title, fill="#F8FAFC", font=title_font)
    draw.text((64, 150), subtitle, fill="#94A3B8", font=sub_font)
    draw.text((64, 200), tags, fill="#64748B", font=_font(22, cjk=cjk))
    draw.rounded_rectangle((64, 270, 64 + 24 + 12 * len(cta), 322), radius=10, fill="#0EA5E9")
    draw.text((88, 282), cta, fill="#0B1220", font=_font(22, bold=True, cjk=cjk))

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="crypto-marketcap-top100")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    ASSETS.mkdir(parents=True, exist_ok=True)
    render_hero_banner(ASSETS / "banner.png")
    render_hero_banner(
        ASSETS / "banner.zh-CN.png",
        cjk=True,
        title="EveryLeaderboard",
        subtitle="客观、可量化的排行榜开放目录",
        tags="销量 · 积分榜 · 市值 · 下载量",
        cta="可直接调用 JSON",
    )

    snap_path = ROOT / "boards" / args.slug / "latest.json"
    if not snap_path.exists():
        print(f"skip board preview: missing {snap_path}")
        return 0

    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    if args.slug == "crypto-marketcap-top100":
        render_top_n(
            snap,
            title="Crypto Market Cap Top 10",
            subtitle="Circulating market capitalization · CoinGecko",
            out=ASSETS / "preview-crypto-top10.png",
            top_n=args.top,
        )
        render_top_n(
            snap,
            title="全球加密货币市值 Top 10",
            subtitle="流通市值 · 数据来源 CoinGecko",
            out=ASSETS / "preview-crypto-top10.zh-CN.png",
            top_n=args.top,
            cjk=True,
            as_of_label="数据日期",
            footer="客观榜单 · JSON API · github.com/chainepic/EveryLeaderboard",
        )
    else:
        render_top_n(
            snap,
            title=args.slug,
            subtitle="EveryLeaderboard snapshot",
            out=ASSETS / f"preview-{args.slug}.png",
            top_n=args.top,
        )

    for name in sorted(p.name for p in ASSETS.glob("*.png")):
        print(f"wrote docs/assets/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

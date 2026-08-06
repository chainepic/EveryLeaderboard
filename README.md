<div align="center">

<img src="docs/assets/logo.svg" alt="EveryLeaderboard logo" width="88" height="88" />

# EveryLeaderboard

**Open catalog of objective, quantifiable leaderboards.**

[English](README.md) · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-0ea5e9?style=flat-square)](LICENSE)
[![Boards](https://img.shields.io/badge/boards-15-0284c7?style=flat-square)](catalogs/index.json)
[![Schema](https://img.shields.io/badge/schema-v1.0.0-38bdf8?style=flat-square)](schemas/)
[![GitHub stars](https://img.shields.io/github/stars/chainepic/EveryLeaderboard?style=flat-square)](https://github.com/chainepic/EveryLeaderboard/stargazers)

<br/>

<img src="docs/assets/banner.png" alt="EveryLeaderboard banner" width="860" />

</div>

---

> [!IMPORTANT]
> Measurable rankings with cited sources only — **not** editorial tier lists or subjective S/A/B opinions.

## Preview

Live board rendered from JSON → shareable PNG (auto-refreshed by Actions when snapshots update):

<div align="center">
  <img src="docs/assets/preview-crypto-top10.png" alt="Crypto Market Cap Top 10 preview" width="860" />
  <p><sub>Crypto Market Cap Top 10 · generated from <code>boards/crypto-marketcap-top100/latest.json</code></sub></p>
</div>

Regenerate locally:

```bash
python scripts/render_preview.py
```

## Why

Rankings are often locked in paywalled PDFs or messy blog HTML. This repo turns stable public sources into:

| Deliverable | Path |
| --- | --- |
| Browsable catalog | [`catalogs/index.json`](catalogs/index.json) |
| Call-ready snapshots | `boards/{slug}/latest.json` |
| Diffable history | `boards/{slug}/history/` |
| Shareable previews | [`docs/assets/`](docs/assets/) |

## Features

| | |
| --- | --- |
| 📊 **Objective only** | Numeric metrics with units |
| 🖼️ **Shareable images** | PNG previews rendered from snapshots |
| ⏱️ **Per-board schedules** | Hourly / daily / weekly / monthly / on-release |
| 🔌 **Connectors** | One adapter per source family |
| 🧾 **Provenance** | Sources + methodology in each `meta.json` |
| 🌐 **Zero-server API** | `raw.githubusercontent.com` / jsDelivr |

## API (zero server)

```bash
curl -sL https://raw.githubusercontent.com/chainepic/EveryLeaderboard/main/catalogs/index.json
curl -sL https://raw.githubusercontent.com/chainepic/EveryLeaderboard/main/boards/crypto-marketcap-top100/latest.json
```

CDN:

```text
https://cdn.jsdelivr.net/gh/chainepic/EveryLeaderboard@main/boards/{slug}/latest.json
```

## Board catalog

| Board | Cadence | Status | Metric |
| --- | --- | --- | --- |
| [crypto-marketcap-top100](boards/crypto-marketcap-top100/meta.json) | every 6h | experimental | market_cap_usd |
| [nba-standings](boards/nba-standings/meta.json) | daily* | planned | win_pct |
| [soccer-pl-table](boards/soccer-pl-table/meta.json) | daily* | planned | points |
| [soccer-ucl-table](boards/soccer-ucl-table/meta.json) | daily* | planned | points |
| [steam-top-played](boards/steam-top-played/meta.json) | daily | planned | ccu |
| [github-trending-daily](boards/github-trending-daily/meta.json) | daily | planned | stars_period |
| [github-trending-weekly](boards/github-trending-weekly/meta.json) | weekly | planned | stars_period |
| [hf-models-trending](boards/hf-models-trending/meta.json) | daily | planned | downloads |
| [npm-react-ecosystem](boards/npm-react-ecosystem/meta.json) | weekly | planned | downloads_week |
| [pypi-top-tracked](boards/pypi-top-tracked/meta.json) | weekly | planned | downloads_month |
| [wikipedia-pageviews-top](boards/wikipedia-pageviews-top/meta.json) | daily | planned | pageviews |
| [china-nev-brand-sales](boards/china-nev-brand-sales/meta.json) | monthly | planned | units |
| [china-passenger-car-sales](boards/china-passenger-car-sales/meta.json) | monthly | planned | units |
| [box-office-weekend-us](boards/box-office-weekend-us/meta.json) | weekly | planned | revenue_usd |
| [imdb-top250](boards/imdb-top250/meta.json) | weekly | planned | rating |

\* Season-aware (`active_months` in meta).

## Quick start

```bash
git clone https://github.com/chainepic/EveryLeaderboard.git
cd EveryLeaderboard
python3 -m pip install -r requirements.txt

python scripts/validate.py
python scripts/run_due.py --dry-run
python scripts/run_due.py --slug crypto-marketcap-top100 --force
python scripts/render_preview.py
```

## Repository layout

```text
boards/<slug>/latest.json    # data
docs/assets/*.png            # shareable previews
scripts/render_preview.py    # JSON → PNG
scripts/run_due.py           # per-board schedule runner
connectors/                  # source adapters
```

```mermaid
flowchart LR
  A[Public sources] --> B[Connectors]
  B --> C[latest.json]
  C --> D[PNG previews]
  C --> E[raw.githubusercontent / jsDelivr]
  F[GitHub Actions] -->|per-board cadence| B
```

## Contributing

Open an issue with: slug, metric + unit, source URL, cadence.  
Subjective / unauditable lists will be rejected.

## License

- **Code**: [MIT](LICENSE)
- **Data**: declared per board in `meta.json` — respect upstream terms

---

<div align="center">
<sub>English · <a href="README.zh-CN.md">简体中文</a></sub>
</div>

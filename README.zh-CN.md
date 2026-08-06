<div align="center">

<img src="docs/assets/logo.svg" alt="EveryLeaderboard logo" width="88" height="88" />

# EveryLeaderboard

**客观、可量化的排行榜开放目录。**

[English](README.md) · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-0ea5e9?style=flat-square)](LICENSE)
[![Boards](https://img.shields.io/badge/boards-22-0284c7?style=flat-square)](catalogs/index.json)
[![Schema](https://img.shields.io/badge/schema-v1.0.0-38bdf8?style=flat-square)](schemas/)
[![GitHub stars](https://img.shields.io/github/stars/chainepic/EveryLeaderboard?style=flat-square)](https://github.com/chainepic/EveryLeaderboard/stargazers)

<br/>

<img src="docs/assets/banner.zh-CN.png" alt="EveryLeaderboard 横幅" width="860" />

</div>

---

> [!IMPORTANT]
> 只收**能量化、能核对来源**的榜单。编辑部主观梯队、S/A/B 观点榜不在范围内。

## 预览图

JSON 快照会渲染成可转发的 PNG（快照更新后由 Actions 重新出图）：

<div align="center">
  <img src="docs/assets/preview-crypto-top10.zh-CN.png" alt="全球加密货币市值 Top 10 预览" width="860" />
  <p><sub>全球加密货币市值 Top 10 · 由 <code>boards/crypto-marketcap-top100/latest.json</code> 生成</sub></p>
</div>

<div align="center">
  <img src="docs/assets/preview-steam-top10.zh-CN.png" alt="Steam 同时在线 Top 10" width="860" />
  <p><sub>Steam 同时在线 Top 10 · 由 <code>boards/steam-top-played/latest.json</code> 生成</sub></p>
</div>


本地重新出图：

```bash
python scripts/render_preview.py
```

## 这个项目解决什么

网上很多「排行」要么锁在付费研报里，要么散落在格式不一的博客表格里。这里把稳定的公开数据源收成：

| 你能拿到什么 | 路径 |
| --- | --- |
| 榜单目录 | [`catalogs/index.json`](catalogs/index.json) |
| 最新快照 | `boards/{slug}/latest.json` |
| 历史存档 | `boards/{slug}/history/` |
| 可传播预览图 | [`docs/assets/`](docs/assets/) |

## 特性

| | |
| --- | --- |
| 📊 **只做客观榜** | 指标带单位，能复算 |
| 🖼️ **自带传播图** | 快照 → PNG，方便分享 |
| ⏱️ **按榜定更新频率** | 小时 / 日 / 周 / 月 / 随源发布 |
| 🔌 **Connector 模型** | 一类数据源一套适配器 |
| 🧾 **留底** | `meta.json` 写清来源与方法 |
| 🌐 **零服务器 API** | raw.githubusercontent / jsDelivr |

## API（不用自建服务）

```bash
curl -sL https://raw.githubusercontent.com/chainepic/EveryLeaderboard/main/catalogs/index.json
curl -sL https://raw.githubusercontent.com/chainepic/EveryLeaderboard/main/boards/crypto-marketcap-top100/latest.json
```

CDN：

```text
https://cdn.jsdelivr.net/gh/chainepic/EveryLeaderboard@main/boards/{slug}/latest.json
```

## 榜单目录

| 榜单 | 标识 (slug) | 更新节奏 | 状态 | 指标 |
| --- | --- | --- | --- | --- |
| [北美周末票房](boards/box-office-weekend-us/meta.json) | `box-office-weekend-us` | 每周 | 试验中 ✅ | 票房 (USD) |
| [Chess.com 闪电棋排位榜](boards/chess-com-blitz/meta.json) | `chess-com-blitz` | 每日 | 试验中 ✅ | 等级分 |
| [Chess.com 快棋排位榜](boards/chess-com-rapid/meta.json) | `chess-com-rapid` | 每日 | 试验中 ✅ | 等级分 |
| [中国新能源车品牌月销量](boards/china-nev-brand-sales/meta.json) | `china-nev-brand-sales` | 每月 | 试验中 ✅ | 销量（辆） |
| [中国乘用车车型月销量](boards/china-passenger-car-sales/meta.json) | `china-passenger-car-sales` | 每月 | 试验中 ✅ | 销量（辆） |
| [全球加密货币市值 Top 100](boards/crypto-marketcap-top100/meta.json) | `crypto-marketcap-top100` | 每 6 小时 | 试验中 ✅ | 流通市值 (USD) |
| [DeFi 协议 TVL 榜](boards/defillama-tvl-top/meta.json) | `defillama-tvl-top` | 每 6 小时 | 试验中 ✅ | 锁仓量 (USD) |
| [GitHub 仓库 Star 榜](boards/github-repos-stars/meta.json) | `github-repos-stars` | 每日 | 试验中 ✅ | 累计 Star |
| [GitHub 日 Star 净增榜](boards/github-star-delta-daily/meta.json) | `github-star-delta-daily` | 每日 | 试验中 ✅ | Star 净增 |
| [GitHub Trending 日榜](boards/github-trending-daily/meta.json) | `github-trending-daily` | 每日 | 试验中 ✅ | 周期 Star 增量 |
| [GitHub Trending 月榜](boards/github-trending-monthly/meta.json) | `github-trending-monthly` | 每周 | 试验中 ✅ | 周期 Star 增量 |
| [GitHub Trending 周榜](boards/github-trending-weekly/meta.json) | `github-trending-weekly` | 每周 | 试验中 ✅ | 周期 Star 增量 |
| [GitHub 用户粉丝榜](boards/github-users-followers/meta.json) | `github-users-followers` | 每日 | 试验中 ✅ | 粉丝数 |
| [Hugging Face 热门模型](boards/hf-models-trending/meta.json) | `hf-models-trending` | 每日 | 规划中 | 下载量 |
| [IMDb Top 250 电影](boards/imdb-top250/meta.json) | `imdb-top250` | 每周 | 规划中 | 评分 |
| [NBA 东西部战绩榜](boards/nba-standings/meta.json) | `nba-standings` | 每日* | 试验中 ✅ | 胜率 |
| [npm React 生态周下载量](boards/npm-react-ecosystem/meta.json) | `npm-react-ecosystem` | 每周 | 规划中 | 近 7 日下载量 |
| [PyPI 追踪包下载量](boards/pypi-top-tracked/meta.json) | `pypi-top-tracked` | 每周 | 规划中 | 近 30 日下载量 |
| [英超积分榜](boards/soccer-pl-table/meta.json) | `soccer-pl-table` | 每日* | 试验中 ✅ | 积分 |
| [欧冠积分榜](boards/soccer-ucl-table/meta.json) | `soccer-ucl-table` | 每日* | 试验中 ✅ | 积分 |
| [Steam 同时在线 Top](boards/steam-top-played/meta.json) | `steam-top-played` | 每日 | 试验中 ✅ | 同时在线人数 |
| [维基百科浏览量 Top](boards/wikipedia-pageviews-top/meta.json) | `wikipedia-pageviews-top` | 每日 | 试验中 ✅ | 浏览量 |

\* 受赛季月份限制（见各榜 `active_months`）。

状态说明：`规划中` = 已登记未接通；`试验中` = 已跑通但可能不稳定；`已上线` = 可放心消费。✅ = 已有 latest 快照。

## 本地跑起来

```bash
git clone https://github.com/chainepic/EveryLeaderboard.git
cd EveryLeaderboard
python3 -m pip install -r requirements.txt

python scripts/validate.py
python scripts/run_due.py --dry-run
python scripts/run_due.py --slug crypto-marketcap-top100 --force
python scripts/render_preview.py
```

## 目录结构

```text
boards/<slug>/latest.json    # 数据
docs/assets/*.png            # 可分享预览图
scripts/render_preview.py    # JSON → PNG
scripts/run_due.py           # 按榜调度
connectors/                  # 数据源适配器
```

```mermaid
flowchart LR
  A[公开数据源] --> B[Connectors]
  B --> C[latest.json]
  C --> D[PNG 预览图]
  C --> E[raw.githubusercontent / jsDelivr]
  F[GitHub Actions] -->|按榜节奏| B
```

## 参与贡献

提 Issue 时请写清：slug、指标与单位、数据源 URL、更新节奏。  
主观榜、无法核对的「人气榜」不会收录。

扩展候选与 GitHub 持续更新源清单见：[扩展规划](docs/EXPANSION.md)。

## 许可证

- **代码**：[MIT](LICENSE)
- **数据**：以各榜 `meta.json` 声明为准，并遵守上游条款

---

<div align="center">
<sub><a href="README.md">English</a> · 简体中文</sub>
</div>

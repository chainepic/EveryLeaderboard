# 扩展规划 · Expansion Roadmap

优先原则：**客观可量化 + 源稳定 + 能自动化**。能复用 GitHub 上已在持续更新的数据集，就先做 **mirror connector**（归一化进我们的 schema），少自己硬爬。

## 已登记、下一批优先接通（P0）

| 中文名 | slug | 建议数据源 | 节奏 | 接入方式 |
| --- | --- | --- | --- | --- |
| GitHub Trending 日/周/月 | `github-trending-*` | [isboyjc/github-trending-api](https://github.com/isboyjc/github-trending-api)、[kingcos/gh-daily](https://github.com/kingcos/gh-daily) | 日/周 | Mirror JSON |
| GitHub 用户粉丝榜 | `github-users-followers` | [jaywcjlove/github-rank](https://github.com/jaywcjlove/github-rank) | 日 | Mirror `users.json` |
| GitHub 仓库 Star 榜 | `github-repos-stars` | 同上 | 日 | Mirror `repos.json` |
| GitHub 日 Star 净增 | `github-star-delta-daily` | [open-source-star-rank](https://github.com/728792899-create/open-source-star-rank) | 日 | Mirror `/data/` |
| DeFi TVL | `defillama-tvl-top` | [DeFiLlama API](https://api.llama.fi/protocols) | 6h | 官方公开 API |
| 加密市值 | `crypto-marketcap-top100` | CoinGecko | 6h | **已接通（experimental）** |

## GitHub 上持续更新、值得跟进的项目

| 项目 | 适合做什么榜 | 备注 |
| --- | --- | --- |
| [isboyjc/github-trending-api](https://github.com/isboyjc/github-trending-api) | Trending 日/周/月 | Actions 写 JSON，raw/CDN 可直接读 |
| [kingcos/gh-daily](https://github.com/kingcos/gh-daily) | Trending 历史存档 | 约 3 小时一刷，带历史目录 |
| [jaywcjlove/github-rank](https://github.com/jaywcjlove/github-rank) | 用户粉丝 / 仓库 Star / Trending | unpkg 可引，社区维护久 |
| [open-source-star-rank](https://github.com/728792899-create/open-source-star-rank) | Star 净增、历史 Top | 强调可复现，有 schema |
| [ChenyuHeee/chinese-car-watch](https://github.com/ChenyuHeee/chinese-car-watch) | 中国车市月销 | 周更 CSV，可参考/协作，勿重复造轮 |

## P1（公开 API，非 GitHub 数据集）

| 方向 | 候选源 | 风险 |
| --- | --- | --- |
| 英超 / 欧冠 | football-data.org | 需免费 API Key |
| NBA 战绩 | ESPN / NBA CDN 包装库 | CI IP 可能被拦，需实测 |
| HF 模型 | Hugging Face Hub API | 限额 |
| npm / PyPI | 官方下载量 API | 做 watchlist，不做「全站 Top」幻觉 |
| 维基浏览 | Wikimedia Pageviews API | 稳 |
| Steam 在线 | Steam Web / Charts | HTML 易碎，优先官方接口 |

## P2 / 暂缓

| 方向 | 原因 |
| --- | --- |
| 全球手机出货（IDC/Counterpoint） | 付费研报，难合法自动化 |
| Amazon BSR 等电商排名 | ToS / 反爬 / 稳定性差 |
| 主观评测、编辑部 S/A/B | 不符合本仓准入规则 |

## 接入策略（建议）

```text
第 1 步  Mirror：GitHub Trending + github-rank + star-delta
第 2 步  官方 API：DeFiLlama、Wikimedia、CoinGecko（已有）
第 3 步  体育 / 车市：football-data、chinese-car-watch 协作或自研 connector
第 4 步  每张 live 榜补 PNG 预览（render_preview.py）
```

新增榜单请同时提供：`title` / `title_zh`、指标中英文、来源 URL、更新节奏。

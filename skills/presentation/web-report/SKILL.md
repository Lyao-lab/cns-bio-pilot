---
name: web-report
description: 生成自包含 HTML 网页报告（分析结果在线分享）。当用户要网页报告、HTML report、在线分享结果、web report、生成报告时触发。嵌入真实分析图 + 关键发现 + 假设台账 + 方法学，单文件可分享，无需服务器/PPT viewer。
license: GPL-3.0
---

# Web Report

## When NOT to use this skill
- 需要演讲幻灯片（PPT）→ 用 `presentation/scientific-slides`
- 需要论文正文（Methods / Results / figure legend）→ 用 `presentation/manuscript-writing`

## Overview

生成**自包含 HTML 网页报告**：`report.json` 驱动，`build_report.py` 渲染单文件 `report.html`——图片 base64 内联、CSS 内联、**无 JS、无外部依赖**，双击打开即看，可直接邮件/微信分享，无需服务器、无需 PPT viewer。

**核心原则**：
- **纯 Python 标准库生成**（json / base64 / pathlib / html），不依赖 jinja2 / bootstrap / plotly
- **图为主，结论为辅**：嵌入真实分析图（UMAP / volcano / 空间切片），不是纯文字堆砌
- **单文件可分享**：所有图片内嵌进 HTML，发给任何人打开即见完整报告
- **学术风样式**：与 PPT preset `cns-bio-light` 同一套色板（Navy #1F3A5F / Green / Red 语义色）

## Workflow: 填 report.json → build_report.py → report.html

### Step 1: Write report.json (the single source)

```json
{
  "title": "Cardiac Fibroblast Atlas",
  "subtitle": "scRNA + Spatial analysis",
  "sections": [
    {"type": "summary", "title": "Overview",
     "content": "32996 cells, 6 FB subtypes, Visium spatial validation"},
    {"type": "findings", "title": "Key Findings",
     "items": ["FB-5 activation (padj<1e-40) [实测]", "CXCL12 axis [文献]"]},
    {"type": "figure", "title": "UMAP", "image": "panels/umap.pdf",
     "caption": "Fig 1. 6 FB subtypes"},
    {"type": "table", "title": "QC Stats",
     "headers": ["Metric","Value"], "rows": [["Cells","32996"],["Genes","30901"]]},
    {"type": "ledger", "title": "Hypothesis Ledger",
     "ledger": [{"hypothesis":"H1: FB activation drives fibrosis","status":"supported","confidence":"high","basis":"pseudobulk DE + spatial validation"}]},
    {"type": "methods", "title": "Methods",
     "content": "OmicVerse 2.3.1, pseudobulk DE (DESeq2), Harmony integration, Visium spatial."}
  ]
}
```

> **report.json 规则**：
> - 6 种 section type 全在语法上支持（见下方 Section types 表），按内容需要选用
> - `image` 字段是**相对 build_report.py 工作目录的路径**（或绝对路径），支持 PDF / PNG / JPG
> - findings 的 `items` 每条**必须带溯源标签** `[实测]` / `[文献]` / `[推断]` 之一（见 Content discipline）

### Step 2: Render

```bash
# 默认输出 report.html
python skills/presentation/web-report/scripts/build_report.py report.json
# 指定输出文件
python skills/presentation/web-report/scripts/build_report.py report.json -o out/report.html
```

> **PDF 图片**：需要 `pip install pymupdf`（与 build_deck.py 一致，自动转 300dpi PNG 内联）；未装时该图渲染为 "pymupdf needed" 占位提示，**不崩**。

### Step 3: Verify

```bash
# 1. 文件生成且非空
python -c "from pathlib import Path; p=Path('report.html'); print(p.exists(), p.stat().st_size/1024, 'KB')"
# 2. 图片真的内联了（应有 data:image base64 串）
grep -c "data:image" report.html
# 3. 双击打开 report.html 目检：图片显示、表格 zebra、status 着色、中文无乱码
```

## Section types（6 种）

| type | 用途 | 必填字段 | 渲染方式 |
|---|---|---|---|
| `summary` | 概述段落 | `content` | `<p>` 段落文本，`\n` 自动分段 |
| `findings` | 关键发现列表 | `items` | 无序列表，每项前加 ▸；`[实测]` 绿 / `[文献]` 蓝 / `[推断]` 灰 |
| `figure` | 分析图 + 图注 | `image`（+ `caption`） | PDF→PNG 后 base64 内联，图注斜体灰 |
| `table` | 统计结果表 | `headers` + `rows` | HTML table，偶数行浅灰 zebra |
| `ledger` | 假设台账 | `ledger` | 四列：Hypothesis \| Status \| Confidence \| Basis；status 着色 |
| `methods` | 方法学 | `content` | 等宽字体灰底框（Consolas monospace） |

**ledger status 着色**：`supported` 绿 / `refuted` 红 / `inconclusive` 黄 / `pending` 灰（未知 status 回退灰）。

## Content discipline

1. **嵌入的图必须是真实分析图**（figure-production 产出的 UMAP / volcano / 空间切片），不是占位符、不是示意图
2. **findings 必须带溯源标签** `[实测]` / `[文献]` / `[推断]`（meta §8c）——读者一眼分清哪些是实测数据、哪些是文献支持、哪些是推断
3. **ledger 从 `hypothesis_ledger.md` 读取真实状态**（status / confidence / basis 逐条照抄，不脑补、不改写）
4. **methods 从 `analysis_log.yml` 读取真实参数**（工具版本 / 统计方法 / 阈值，与实测一致）
5. **数值诚实**：报告里每个数字必须能指到对应 figure / DE 表 / ledger 条目；没有显著差异就写 "No significant effect"，不编故事

## Prerequisites (where inputs come from)

- **真实分析图** → `visualization/figure-production` 产出的 PNG/PDF（UMAP / volcano / heatmap / 空间切片）
- **故事与结论** → `story_builder` 的结论/因果链（组织 findings 和 summary）
- **假设台账** → 项目的 `hypothesis_ledger.md`（ledger section 数据源）
- **方法学** → 项目的 `analysis_log.yml`（methods section 数据源）
- **环境**：Python ≥3.8 标准库即可；仅当用 PDF 图时需要 `pip install pymupdf`

## When to leave this skill (where to go)

- 需要演讲幻灯片 → `presentation/scientific-slides`
- 需要论文正文（Methods / Results / figure legends）→ `presentation/manuscript-writing`
- 需要发表级单图（非报告）→ `visualization/figure-production`
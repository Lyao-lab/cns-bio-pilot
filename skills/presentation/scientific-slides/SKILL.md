---
name: scientific-slides
description: 用 python-pptx 或 LaTeX Beamer 生成科研演讲幻灯片，覆盖正式会议 talk 与内部组会/lab meeting/进度汇报两类场景。当用户要做 PPT、幻灯片、slides、汇报、beamer、presentation、组会、lab meeting、project review、周报月报时触发。纯代码生成，不依赖 AI 生图 API——嵌入真实分析图（UMAP/火山图/空间切片等），outline.json 驱动，含 readability 契约与几何 QA。
allowed-tools: Read Write Edit Bash
license: MIT
---

# Scientific Slides

## When NOT to use this skill
- Writing paper Methods / Results / figure legend text → use `presentation/manuscript-writing`
- Standalone publication-grade figure (not a slide) → use `visualization/figure-production`
- Drawing mechanism / flow / architecture diagrams (not slides) → use `visualization/scientific-schematics`

## Overview

This skill generates research presentation slides with **python-pptx** (default) or **LaTeX Beamer**. **Core principle: source-first, pure code, no dependency on AI image-generation APIs**. It covers two modes: **formal talk** (default — conference / defense / grand round) and **Lab meeting** (group meeting / progress report / PI update — discussion-driven + data-honesty boundary).

**Design philosophy** (drawn from siril9/presentation-skill + anthropics/pptx patterns):
- **Deck as Code**: `outline.json` is the single source; a script renders `.pptx`; a QA loop verifies layout — no one-off inline python-pptx; edit the source, not the artifact
- **图为主，文字在备注**：每张幻灯片以**真实分析图为主体**（占内容区 ≥70%）。图的解读（fig legend / take-home / 数据出处 / 统计信息）写在** PowerPoint 备注栏**（speaker notes），不堆在幻灯片页面上。讲解时看备注，观众看图。
- **图用英文，备注用中文**：幻灯片页面上的标题、图注、坐标轴标签等保持**英文**（与发表级 figure 一致）；备注栏（speaker notes）用**中文**写解读和讲解提示。
- **图形式多样化**：禁止连续 3+ 张相同图型。一张 PPT 里应该有 UMAP / volcano / heatmap / violin / spatial section / CCC / trajectory 等多种形式。**不要大量使用 bar chart**——比例变化用堆叠柱可以，但连续 3+ 张 bar = 视觉疲劳。
- **Visual-First**: every slide embeds a real analysis figure (UMAP / volcano / spatial section), not a bullet-list pileup
- **Research-Backed**: every data figure annotates N / statistical test / threshold (Wilcoxon+FDR / Moran's I) — 写在备注里
- **Readability Contract**: title ≥24pt / body ≥12pt / caption ≥7.5pt / chart labels ≥7pt (preflight-enforced)
- **Anti-AI-taste iron rule** (from anthropics/pptx): **never add a decorative line under a title** — that is the hallmark of AI-generated slides

## When to Use This Skill

- Conference talk (5-20 min) / seminar (45-60 min) / defense / grant pitch / journal club
- Need to embed real analysis figures (PNGs from `visualization/figure-production`)
- Need an editable .pptx (peers/advisor will edit text) or a compiled PDF (Beamer)

## Workflow: outline.json source-first (python-pptx)

### Step 1: Write outline.json (the single source)

```json
{
  "title": "Single-cell + Spatial Transcriptomics Analysis",
  "subtitle": "OmicVerse + squidpy pipeline",
  "preset": "cns-bio-light",
  "slides": [
    {"variant": "title", "title": "Single-cell + Spatial Transcriptomics Analysis", "subtitle": "OmicVerse + squidpy"},
    {"variant": "figure-hero", "title": "Cell type atlas",
     "image": "figures/umap_celltype.png",
     "caption": "Fig 1. UMAP by cell type (N=2700, leiden res=0.6)",
     "notes": "10 个细胞类型，Fibro 占比最高（44%）。UMAP 分群清晰，无明显批次效应。每个 cluster 的 marker 基因见附表。"},
    {"variant": "figure-dual", "title": "Normal vs POP composition",
     "image": "figures/prop_normal.png", "caption_left": "Normal",
     "image2": "figures/prop_pop.png", "caption_right": "POP",
     "notes": "Fibro 比例 44%→57%（+13pp, padj<1e-40），M2 巨噬 +16.7%。其余细胞类型无显著变化。"},
    {"variant": "figure-hero", "title": "Differential expression",
     "image": "figures/volcano.png",
     "caption": "Fig 3. Volcano (Padj<0.05 & |log2FC|>1, BH-FDR)",
     "notes": "602 个显著差异基因。上调 top: CXCL12, COL1A1, PDGFRB（纤维化通路）。下调 top: LDHB, RPS12（代谢转换）。"},
    {"variant": "figure-grid", "title": "Fibroblast subtype analysis",
     "images": ["figures/fibro_umap.png","figures/fibro_dotplot.png","figures/fibro_violin.png","figures/fibro_heatmap.png"],
     "caption": "Fig 4. Fibro subtypes: UMAP / dotplot / violin / heatmap",
     "notes": "Quiescent_1→2/3 内部重塑。CXCL12 在 Quiescent_2/3 特异高表达。轨迹分析显示静息态向活化态转换。"},
    {"variant": "figure-hero", "title": "Spatial validation: CXCL12 + M2",
     "image": "figures/spatial_cxcl12.png",
     "caption": "Fig 5. CXCL12 spatial expression + M2 macrophage co-localization",
     "notes": "CXCL12+ Fibro 与 M2 巨噬在纤维化区域空间共定位（距离 <50μm）。支持 CXCL12-CXCR4 轴驱动纤维化-免疫正反馈的假说。"},
    {"variant": "methods-flow", "title": "Pipeline", "steps": ["QC","Cluster","Annotate","DE","CCC","Spatial"]}
  ]
}
```

> **outline.json 规则**：
> - 页面内容（title / caption / 轴标签）用**英文**（与发表级 figure 一致）
> - `notes` 字段用**中文**写解读（take-home + 关键数字 + 讲解提示）
> - 图形式**多样化**：不要连续 3+ 张相同类型；不要大量用 bar chart

### Step 2: Render (python-pptx)

```bash
# Default python-pptx render (no Node / AI API needed)
python scripts/build_deck.py outline.json -o presentation.pptx
# Optional: LibreOffice PDF export (skip if LibreOffice unavailable)
soffice --headless --convert-to pdf presentation.pptx
```

> **Chinese in PPT/PDF**: `build_deck.py` sets `font.name = 'Microsoft YaHei'` on every text element (verified) — PowerPoint renders Chinese correctly. For **PDF export via LibreOffice**, the system needs the font installed (`YaHei` is standard on Windows); on Linux servers install `fonts-noto-cjk` first. For **Beamer** (LaTeX PDF), use **XeLaTeX** (not pdflatex) + `\usepackage{ctex}` or `\setCJKmainfont{SimHei}` — pdflatex cannot handle CJK.

### Step 3: QA Gate (mandatory, three checks)

```bash
# 1. Geometric QA: overflow / overlap / undersized fonts (readability contract)
python scripts/qa_deck.py presentation.pptx
# 2. Content/semantic validation: readability contract + placeholder leakage + structural integrity
python scripts/validate_presentation.py presentation.pptx
# 3. Visual review (optional, via subagent): open the .pptx manually, or render PDF thumbnails
```

> **USE SUBAGENTS for visual QA** (from anthropics/pptx): reviewing your own code invites confirmation bias — let a subagent check overlap / overflow / contrast with fresh eyes. "If you don't spot any problem at first glance, you aren't looking closely enough."

## Slide Variants (12 种布局，多样化 + 防重叠)

> **布局安全间距铁律**：图片和文字之间必须留 ≥0.3inch (≈8mm) 安全间距。图片区域和文字区域**不重叠**——每个元素有明确的 bounding box，代码中用 `_safe_zone()` 函数强制检查。

| variant | 用途 | 布局规则 | 适用场景 |
|---|---|---|---|
| `title` | 标题页 | 标题居中 40pt + 副标题 20pt，无装饰线 | 开场 |
| `section` | 章节分隔 | 单行居中 36pt，留白 >60% | 转场 |
| **`figure-hero`** | 全宽大图 | 图片占满可用区域（左 0.5→右 12.8inch），图注在图片下方独立行，**无文字侧栏** | 最有冲击力的单张图（UMAP 全景 / 空间切片） |
| `figure-sidebar` | 图+文分屏 | 图片左 55%（0.5→7.3inch），文字右 40%（7.8→12.8inch），**间距 0.5inch** | 图+解读（DE 火山图 + top genes 列表） |
| **`figure-dual`** | 左右双图对比 | 图1左 40%（0.5→5.8inch）+ 图2右 40%（6.5→11.8inch），共用标题，各自图注；**可加中间 1 行文字注释** | Normal vs Disease / Pre vs Post / 两个条件对比 |
| **`figure-top-text`** | 图上文下 | 文字在上（0.8→3.5inch），图在下（3.8→7.0inch），**间距 0.3inch** | 先给 take-home 再展示证据 |
| **`figure-grid`** | 2×2 四宫格 | 四张小图 + 统一标题 + 统一图注；每张 ≤3.5×2.8inch；间距 0.3inch | marker dotplot + heatmap + proportion + violin 概览 |
| `scientific-figure` | 2-4 panel（兼容旧版） | 同 figure-sidebar，但允许 2-4 张子图拼成一张 PNG 嵌入 | 复合图 |
| `results-table` | 结果表格 | 表头 12pt bold，数据 11pt，pass 绿/fail 红，数字右对齐 | QC 统计 / SVG 排名 |
| `methods-flow` | 流程图 | 水平箭头流，每步一个词 18pt，≤8 步 | pipeline 概览 |
| `bullets` | 纯文字 | ≤4 行，每行 ≤6 词，18pt | 总结 / 过渡 |
| **`split-compare`** | 左右分屏对比 | 左半 50%（含标题+图+文）vs 右半 50%（标题+图+文）；中间分隔线 0.5pt | 两种方法对比 / 两个数据集对比 |

### 防重叠规则（代码强制，不是建议）

```python
# build_deck.py 中每个布局函数都调用的安全检查：
SAFE_GAP = Inches(0.3)  # 图片与文字之间的最小安全间距

def _safe_zones(width_in=13.333, height_in=7.5):
    """返回安全区域字典——每个元素只能在自己的区域内"""
    title_zone = (0.5, 0.3, 12.3, 1.0)      # 标题区: top 0.3-1.0
    content_zone = (0.5, 1.2, 12.3, 5.3)     # 内容区: top 1.2-6.5
    caption_zone = (0.5, 6.7, 12.3, 0.6)     # 图注区: top 6.7-7.2
    # 图片放 content_zone 内，文字也放 content_zone 内，但两者在水平/垂直方向上不重叠
    return {"title": title_zone, "content": content_zone, "caption": caption_zone}
```

**规则**：
1. **标题区（0.3-1.0inch）**不放图、不放正文——只放标题
2. **图注区（6.7-7.2inch）**不放图、不放正文——只放 caption
3. **内容区（1.2-6.5inch）**内图片和文字**水平分离**：图片在左半区，文字在右半区，中间 ≥0.3inch 空白
4. **全宽图片**（figure-hero）：图片占满内容区宽度，文字移到图注区或下一张幻灯片
5. **上下布局**（figure-top-text）：文字在上 1/3，图在下 2/3，中间 0.3inch

### 图形式多样化原则

不要每张都用"图左+文右"（image-sidebar）。根据内容选布局：

| 内容类型 | 推荐布局 | 理由 |
|---|---|---|
| UMAP / 空间切片全景 | `figure-hero` | 全宽冲击力 |
| 火山图 + top genes 列表 | `figure-sidebar` | 图+文互补 |
| Normal vs Disease 对比 | `figure-dual` | 直接对比 |
| "先说结论再给证据" | `figure-top-text` | 叙事驱动 |
| 4 种分析结果概览 | `figure-grid` | 信息密度 |
| 两种方法/数据集对比 | `split-compare` | 方法学对比 |

**同一套 PPT 里至少用 3 种不同布局**——全是 figure-sidebar = 视觉单调。

> **scientific-figure key** (核心生信场景)：在 Python 里 `bbox_inches='tight'` 导出后，用 PIL `ImageOps.crop` 去白边再嵌入，否则幻灯片会有丑陋的白色边框。

## Preset: cns-bio-light (bioinformatics-specific)

```
Background: white (#FFFFFF)
Primary:   Navy (#1F3A5F)      — title / emphasis
Secondary: Blue (#3D7AAB)      — subheadings
Semantic:  Green (#2E8B57) pass / Red (#E25D5D) fail / Orange (#E8A838) warning
Body:      Dark gray (#333333)
Caption:   Light gray (#666666), italic
Font:      Title Calibri/Arial Bold; body Calibri/Arial
```

## Readability Contract (preflight-enforced)

| element | min font size | rationale |
|---|---|---|
| Title | 24pt | readable from a distance |
| Body bullet | 12pt (ideal 14-18pt) | readable when projected |
| Caption / axis | 7.5pt | reference only |
| In-chart label | 7pt | reference only |
| Footer | 7pt, reserve ≥0.25in | does not squeeze content |

> `qa_deck.py` scans every text box and errors on any font size below threshold (caught before render, not by eye).

## LaTeX Beamer alternative (academic / formal)

Use Beamer when you need a compiled PDF and prefer LaTeX. Templates live in `assets/beamer_template_{conference,seminar,defense}.tex`; the full guide is `references/beamer_guide.md`.

```bash
pdflatex beamer_template_conference.tex  # compile (English-only)
# For Chinese content: use xelatex + \usepackage{ctex} (pdflatex cannot handle CJK)
xelatex beamer_template_conference.tex   # Chinese-safe compile
# Prefer Beamer for many flow diagrams/equations; python-pptx for many figures
```

## References index (load on demand)

| what you need | which file |
|---|---|
| Content/Design/Timing pitfalls + 10 principles | `references/pitfalls.md` |
| Full LaTeX Beamer document | `references/beamer_guide.md` |
| **Lab meeting mode** (group meeting / progress / PI update — 9 steps + A-I output + Hard Rules + 7 rule modules) | `references/lab_meeting/lab_meeting_workflow.md` + `references/lab_meeting/rules/*.md` |
| Figure aesthetics (color / font / non-overlap) | top-level `references/figure_guide.md` |
| Multi-panel composition (layout / shared legend / panel labels) | top-level `references/figure_guide.md` |

> Removed in v12.1 (redundant with top-level figure refs): talk_types_guide, presentation_structure, slide_design_principles, data_visualization_slides, visual_review_workflow, core_capabilities, development_workflow. The 7-step Quick Route + Pre-Output Checklist + Key pitfalls in this SKILL.md already cover slide structure/design/review essentials.

## Assets (templates)
- `assets/beamer_template_conference.tex` / `_seminar.tex` / `_defense.tex`
- `assets/powerpoint_design_guide.md` / `assets/timing_guidelines.md`

## Prerequisites (where inputs come from)
- **Real analysis figures** → PNGs from `visualization/figure-production` (ov.pl.embedding/volcano) or `visualization/figure-production` (6-panel composites)
- **Spatial section images** → `sq.pl.spatial_scatter` output from `spatial/omicverse-spatial`
- **Result data** → analyzed h5ad / DE tables / SVG tables (feed into the results-table variant)
- **Citations** → 3-5 references in intro, 3-5 in discussion (research-lookup)
- **Environment**: `pip install python-pptx Pillow` (no Node / AI API dependency)

## Pre-Output Checklist (must pass before delivery)
- [ ] Numeric integrity: every quantitative figure keeps N / statistical test / error bars
- [ ] Cross-condition consistency: is the effect universal or cell-type-specific?
- [ ] Citation support: state exactly which figure / statistic backs the main conclusion
- [ ] No speculation: when there is no significant difference, write "No significant effect" — do not fabricate a story
- [ ] Association ≠ causation: use "associated with"; regulates/causes requires experimental evidence
- [ ] Readability contract: title ≥24pt / body ≥12pt / caption ≥7.5pt
- [ ] Anti-AI-taste: no decorative line under titles, no placeholder leakage
- [ ] Run qa_deck.py (geometry) + validate_presentation.py (content/placeholders) ✅

## When to leave this skill (where to go)
- Writing paper Methods / Results / figure legends → the corresponding writer skill
- Standalone publication-grade figure → `visualization/figure-production`
- Mechanism / flow diagrams → `visualization/scientific-schematics`
- After completion, run `python scripts/qa_deck.py presentation.pptx` to verify

---

## Mode: Lab Meeting (group meeting / progress report / PI update)

> Merged from the original `presentation/lab-meeting-slides` skill (merged 2026-07).
> Use this mode when the task is an **internal group meeting / lab meeting / project review / weekly-monthly report / PI update**. It differs from the default formal-talk mode in: **discussion-driven + data-honesty boundary + no inflating progress**.

### When to enter lab-meeting mode

The user says "make a group-meeting PPT", "organize a lab meeting", "weekly/monthly deck", "project review", "give the PI a progress update", etc.

### Workflow

The full 9-step workflow + mandatory output structure (A-I) + Hard Rules live in **`references/lab_meeting/lab_meeting_workflow.md`**. Rule modules load on demand from `references/lab_meeting/rules/*.md` (clarification-first / meeting-goal-selection / slide-priority / data-honesty-boundary / next-step-structuring / logic-reporting / hard-rules).

### outline.json differences vs the formal-talk mode

| dimension | formal talk | Lab meeting |
|---|---|---|
| Background slides | moderate | **minimal** (the team knows the background) |
| Data slides | curated polished figure | **raw/intermediate results OK, seeking feedback** |
| Incomplete results | packaged as conclusions | **honestly marked "exploratory/unresolved"** |
| Next steps | outlook | **explicit proposals, open for discussion** |

### Key discipline (do not violate)

1. **Never fabricate** progress / figures / results — only organize what the user has supplied
2. When the meeting goal + project status are unclear, **ask first**; do not emit a full structure
3. **Do not mask** blocked progress with decorative background slides
4. **Do not present** open next-step ideas as finalized commitments

> Once you have the lab-meeting structure, still render the .pptx via the main `build_deck.py` — only the outline.json content follows the lab-meeting proportions (less background, more open-problem, more next-step).

## Key pitfalls (common LLM slide mistakes)

- **No decorative line under titles** — the "AI taste" hallmark of AI-generated slides (anthropics/pptx iron rule)
- **Every data figure must annotate N / statistical test** — LLMs tend to produce "pretty but N-less" figures
- **Placeholder leakage**: TODO/lorem/xxx/placeholder must be caught by `validate_presentation.py`
- **Image overflow**: `build_deck.py` already enforces height constraints, but very small images blur when enlarged — preflight-check DPI
- **scientific-figure ≤4 panels**: more than 4 is visual overload; LLMs tend to stack 6+ panels
- **≤4 bullets / ≤6 words each**: LLMs tend to write long bullets, turning slides into documents
- **Figures must be real analysis plots** (UMAP / volcano / spatial section), not bullet-list pileups — the core anti-AI-taste rule
- **Run both qa_deck.py + validate_presentation.py** — triple check (geometry / font size / placeholders); LLMs must never ship a deck unverified

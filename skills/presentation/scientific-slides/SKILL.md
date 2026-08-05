---
name: scientific-slides
description: 用 python-pptx 或 LaTeX Beamer 生成科研演讲幻灯片，覆盖正式会议 talk 与内部组会/lab meeting/进度汇报两类场景。当用户要做 PPT、幻灯片、slides、汇报、beamer、presentation、组会、lab meeting、project review、周报月报时触发。纯代码生成，不依赖 AI 生图 API——嵌入真实分析图（UMAP/火山图/空间切片等），outline.json 驱动，含 readability 契约与几何 QA。
license: MIT
allowed-tools: Read Write Edit Bash
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

## Talk Arc（汇报叙事弧模板）

> **先读 `references/discovery_miner.md` + `references/story_builder.md`** —— 发现挖掘 + 故事构建（含逻辑漏洞扫描 + 补缺分析）。
> 构建汇报前必须先完成 story_builder Step 2b（逻辑漏洞扫描）：**因果链里有跳步或缺证据的地方，先补分析再组织汇报**——不要带着漏洞做 PPT。
> 然后按以下弧组织幻灯片。**标题必须是结论句**（assertion-evidence 模型，Naegle 2021 Rule 3），禁止 "Results"/"Analysis" 式标签标题。

### 标准 10 页叙事弧

| 页 | arc_role | 内容 | 标题示例（结论式） |
|---|---|---|---|
| 1 | hook | 临床/生物学问题 + 现有认知的不足 | "POP 的纤维化机制不明：谁是驱动者？" |
| 2 | design | 队列 + 技术组合 + 分析流程 | "10 例配对 scRNA + Visium 多模态设计" |
| 3 | atlas | UMAP 全景 + 组成（**UMAP 全场只用一次**） | "10 cell types identified; Fibro dominant (44%)" |
| 4 | finding-1 | 组成变化定量（推进因果链第一环） | "Fibroblast expand 13pp in POP (padj<1e-40)" |
| 5 | finding-2 | 亚群细分/分子变化（第二环） | "Quiescent_1→2/3 rewiring, CXCL12↑" |
| 6 | mechanism | 通讯/轨迹/GRN 证据（第三环） | "CXCL12-CXCR4 is the top Fibro→Mac axis" |
| 7 | spatial | 空间验证（正交证据） | "CXCL12+ Fibro and M2 co-localize in fibrotic zones" |
| 8 | sowhat | 功能/临床意义 | "CXCL12-CXCR4 axis: potential anti-fibrotic target" |
| 9 | model | 模型图/总结图 | "Proposed model: Fibro-Mac positive feedback loop" |
| 10 | takehome | ≤3 条 take-home | "3 key findings: rewiring / CXCL12 / spatial niche" |

> **规则**：每页标题 = 该页结论（从 story_builder Step 3 主结论/因果链取词）。
> **UMAP 全场只用一次**（展示结构，不做定量论证）。
> 空间图必须配定量 panel（箱线/距离曲线），单独的"好看切片图"不构成证据。

### 场景预设

| 场景 | 时长 | 页数 | 背景:方法:发现:讨论 | 诚实边界 |
|---|---|---|---|---|
| 会议 talk | 10-20min | 10-15 | 1:1:6:2 | 结论措辞保守 |
| 答辩 | 30-45min | 20-30 | 2:2:5:1 | 可行性+前期基础重 |
| 基金 pitch | 10min | 8-10 | 1:1:6:2 | 创新性+前期数据重 |
| 周报/月报 | 5-10min | 5-8 | 0:0:7:3 | 诚实标"exploratory"（走 lab-meeting 模式） |
| 年会 seminar | 45-60min | 25-40 | 2:2:4:2 | mechanism+validation 加深 |
| Journal club | 20-30min | 15-20 | 复现原论文弧 | 解构他人论文叙事 |

### 图表选择决策表（你想论证什么 → 该画什么图）

| 你要论证 | 首选图型 | variant | 备注必写项 |
|---|---|---|---|
| 有哪些细胞 | UMAP（全场仅此一次） | figure-hero | N + resolution + batch check |
| 谁的比例变了 | 堆叠柱 + 患者级箱线 | figure-dual | n=patients + 检验方法 + padj |
| 哪些基因变了 | volcano + top genes | figure-sidebar | threshold + 校正方法 |
| 什么通路激活 | 富集条形图（GO/KEGG） | figure-sidebar | gene set 来源 + FDR |
| 谁跟谁通讯 | L-R bubble / heatmap | figure-sidebar | 方法（CellChat/LIANA）+ scope |
| 细胞怎么转换 | PAGA + pseudotime UMAP | figure-grid | kernel 类型 + 方向性证据 |
| 在组织中真的发生 | 空间 overlay + 定量曲线 | figure-dual | 距离统计 + 置换检验 p |
| 两种条件对比 | 左右分屏 | figure-dual / split-compare | 对比维度 + N |

> **图型纪律**：禁止连续 3+ 张相同图型；不要大量用 bar chart；circle plot 信息密度低不推荐。

### 实战教训：PPT 组织的 8 个高频坑（从真实迭代提炼）

> 以下教训来自一次 16-slide 瓣膜发育 PPT 的完整迭代（11 脚本、15 图、多轮返工）。

| # | 坑 | 表现 | 解决 |
|---|---|---|---|
| 1 | **背景信息放太后** | "心脏组成动态"放在 S11，读者已忘 atlas 背景 | 背景（组成/QC）紧跟 atlas（S2→S3），不拖到最后 |
| 2 | **两页讲同一件事** | S4 空间架构 + S5 基因梯度 = 重复空间差异 | 合并成一页；或一页定量一页定性（不重叠） |
| 3 | **机制页与架构页脱节** | ECM 来源（S6）与空间架构（S5）隔了几页 | 机制紧跟发现（架构→来源解释→通讯） |
| 4 | **缺 model 页** | 从发现直接跳结论，无整合模型 | Talk Arc 必须有 model 页（三轴整合图/总结） |
| 5 | **标题字号太大换行** | 28pt 标题在 13.3" 宽 slide 上换两行 | 标题 20pt + 全宽 12.7" + 确保一行 |
| 6 | **figure-hero 覆盖率低** | 图只占 slide 40%（大量留白） | 图宽高比匹配 slide（2:1）；非宽图用 `max_h` 突破 |
| 7 | **硬编码 spec 值** | 图上标 ρ=-0.877（旧值），实际算出 -0.80 | 永远用 computed 值，print 对照 |
| 8 | **Panel B 空/被挤压** | Panel A legend 移位 → Panel B 变空 | 去掉冗余 Panel B（如果 Panel A 已含信息） |

### 空间转录组 PPT 的特殊纪律

空间转录组论文的 PPT 比纯 scRNA 更容易出问题，额外纪律：

1. **必须有标准反卷积空间图**：全切片 × 多细胞类型 × 三时点（cell2location proportion），不只是 niche bbox
2. **必须有无监督域图**：BANKSY/BayesSpace domain（不依赖注释），与反卷积互验证
3. **niche bbox 放大 + 全切片对比**：两张都要——bbox 看细节，全切片看 context
4. **梯度必须连续曲线 + 离散热图**：core/ring 热图（离散）+ 距离-表达曲线（连续）互验证
5. **COMMOT/通讯图必须三时点**：方向变化是跨时点的核心发现，单时点看不到
6. **不要在散点上画圈**（convex hull/轮廓）——用户反感；用文字注释或 inset 代替

## Workflow: outline.json source-first (python-pptx)

### Step 1: Write outline.json (the single source)

```json
{
  "title": "Single-cell + Spatial Transcriptomics Analysis",
  "subtitle": "OmicVerse + squidpy pipeline",
  "preset": "cns-bio-light",
  "slides": [
    {"variant": "title", "title": "POP 的纤维化机制不明：谁是驱动者？", "subtitle": "Single-cell + Spatial Transcriptomics", "arc_role": "hook"},
    {"variant": "methods-flow", "title": "10 例配对 scRNA + Visium 多模态设计", "arc_role": "design", "steps": ["QC","Cluster","Annotate","DE","CCC","Spatial"]},
    {"variant": "figure-hero", "title": "10 cell types; Fibroblast dominant (44%)",
     "image": "figures/umap_celltype.png",
     "caption": "Fig 1. UMAP by cell type (N=2700)",
     "arc_role": "atlas",
     "notes": "10 个细胞类型，Fibro 占比最高（44%）。UMAP 分群清晰，无明显批次效应。"},
    {"variant": "figure-dual", "title": "Fibroblast expand 13pp in POP (padj<1e-40)",
     "image": "figures/prop_normal.png", "caption_left": "Normal",
     "image2": "figures/prop_pop.png", "caption_right": "POP",
     "arc_role": "finding",
     "notes": "Fibro 比例 44%→57%（+13pp），M2 巨噬 +16.7%。"},
    {"variant": "figure-hero", "title": "Quiescent_1→2/3 rewiring; CXCL12↑",
     "image": "figures/volcano.png",
     "caption": "Fig 3. Volcano (Padj<0.05 & |log2FC|>1)",
     "arc_role": "finding",
     "notes": "602 个显著差异基因。上调 top: CXCL12, COL1A1, PDGFRB。"},
    {"variant": "figure-hero", "title": "CXCL12-CXCR4 is the top Fibro→Mac axis",
     "image": "figures/ccc_heatmap.png",
     "caption": "Fig 4. CellChat L-R heatmap",
     "arc_role": "mechanism",
     "notes": "CXCL12-CXCR4 通讯 score 在 Fibro-Mac 对中最高（0.85），disease 组显著增强。"},
    {"variant": "figure-dual", "title": "CXCL12+ Fibro and M2 co-localize in fibrotic zones",
     "image": "figures/spatial_cxcl12.png", "caption_left": "CXCL12",
     "image2": "figures/spatial_m2.png", "caption_right": "M2 macrophage",
     "arc_role": "spatial",
     "notes": "CXCL12+ Fibro 与 M2 巨噬在纤维化区域空间共定位（距离 <50μm，置换检验 p<0.01）。"},
    {"variant": "bullets", "title": "CXCL12-CXCR4 axis: potential anti-fibrotic target",
     "arc_role": "sowhat",
     "bullets": ["Fibro-Mac positive feedback loop", "CXCL12 blockade: testable hypothesis", "Niche-level targeting vs cell-type targeting"]},
    {"variant": "bullets", "title": "3 key findings",
     "arc_role": "takehome",
     "bullets": ["Fibro quiescent rewiring (not myofibroblast)", "CXCL12-CXCR4 connects fibrosis-inflammation", "Spatial niche validates the loop"]}
  ]
}
```
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
| **Lab meeting mode** (group meeting / progress / PI update — 9 steps + A-I output + Hard Rules + 7 rule modules) | `references/lab_meeting/lab_meeting_workflow.md` + `references/lab_meeting/lab_meeting_rules.md` |
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

> Merged from the original `presentation/lab-meeting-slides` skill (merged 2026-07 (historical)).
> Use this mode when the task is an **internal group meeting / lab meeting / project review / weekly-monthly report / PI update**. It differs from the default formal-talk mode in: **discussion-driven + data-honesty boundary + no inflating progress**.

### When to enter lab-meeting mode

The user says "make a group-meeting PPT", "organize a lab meeting", "weekly/monthly deck", "project review", "give the PI a progress update", etc.

### Workflow

The full 9-step workflow + mandatory output structure (A-I) + Hard Rules live in **`references/lab_meeting/lab_meeting_workflow.md`**. Rule modules load on demand from `references/lab_meeting/lab_meeting_rules.md` (sections: Clarification First / Meeting Goal Selection / Slide Priority / Data Honesty Boundary / Next Step Structuring / Logic Reporting / Hard Rules).

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

---

## Worked Example：完整 PPT outline.json（从 hook 到 takehome）

> 以下是真实心脏瓣膜项目的 10-slide PPT，标题全部为**断言式**（结论句），arc_role 完整覆盖 hook→takehome。

```json
{
  "title": "Valve Interstitial Cell Activation Drives Fibrotic Niche Formation",
  "subtitle": "Single-cell + spatial transcriptomics of cardiac valve development",
  "preset": "cns-bio-light",
  "slides": [
    {"variant": "title", "arc_role": "hook",
     "title": "What drives valve fibrosis? The spatial architecture is unknown"},
    {"variant": "methods-flow", "arc_role": "design",
     "title": "Multi-modal: scRNA (3 timepoints) + Visium (10 sections)",
     "steps": ["QC","Cluster","Annotate","DE","Niche","CCC"]},
    {"variant": "figure-hero", "arc_role": "atlas",
     "title": "8 cell types; VIC dominant (35-52%)",
     "image": "panels/umap_atlas.png",
     "caption": "Fig 1. UMAP across 13w/24w/36w (N=15,000)",
     "notes": "VIC 是最大群，三时点组成变化显著。UMAP 分群清晰，无明显批次。"},
    {"variant": "figure-dual", "arc_role": "finding",
     "title": "VIC expand 17pp and shift Quiescent→Activated",
     "image": "panels/vic_13w.png", "caption_left": "13w",
     "image2": "panels/vic_36w.png", "caption_right": "36w",
     "notes": "VIC 从 35%→52%。Quiescent 亚群减少，Activated 增多。轨迹分析确认方向。"},
    {"variant": "figure-hero", "arc_role": "finding",
     "title": "Activated VIC upregulate COL1A1/COL3A1/POSTN (ECM remodeling)",
     "image": "panels/de_scatter.png",
     "caption": "Fig 3. Grouped scatter: log2FC per timepoint",
     "notes": "三时点 DE 分组散点图。ECM 基因在 36w 显著上调。GSEA 确认 ECM 通路 NES=2.1。"},
    {"variant": "figure-hero", "arc_role": "mechanism",
     "title": "BANKSY identifies 'fibrotic front' niche (8/10 sections)",
     "image": "panels/spatial_domains.png",
     "caption": "Fig 4. Spatial domain map + H&E",
     "notes": "纤维化前沿在 8/10 个样本中出现（>20% 阈值）。Domain marker 富集 ECM 基因。"},
    {"variant": "figure-dual", "arc_role": "spatial",
     "title": "CXCL12+VIC co-localize with CD68+Macrophage (<50μm)",
     "image": "panels/spatial_cxcl12.png", "caption_left": "CXCL12",
     "image2": "panels/spatial_cd68.png", "caption_right": "CD68 Macrophage",
     "notes": "空间共定位确认。距离定量曲线显示 <50μm 的富集（p<0.01）。"},
    {"variant": "figure-hero", "arc_role": "sowhat",
     "title": "CXCL12 axis: druggable target (validated in heart failure, PMID:39443792)",
     "image": "panels/model.png",
     "caption": "Proposed model: VIC-Mac positive feedback loop",
     "notes": "CXCL12 阻断在心衰模型中已有验证。瓣膜纤维化的潜在干预靶点。"},
    {"variant": "bullets", "arc_role": "takehome",
     "title": "3 key findings",
     "bullets": ["VIC activation forms spatial niche", "CXCL12 connects fibrosis-immunity", "Niche is druggable target"]}
  ]
}
```

**这个示例示范了**：
1. 每页标题是**结论句**（不是 "Results" / "Analysis"）
2. arc_role 完整覆盖 hook→design→atlas→finding×2→mechanism→spatial→sowhat→takehome
3. 图型多样化：UMAP / dual-compare / grouped scatter / spatial overlay / model diagram / bullets
4. notes 全中文写解读（take-home + 关键数字 + 讲解提示）
5. 页面文字全英文（图用英文），备注全中文

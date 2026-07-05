---
name: scientific-slides
description: 用 python-pptx 或 LaTeX Beamer 生成发表级科研演讲幻灯片（会议/研讨会/答辩/grant pitch/journal club）。当用户要做 PPT、幻灯片、slides、汇报、beamer、presentation 时触发。纯代码生成，不依赖 AI 生图 API——嵌入真实分析图（UMAP/火山图/空间切片等），outline.json 驱动，含 readability 契约与几何 QA。
allowed-tools: Read Write Edit Bash
license: MIT
---

# Scientific Slides

## When NOT to use this skill
- 内部组会 / 进度汇报（非正式，需讨论导向结构）→ 改用 `presentation/lab-meeting-slides`
- 写论文 Methods / Results / 图注文字 → 改用 `presentation/methods-writer` / `presentation/results-writer` / `presentation/figure-legend-writer`
- 单独制作发表级 figure（不是 slide）→ 改用 `visualization/multi-panel-figures`
- 画机制图/流程图/架构图（非 slide）→ 改用 `visualization/scientific-schematics`
- 论文图形摘要 → 改用 `visualization/graphical-abstract`

## Overview

本 skill 用 **python-pptx**（默认）或 **LaTeX Beamer** 生成科研演讲幻灯片。**核心原则：source-first，纯代码，不依赖 AI 生图 API**。

**设计哲学**（吸收 siril9/presentation-skill + anthropics/pptx 范式）：
- **Deck as Code**：`outline.json` 是唯一源，脚本渲染 `.pptx`，QA 循环校验排版——禁止写一次性 inline python-pptx，改 source 不改 artifact
- **Visual-First**：每张 slide 嵌真实分析图（UMAP/火山/空间切片），不是 bullet list 堆砌
- **Research-Backed**：每张数据图标注 N / 统计检验 / 阈值（Wilcoxon+FDR / Moran's I）
- **Minimal Text**：bullet 是提示词，你口头讲解；3-4 条，每条 ≤6 词，24-28pt
- **Readability Contract**：标题≥24pt / 正文≥12pt / 图注≥7.5pt / 图表标签≥7pt（preflight 强制）
- **反 AI 味铁律**（抄 anthropics/pptx）：**永远不在标题下加装饰线**——这是 AI 生成 slide 的标志

## When to Use This Skill

- 会议报告（5-20 分钟）/ 学术研讨会（45-60 分钟）/ 答辩 / grant pitch / journal club
- 需要嵌入真实分析图（来自 `visualization/omicverse-plotting` 或 `multi-panel-figures` 的 PNG）
- 需要可编辑 .pptx（同事/导师要改字）或编译 PDF（Beamer）

## 工作流：outline.json source-first（python-pptx）

### Step 1: 写 outline.json（唯一源）

```json
{
  "title": "cns-bio-pilot 生信分析流程验证",
  "subtitle": "基于 OmicVerse + squidpy 的单细胞与空间转录组全流程",
  "preset": "cns-bio-light",
  "slides": [
    {"variant": "title", "title": "...", "subtitle": "..."},
    {"variant": "scientific-figure", "title": "单细胞聚类",
     "image": "figures/umap_celltype.png",
     "caption": "图1. UMAP 按细胞类型（N=2,700，leiden res=0.6）",
     "bullets": ["6 个聚类", "CD4 T / Mono / B / CD8 T / NK / 血小板"]},
    {"variant": "image-sidebar", "title": "差异表达",
     "image": "figures/volcano.png",
     "caption": "图2. 火山图（Padj<0.05 & |log2FC|>1，BH-FDR）",
     "bullets": ["602 显著基因", "Top: RPS12/LDHB（T 细胞代谢）"]},
    {"variant": "results-table", "title": "空转 SVG",
     "table": {"headers": ["Rank","Gene","I","p"],"rows": [["1","Pcp2","0.85","<0.001"]]}},
    {"variant": "methods-flow", "title": "流程", "steps": ["QC","聚类","注释","DE"]}
  ]
}
```

### Step 2: 渲染（python-pptx）

```bash
# 默认 python-pptx 渲染（无需 Node/AI API）
python scripts/build_deck.py outline.json -o presentation.pptx
# 可选：LibreOffice 导出 PDF（无 LibreOffice 时跳过）
soffice --headless --convert-to pdf presentation.pptx
```

### Step 3: QA Gate（强制，三道检查）

```bash
# 1. 几何 QA：溢出/重叠/小字号（readability contract）
python scripts/qa_deck.py presentation.pptx
# 2. 占位符 grep：检测 TODO/lorem/xxx/placeholder 泄漏
python scripts/qa_placeholders.py presentation.pptx
# 3. 视觉复查（可选）：渲染缩略图人工/subagent 审
python scripts/thumbnail_deck.py presentation.pptx --pages 1-5
```

> **USE SUBAGENTS for visual QA**（抄 anthropics/pptx）：你看自己的代码会有确认偏误，让 subagent 用全新视角查重叠/溢出/对比度。"如果你第一眼没发现任何问题，说明你看得不够仔细。"

## Slide Variants（版式纪律，吸收 siril9）

| variant | 用途 | 排版纪律 |
|---|---|---|
| `title` | 标题页 | 居中大标题，副标题，无装饰线 |
| `section` | 章节分隔 | 单行居中，留白>60% |
| `scientific-figure` | 2-4 panel 真实图 | **最多 4 panel，超过 preflight 报错**；tight bbox，trim whitespace |
| `image-sidebar` | 1 大图 + 文字解读 | 图占 60%，bullet 占 35%，图注在图下 |
| `results-table` | 结果表（带语义色） | pass/fail 用绿/红，数字右对齐 |
| `methods-flow` | 方法流程 | 横向/纵向步骤箭头，每步 1 词 |
| `bullets` | 纯文字（少用） | ≤4 bullet，每条 ≤6 词 |

> **scientific-figure 关键**（生信核心场景）：Python 出图（matplotlib/ov.pl）时，导出目标 aspect ratio + `bbox_inches='tight'` + `trim_image_whitespace.py` 去白边，再嵌入。否则 slide 会有难看的白框。

## Preset：cns-bio-light（生信专用）

```
背景: 白 (#FFFFFF)
主色: Navy (#1F3A5F)     — 标题/强调
辅助: 蓝 (#3D7AAB)        — 次级标题
语义: 绿 (#2E8B57) pass / 红 (#E25D5D) fail / 橙 (#E8A838) warning
正文: 深灰 (#333333)
图注: 浅灰 (#666666) 斜体
字体: 标题 Calibri/Arial Bold，正文 Calibri/Arial
```

## Readability Contract（preflight 强制）

| 元素 | 最小字号 | 理由 |
|---|---|---|
| 标题 | 24pt | 远处可读 |
| 正文 bullet | 12pt（理想 14-18pt） | 投影可读 |
| 图注/坐标轴 | 7.5pt | 仅参考 |
| 图表内标签 | 7pt | 仅参考 |
| 页脚 | 7pt，预留 ≥0.25in | 不挤压内容 |

> `qa_deck.py` 会扫描所有文本框，发现 <阈值 的字号直接报错（render 前拦住，不靠肉眼）。

## LaTeX Beamer 备选（学术正式）

需要编译 PDF 且偏好 LaTeX 时用 Beamer。模板见 `assets/beamer_template_{conference,seminar,defense}.tex`，完整指南见 `references/beamer_guide.md`。

```bash
pdflatex beamer_template_conference.tex  # 编译
# 流程图/方程多时用 Beamer；图多时用 python-pptx
```

## References 索引（按需加载）

| 需要什么 | 读哪个文件 |
|---|---|
| 科研叙事结构（story arc / 5 talk types / timing） | `references/talk_types_guide.md` + `references/presentation_structure.md` |
| 排版/配色/布局/无障碍/视觉层级 | `references/slide_design_principles.md` |
| 把期刊 figure 改成 slide-friendly | `references/data_visualization_slides.md` |
| Content/Design/Timing 三类坑 + 10 条原则 | `references/pitfalls.md` |
| LaTeX Beamer 完整文档 | `references/beamer_guide.md` |
| 视觉复查工作流（PDF→图、问题记录、迭代） | `references/visual_review_workflow.md` |

## Assets（模板）
- `assets/beamer_template_conference.tex` / `_seminar.tex` / `_defense.tex`
- `assets/powerpoint_design_guide.md` / `assets/timing_guidelines.md`

## 前置依赖（从哪来）
- **真实分析图** → `visualization/omicverse-plotting`（ov.pl.embedding/volcano）或 `visualization/multi-panel-figures`（6 panel 拼图）产出的 PNG
- **空转空间切片图** → `spatial/omicverse-spatial` 的 `sq.pl.spatial_scatter` 输出
- **结果数据** → 分析 h5ad / DE 表 / SVG 表（写进 results-table variant）
- **文献引用** → intro 引 3-5 篇，discussion 引 3-5 篇（research-lookup）
- **环境**：`pip install python-pptx Pillow`（无 Node/AI API 依赖）

## Pre-Output Checklist（出报告前必过）
- [ ] 数值完整性：每张定量图保留 N / 统计检验 / 误差线
- [ ] 交叉条件一致性：效果是 universal 还是 cell-type-specific？
- [ ] 引用支撑：明确哪张图/哪个统计支持主结论
- [ ] 避免臆测：无显著差异时写 "No significant effect"，不硬编故事
- [ ] 关联≠因果：用 "associated with"，regulates/causes 需实验证据
- [ ] readability contract：标题≥24pt / 正文≥12pt / 图注≥7.5pt
- [ ] 反 AI 味：标题下无装饰线，无占位符泄漏
- [ ] 跑 qa_deck.py（几何）+ qa_placeholders.py（占位符）✅

## 何时离开本 skill（去哪）
- 内部组会 / 进度汇报 → `presentation/lab-meeting-slides`
- 写论文 Methods / Results / 图注 → 对应 writer skill
- 单独发表级 figure → `visualization/multi-panel-figures`
- 机制/流程图 → `visualization/scientific-schematics`
- 完成后跑 `python scripts/qa_deck.py presentation.pptx` 校验

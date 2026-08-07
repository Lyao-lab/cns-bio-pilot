---
name: scientific-schematics
description: 纯代码（matplotlib+networkx）生成科学示意图模板库：分析流程图、信号通路、反馈环路、对比图、图形摘要。JSON 参数驱动，无需 AI API。当用户要画机制图、流程图、通路图、反馈环路、图形摘要时触发。
license: MIT
metadata:
  author: AIPOCH
---

## When NOT to use this skill
- Data-driven plots (UMAP/volcano/heatmap/dotplot) → use `visualization/figure-production` (ov.pl.*)
- 6-panel composite publication figure (already have sub-figures to assemble) → use `visualization/figure-production`
- Need Nano Banana Pro to generate slide visuals with research context → use `presentation/scientific-slides`

# Scientific Schematics Skill

## When to Use
- Creating **journal-ready** mechanism/flow/pathway figures (clean typography, consistent styling, high resolution) directly from structured JSON parameters.
- Producing **poster-friendly** diagrams that prioritize readability at distance (larger labels, stronger contrast).
- Drafting **signal pathway** visuals (e.g., CXCL12 → CXCR4 → macrophage activation) for papers or slides.
- Drawing **feedback loops** (positive/negative regulatory circuits) for mechanism figures.
- Building **left-right comparison** figures (Normal vs Disease, Control vs Treatment).
- **Graphical Abstract / TOC figure**: assemble an Input → Process → Output three-column summary from a paper abstract (see "Mode: Graphical Abstract" below).
- Rapidly iterating on a diagram concept by editing JSON parameters — no API calls, no waiting.

## Key Features
- **Pure code, no AI API**: matplotlib + networkx render everything locally; zero network calls, zero API keys.
- **JSON-parameter driven**: every template reads its layout/content from a `params` dict, so edits are one-line JSON changes.
- **5 ready-made templates**: flow diagram, pathway cascade, feedback loop, left-right comparison, three-column graphical abstract.
- **Consistent styling**: Morlandi palette + Navy titles, 300 DPI output, `.png/.pdf/.svg` auto-selected by output suffix.
- Reference guidance (inline sections below):
  - Best practices: see §Best Practices below
  - Template params: see §5 Templates below
  - Graphical abstract layout: see `references/graphical_abstract_layout.md`

## Dependencies
- Python 3.10+ (recommended)
- Python packages (all present in the `sc` conda env):
  - `matplotlib`
  - `networkx`
  - `numpy`
- No environment variables required.

## Example Usage

### 1) Run a template with default example params (see what a template looks like first)
```bash
python scripts/generate_schematic.py --template flow
```

### 2) Run with inline JSON params
```bash
python scripts/generate_schematic.py --template feedback_loop \
  --params '{"loop_type":"positive","nodes":[{"id":"F","label":"Fibroblast","color":0},{"id":"M","label":"Macrophage","color":2}],"edges":[{"from":"F","to":"M","label":"CXCL12"},{"from":"M","to":"F","label":"TGFb"}],"title":"Feedback loop"}' \
  -o figures/feedback_loop.png
```

### 3) Run with a params JSON file
```bash
python scripts/generate_schematic.py --template pathway \
  --params params/pathway.json -o figures/pathway.pdf
```

### 4) Adjust resolution / output format
```bash
python scripts/generate_schematic.py --template comparison \
  --params '{"left":{"title":"Normal","items":["Low fibrosis","Quiescent FB"]},"right":{"title":"Disease","items":["High fibrosis","Activated FB"]},"title":"Normal vs Disease"}' \
  -o figures/comparison.svg --dpi 300
```

## CLI

```
python scripts/generate_schematic.py --template TEMPLATE [--params PARAMS] [-o OUTPUT] [--dpi DPI]

  TEMPLATE  flow | pathway | feedback | comparison | graphical_abstract
            （兼容别名：flow_diagram, pathway_diagram, feedback_loop, loop,
              comparison_diagram, graphical, abstract）
  PARAMS    JSON 文件路径，或内联 JSON 字符串；省略 → 用模板默认示例参数
  OUTPUT    输出路径，按后缀自动选择 .png/.pdf/.svg（默认 schematic.png）
  DPI       输出分辨率，默认 300
```

## 5 Templates

所有模板统一配色（Morlandi 色板 + Navy 标题 `#1F3A5F`），默认 `figsize=(10,6)`（graphical_abstract 用 `(12,5)`），背景白色、无坐标轴。每个模板的参数都有合理默认值——只传部分字段时其余沿用默认。

### 1. flow — 分析流程图
水平箭头流，每步一个圆角矩形；**steps > 6 时自动换行成 2 行蛇形**。
```json
{
  "steps": ["QC", "Cluster", "Annotate", "DE", "CCC", "Spatial"],
  "title": "Analysis pipeline"
}
```

### 2. pathway — 信号通路级联
节点自动布局（有向无环则按拓扑层次水平推进），带 edge label 的箭头。`color` 为 MORLANDI 色板索引（0-5）。
```json
{
  "nodes": [
    {"id": "A", "label": "CXCL12+ Fibro", "color": 0},
    {"id": "B", "label": "CXCR4+ Mac", "color": 2},
    {"id": "C", "label": "M2 activation", "color": 1}
  ],
  "edges": [
    {"from": "A", "to": "B", "label": "CXCL12-CXCR4"},
    {"from": "B", "to": "C", "label": "activates"}
  ],
  "title": "Signaling pathway"
}
```

### 3. feedback — 反馈环路
节点环形排列（极坐标算位置），弧形箭头；中心标记正反馈 `+`（红）/ 负反馈 `⊖`（蓝）。
```json
{
  "loop_type": "positive",
  "nodes": [
    {"id": "F", "label": "Fibroblast", "color": 0},
    {"id": "M", "label": "Macrophage", "color": 2}
  ],
  "edges": [
    {"from": "F", "to": "M", "label": "CXCL12"},
    {"from": "M", "to": "F", "label": "TGFb"}
  ],
  "title": "Feedback loop"
}
```

### 4. comparison — 左右对比图
左右两个面板（标题框 + 条目列表），中间虚线分隔；右栏可加浅红底色突出差异。
```json
{
  "left":  {"title": "Normal",  "items": ["Low fibrosis", "Quiescent FB", "Few immune"]},
  "right": {"title": "Disease", "items": ["High fibrosis", "Activated FB", "Mac infiltrate"]},
  "title": "Normal vs Disease"
}
```

### 5. graphical_abstract — 三栏图形摘要
Input → Method → Finding 三栏并列，每栏标题框（带 icon）+ 条目列表，栏间箭头，顶部统一标题。icon 默认用 DejaVu Sans 可渲染符号（▷/⚙/★）；若系统装有 emoji 字体也可传 emoji。
```json
{
  "columns": [
    {"title": "Input",   "icon": "▷", "items": ["Patient samples"]},
    {"title": "Method",  "icon": "⚙", "items": ["scRNA-seq", "Spatial"]},
    {"title": "Finding", "icon": "★", "items": ["FB subtypes", "CXCL12 axis"]}
  ],
  "title": "Graphical Abstract"
}
```

## Implementation Details
### Pipeline
1. **Parse**: `--template` 定位模板函数，`--params` 解析 JSON（文件路径或内联字符串）。
2. **Render**: 模板函数在 matplotlib axes 上绘制（FancyBboxPatch 节点 / FancyArrowPatch 箭头 / 文本标签）。
3. **Save**: 按 `-o` 后缀（`.png/.pdf/.svg`）调用 `fig.savefig`，默认 dpi=300。

### Key Parameters
- `--template <flow|pathway|feedback|comparison|graphical_abstract>`: 选择模板。
- `--params <json|file>`: 模板内容与布局参数；省略时用模板默认示例。
- `-o <path>`: 输出路径（后缀决定格式）。
- `--dpi <int>`: 输出分辨率（默认 300）。

## Prerequisites (where inputs come from)

- **Structured JSON params** → template content (steps / nodes+edges / loop type / comparison panels / abstract columns), typically derived from the analysis narrative or manuscript text
- **Environment**: no API keys; Python 3.10+ with `matplotlib` / `networkx` / `numpy` (all in `sc` env)
- Reference docs: see §Best Practices and §5 Templates above
- Script entry `scripts/generate_schematic.py`

## Pre-Output Checklist (core rules in **top-level** `references/meta_methodology.md` + skill-specific)

- [ ] Core rules passed (fact-based / pseudobulk / search-first / postcheck / checkpoint — see `SKILL.md` Core Rules)
- [ ] No fake/placeholder data in schematic (pure mechanism, no bars/plots)
- [ ] Template chosen and params JSON validated (no missing keys — each missing field falls back to a sane default)
- [ ] Output rendered and opened (non-empty, labels legible, colors from Morlandi palette)

## Best Practices

### Design Guidelines
1.  **Colorblind Safety**: The Morlandi palette is low-saturation and colorblind-safe; do not introduce raw red/green juxtaposition.
2.  **Whitespace**: Keep node/box spacing generous; the snake line-wrap in `flow` (>6 steps) prevents crowding.
3.  **Typography**: Titles Navy 16pt bold, nodes 10pt, edge labels 8pt italic — consistent hierarchy.
4.  **Consistency**: Arrowheads and line weights are fixed globally (FancyArrowPatch `->` style); keep custom params content-only.

### Journal vs. Poster
- **Journal**: Keep default 300 DPI; compact labels.
- **Poster**: Increase `--dpi` and/or pass longer labels in params for readability at distance.

## Supported Diagram Categories

### Analysis Pipelines
- Preprocessing / clustering / annotation / DE / CCC / spatial workflows (6 steps single row, >6 two-row snake)

### Biological Pathways
- Signal transduction cascades (A → B → C with mechanism labels)
- Positive / negative feedback regulatory loops

### Comparisons
- Normal vs Disease, Control vs Treatment, before vs after panels

### Graphical Abstracts
- Three-column Input → Method → Finding summaries for papers / TOC figures

## When to leave this skill (where to go)

- Assemble the generated schematic into a publication figure → `visualization/figure-production`
- Write the schematic legend → `presentation/manuscript-writing`
- Embed into a slide → `presentation/scientific-slides` (add `"image": "figures/output.png"` to outline.json)
- Note: this skill outputs mechanism/schematic/graphical-abstract figures; data-driven plots (UMAP/volcano/heatmap) go to `visualization/figure-production`

## Mode: Graphical Abstract (merged from former graphical-abstract skill)

When the task is **generating a Graphical Abstract / TOC figure for a paper**, use `references/graphical_abstract_layout.md` as the layout reference, then render with the `graphical_abstract` template:

1. **Parse the abstract** → extract topic / methods / findings / implications
2. **Map visual elements** → for each concept choose an icon + color index + items list (palette follows the Morlandi palette above)
3. **Choose the layout** → three-column horizontal (Input → Process → Output) is the default; `comparison` template covers left-right narrative; `flow`/`pathway` cover vertical/multi-step mechanisms
4. **Render with the template** → write the abstract-derived content into the `columns` JSON and run:

```bash
python scripts/generate_schematic.py --template graphical_abstract \
  --params '{"columns":[{"title":"Input","icon":"▷","items":["..."]},{"title":"Method","icon":"⚙","items":["..."]},{"title":"Finding","icon":"★","items":["..."]}],"title":"..."}' \
  -o figures/abstract.png
```

For detailed layout rules and grid templates, see `references/graphical_abstract_layout.md`.

## Key pitfalls

- **JSON syntax errors**: `--params` inline strings must be valid JSON (double quotes); if in doubt write params to a file and pass the path
- **Template name typos**: use the canonical names or listed aliases; arbitrary names exit with an error listing available templates
- **Emoji icons**: DejaVu Sans (matplotlib default) cannot render emoji — use the built-in symbols (▷/⚙/★) unless your system has an emoji font installed
- **Schematic ≠ data figure**: pure mechanism/flow only; data-driven plots (UMAP/volcano) go to `visualization/figure-production`
- **No quantitative data invented**: the templates draw labels/boxes only — never fabricate numbers in params
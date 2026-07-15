---
name: scientific-slides
description: 用 python-pptx 或 LaTeX Beamer 生成科研演讲幻灯片，覆盖正式会议 talk 与内部组会/lab meeting/进度汇报两类场景。当用户要做 PPT、幻灯片、slides、汇报、beamer、presentation、组会、lab meeting、project review、周报月报时触发。纯代码生成，不依赖 AI 生图 API——嵌入真实分析图（UMAP/火山图/空间切片等），outline.json 驱动，含 readability 契约与几何 QA。
allowed-tools: Read Write Edit Bash
license: MIT
---

# Scientific Slides

## When NOT to use this skill
- Writing paper Methods / Results / figure legend text → use `presentation/methods-writer` / `presentation/results-writer` / `presentation/figure-legend-writer`
- Standalone publication-grade figure (not a slide) → use `visualization/multi-panel-figures`
- Drawing mechanism / flow / architecture diagrams (not slides) → use `visualization/scientific-schematics`

## Overview

This skill generates research presentation slides with **python-pptx** (default) or **LaTeX Beamer**. **Core principle: source-first, pure code, no dependency on AI image-generation APIs**. It covers two modes: **formal talk** (default — conference / defense / grand round) and **Lab meeting** (group meeting / progress report / PI update — discussion-driven + data-honesty boundary).

**Design philosophy** (drawn from siril9/presentation-skill + anthropics/pptx patterns):
- **Deck as Code**: `outline.json` is the single source; a script renders `.pptx`; a QA loop verifies layout — no one-off inline python-pptx; edit the source, not the artifact
- **Visual-First**: every slide embeds a real analysis figure (UMAP / volcano / spatial section), not a bullet-list pileup
- **Research-Backed**: every data figure annotates N / statistical test / threshold (Wilcoxon+FDR / Moran's I)
- **Minimal Text**: bullets are prompts; you narrate verbally — 3-4 bullets, ≤6 words each, 24-28pt
- **Readability Contract**: title ≥24pt / body ≥12pt / caption ≥7.5pt / chart labels ≥7pt (preflight-enforced)
- **Anti-AI-taste iron rule** (from anthropics/pptx): **never add a decorative line under a title** — that is the hallmark of AI-generated slides

## When to Use This Skill

- Conference talk (5-20 min) / seminar (45-60 min) / defense / grant pitch / journal club
- Need to embed real analysis figures (PNGs from `visualization/omicverse-plotting` or `multi-panel-figures`)
- Need an editable .pptx (peers/advisor will edit text) or a compiled PDF (Beamer)

## Workflow: outline.json source-first (python-pptx)

### Step 1: Write outline.json (the single source)

```json
{
  "title": "cns-bio-pilot Bioinformatics Pipeline Validation",
  "subtitle": "Single-cell + spatial transcriptomics full pipeline with OmicVerse + squidpy",
  "preset": "cns-bio-light",
  "slides": [
    {"variant": "title", "title": "...", "subtitle": "..."},
    {"variant": "scientific-figure", "title": "Single-cell clustering",
     "image": "figures/umap_celltype.png",
     "caption": "Fig 1. UMAP by cell type (N=2,700, leiden res=0.6)",
     "bullets": ["6 clusters", "CD4 T / Mono / B / CD8 T / NK / Platelet"]},
    {"variant": "image-sidebar", "title": "Differential expression",
     "image": "figures/volcano.png",
     "caption": "Fig 2. Volcano (Padj<0.05 & |log2FC|>1, BH-FDR)",
     "bullets": ["602 sig genes", "Top: RPS12/LDHB (T-cell metabolism)"]},
    {"variant": "results-table", "title": "Spatial SVGs",
     "table": {"headers": ["Rank","Gene","I","p"],"rows": [["1","Pcp2","0.85","<0.001"]]}},
    {"variant": "methods-flow", "title": "Pipeline", "steps": ["QC","Cluster","Annotate","DE"]}
  ]
}
```

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

## Slide Variants (layout discipline, drawn from siril9)

| variant | use | layout discipline |
|---|---|---|
| `title` | title page | centered large title, subtitle, no decorative line |
| `section` | section divider | single centered line, whitespace >60% |
| `scientific-figure` | 2-4 panel real figure | **max 4 panels, preflight errors beyond that**; tight bbox, trim whitespace |
| `image-sidebar` | 1 large figure + text interpretation | figure 60%, bullets 35%, caption below figure |
| `results-table` | results table (with semantic color) | pass/fail in green/red, numbers right-aligned |
| `methods-flow` | method flow | horizontal/vertical step arrows, one word per step |
| `bullets` | text-only (use sparingly) | ≤4 bullets, ≤6 words each |

> **scientific-figure key** (core bioinformatics scenario): when plotting in Python (matplotlib/ov.pl), export at the target aspect ratio + `bbox_inches='tight'` + `trim_image_whitespace.py` to strip margins, then embed. Otherwise the slide gets an ugly white border.

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
| Figure aesthetics (color / font / non-overlap) | top-level `references/figure_aesthetics.md` |
| Multi-panel composition (layout / shared legend / panel labels) | top-level `references/figure_layout.md` |

> Removed in v12.1 (redundant with top-level figure refs): talk_types_guide, presentation_structure, slide_design_principles, data_visualization_slides, visual_review_workflow, core_capabilities, development_workflow. The 7-step Quick Route + Pre-Output Checklist + Key pitfalls in this SKILL.md already cover slide structure/design/review essentials.

## Assets (templates)
- `assets/beamer_template_conference.tex` / `_seminar.tex` / `_defense.tex`
- `assets/powerpoint_design_guide.md` / `assets/timing_guidelines.md`

## Prerequisites (where inputs come from)
- **Real analysis figures** → PNGs from `visualization/omicverse-plotting` (ov.pl.embedding/volcano) or `visualization/multi-panel-figures` (6-panel composites)
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
- Standalone publication-grade figure → `visualization/multi-panel-figures`
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

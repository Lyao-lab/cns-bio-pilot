---
name: scientific-schematics
description: 自动生成发表级科学示意图（机制图/流程图/架构图/路径图/图形摘要 Graphical Abstract）。从自然语言描述或论文 abstract 出发，经 AI 生成→视觉审查→精炼循环产出 journal/poster 级图片。当用户要画机制图、流程图、神经网络架构、信号通路、论文图形摘要/TOC 图时触发。
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills) (merged the abstract→layout capability of the former `visualization/graphical-abstract` skill in 2026-07)

## When NOT to use this skill
- Data-driven plots (UMAP/volcano/heatmap/dotplot) → use `visualization/omicverse-plotting` (ov.pl.*)
- 6-panel composite publication figure (already have sub-figures to assemble) → use `visualization/multi-panel-figures`
- Need Nano Banana Pro to generate slide visuals with research context → use `presentation/scientific-slides`

# Scientific Schematics Skill

## When to Use
- Creating **journal-ready** figures (clean typography, consistent styling, high resolution) from a short textual description.
- Producing **poster-friendly** diagrams that prioritize readability at distance (larger labels, stronger contrast).
- Drafting **neural network architecture** schematics (e.g., Transformer blocks, attention modules) for papers or slides.
- Generating **biological pathway** visuals (e.g., Krebs cycle) with iterative quality review.
- **Graphical Abstract / TOC figure**: recommend layout + elements + AI prompts from a paper abstract (see "Mode: Graphical Abstract" below).
- Rapidly iterating on a diagram concept when you need **AI-assisted refinement loops** instead of manual redraws.

## Key Features
- **Text-to-diagram automation**: Converts a natural-language prompt into a publication-quality schematic.
- **Iterative generate → review → refine loop**: Automatically improves the figure until a quality threshold is met.
- **Document-type aware critique**: Reviewer feedback adapts to `journal` vs `poster` requirements.
- **Model-configurable pipeline**: Choose separate LLMs for generation and vision-based review.
- **Output validation**: Performs final checks (e.g., resolution/accessibility considerations) before saving to `figures/`.
- Reference guidance:
  - Best practices: `references/best_practices.md`
  - Supported diagram categories: `references/diagram_types.md`

## Dependencies
- Python 3.10+ (recommended)
- Python packages:
  - `pillow` (PIL)
  - `matplotlib`
  - `requests`
- Environment:
  - `OPENROUTER_API_KEY` (required)

## Example Usage
### 1) Set the OpenRouter API key
**Windows (PowerShell)**
```powershell
$env:OPENROUTER_API_KEY="your_key_here"
```

**Linux/macOS**
```bash
export OPENROUTER_API_KEY="your_key_here"
```

### 2) Run the generator (journal/poster)
```bash
python scripts/generate_schematic.py "Transformer architecture with attention mechanism" --doc-type journal
```

### 3) Override the generation model
```bash
python scripts/generate_schematic.py "Krebs cycle" --doc-type journal --generator anthropic/claude-3.5-sonnet
```

### 4) (Optional) Override both generator and reviewer
```bash
python scripts/generate_schematic.py "Flowchart of a clinical trial enrollment pipeline" \
  --doc-type poster \
  --generator google/gemini-2.0-flash-001 \
  --reviewer google/gemini-2.0-flash-001
```

## Implementation Details
### Pipeline Stages
1. **Generation**
   - A code-capable LLM converts the prompt into a diagram image.
   - Default generator model: `google/gemini-2.0-flash-001`.

2. **Review**
   - A vision-capable LLM evaluates the generated image against the target `--doc-type`.
   - Default reviewer model: `google/gemini-2.0-flash-001`.
   - The reviewer returns actionable critique and a numeric quality score.

3. **Refinement Loop**
   - If the score is below the acceptance threshold (e.g., **8.5/10**), the system re-enters generation using the reviewer's feedback as constraints.
   - This repeats until the threshold is met or the run terminates by internal stopping conditions.

4. **Finalization**
   - Performs final checks such as **resolution suitability** and **accessibility-oriented considerations** (e.g., legibility).
   - Saves the final artifact to the `figures/` directory.

### Key Parameters
- `--doc-type <journal|poster>`: Controls review criteria (e.g., density/precision for journals vs readability/scale for posters).
- `--generator <model_id>`: Model used to produce the diagram.
- `--reviewer <model_id>`: Model used to critique the diagram.
- **Quality threshold**: A numeric cutoff (example: `8.5/10`) that determines whether refinement continues.

## Prerequisites (where inputs come from)

- **Natural-language description** → text describing the mechanism/flow/architecture (from `presentation/results-writer` method narrative, or directly from the user)
- **Optional reference figure** → existing sketch/schematic (to assist generation)
- **Environment**: `OPENROUTER_API_KEY` (required); Python 3.10+, deps `pillow`/`matplotlib`/`requests`
- Reference docs: `references/best_practices.md`, `references/diagram_types.md`
- Script entry `scripts/generate_schematic.py`

## Pre-Output Checklist (must pass before exporting a figure)
- [ ] Numerical integrity: if the schematic contains quantitative elements (e.g., scale bars / arrow thickness), retain N / statistical basis
- [ ] Axis labels / legend / colorblind-friendly: clear labels, colorblind-safe palette (avoid pure red-green)
- [ ] Citation support: literature/data sources underlying the mechanism diagram are explicit
- [ ] Avoid speculation: unverified steps labeled "hypothesized", not drawn as established fact
- [ ] Correlation ≠ causation: use "associated with"; regulates/causes requires experimental evidence
- [ ] Run postcheck.py ✅

## When to leave this skill (where to go)

- Assemble the generated schematic into a publication figure → `visualization/multi-panel-figures`
- Write the schematic legend → `presentation/figure-legend-writer`
- Embed into a slide → `presentation/scientific-slides` (`--attach figures/output.png`)
- Note: this skill outputs mechanism/schematic/graphical-abstract figures; data-driven plots (UMAP/volcano/heatmap) go to `visualization/omicverse-plotting`

## Mode: Graphical Abstract (merged from former graphical-abstract skill)

When the task is **generating a Graphical Abstract / TOC figure for a paper**, follow the 4-step workflow in `references/graphical_abstract_layout.md`:

1. **Parse the abstract** → extract topic / methods / findings / implications
2. **Map visual elements** → for each concept choose a symbol + palette + position (palette follows `references/figure_aesthetics.md` dual-track)
3. **Recommend a layout grid** → choose by the abstract's narrative structure (three-column horizontal / vertical flow / left-right comparison / central radial)
4. **Generate AI prompts** → produce both Midjourney-style and DALL-E-style versions

After producing the blueprint, **use this skill's `generate_schematic.py` main loop to actually generate the image** (generate→review→refine, threshold 8.5/10) — this is the key improvement from merging graphical-abstract: the former skill only produced half-finished prompts, now it closes the loop to image generation.

```bash
# Example: generate a graphical abstract from an abstract
python scripts/generate_schematic.py "Graphical abstract: [central element + flow inferred from abstract]" \
  --doc-type journal
```

For detailed layout rules, grid templates, and AI prompt templates, see `references/graphical_abstract_layout.md`.

## Key pitfalls

- **Depends on OPENROUTER_API_KEY**: without the env var, generate_schematic.py fails — run `export OPENROUTER_API_KEY=...` first
- **Quality threshold 8.5/10**: the refine loop regenerates repeatedly if the threshold isn't met — set max_iter to avoid infinite loops
- **AI-generated figures ≠ accurate figures**: the model may draw biological facts incorrectly (e.g., labeling a T-cell marker as a B-cell) — **manually verify the mechanism/labels**; don't blindly trust AI output
- **graphical-abstract mode only produces prompts**: the former graphical-abstract skill's abstract→layout capability has been merged in, but Midjourney/DALL-E still need external image-generation tools
- **scientific-schematics is for non-data figures**: pure mechanism/flow; data-driven plots (UMAP/volcano) go to `visualization/omicverse-plotting`
- **AI "fake data" risk**: the model sometimes draws placeholder elements that look like bar charts — during review confirm there is no quantitative data, purely schematic

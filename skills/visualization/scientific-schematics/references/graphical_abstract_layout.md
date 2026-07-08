# Graphical Abstract Layout Recommendation

> Recommend the layout, elements, palette, and AI prompts for a Graphical Abstract / TOC figure from a paper abstract.
> Merged from the former `visualization/graphical-abstract` skill (downgraded to a reference in 2026-07, since actual image generation is still done by `generate_schematic.py`).
> **Usage**: when `scientific-schematics` runs with `--mode graphical-abstract`, follow the steps in this document to produce a layout blueprint + AI prompts, then run the main skill's generate→review→refine loop.

---

## When to use this mode

- The target journal requires a Graphical Abstract / TOC figure
- You already have a paper abstract or Results narrative and want to design a summary figure from it
- **Not applicable**: data-driven figures (UMAP/volcano), 6-panel assemblies, pure mechanism schematics (no abstract constraint) → use scientific-schematics default mode

---

## Workflow (4 steps)

### Step 1: Parse the abstract, extract key concepts

Extract four categories of information from the abstract text:
- **Core research topic**: the research subject (e.g., "protein structure prediction")
- **Methods/techniques**: methods/technologies (e.g., "transformer + geometric constraints")
- **Key findings/results**: core findings (e.g., "CASP14 SOTA")
- **Implications**: significance (e.g., "accelerated drug design")

### Step 2: Map to visual elements

For each concept choose a visual symbol + palette + position:

| Element type | Visual symbol examples | Palette (per figure_aesthetics.md dual-track) |
|---|---|---|
| Biological concept | 🧬 DNA / 🦠 cell / 🧠 neuron | Morandi discrete colors |
| Method/algorithm | ⚙️ gear / 🤖 AI / 📊 chart | Morandi discrete colors |
| Result | 🏆 trophy / 📈 rising curve | High = dark red (continuous color) |
| Process | → arrow / 🔀 fork | Neutral gray |

**Palette discipline**: colorblind-safe (no pure red-green juxtaposition), low saturation (Morandi-fied), unified with the main-text figure palette.

### Step 3: Recommend a layout grid

Choose the layout by the abstract's narrative structure:

```
Narrative = "Input → Process → Output"      → three-column horizontal
Narrative = "Problem → Method → Result"     → three-column horizontal
Narrative = "multi-layer mechanism (A affects B affects C)" → vertical flow
Narrative = "comparison (Control vs Treatment)" → left-right comparison
Narrative = "complex system"                → central radial
```

Layout example (three-column horizontal):
```
┌─────────────────────────────────┐
│        [Title/Concept]          │
│            🧬🤖                 │
├──────────┬──────────┬───────────┤
│  Input   │ Process  │  Output   │
│   📥     │   ⚙️     │    📈     │
└──────────┴──────────┴───────────┘
```

### Step 4: Generate AI prompts

Produce two prompts for external image tools (or this skill's generate stage):

**Midjourney style** (short, keyword-based, with parameters):
```
Scientific graphical abstract, [topic], [key visual elements], [palette] background,
clean minimalist style, academic journal style, high quality --ar 16:9 --v 6
```

**DALL-E / natural-language style** (long, descriptive):
```
A clean scientific illustration for a research paper about [topic].
Show [central element] surrounded by [auxiliary elements]. Use [palette].
Include [geometric shapes] representing [data flow / mechanism].
Modern, minimalist academic style suitable for a Nature or Science journal cover.
```

---

## Output format (blueprint delivered to the user / generation stage)

```markdown
# Graphical Abstract Recommendation

## Abstract Summary
**Topic**: ...
**Method**: ...
**Result**: ...

## Key Concepts
- 🧬 [concept 1]
- 🤖 [concept 2]
- 📊 [concept 3]

## Visual Elements
| Element | Symbol | Position | Color |
|---------|--------|----------|-------|
| Core Concept | ... | Center | ... |
| Method | ... | Left | ... |
| Result | ... | Right | ... |

## Layout Suggestion
[ASCII grid]

## AI Art Prompts
### Midjourney
[prompt]
### DALL-E
[prompt]
```

---

## Discipline (inherited from the former skill)

- **Numerical integrity**: if the summary figure cites quantitative results, annotate N / statistical source
- **Avoid speculation**: unverified mechanisms labeled "proposed", not drawn as confirmed
- **Correlation ≠ causation**: use "associated with"; regulates/causes requires experimental evidence
- **Citation support**: the core conclusions underlying the summary have corresponding main-text figures/statistics
- **Palette**: follow `references/figure_aesthetics.md` dual-track palette (Morandi discrete + blue-white-red continuous)

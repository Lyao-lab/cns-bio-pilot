# Figure Design: Chart-Type Selection & Information Hierarchy

> What to plot (and what NOT to plot) — the higher-level design wisdom that separates CNS figures from generic plots. This is the third figure reference, complementing:
> - `figure_aesthetics.md` — technical spec (DPI / fonts / color / non-overlap)
> - `figure_layout.md` — multi-panel composition (gridspec / shared legend / panel labels)
> - **this file** — what chart type, how to organize information, how to show statistics

Sources: Rougier et al. 2014 PLOS Comp Biol (Ten Simple Rules for Better Figures), Weissgerber et al. 2015 PLOS Biol (Beyond bar graphs), Krzywinski & Altman 2013 Nat Methods (Error bars), Heumos et al. 2023 Nat Rev Genet (sc-best-practices), Wilke 2019 (Fundamentals of Data Visualization), Tufte (Visual Display), Cell Press / Nature figure guidelines.

---

## 1. Chart-type decision tables (what to plot for each bio data scenario)

### Cell-type composition comparison

| Use | When | Don't use when |
|---|---|---|
| **Stacked/grouped bar** | Comparing cell-type fractions across donors/conditions (≥2 groups) | Single snapshot with ≤4 types → pie ok |
| **Pie chart** | ≤4-5 categories, single sample, part-of-whole is the message | NEVER for cross-condition comparison (humans can't compare pie slice angles across pies) |
| **Grouped bar > stacked bar** | Reader must compare individual cell-type values (not totals) across groups | When totals matter more than components |
| **100% stacked bar** | Total cell counts differ wildly across samples; only relative composition matters | When absolute counts are informative |

> Wilke 2019 Ch.10; Bang Wong Nat Methods Points of View 2011.

### Marker gene expression across cell types

| Use | When | Don't use when |
|---|---|---|
| **Dotplot** | cell types ≤6 AND markers ≤~20 (encodes 2 quantities compactly: size=%expressing, color=mean expr) | >20 markers → unreadable, switch to heatmap |
| **Violin + box + points** | ≤8 cell types AND ≤10 markers; distribution shape matters (bimodality/skew) | n>200/group → points become a blob, drop to violin only |
| **Heatmap (row z-score)** | >20 markers × >6 cell types; full signature matrix at once | ≤6 markers → dotplot is cleaner |
| **Feature plot (UMAP colored)** | 1-3 genes; showing spatial localization of expression within embedding | >6 genes → use multi-panel matrix (figure_layout.md Template B) |
| **❌ Avoid: violin-only for >15 markers** | too many violins become unreadable | — |

> Heumos et al. 2023 (sc-best-practices.org); Wilke 2019 Ch.7; Weissgerber 2015 (show every point).

### Differential expression results

| Use | When |
|---|---|
| **Volcano** (x=log2FC, y=-log10 padj) | Default for final DE presentation — communicates "both significant AND large-effect" |
| **MA plot** (log-ratio vs mean expr) | QC / normalization diagnostic; detects intensity-dependent bias. Use ALONGSIDE volcano, not instead of |
| **Always**: use **padj** (not raw p); apply **lfcShrink** (DESeq2) before plotting; label top hits |

> McDermaid et al. 2018 Front Genet (PMC6954399); sc-best-practices.org DE chapter.

### Trajectory / pseudotime

| Use | When |
|---|---|
| **PAGA graph + UMAP colored by pseudotime** | Default — abstracted topology as edges + cells colored by pseudotime |
| **Gene-along-pseudotime** (line/heatmap) | Companion panel linking trajectory to molecular changes |
| **❌ NEVER a single linear "path" curve for branched topology** | Use PAGA / diffusion map that preserves branching; a forced linear curve misrepresents biology |

> sc-best-practices.org Pseudotemporal ordering; Wolf et al. 2019 (PAGA).

### Spatial expression

| Use | When |
|---|---|
| **Tissue H&E + spatial feature overlay** | Default — gene expression overlaid on the tissue image (NOT abstract coordinates) |
| **One gene per panel; shared color scale** | Multi-gene spatial panels — facilitates direct cross-gene comparison |

> Heumos 2023; Bioconductor OSTA; Gehlenborg & Wong Nat Methods PoV 2012.

### Cell-cell communication

| Use | When |
|---|---|
| **Circle / chord plot** | L-R signaling counts summary between cell groups (circle = directionality; chord = flow) |
| **Bubble plot** | "Which L-R pairs" matter (pathway × cell-group), not aggregate counts |
| **Spatial plot** | Spatial transcriptomics — communication constrained by physical proximity |
| **❌ Limit chord to ≤8-10 cell groups** | Beyond that unreadable — collapse rare groups or switch to heatmap |

> Jin et al. 2021 Nat Commun (CellChat); sc-best-practices.org CCC chapter.

---

## 2. Visual hierarchy (information organization within a figure)

**Six rules** — each panel/figure must pass:

1. **One take-home message per figure.** If you cannot state it in one sentence, split the figure. *Write the one-sentence message BEFORE drawing; every panel must serve it — remove panels that don't.* (Rougier 2014 Rule 2)
2. **Panel order = narrative order**, typically overview → mechanism → validation. Left-to-right, top-to-bottom. A reader unfamiliar with the work should follow A→B→C without jumping. (Rougier 2014 Rule 1; Nature author guide)
3. **Adapt to the medium.** Print/poster = high contrast + large labels; slide = minimal text; paper = caption-driven. Reusing one figure across all three without adjustment fails. (Rougier 2014 Rule 3)
4. **Caption is not optional** — figure + caption must be interpretable WITHOUT the main text. Cover the body text; can a reader in your field still understand it? (Rougier 2014 Rule 4; Nature)
5. **Insets/zooms ONLY when** fine detail must be seen in context (UMAP region, tissue ROI). Connect inset to source with a box/line + label magnification. **Never use an inset just to fit more data** — that signals the panel should be split. (Rougier 2014 Rule 2/5; Wilke 2019 Ch.21)
6. **Do not trust defaults.** matplotlib/seaborn/ggplot defaults are generic; set fonts/colors/layout deliberately to match the message. If it looks like an unstyled default, revise. (Rougier 2014 Rule 5)

---

## 3. Statistical visualization standards (must-haves in biofigures)

**Seven rules:**

1. **Show individual data points** when n<30/group (preferably always). Bar/line graphs of continuous data hide the distribution — many different distributions produce the same bar. Use scatter/box/violin showing every point. (Weissgerber 2015 PLOS Biol, 1000+ citations)
2. **Choose error bars deliberately:**
   - **SD** = spread of data (describing the sample)
   - **95% CI** = precision of the mean (for inference) — **default for comparative plots**
   - **SEM discouraged** alone — it's ~67% CI and frequently mistaken for SD
   (Krzywinski & Altman 2013 Nat Methods; GraphPad guide)
3. **Error bar type + n MUST be in the legend.** One sentence: "Error bars = 95% CI; n = X biological replicates per group." (Krzywinski & Altman 2013)
4. **P-value star convention** (define in legend — NOT globally standardized):
   `ns` P>0.05 | `*` P≤0.05 | `**` P≤0.01 | `***` P≤0.001 | `****` P≤0.0001
   Increasingly, report exact P values, not stars alone. (GraphPad convention)
5. **Always display n** (text / legend / axis). State biological vs technical replicates — inference must be on biological n. Missing n = top reviewer-rejection reason. (Weissgerber 2015; Krzywinski & Altman 2013)
6. **Do not mislead with the y-axis.** Bar charts must start at zero; truncated y-axis to exaggerate a small difference is an integrity violation. Label log-scale axes clearly. (Weissgerber 2015; Rougier 2014 Rule 6; Tufte)
7. **Do not infer significance from error-bar overlap.** Non-overlapping 95% CIs is suggestive but NOT equivalent to a formal test; overlapping CIs does NOT rule out significance. Always back visual comparisons with the actual test reported in the legend. (Krzywinski & Altman 2013)

---

## 4. Data-ink ratio (Tufte) applied to biofigures

**Five rules:**

1. **Maximize data-ink ratio** = (non-redundant ink encoding data) / (total ink). Strip anything not encoding data. (Tufte, *Visual Display*)
2. **Remove chartjunk**: unnecessary gridlines, 3D effects, shadows, decorative backgrounds, heavy borders. A UMAP does not need a box or grey background; a heatmap does not need 3D bars. (Tufte)
3. **Eliminate redundant data-ink.** If violin + box + bar + dot all show the same metric, pick ONE (prefer the one showing individual points). (Tufte; Weissgerber 2015)
4. **Consolidate redundant colorbars/legends.** Multiple panels sharing the same color scale → one shared colorbar + "shared scale" note. Per-panel colorbars encoding identical scale waste ink and invite misreading. (Gehlenborg & Wong 2012 Nat Methods; Tufte)
5. **Do a "subtraction pass" before submission.** The first draft always has excess ink. Final figure should contain only: data, minimal axes/labels, one legend, one colorbar where needed. (Tufte; Rougier 2014 Rule 5)

---

## 5. Self-contained figure legend structure (CNS standard)

Every figure legend must contain these blocks, in order:

1. **Title sentence** — one sentence summarizing the figure's main finding (NOT just "Figure 1"). No citations in the title. (Cell Press figure guidelines; Nature)
2. **Panel-by-panel description** — A, B, C... in order. State what is shown, axis meaning, color/shape encoding. (Nature author guide)
3. **Statistics block** — (a) error bar type (SD/SEM/95% CI), (b) sample size n (biological vs technical), (c) statistical test, (d) significance annotation (star thresholds or exact P). Missing any → revision. (Krzywinski & Altman 2013; Weissgerber 2015)
4. **Define all symbols/abbreviations** — *, **, #, color codes, non-standard notation. (Cell Press; MDPI)
5. **Methods reference** — "Differential expression performed as described in Methods" / STAR Methods. Don't put full methods in the legend beyond what's needed to read the figure. (Cell Press STAR Methods; Nature)
6. **Sequential labeling & citation** — Figure 1, 2, ...; supplemental as Figure S1. Every figure cited in main text. All parts of a multi-panel figure grouped together. (Cell Press submission requirement)

---

## Self-check before exporting any figure (paste into every plotting session)

- [ ] **One take-home message** — can you state it in one sentence? Does every panel serve it?
- [ ] **Right chart type** — checked against §1 decision tables?
- [ ] **Individual data points shown** (if n<30/group)?
- [ ] **Error bar type stated** (SD / 95% CI — not SEM alone)?
- [ ] **n displayed** + biological vs technical replicates clear?
- [ ] **P-value annotation defined** (star thresholds in legend)?
- [ ] **No misleading y-axis** (bars start at zero; log axis labeled)?
- [ ] **No redundant panels** (4 panels saying the same → cut to 1)?
- [ ] **Chartjunk removed** (no unnecessary grid/border/3D/background)?
- [ ] **Shared colorbar/legend consolidated** (not duplicated per panel)?
- [ ] **Legend self-contained** (title sentence + panel desc + stats block)?
- [ ] Technical spec passed (figure_aesthetics.md) + layout passed (figure_layout.md)?

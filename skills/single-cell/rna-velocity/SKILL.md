---
name: rna-velocity
description: RNA velocity 全家桶。基于 OmicVerse V2 的 ov.single.Velo（统一 dynamo/scvelo/latentvelo/graphvelo/regvelo 五引擎）从 spliced/unspliced 推断方向、潜在时间、驱动基因；下游命运推断走 CellRank 2（统一 kernel 框架）；cellDancer/DeepVelo/pyro-Velocity 等未封装算法走原生 fallback。
---

## When NOT to use this skill
- Only need pseudotime / trajectory (no spliced/unspliced required) → `single-cell/omicverse-pipeline` (`ov.single.Monocle` / PAGA)
- No S/U layers and you cannot re-run velocyto/kb_python → RNA velocity is not possible; use pseudotime instead
- R/Seurat environment and no deep velocity tool → `single-cell/scop` (`RunSCVELO`)
- Assemble a publication-grade velocity figure → finish the plot first, then `visualization/multi-panel-figures`

# OmicVerse RNA Velocity

`pip install omicverse` (V2). OmicVerse unifies 5 velocity engines under `ov.single.Velo`; downstream fate inference integrates CellRank 2 natively.

## 0. Must read: what a trustworthy velocity is (2023–2026 benchmark consensus)

> Read this before running any velocity — to avoid misreading velocity as "instantaneous single-cell rate."

| Key paper | Core caution |
|---|---|
| **Marot-Lassauzaie 2023, Genome Biol** | ⚠️ "velocity estimates neither gene-level nor cell-level expression rates" — it is essentially a neighborhood-smoothed trend and should be read as a **population-level direction**. |
| **Luo 2026, Cell Rep Methods** (17 datasets / 15 methods) | No single best method; scVelo dynamical / UniTVelo give more stable directions; DeepVelo(GCN) / cellDancer are more accurate in multi-lineage systems; dynamo wins on metabolic-labeling data. |
| **Ancheta 2026, PLOS Comput Biol** | Cross-context consistency is poor; kinetic methods are more trustworthy in strong-signal systems. |
| **Gorin 2022, PLOS Comput Biol** | The steady-state assumption + automatic switch-gene selection is unstable and can be manipulated by noise. |

**Trustworthy scenarios**: strong unidirectional developmental signal, metabolic-labeling time stamps, population-level flow visualization, multi-method / multi-kernel consensus.
**Untrustworthy scenarios**: direction changes after count-splitting, steady-state assumption violated (common in developmental systems), treating latent time as real physical time.

---

## 1. Prerequisites (data generation)

All velocity algorithms need `layers['spliced']` and `layers['unspliced']`:

| Tool | Command | Notes |
|---|---|---|
| **velocyto** | `velocyto run10x` / `run` | classic |
| **STARsolo** | `--velocyto` mode | older: `--splice-unsplice-output` |
| **kallisto\|bustools** | `kb python lamanno` | 4 loom files (S/U/ambiguous/ambiguous2) |
| **alevin-fry / simpleaf** | `--usa` | unspliced/spliced/ambiguous |

Merge into the processed AnnData (with UMAP/clustering):
```python
import scvelo as scv
adata = scv.utils.merge(adata_processed, scv.read('velocyto.loom'))
```

---

## 2. Five-engine main entry (`ov.single.Velo`)

Source-checked ([omicverse/single/_velo.py](https://github.com/Starlitnightly/omicverse), 2026-07 master): `cal_velocity(method=...)` accepts 5 values.

| `method` | Backend | Innovation | Use case |
|---|---|---|---|
| `'scvelo'` | scVelo stochastic/dynamical | EM fits full kinetics (α,β,γ) | **default baseline**, routine 10x S/U |
| `'dynamo'` | dynamo.cell_velocities | vector-field reconstruction | with **4sU/SLAM metabolic labeling** (`new/total/label_time`) |
| `'latentvelo'` | LatentVelo (VAE/AnnotVAE) | latent-space VAE, can inject cell-type/batch priors | strong batch effects, needs type prior |
| `'graphvelo'` | GraphVelo | graph-convolution refinement (run scvelo/dynamo first, then refine) | multi-lineage, unstable direction |
| `'regvelo'` | RegVelo (REGVELOVI, scvi ecosystem) | GRN-prior-regularized + supports perturbation simulation | with a TF-target GRN, in-silico blockade |

```python
import omicverse as ov
v = ov.single.Velo(adata)
v.preprocess(recipe='monocle', n_neighbors=30, n_pcs=30)   # verified signature (scop-style)
v.cal_velocity(method='scvelo', n_top_genes=2000)          # NOTE: n_top_genes lives here, not in preprocess.
                                                            # omicverse default method='dynamo'; 'scvelo' is the recommended baseline.
# results: adata.layers['velocity'], adata.obsm['velocity_umap']
```

### RegVelo specifics (GRN regularization + perturbation simulation)

```python
v.prepare_regvelo(prior_grn=grn_df, regulators='is_tf')   # prior TF-target network
v.cal_velocity(method='regvelo')
v.regvelo_perturb(tf='FOXP3', effects=0, cutoff=0.001)    # in-silico TF blockade
v.cell_fate_perturbation(...)                              # fate-probability change
v.velocity_effect(...)                                     # cosine change of velocity direction
```

> RegVelo needs a prior GRN (stored in `adata.uns['skeleton']`); without a prior, fall back to `'scvelo'`/`'dynamo'`.

---

## 3. Downstream fate inference: CellRank 2 (strongly recommended, replaces scVelo's built-in PAGA)

**Why not scVelo's built-in terminal_states/PAGA**: it only accepts scVelo's own velocity, cannot fuse metabolic-labeling time, gives only hard assignments, and struggles past 50K cells.

**CellRank 2** strengths (Lange/Weiler 2024, *Nat Methods*): unified multi-kernel framework, probabilistic fate, scales to millions of cells, scverse-native.

### Four kernels

| Kernel | Input | Scenario |
|---|---|---|
| **VelocityKernel** | `layers['velocity']` (from any velocity algorithm) | default; absorbs scVelo/cellDancer/veloVI output |
| **PseudotimeKernel** | any pseudotime (DPT/Palantir/Monocle) | fallback when no S/U |
| **RealTimeKernel** ⭐ | experimental time points (4sU/SLAM multi-timepoint) via moscot OTP | metabolic-labeling real time |
| **CytoTRACEKernel** | CytoTRACE stemness score | stemness-driven fate |

### OmicVerse native integration (one line)

```python
v.cellrank_fate(cluster_key='celltype',
                terminal_states=['Beta','Alpha'],   # optional; auto-estimated otherwise
                n_states=8)
# result: adata.uns['velocity_cellrank'] (fate probabilities + macrostates + terminal states)
```

### Native CellRank 2 (multi-kernel combos, more flexible)

```python
import cellrank as cr
vk = cr.kernels.VelocityKernel(adata, xkey='Ms', vkey='velocity')
ck = cr.kernels.ConnectivityKernel(adata, conn_key='connectivities')
combined_kernel = 0.8 * vk + 0.2 * ck       # arbitrary linear combination
estimator = cr.estimators.GPCCA(combined_kernel)
estimator.compute_schur(); estimator.compute_macrostates(n_states=8)
estimator.set_terminal_states_from_macrostates(['Beta','Alpha'])
estimator.compute_fate_probabilities()
estimator.plot_fate_probabilities()         # probabilistic fate map (not hard clusters)
```

> veloVI output feeds VelocityKernel seamlessly; dynamo's `velocity_S` layer is likewise compatible; pyro-Velocity posterior samples can inject uncertainty.

---

## 4. Unwrapped algorithms → native fallback (honestly labeled)

> **Important fact**: omicverse `ov.single.Velo` does **NOT wrap** cellDancer / DeepVelo / pyro-Velocity / UniTVelo / veloVI / VeloVAE. Install each from PyPI independently, follow its official docs, then write the result into `layers['velocity']` and return to omicverse/cellrank for plotting.

| Algorithm | PyPI | When to use it (vs the 5 omicverse engines) |
|---|---|---|
| **cell2fate** | `cell2fate` | **Fully Bayesian, linearized velocity ODE; outputs velocity *modules* (co-regulated gene modules) for more robust fate prediction — Nat Methods 2025** ([s41592-025-02608-3](https://www.nature.com/articles/s41592-025-02608-3)); recommended when scVelo-stochastic directions look noisy |
| **cellDancer** | `celldancer` | **>50K large samples** (relay model scales to millions, single-cell-resolution rate) |
| **DeepVelo (GCN)** | source install | **multi-lineage / fate bifurcation** (Cui 2024 Genome Biol; graph convolution handles multiple directions) |
| **pyro-Velocity** | `pyrovelocity` | **quantify uncertainty** (Bayesian posterior gives velocity confidence intervals). The 17-study benchmark (Cell Rep Methods 2026) ranks pyro-Velocity(m2) + scVelo-stochastic as the most self-consistent pair (A²>0.7) |
| **veloVI** | `velovi` (scvi ecosystem) | scverse-native variational inference, transcriptome-level uncertainty |
| **UniTVelo** | `unitvelo` | auto-identifies switch genes, unified global time |
| **VeloVAE/FullTimeline** | `velovae` | continuous latent time, piecewise concatenation of the full developmental axis |

> **Benchmark consensus (Cell Reports Methods 2026, 17 datasets / 15 methods)**: **scVelo-stochastic is the most stable default** (highest self-consistency with pyro-Velocity, A²>0.7); pyro-Velocity for uncertainty quantification; cellDancer / UniTVelo cap around ~10k cells; pyro-Velocity scales to ~50k. cell2fate is the new Bayesian/modular direction. No single winner — run ≥2 engines and report consensus directions.

```python
# cellDancer fallback example (>50K cells)
import celldancer as cd
cd.tl.estimation_ucd(adata_cd, ...)             # native API (see its tutorial)
cd.tl.velocity_cell_dancer(adata_cd, n_jobs=8)
adata.layers['velocity'] = adata_cd.layers['velocity'].copy()  # write back
# then run cellrank_fate or scv.pl.velocity_embedding for plotting
```

---

## 5. When to fall back to native scVelo (deep tuning)

Fine-grained controls not exposed by `ov.single.Velo`:
- custom `fit_alpha/beta/gamma` priors, fixing parameters for specific genes
- `recover_dynamics(use_raw=False, fit_scaling=True)` combos
- custom PAGA edge weights `scv.tl.paga(groups=...)`
- direct manipulation of `layers['fit_t']`/`fit_alpha` for driver-gene ranking and phase portraits

```python
import scvelo as scv
scv.tl.recover_dynamics(adata, n_jobs=8, use_raw=False, fit_scaling=True)
scv.tl.velocity(adata, mode='dynamical')
scv.tl.velocity_graph(adata)
scv.tl.rank_velocity_genes(adata, groupby='leiden', min_corr=0.3)
```

---

## 6. Output keys cheat sheet (dynamical model)

| Location | Key | Meaning |
|---|---|---|
| `adata.layers` | `velocity` | velocity vector |
| `adata.obsm` | `velocity_umap` | UMAP-projected arrows |
| `adata.obs` | `latent_time` | latent time (dynamical only; **NOT real physical time**) |
| `adata.obs` | `velocity_length` / `velocity_confidence` | velocity magnitude / confidence |
| `adata.var` | `fit_likelihood` / `fit_alpha/beta/gamma` | fit quality / transcription·splicing·degradation rates |
| `adata.uns` | `velocity_graph` | cell transition-probability matrix |
| `adata.uns` | `velocity_cellrank` (injected by omicverse) | CellRank fate probabilities + terminal states |

---

## 7. Visualization (see `visualization/omicverse-plotting`)

```python
ov.pl.embedding(adata, basis='X_umap', color='leiden',
                velocity=True, arrow_length=3)             # flow arrows
ov.pl.embedding(adata, basis='X_umap', color='latent_time', cmap='gnuplot')
v.velocity_streamplot(basis='umap', velocity_key='velocity_S_umap')  # streamlines
```

---

## 8. Selection decision table (scenario → algorithm)

| Scenario | First choice | Second choice |
|---|---|---|
| Routine 10x S/U, exploratory | **`method='scvelo'`** | UniTVelo |
| With 4sU/SLAM metabolic labels | **`method='dynamo'`** | CellRank RealTimeKernel |
| Strong batch effects | **`method='latentvelo'`** (batch_key) | VeloVGI |
| Multi-lineage / fate bifurcation | `method='graphvelo'` or DeepVelo(GCN) | cellDancer |
| >50K large samples | **cellDancer** (fallback) | veloVI |
| Quantify uncertainty | **pyro-Velocity** (fallback) | veloVI |
| GRN + perturbation simulation | **`method='regvelo'`** | — |
| Downstream fate inference | **CellRank 2** (unified kernels) | scVelo PAGA |
| Run fast (exploratory) | scVelo stochastic | omicverse `'scvelo'` |

---

## 9. Best practices

- **Explore with stochastic first, then dynamical for the main figure**: dynamical takes ~10–30 min for 10K cells.
- **≥2000 cells**, otherwise velocity is noisy and arrows are messy.
- **Need good intron coverage**: reads <100 bp easily lose unspliced.
- **Arrows must match known biology**: random arrows usually mean wrong n_neighbors or shallow sequencing.
- **Sanity check**: root-cell markers should have high unspliced/spliced ratio.
- **Multi-method consensus > single-method conclusion**: any direction-sensitive claim ("X transitions to Y") should run ≥2 engines as cross-check.
- **Velocity ≠ real time**: unless calibrated by metabolic labels, latent_time is only for ordering, not duration inference.

## Decision aid: when to leave this skill

| Need | Go to |
|---|---|
| Pseudotime (no S/U needed) | `single-cell/omicverse-pipeline` → `ov.single.Monocle` |
| TF-target GRN construction (a regvelo prerequisite) | standalone pySCENIC / CellOracle / GRNBoost2 (NOT in scop 0.8.0 — install directly); or `single-cell/perturbation-prediction` Route B |
| Assemble a velocity figure for publication | `visualization/multi-panel-figures` |
| Use RegVelo perturbation simulation for prediction | `single-cell/perturbation-prediction` (if no GRN prior needed) |

## Prerequisites (where data comes from)

- **spliced/unspliced layers**: must exist (produced by velocyto / STARsolo / kallisto\|bustools lamanno / alevin-fry --usa)
- **Processed AnnData** (with UMAP/clustering) → from `single-cell/omicverse-pipeline`
- **`ov.pp.neighbors`** must run first — the moments step depends on the neighbor graph
- **≥2000 cells + good intron coverage** — otherwise arrows are noisy
- Metabolic-labeling data (4sU/SLAM) → `layers['new'/'total'/'label_time']`, use `method='dynamo'`

## Key pitfalls

- `ov.single.Velo` requires `ov.pp.neighbors` to exist first, otherwise the moments step errors.
- Only `mode='dynamical'` produces `latent_time`; stochastic gives only `velocity_pseudotime`.
- **omicverse does NOT wrap cellDancer/DeepVelo/pyro-Velocity** — do not look for these methods inside `ov.single.Velo`.
- After falling back to native, to use `ov.pl.embedding(velocity=True)` again, confirm `obsm['velocity_umap']` is written.
- When merging looms across samples, filter per sample first then merge — never stack directly (boundary-cell velocities are artefactual).
- RegVelo fails without a prior GRN; build one via `prepare_regvelo` first.
- **Interpretation discipline**: Marot-Lassauzaie 2023 already proved velocity is a neighborhood-smoothed trend — do NOT write in a paper "cell X is transitioning to state Y at rate V."

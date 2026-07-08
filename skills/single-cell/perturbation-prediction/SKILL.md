---
name: perturbation-prediction
description: 【预测未做实验的】单细胞扰动响应，含两条互补技术路线：① 算法扰动预测（ML-based：GEARS/CPA/scGPT/scGen，需 Perturb-seq 训练数据）；② 虚拟敲除（GRN-based：CellOracle/SCENIC+/scTenifoldKnk，仅需 WT scRNA-seq，通过 GRN 推断+信号传播模拟 KO）。当用户要预测未见扰动、in silico knockout、虚拟敲除、TF 功能筛查、扰动响应预测、unseen perturbation、药物响应预测时触发。
---

## When NOT to use this skill
- Perturbation experiment already done; only analyze measured results (differential perturbation response, Mixscape classification, guide QC) → `single-cell/perturb-seq`
- Just routine batch correction (not predicting new perturbations) → `single-cell/omicverse-pipeline` (Harmony/scVI)
- Plot prediction results / assemble a publication figure → finish prediction first, then `visualization/omicverse-plotting` → `visualization/multi-panel-figures`

# Single-Cell Perturbation Prediction — Two Complementary Routes

Predict the single-cell response of **unmeasured** perturbations (gene KO/OE, drug treatment). Two fundamentally different technical routes serve different input-data scenarios — pick by what data you have.

## ⚠️ First: choose the route by what data you have

```
Do you have Perturb-seq / CROP-seq training data (paired control-perturbation cells)?
│
├─ YES → Route A: ML-based perturbation prediction
│        (GEARS / CPA / scGPT / scGen — needs training perturbations)
│
└─ NO  → Route B: GRN-based virtual knockout
         (CellOracle / SCENIC+ / scTenifoldKnk — only needs WT scRNA-seq)
```

| Dimension | **Route A — ML-based** | **Route B — GRN-based virtual KO** |
|---|---|---|
| Training data | **Perturb-seq required** (paired control-perturbation) | **Only WT scRNA-seq** (+ optional scATAC) |
| Mechanism | Learn perturbation response pattern, generalize to unseen | Infer GRN → set TF=0 → iteratively propagate fold-change |
| Output | End-to-end post-perturbation expression vector | TF→target rewiring + cell-state shift + DRG ranking |
| Interpretability | Low (black-box NN) | High (every edge / regulon traceable) |
| Typical use | Drug response, gene essentiality, cross-cell-line prediction | TF function screen, cell-identity mechanism hypothesis, enhancer regulation |
| Multi-gene combinatorial KO | GEARS explicitly supports | Possible but limited accuracy |
| Accuracy (when Perturb-seq exists) | Theoretically higher, but empirically often ≤ linear baseline | Mechanistic approximation |
| Wrapper status | pertpy / omicverse | **Not wrapped** — install standalone |

---

# Route A — ML-based Perturbation Prediction

Based on [scPerturBench](https://github.com/bm2-lab/scPerturBench) (27 methods × 29 datasets, Nature Methods 2025) and the 2025 controversy literature.

## ⚠️ The 2025 DL-vs-linear-baseline controversy

**Nature Methods 2025 (Ahmed et al.) reported "DL models are no better than simple linear models for transcriptome-level perturbation prediction."** A bioRxiv reply (Replogle et al.) argued "DL is in fact better under correct evaluation." Conclusion not yet stable, therefore:
- **Always run a linear baseline as control** (scPerturBench `linearModel`)
- **Multi-metric evaluation** (MSE/PCC-delta/E-distance/Wasserstein/KL/Common-DEGs)
- **Declare evaluation setting** (i.i.d vs o.o.d, DEG definition) when reporting

## Two ML prediction scenarios

| Scenario | Task | Recommended method family |
|---|---|---|
| **Cellular-context generalization** | Known perturbation, predict in a new cell type / batch / cell line | scGen / trVAE / biolord / scDisInFact / scPRAM / CPA |
| **Perturbation generalization** | Known cell context, predict **unseen gene/drug** perturbations | GEARS / scGPT / GenePert / AttentionPert / chemCPA |

## Method selection (27 methods condensed to practical picks)

### 🧬 Genetic perturbation (CRISPR KO/OE)

| Method | Type | When | Install |
|---|---|---|---|
| **GEARS** | GO + co-expression graph GNN | **First choice for genetic perturbation**, Nature Biotech 2022; multi-gene combinatorial | `pip install cell-gears` (pertpy-wrapped) |
| **scGPT (perturbation)** | Foundation-model finetune | Large-scale / cross-dataset; **must use perturbation pretrained weights** | `pip install scgpt` + GPU |
| **GenePert** | GenePT embedding | 2024 new method, strong gene-semantic embedding | [zou-group/GenePert](https://github.com/zou-group/GenePert) |
| **AttentionPert** | Multi-scale attention | Multiplexed multi-gene perturbation | [BaiDing1234/AttentionPert](https://github.com/BaiDing1234/AttentionPert) |
| **linearModel** | Linear baseline | **Mandatory control**, often surprisingly strong | scPerturBench built-in |

### 💊 Chemical perturbation (drug / dose)

| Method | Type | When |
|---|---|---|
| **CPA** | Compositional-parsing VAE | **Workhorse for chemical perturbation**, Multi-bin Mol Syst Biol 2023 |
| **chemCPA** | CPA + chemical structure | Drug molecular-structure aware |
| **scVIDR** | Dose-response VAE | Dose-gradient prediction |
| **cycleCDR** | Cycle-consistent | Cross-cell-line drug response |

### 🔄 Cellular-context generalization

| Method | Type | When |
|---|---|---|
| **scGen** | Conditional VAE | **Entry-level first choice**, simple and stable, Nature Methods 2019 |
| **biolord** | Disentangled embedding | Strong cross-cell-line generalization |
| **scDisInFact** | Disentangled factors | Multi-batch multi-condition |
| **CellOT** | Neural optimal transport | Distribution-level modeling |
| **LEMUR** | Cluster-free multi-condition DE on Grassmann manifold | **Ahlmann-Eltze & Huber, Nat Genet 2025** ([s41588-024-01996-0](https://www.nature.com/articles/s41588-024-01996-0)); same lab as the Nat Methods 2025 linear-baseline paper; baseline-flavored, naturally extends to perturbation multi-condition comparison |

## ML route workflow

### Step 0: Data preparation
```python
# Standard Perturb-seq AnnData
adata.obs['perturbation']   # 'control' | 'geneA' | 'geneA+geneB'
adata.obs['dose']           # dose for chemical perturbation
adata.obs['cell_type']      # cell context (for o.o.d)
adata.obs['batch']
# Keep raw counts; ≥1000 cell/condition
```

### Step 1: Linear baseline first (mandatory control)
```python
# scPerturBench linearModel env — ~30 lines, CPU seconds
# Idea: control mean + a perturbation shift vector learned from training set
# If a DL model cannot beat this → do not publish the DL model
```

### Step 2: Pick DL method by scenario
```python
# Genetic perturbation (unseen gene) → GEARS
from gears import GEARS
gear = GEARS(adata, model_dir="./gears_model")
gear.model_initialize(); gear.train(seed=42)
pred = gear.predict_perturbation(["GeneX"])

# Chemical perturbation → CPA
import cpa
model = cpa.CPA(adata, covar_keys=['cell_type'], pert_key='perturbation',
                dose_key='dose', hidden_layers=[128, 128])
model.train(n_epochs=200); pred = model.predict(['DrugY'], dose=10.0)

# Cross-cell-context → scGen
import scgen
model = scgen.SCGEN(adata); model.train(max_epochs=100)
pred = model.predict_response(adata, ctrl_key='control', stim_key='IFN',
                              celltype_to_predict='CD4T')
```

### Step 3: Multi-metric evaluation (do not skip)
```python
# scPerturBench calPerformance — six complementary metrics, report all:
# MSE / PCC-delta / E-distance / Wasserstein / KL-divergence / Common-DEGs
# Distinguish i.i.d vs o.o.d; report DEG definition (e.g. |log2FC|>0.5 & Padj<0.05)
```

---

# Route B — GRN-based Virtual Knockout

Predict "what happens if gene X is knocked out" using **only WT scRNA-seq** (no Perturb-seq training needed). Infer a gene regulatory network, set the target gene's input to 0, and iteratively propagate the fold-change through the network.

## Common 5-step backbone (shared by CellOracle / SCENIC+)

```
Step 1  Infer GRN (TF → target edges)
Step 2  Train a regressor f_g(TF_1..TF_k) → expr_g for each target gene
Step 3  Apply virtual KO: set the knocked-out gene's expression (as TF) to 0
Step 4  Iteratively propagate fold-change (n_rounds ≈ 3):
          fc_g = f_g(TFs_with_X=0) / f_g(TFs_with_X=original)
          expr_g ← expr_g × fc_g
Step 5  Downstream: cell-state shift (UMAP displacement, transition probability)
        → can feed into CellRank 2 for fate mapping
```

## Three tools (pick by input richness)

### B.1 CellOracle — gold standard (recommends scATAC)

| Field | Value |
|---|---|
| Paper | **Kamimoto et al. 2023, *Nature* 614:742–751** |
| Install | `pip install celloracle` (v0.20.0) — **not wrapped in omicverse/pertpy** |
| GRN inference | Ridge / Bayesian Ridge regression with TF motif / scATAC prior |
| Input | WT scRNA-seq + TF→target prior (scATAC strongly recommended; built-in base GRN if no ATAC, lower accuracy) |
| Output | Per-cell in-silico KO expression matrix + cell-state shift vector + UMAP displacement + TF importance ranking |

```python
import celloracle as co
oracle = co.Oracle()
oracle.import_data(adata)               # WT AnnData
oracle.do_co_regression(... )           # GRN inference
oracle.simulate_shift(perturb_condition="TfX", n_propagation=3)
oracle.estimate_transition_prob(n_mul=50)
oracle.simulate_random_walks(n_steps=100)  # predict where cells go post-KO
```

### B.2 SCENIC+ — enhancer-level eGRN + built-in KO simulation

| Field | Value |
|---|---|
| Paper | **Bravo González-Blas et al. 2023, *Nature Methods* 20:1355–1367** |
| Install | `pip install scenicplus` (still alpha, API 1.0a1) — **not wrapped** |
| GRN inference | Gradient Boosting / RF regression + eRegulons (TF + targets + target enhancers) |
| Input | scRNA-seq + **scATAC-seq** (key for eGRN) + motif DB (cisTarget / pycistarget) |
| Output | Predicted KO fold-change per gene + perturbed expression matrix + regulon activity change |

> ⚠️ The KO API is **module-level functions in `scenicplus.simulation`**, NOT a method on the SCENIC+ object. The often-cited `scplus_obj.simulate_perturbation()` **does not exist**.

```python
from scenicplus.simulation import train_gene_expression_models, simulate_perturbation
# 1. Extract TF→target dict + expression matrix from scplus_obj eRegulons
gene_to_TF = {...}; df_EXP = scplus_obj.to_df(...)
# 2. Train per-gene GBM regressor
regressors = train_gene_expression_models(df_EXP, gene_to_TF,
    regressor_type="GBM",
    regressor_kwargs={"learning_rate":0.01,"n_estimators":500,"max_features":0.1})
# 3. Apply KO + iterate fold-change propagation
simulated = simulate_perturbation(df_EXP, gene_to_perturb="TF_OF_INTEREST",
    regressors=regressors, n_rounds=3)
```

### B.3 scTenifoldKnk — lightweight R screening (lowest barrier)

| Field | Value |
|---|---|
| Paper | **Osório, Zhong, Cai et al. 2022, *Patterns* 3(3):100456** (Cell Press) — note: not "Iaconis 2024" |
| Install | R: `install.packages("scTenifoldKnk")` |
| GRN inference | PCR + low-rank tensor / NMF + manifold alignment |
| Input | **Only WT scRNA-seq** (≥500 cells; no ATAC, no motif, no prior) |
| Output | **DRG ranking table** (differentially regulated genes post-KO) — does NOT output cell-state shift or expression matrix |

```r
library(scTenifoldKnk)
KO_mat <- scTenifoldKnk(WT_mat, KO = "GeneX")
# auto: delete GeneX → reconstruct GRN → manifold alignment → DRG ranking
```

## GRN-KO method selection

| You have... | First choice | Why |
|---|---|---|
| WT scRNA + scATAC | **CellOracle** | scATAC prior gives best TF→target resolution |
| WT scRNA + scATAC + want enhancer-level | **SCENIC+** | eRegulons include enhancers |
| Only WT scRNA, want quick screen | **scTenifoldKnk** (R) | Lowest barrier, but only DRG ranking (no cell-state shift) |
| Only WT scRNA, want full cell-state shift | **CellOracle** with built-in base GRN | Acceptable accuracy without ATAC |
| Want enhancer-level + Python-only | **SCENIC+** (RNA-only mode reduced) | Lower eGRN quality without ATAC |

## GRN-KO downstream (fate mapping)

The KO-induced transition probability / shift vector from CellOracle/SCENIC+ can feed into **CellRank 2** (`single-cell/rna-velocity` section 3 has `cellrank_fate`) for fate prediction — "after KO, where do cells go?". **RegVelo** (Wang 2026, theislab/regvelo) couples RNA velocity + GRN in a Bayesian deep generative model, a 2025-2026 GRN-KO trend.

## ⚠️ GRN-KO honest caveats

- **Not wrapped in pertpy/omicverse** — install CellOracle / SCENIC+ / scTenifoldKnk directly
- **Mechanistic approximation, not measurement** — predictions are hypotheses requiring wet-lab validation
- **GRN inference is the bottleneck** — garbage GRN in → garbage KO out; invest in ATAC prior when possible. **Multi-method GRN consensus strongly recommended** — run ≥2 (e.g. SCENIC+ + Pando / FigR for Multiome) and report overlap; CausalBench (Chevalley 2025, 97+ citations) and GRETA (Badia-i-Mompel 2024) showed GRN inference uncertainty is high, single-method GRNs are unreliable.
- **pySCENIC / GRNBoost2 (expression-only) are fallbacks in the Multiome era** — when ATAC is available, SCENIC+ / Pando / FigR give enhancer-level resolution; expression-only GRNs miss distal regulation. Use pySCENIC only as last-resort fallback and treat results with caution.
- **Multiome GRN alternatives to SCENIC+**: **Pando** (quadbio/Pando) and **FigR** (linear-model-based, fast) — both integrate RNA + ATAC for GRN inference. Domain consensus: SCENIC+ as primary, Pando/FigR as cross-validation.
- **No benchmark vs ML-based on shared datasets** — Gavriilidis 2024 (CSBJ) treats them as **complementary, not competing**; pick by data availability, not "accuracy ranking"

---

# Cross-route: when to use which (decision tree)

```
What do you want to predict?
│
├─ Have Perturb-seq training data?
│   ├─ YES → Route A (ML-based)
│   │   ├─ Unseen genetic perturbation → GEARS / scGPT-perturbation / GenePert
│   │   ├─ Unseen chemical → CPA / chemCPA / scVIDR
│   │   ├─ Known perturbation, new cell context → scGen / biolord / scDisInFact
│   │   └─ Always run linear baseline first (Nature Methods 2025)
│   │
│   └─ NO → Route B (GRN-based virtual KO)
│       ├─ Have scATAC → CellOracle (best) or SCENIC+ (enhancer-level)
│       ├─ WT scRNA only, want full shift → CellOracle with base GRN
│       └─ WT scRNA only, quick screen → scTenifoldKnk (R, DRG ranking)
│
└─ Both routes are hypotheses, not ground truth — wet-lab validation required
```

---

# Discipline (each item with its reason)

1. **Route A only — Always run the linear baseline**: scPerturBench proves simple models often beat DL; no baseline = unpublishable, meta-methodology principle ④.
2. **Route A only — Report evaluation setting**: i.i.d vs o.o.d, DEG definition, whether controls/perturbations are held out.
3. **Route A only — Multiple metrics**: a single MSE misleads; report at least PCC-delta + Common-DEGs + E-distance.
4. **Route A only — Rigorous hold-out**: training set must not contain the target perturbation.
5. **Route B only — GRN inference is the bottleneck**: invest in scATAC prior when possible; garbage GRN → garbage KO.
6. **Both routes — Conservative interpretation**: predictions are DEG trend / mechanism hypothesis, not absolute truth; in-vitro → in-vivo extrapolation needs extra validation.
7. **Both routes — Compute budget**: scGPT/GEARS/CPA finetune GPU 1-3h; CellOracle/SCENIC+ GBM training 10-60 min; scTenifoldKnk CPU minutes.
8. **Both routes — Data scale**: Route A needs ≥1000 cell/condition; Route B needs ≥500 cells for stable GRN.

## Prerequisites (where data comes from)

- **Route A (ML-based)**: standard Perturb-seq / CROP-seq AnnData with `obs['perturbation']` (includes `'control'` and known names; multiplexed with `+`), `obs['cell_type']`, `obs['batch']`; chemical perturbation needs `obs['dose']`. Raw counts preserved, ≥1000 cell/condition, GPU for DL finetune.
- **Route B (GRN-KO)**: WT scRNA-seq AnnData with at least basic preprocessing (QC, normalization, clustering); scATAC-seq strongly recommended for CellOracle/SCENIC+; motif database (cisTarget/pycistarget) for SCENIC+.

## When to leave this skill

- Perturbation experiment done; only analyze measured response → `single-cell/perturb-seq` (pertpy Mixscape / differential perturbation)
- Plot predictions / assemble figure → `visualization/omicverse-plotting` → `visualization/multi-panel-figures`
- Write Methods / Results → `presentation/methods-writer` / `presentation/results-writer`
- **Declare evaluation setting (Route A) or GRN quality (Route B) when reporting — scientific red line.** Conclusions can reverse under different settings (2025 Nature Methods); GRN-KO conclusions depend entirely on the input GRN quality.

## Key pitfalls

- **Route A — Always run linear baseline** (scPerturBench `linearModel`) — Nature Methods 2025 proves DL may not beat linear; no baseline = unpublishable, meta-methodology principle ④.
- **Route A — i.i.d vs o.o.d**: i.i.d (same perturbation in train/test split) trivially easy; o.o.d (unseen perturbation) is the real test — reporting only i.i.d = implicit cherry-picking.
- **Route A — Training-set leakage**: careless train/test split lets target perturbation info leak; "prediction" becomes "memorization."
- **Route A — DEG definition sensitivity**: top-K vs Padj<0.05 & |LFC|>1 can reverse conclusions; declare the DEG definition.
- **Route A — scGPT/Geneformer zero-shot perturbation is limited** (2025 Genome Biology evaluation) — do not trust zero-shot predictions.
- **Route B — Not wrapped in pertpy/omicverse**: install CellOracle/SCENIC+/scTenifoldKnk directly; do not look for them inside `ov.single.*` or `pt.tl.*`.
- **Route B — SCENIC+ KO is module-level functions** (`scenicplus.simulation.train_gene_expression_models` / `simulate_perturbation`), NOT a method on the SCENIC+ object — the often-cited `scplus_obj.simulate_perturbation()` does not exist.
- **Route B — scTenifoldKnk citation is Osório 2022 *Patterns*, not "Iaconis 2024"**.
- **Route B — No ATAC = lower GRN quality**: CellOracle/SCENIC+ without scATAC prior still run but TF→target resolution drops significantly.
- **Both routes — GPU required for DL**: scGPT/GEARS/CPA finetune infeasible on CPU; without GPU pick linear baseline (Route A) or scTenifoldKnk/CellOracle-base-GRN (Route B).
- **Both routes — n_replicates ≥3 per perturbation** (Route A) / ≥500 cells (Route B): otherwise training unstable / GRN noisy.

## Reference resources

- [scPerturBench (27-method benchmark)](https://github.com/bm2-lab/scPerturBench) + [Nature Methods 2025](https://www.nature.com/articles/s41592-025-02980-0)
- [pertpy (scverse unified API, Route A only)](https://pertpy.readthedocs.io/)
- [sc-best-practices perturbation modeling](https://www.sc-best-practices.org/conditions/perturbation_modeling.html)
- [OP3 NeurIPS 2024 benchmark](https://openproblems.bio/results/perturbation_prediction)
- [CellOracle docs](https://morris-lab.github.io/CellOracle.documentation/)
- [SCENIC+ KO tutorial](https://scenicplus.readthedocs.io/en/latest/Perturbation_simulation.html)
- [scTenifoldKnk](https://github.com/cailab-tamu/scTenifoldKnk)
- [Gavriilidis 2024 CSBJ review (Route A vs B as complementary)](https://doi.org/10.1016/j.csbj.2024.05.017)

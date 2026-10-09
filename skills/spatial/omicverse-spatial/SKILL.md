---
name: omicverse-spatial
description: 空间转录组全流程（IO→空间邻域→QC→空间域→SVG→通讯→可视化）基于 OmicVerse V2 统一 API，覆盖 Visium/Xenium/Nanostring 等常规分辨率平台（高分平台 Stereo-seq/Visium HD/MERFISH 走 spatial/multiomics）。一个 import omicverse as ov 完成 90% 常规空转分析。当用户要做空间转录组、空间 domain、SVG、空间通讯、空转可视化时触发。
---

> **派发子任务自守**：本 skill 若再向下派发任何执行子任务，先把 `references/dispatch_cheatsheet.md` 的相关硬规则（A-E）写进子任务 spec——子智能体看不到本会话上下文，没写进 spec 的规则等于不存在。

## When NOT to use this skill
- Spot/cell deconvolution (cell2location/RCTD/Tangram to estimate cell composition) → use `spatial/deconvolution` (`ov.space.Deconvolution` wraps 5 methods)
- High-resolution platforms (Stereo-seq / Slide-seq / Visium HD subcellular) + cellpose segmentation → use `spatial/multiomics`
- Spatial proteomics (CODEX/IMC/MIBI) → use `spatial/proteomics` (scimap, not spatial transcriptomics)
- Conventional single-cell (no spatial coordinates) → use `single-cell/omicverse-pipeline`

# OmicVerse Spatial Transcriptomics Pipeline

> **2026-10 前沿层**：空转选型/多样本统计/3D/FM 先读 `references/spatial_frontiers_2026.md`（§0 第一律：先查 2026 基准再选工具；§1 全管线裁决；§3 VIMA/TESSERA 统计教义）。本文件仍是常规平台执行体。

## 📋 Analysis Code Templates

All spatial analysis code templates live in `references/analysis/templates/spatial.md` (35+ ov.space API covered):

| 内容 | 关键 API |
|---|---|
| 数据 IO | sc.read_visium / ov.io.read_visium_hd/xenium/nanostring |
| QC + 预处理 | ov.pp.qc + ov.pp.preprocess(shiftlog\|pearson) |
| 空间 domain | pySTAGATE / CAST / GASTON / STT / cellcharter / merge_cluster |
| SVG | svg(PROST) / spatial_autocorr(Moran) / sepal |
| 去卷积 | Deconvolution / Tangram / CellLoc / CellMap / split_purify |
| 空间统计 | nhood_enrichment / co_occurrence / ripley / centrality_scores |
| Visium HD | bin2cell / salvage_secondary_labels |

**本文件只保留流程/决策指导；可执行代码一律以 references/analysis/templates/spatial.md 为权威。**

**Merged from former skills**: original preprocessing / data-io / domains / neighbors / statistics / visualization / communication / image-analysis (these standalone skills no longer exist; functionality unified in OmicVerse V2). **Deconvolution is NOT in this skill** — cell2location/RCTD etc. go to `spatial/deconvolution`. High-resolution platforms: see `spatial/multiomics`; spatial proteomics: see `spatial/proteomics`.

`pip install omicverse` (V2). Built on scanpy/squidpy/anndata.

> **Iteration reminder**: Run in batches; after each batch return to `research-planner` Phase R (Core Rule 8). Do not auto-run end-to-end.

> **Hypothesis ledger** (Core Rule 7): If you did NOT come from `research-planner`, create a mini `hypothesis_ledger.md` now (H1 + status:pending + unexpected-finding slot). Phase R R1 will update it.

## 0. Initialization

```python
import omicverse as ov
ov.plot_set()
```

## 1. Data IO (by platform)

> **Network reachability, tested tiers** (2026-07, restricted-network environment):
> | Source | Reachability | Usage |
> |---|---|---|
> | `sc.datasets.visium_sge(sample_id)` | ✅ stable | 10x official CDN; first choice for public Visium samples |
> | `sq.datasets.visium_hne_adata()` | ❌ 403 | squidpy self-hosted CDN; unreachable on restricted networks |
> | `ov.datasets.hg_forebrain_glutamatergic()` | ❌ fails | loom download error |
> | Local spaceranger output | ✅ most reliable | `squidpy.read_visium('dir/')` |
> | GEO direct link (h5ad) | ⚠️ network-dependent | `sc.read_h5ad()` |
>
> **Strategy**: prefer `sc.datasets.visium_sge`; on failure, manually download spaceranger output from GEO/10x and read with `sq.read_visium()`. Same for single-cell references — prefer local; when CDN is unreliable, fetch raw fastq/counts via GEOparse and process yourself.

> 代码模板：references/analysis/templates/setup.md（数据 IO 速查）与 templates/spatial.md「数据 IO」节。

| Platform | Function | Resolution |
|---|---|---|
| Visium | `sc.read_visium` | 55μm spot |
| Visium HD | `ov.io.read_visium_hd` | 2-8μm bin |
| Xenium | `ov.io.read_xenium` | subcellular |
| Nanostring | `ov.io.read_nanostring` | single-cell grade |

## 2. QC + preprocessing

> 代码模板：references/analysis/templates/spatial.md「空转 QC + 预处理」+ templates/sc_basic.md。
> 注意保留 `adata.layers['counts']`（去卷积必需）。

## 3. Spatial neighbor graph (core)

> 代码模板：references/analysis/templates/spatial.md「空间邻居图」。

> **API correction**: was previously written as `ov.pp.spatial_neighbors` — that does NOT exist. The correct location is **`ov.space.spatial_neighbors`** (verified; see `compat.yaml`). `ov.pp` only has `neighbors` (non-spatial).

（spatial_neighbors 必须先跑，见 Prerequisites）

## 4. Spatial domains / tissue regions

> **Verified in omicverse** (version in `compat.yaml`) — ov.space wraps these domain methods: `pySTAGATE` / `pySTAligner` / `pySpaceFlow` / `GASTON`. **BANKSY / BINARY / GraphST / MENDER / SpatialGlue are NOT wrapped in ov.space** — install each as a standalone package or use squidpy/BayesSpace equivalents.

> 代码模板：references/analysis/templates/spatial.md「空间 domain」。

**NOT wrapped in ov.space (install standalone)**:
- **BANKSY** (Nat Genet 2024, sharp boundaries): `pip install banksy` + [prabhakarlab/Banksy_py](https://github.com/prabhakarlab/Banksy_py)
- **BINARY** (self-supervised): standalone
- **GraphST** (large data): `pip install GraphST`
- **MENDER** (2024 Nat Commun, cell-type-aware, fast): standalone
- **SpatialGlue** (2024 Nat Methods, multi-omics): standalone
- **BayesSpace** (R): now wrapped in scop 0.8.9 as `RunBayesSpace`; or standalone `BayesSpace` package for low-level API

Decision: default STAGATE (wrapped); isoform-aware or continuous-depth domains → GASTON (wrapped); sharp boundaries → BANKSY (standalone); large samples → GraphST (standalone); cell-type-aware speed → MENDER (standalone); multi-omics → SpatialGlue (standalone).

> **2026 基准更新（SACCELERATOR, Nat Methods 2026-08, 22 法 × 15 数据集 × 170+ 样本）**：单方法定稿已不合规——①参数敏感性可超过方法间差异；②人工 GT 注释不适合做金标准；③扩展性：仅 5/22 能处理 46 万细胞级、仅 CellCharter 能吃 Visium HD 2μm。**新标准 = ≥2 方法共识聚类 + ARI 一致性 + 专家在环**（与 2025 基准"跑至少 2 方法"结论同向升级）。另：**域分割工具 ≠ niche 识别工具**（CosMx 基准 2026：多数默认配置恢复不了 niche 边界，需核心谱系加权）——niche 分析走"类型组合+邻域统计"路线，详见 `references/spatial_frontiers_2026.md` §1。

## 5. Spatially variable genes (SVG)

> 代码模板：references/analysis/templates/spatial.md「空间变异基因（SVG）」。

> **Windows + squidpy gotcha**: when using `squidpy.gr.spatial_autocorr`, `n_perms>=1` triggers multiprocessing that hangs under stdin/heredoc mode. **Write the script to a `.py` file** and run `python script.py`, wrapped in `if __name__=='__main__':`. Also `sq.pl.spatial_scatter(save='x.png')` writes to a `figures/` subdir, not the current dir. 10x Visium data often has duplicate var_names — first run `adata = adata[:, ~adata.var_names.duplicated()].copy()`.

## 6. Spatial cell-cell communication

> **API correction (see compat.yaml)**: `ov.space.COMMOT` 顶层 does **not** exist (only `_commot` private + `create_communication_anndata` helper) — but the wrapper **`ov.external.commot.pp/tl`** works end-to-end (fetal_heart 项目实测, ov 2.3.1): `ligand_receptor_database → filter_lr_database → spatial_communication`，结果在 `obsm['commot-CellChat-sum-sender'/'-receiver']`。也可用 **COMMOT standalone** 或 **squidpy.gr.nhood_enrichment / liana spatial mode**。

> 代码模板：references/analysis/templates/spatial.md「空间通讯」。

> **Spatial CCC ranking (2026 Genome Biology benchmark, 9 methods: CellPhoneDB v3/CellChat v2/SpaTalk/SpatialDM/COMMOT/SCOTIA/NicheDE/SpaCCI/CellNEST)**: ①方法间一致性低（多数指标 <0.42）——≥2 方法共识仍是底线；②**性能依赖数据分辨率：非空间先验工具（CellPhoneDB/CellChat 类）在成像平台（Xenium/CosMx/MERFISH）有系统风险**；③SpaCCI 综合最稳健；④COMMOT/SpatialDM 类空间专属方法在配体-受体共定位上更可靠。**选型规则：测序平台（Visium/Stereo-seq）→ COMMOT+LIANA 双报；成像平台 → 加 SpaCCI/SpatialDM（未装，装前见 `references/spatial_frontiers_2026.md` §7）**。较早的 bioRxiv 2026.05.19 SpatialCCCbench 结论同向（按场景选工具，无通用最优）。

## 7. Visualization (see visualization/figure-production)

> 代码模板：references/plotting_reference.md（plot_spatial/plot_umap 统一入口）。

H&E / IF image analysis: ov V2 integrates basic registration; complex registration (StarFusion/SpacesID) still possible via `squidpy.pl.spatial_scatter` + the `adata.uns['spatial']` image stack returned by `ov.io.read_*`.

## Prerequisites (where it comes from)

- **Raw spatial data** (spaceranger / star-solo / SAW output) → contains `adata.obsm['spatial']` coordinates + `uns['spatial']` H&E images
- **`layers['counts']` must be preserved** — SVG/deconvolution predecessors use raw counts
- **Spatial neighbor graph**: `ov.space.spatial_neighbors` (NOT `ov.pp.spatial_neighbors`) must run before spatial domains/SVG/communication — all spatial methods consume this graph.
- **High-resolution platforms** (Stereo-seq/Visium HD) → `spatial/multiomics` (cellpose segmentation)
- **Spot cell composition estimation** → `spatial/deconvolution`

## Decision quick-reference: when to leave this skill

| Need | Go to |
|---|---|
| After each analysis batch (domain detection/SVG/CCC/spatial mapping) — **before the next batch** | `single-cell/research-planner` **Phase R** (Review & Re-plan, Core Rule 8) — interpret results, discuss direction with researcher, revise plan |
| Spot/cell deconvolution (cell2location etc.) | `spatial/deconvolution` |
| Stereo-seq / high-resolution platform workflow | `spatial/multiomics` |
| Spatial proteomics (CODEX/IMC/MIBI) | `spatial/proteomics` |

## Key pitfalls

- **spatial_neighbors 必须先跑** — 见 Prerequisites（在 `ov.space`，不在 `ov.pp`）。
- Default n_neighbors differs by platform: Visium hex grid uses 6; Xenium/HD try 4-8.
- SVG uses Moran's I, threshold starts at 0.3; too strict misses weak-spatial-pattern genes.
- Before deconvolution, confirm `adata.layers['counts']` was not overwritten by normalization.
- Visium HD uses `read_visium_hd`; do not downgrade to `sc.read_visium` — bin metadata is lost.

---
name: perturbation
description: 扰动分析全流程——两条路径：(A) 实测 Perturb-seq 数据分析（Mixscape/pseudobulk DE/pertpy）；(B) 未测扰动的 in silico 预测（Arc State / GEARS/CPA/scGPT 或 GRN-based CellOracle/SCENIC+/scTenifoldKnk）。当用户要做 CRISPR screen 分析、perturbation prediction、gene KO 预测、扰动响应、药物响应预测、Mixscape、GEARS、CellOracle、State、虚拟细胞 (virtual cell) 时触发。
---

## When NOT to use this skill
- Only need a single-KO signature without screen design → `single-cell/omicverse-pipeline` (pseudobulk DE + enrichment)
- Perturbation via RNA-velocity in-silico blockade (RegVelo) → `single-cell/rna-velocity` (`v.regvelo_perturb`)
- GRN construction only (no perturbation readout) → standalone pySCENIC / GRNBoost2, or scop `RunSCENIC`/`RunGRNBoost2`/`RunscTenifoldKnk`
- R/Seurat environment → `single-cell/scop` (`RunSCENICPlus` / `RunscTenifoldKnk` for Path B)

> **Iteration reminder (Core Rule 8)**: This pipeline is run in batches. After each perturbation-analysis batch (e.g., Mixscape signature; or pseudobulk DE + enrichment), return to `research-planner` Phase R to review results with the researcher before the next batch. Do not auto-run end-to-end.

# Perturbation Analysis (Measured + Predicted)

**两条路径**（按数据可用性选）：
- **Path A: Measured**（有 Perturb-seq 实测数据）→ Mixscape → pseudobulk DE → pathway
- **Path B: Predicted**（只有 WT scRNA-seq，预测未见扰动效果）→ ML-based 或 GRN-based

---

## Path A: Measured Perturb-seq Analysis

**输入**：CRISPR Perturb-seq 数据（cells × genes + guide/perturbation 标注）

**流程**：
```
1. QC + guide assignment (pertpy / Mixscape)
2. Filter non-targeting controls
3. Pseudobulk DE per perturbation (PyDESeq2 via pertpy)
4. Perturbation signature (Mixscape.perturbation_signature)
5. Pathway enrichment (decoupler get_ora_df)
6. Visualization (volcano / heatmap / centroid embedding)
```

**关键代码**（pertpy 1.0+ API）：
```python
import pertpy as pt
# Pseudobulk + DE
pdata = pt.tl.PseudobulkSpace().compute(adata, target_col='target_gene', mode="sum")
# Filter tiny pseudobulks AFTER compute (no min_cells arg in pertpy 1.0):
pdata = pdata[pdata.obs_names.isin(
    adata.obs.groupby('target_gene').size()[lambda s: s >= 30].index)].copy()
de = pt.tl.PyDESeq2.compare_groups(pdata, column='target_gene',
    baseline='non-targeting', groups_to_compare=[...])
# Mixscape signature
ms = pt.tl.Mixscape()
ms.perturbation_signature(adata, pert_key='target_gene', control='non-targeting')
# Enrichment (decoupler, NOT pertpy's removed module)
import decoupler as dc
sig_genes = de[(de['adj_p_value']<0.05) & (de['log_fc'].abs()>0.5)]['variable'].tolist()
# get_ora_df expects the DE DataFrame (genes × FC/p-value), not a bare gene list;
# pass the DataFrame and restrict the foreground via mask=sig_genes.
# verify signature against installed decoupler version (meta §6)
ora = dc.get_ora_df(de, dc.get_resource('MSigDB'), mask=sig_genes,
    source='geneset', target='genesymbol')
```

**R/Seurat 路径**（scop 0.8.9 未包装 Mixscape，用 Seurat 原生）：
```r
# Mixscape via Seurat native (scop 0.8.9 does not wrap Mixscape as of this version)
srt <- RunMixscape(srt, ...)  # Seurat 原生，非 scop 包装
```

---

## Path B: Predicted Perturbation (in silico)

**输入**：WT scRNA-seq（无扰动数据），想预测某基因 KO 的效果

### B1: ML-based（需 Perturb-seq 训练数据）

| Tool | 适用 | 关键限制 |
|---|---|---|
| **Arc State** ⭐ | 跨细胞类型的 KO/药物/细胞因子 zero/few-shot 预测（训练 >100M cells，含 Tahoe-100M；Cell 2026） | **非商业 license**（学术可用须引用）；需 GPU；独立 CLI（`uv tool install arc-state`，不进 sc env）；**必须跑 linear baseline 对比** |
| **GEARS** | 组合扰动预测（双基因 KO） | 需 Perturb-seq 训练集 |
| **CPA** | 药物 + 基因扰动 | 需药物处理训练数据 |
| **scGPT** | 零样本泛化 | 需 GPU；**必须跑 linear baseline 对比**（Nat Methods 2025） |

```python
# Arc State 核心调用（完整示例代码：references/analysis/templates/sc_perturbation_state.md）
# Bash（GPU 机器，独立 uv 环境）：uv tool install arc-state
# ① 输入：normalize_total+log1p+HVG 存 adata.obsm['X_hvg']；要预测的扰动写 obs['target_gene']
# ② 推理：state tx infer --adata state_input.h5ad --pert-col target_gene \
#        --embed-key X_hvg --checkpoint <ckpt> --output pred.h5ad   (flags 先 --help 验证)
# ③ 下游：pred 读回 scanpy → Δ signature → decoupler 富集 → 出图
```

> **铁律：任何 ML 预测必须与 linear baseline 对比**。5 个 FM 在 perturbation prediction 上全输给 linear model（Ahlmann-Eltze et al. Nat Methods 2025）。只有明确优于 baseline 才用 FM 结果。State 是少数自带强 linear baseline 对比的新模型（Cell 2026），但铁律仍适用：用它 zeroshot/fewshot 留出集（有实测对照）验证后方可采信。

### B2: GRN-based（只需 WT scRNA-seq，无需训练）

| Tool | 机制 | 安装 |
|---|---|---|
| **CellOracle** | GRN → 模拟 KO → 向量场偏移 | `pip install celloracle`（Python） |
| **SCENIC+** | 多组学 GRN → eRegulon KO | scop `RunSCENICPlus` 或 `pip install scenicplus` |
| **scTenifoldKnk** | 随机网络 → KO 排序 | scop `RunscTenifoldKnk`（R） |

```python
# CellOracle: GRN → virtual KO
import celloracle as co
oracle = co.Oracle()
oracle.import_anndata_as_raw_count(adata, cluster_column='celltype')
oracle.import_TF_data(TF_info_matrix=grn)
oracle.perform_GRN_inference()
# Simulate KO
oracle.simulate_shift(perturb_condition={'GeneX': 0.0})
```

---

## 通用规则

- **DE 用 pseudobulk**（不用 per-cell Wilcoxon）
- **预测 ≠ 验证**：in silico 结果是假说，不是结论；写 "predicted" / "in silico"
- **baseline 对比必须**：ML 预测 vs linear model；GRN-KO vs random gene KO
- **pertpy 1.0 breaking changes**：`PseudobulkDE` → `PseudobulkSpace`；`pt.pl.*` 为空（用 model 自带 plot）
- **State 红线**：非商业 license（学术可用，论文必引 Adduri et al. Cell 2026）；checkpoint 版本+日期入 analysis_log；输出一律标 "State-predicted (in silico)"

## 工具

- `scripts/cns_style/ 包` — 出图美学
- `references/figure_guide.md` — 视觉规格
- pertpy 1.0+ / decoupler / CellOracle / scop 0.8.9 / arc-state CLI（uv tool，GPU）

## When to leave this skill (where to go)

- After perturbation analysis batch — **before downstream** → `single-cell/research-planner` **Phase R** (Review & Re-plan, Core Rule 8): interpret results, discuss with researcher, revise plan
- Plotting perturbation effects → `visualization/figure-production`
- Writing Methods/Results → `presentation/manuscript-writing`

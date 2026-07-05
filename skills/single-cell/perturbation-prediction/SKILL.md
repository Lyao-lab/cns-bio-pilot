---
name: perturbation-prediction
description: 预测单细胞基因/化学扰动的转录组响应（Perturb-seq/CROP-seq/药物处理）。Triggers on: 扰动预测、perturbation prediction、Perturb-seq、CROP-seq、gene knockout prediction、gene perturbation、knockout 预测、过表达预测、overexpression、化学扰动、chemical perturbation、药物响应预测、drug response prediction、unseen perturbation、未见扰动、GEARS、scGPT perturbation、CPA、scGen、scPreGAN、CellOT、scPRAM、biolord、scDisInFact、AttentionPert、GenePert、scPerturBench、in silico perturbation. Covers genetic (CRISPR KO/OE) and chemical (drug/dose) perturbation response prediction, cellular-context generalization (i.i.d/o.o.d) and unseen-perturbation generalization. When the user wants to predict how cells respond to a perturbation they have NOT experimentally tested, read this skill.
---

# 单细胞扰动响应预测（Perturbation Prediction）

预测**未做实验**的扰动（基因敲除/过表达、药物处理）会产生的单细胞转录组响应。基于 [scPerturBench](https://github.com/bm2-lab/scPerturBench)（27 法 × 29 数据集，Nature Methods 2025）和 2025 年争议文献的实证结论。

## ⚠️ 关键前置：DL 模型 vs 线性 baseline 的 2025 争议

在选算法前必须知道：**2025 年 Nature Methods（Ahmed et al.）报告"DL 模型在转录组级扰动预测上并不优于简单线性模型"**，随后 bioRxiv（Replogle 等）反驳称"DL 在正确评估下确实更优"。结论尚未稳定，因此：

- **不要盲信任何单一 DL 模型的论文宣称**
- **始终跑一个 linear baseline 作对照**（scPerturBench 的 `linearModel` 环境）
- **多指标评估**（MSE/PCC-delta/E-distance/Wasserstein/KL/Common-DEGs），单指标易误导
- 论文报告时**必须声明评估设置**（i.i.d 还是 o.o.d，DEG 定义）

参考：
- [Ahmed et al., Nature Methods 2025](https://www.nature.com/articles/s41592-025-02772-6)（DL 不胜线性）
- [bioRxiv 反驳 2025](https://www.biorxiv.org/content/10.1101/2025.10.20.683304v1)（DL 在正确评估下更优）
- [Bioinformatics 2025 简单对照超越 DL](https://academic.oup.com/bioinformatics/article/41/6/btaf317/8142305)

## 两大预测场景（决定方法选择）

| 场景 | 任务 | 推荐方法族 |
|---|---|---|
| **细胞情境泛化**（cellular-context generalization） | 已知扰动，在新细胞类型/批次/细胞系上预测 | scGen / trVAE / biolord / scDisInFact / scPRAM / CPA |
| **扰动泛化**（perturbation generalization） | 已知细胞情境，预测**未见过的基因/药物**扰动 | GEARS / scGPT / GenePert / AttentionPert / chemCPA |

每个场景还分 **i.i.d**（同分布测试）和 **o.o.d**（分布外测试）—— o.o.d 更难、更接近真实应用，报告时务必注明。

## 方法选型表（27 法精简为实战推荐）

### 🧬 基因扰动（genetic，CRISPR KO/OE）

| 方法 | 类型 | 何时用 | 安装 |
|---|---|---|---|
| **GEARS** | GO+共表达图 GNN | **基因扰动首选**，Nature Biotech 2022，多基因组合扰动 | `pip install cell-gears`（omicverse/scop 集成） |
| **scGPT (perturbation)** | 基础模型 finetune | 大规模/跨数据集；**必须用 perturbation 预训练权重** | `pip install scgpt` + GPU |
| **GenePert** | GenePT 嵌入 | 2024 新法，基因语义嵌入强 | [zou-group/GenePert](https://github.com/zou-group/GenePert) |
| **AttentionPert** | 多尺度注意力 | 多重基因扰动（multiplexed） | [BaiDing1234/AttentionPert](https://github.com/BaiDing1234/AttentionPert) |
| **linearModel** | 线性 baseline | **必跑对照**，常出乎意料地好 | scPerturBench 内置 |

### 💊 化学扰动（chemical，药物/剂量）

| 方法 | 类型 | 何时用 | 安装 |
|---|---|---|---|
| **CPA** | 组合解析 VAE | **化学扰动主力**，Multi-bin Mol Syst Biol 2023 | `pip install cpa-tools`（omicverse/scop 集成） |
| **chemCPA** | CPA + 化学结构 | 药物分子结构感知 | [theislab/chemCPA](https://github.com/theislab/chemCPA) |
| **scVIDR** | 剂量响应 VAE | 剂量梯度预测 | [BhattacharyaLab/scVIDR](https://github.com/BhattacharyaLab/scVIDR) |
| **cycleCDR** | 循环一致 | 跨细胞系药物响应 | scPerturBench 内 |

### 🔄 细胞情境泛化（已知扰动，新细胞情境）

| 方法 | 类型 | 何时用 |
|---|---|---|
| **scGen** | Conditional VAE | **入门首选**，简单稳定，Nature Methods 2019 |
| **trVAE** | Transfer VAE | o.o.d 跨批次 |
| **biolord** | 解析嵌入 | 跨细胞系泛化强（+ bioLord-emCell 增强版） |
| **scDisInFact** | 解析因子 | 多批次多条件 |
| **scPRAM** | 注意力机制 | Bioinformatics 2024 |
| **scPreGAN** | GAN | 早期方法，偶用 |
| **CellOT** | 神经最优传输 | 分布级建模 |

### 🛠 一站式基准（强烈推荐先跑）

| 资源 | 用途 |
|---|---|
| [**scPerturBench**](https://github.com/bm2-lab/scPerturBench) ⭐91 | 27 法统一接口 + 9 conda 环境 + Podman 镜像（40GB，含全部依赖）+ [结果可视化网站](https://bm2-lab.github.io/scPerturBench-reproducibility/) |
| **pertpy**（scverse） | scRNA 扰动分析统一 API（omicverse 集成），含 GEARS/CPA/scGen wrapper |
| [**OP3**](https://openproblems.bio/results/perturbation_prediction)（NeurIPS 2024） | 活基准，化学扰动 Kaggle 竞赛方法 |

## 推荐工作流

### Step 0: 数据准备

```python
# Perturb-seq / CROP-seq 标准 AnnData
import scanpy as sc
adata = sc.read_h5ad("perturb_seq.h5ad")
# 关键字段：
#   adata.obs['perturbation']   # 'control' | 'geneA' | 'geneA+geneB'（多重）
#   adata.obs['dose']           # 化学扰动的剂量（药物用）
#   adata.obs['cell_type']      # 细胞情境（o.o.d 评估用）
#   adata.obs['batch']          # 批次
# 质控同常规 scRNA-seq（见 omicverse-pipeline），保留 raw counts
```

### Step 1: 先跑 linear baseline（强制对照）

```python
# scPerturBench 的 linearModel 环境
# 思路：对每个 DEG，用 control 均值 + 训练集学到的扰动位移向量
# 30 行代码，CPU 秒级完成
# 如果 DL 模型打不过它 → 不要发 DL 模型
```

### Step 2: 按场景选 DL 方法

```python
# === 基因扰动（未见基因）→ GEARS ===
from gears import GEARS
gear = GEARS(adata, model_dir="./gears_model")
gear.model_initialize()        # 构建 GO + 共表达图
gear.train(seed=42)            # GPU 推荐
pred = gear.predict_perturbation(["GeneX"])  # 预测未做的 KO

# === 化学扰动 → CPA ===
import cpa
model = cpa.CPA(adata,
                covar_keys=['cell_type'],
                pert_key='perturbation',     # 药物名
                dose_key='dose',
                hidden_layers=[128, 128])
model.train(n_epochs=200)
pred = model.predict(['DrugY'], dose=10.0)

# === 跨细胞情境 → scGen ===
import scgen
model = scgen.SCGEN(adata)
model.train(max_epochs=100)
pred = model.predict_response(adata, ctrl_key='control', stim_key='IFN',
                              celltype_to_predict='CD4T')  # 新细胞类型
```

### Step 3: 多指标评估（不可省）

```python
# scPerturBench 的 calPerformance（pertpyV7 环境）
# 6 个互补指标，全部报告：
# - MSE：均方误差（绝对值，依赖归一化）
# - PCC-delta：位移的 Pearson 相关（方向性）
# - E-distance：能量距离（分布级）
# - Wasserstein：分布位移
# - KL-divergence：分布差异
# - Common-DEGs：预测与真实 top-DEG 的重叠（生物学最相关）
# 评估时区分 i.i.d / o.o.d，并报告 DEG 定义（如 |log2FC|>0.5 & Padj<0.05）
```

## omicverse / scop / pertpy 集成

```python
# omicverse（轻量调用）
import omicverse as ov
# ov 单细胞流水线预处理后，扰动分析走 pertpy
# ov.fm.scgpt 提供 zero-shot embedding（非 finetune）

# pertpy（scverse 统一 API，强烈推荐）
import pertpy as pt
pt.tl.GEARS(adata)          # wrapper
pt.tl.CPA(adata)            # wrapper
pt.tl.Scgen(adata)          # wrapper
pt.tl.BulkTrajVCI(adata)    # 评估工具

# scop（R）
srt <- RunscFEA(srt)        # 代谢通量扰动
srt <- RunscTenifoldKnk(srt)  # 基因模块 knockout 模拟
```

## 决策树

```
要预测什么？
│
├─ 已知扰动，新细胞情境（药物跨细胞系/批次）
│   ├─ 先 scGen（简单稳定）
│   ├─ 跨细胞系泛化差 → biolord + bioLord-emCell（先验增强）
│   └─ 多批次 → scDisInFact
│
├─ 未见基因扰动（没敲过的基因）
│   ├─ 单/双基因 → GEARS（图神经网络，GO 先验）
│   ├─ 大规模/跨数据集 → scGPT perturbation（GPU 必须，用 perturbation 权重）
│   ├─ 多重扰动（multiplexed）→ AttentionPert
│   └─ 2024 新法 → GenePert（GenePT 嵌入）
│
├─ 未见化学扰动（没测过的药物）
│   ├─ 主力 → CPA（组合解析）
│   ├─ 药物结构重要 → chemCPA
│   └─ 剂量梯度 → scVIDR
│
└─ 分布级建模（不只均值）
    └─ CellOT（神经最优传输）/ SCREEN
```

## Discipline（强制）

1. **必跑 linear baseline**：scPerturBench 证明简单模型常超 DL；不报告 baseline = 不可发表
2. **报告评估设置**：i.i.d vs o.o.d，DEG 定义，是否 held-out 控制/扰动
3. **多指标**：单一 MSE 会误导（均值预测常胜但失去异质性）；至少报 PCC-delta + Common-DEGs + E-distance
4. **Held-out 严谨**：训练集不能含目标扰动；NON-targeting/control 不能同时进 train 和 test
5. **保守解读**：预测的是 DEG 趋势，不是绝对表达；体外 → 体内推断需额外验证
6. **算力预算**：scGPT finetune GPU 1-3h；GEARS CPU 可跑但慢；CPA GPU 推荐；先小子集验证流程
7. **数据规模**：扰动预测需足够 control + 已知扰动；<1000 cell/条件时所有方法都不稳

## 何时不用这个 skill

- 已做了扰动实验，只需分析结果 → 用 `single-cell/perturb-seq`（pertpy 的下游分析：差异扰动响应、扰动一致性等）
- 想做基因必需性/功能 → `scTenifold`（在 scop 里：`RunscTenifoldKnk`/`RunscTenifoldNet`）
- 常规批次校正（不是预测新扰动）→ `omicverse-pipeline` 的 Harmony/scVI

## 参考资源

- [scPerturBench（27 法基准）](https://github.com/bm2-lab/scPerturBench) + [Nature Methods 2025](https://www.nature.com/articles/s41592-025-02980-0)
- [pertpy（scverse 统一 API）](https://pertpy.readthedocs.io/)
- [sc-best-practices 扰动建模](https://www.sc-best-practices.org/conditions/perturbation_modeling.html)
- [OP3 NeurIPS 2024 基准](https://openproblems.bio/results/perturbation_prediction)
- [方法清单汇总（xianglin226）](https://github.com/xianglin226/Benchmarking-Single-Cell-Perturbation)

## 前置依赖（从哪来）

- **Perturb-seq / CROP-seq 标准 `AnnData`** → `single-cell/perturb-seq`（实验数据读入+QC）或直接从 `single-cell/omicverse-pipeline` 预处理后传入
- **必需 obs 列**：`adata.obs['perturbation']`（含 `'control'` 与已知扰动名，多重扰动用 `+` 连接）、`adata.obs['cell_type']`（o.o.d 评估）、`adata.obs['batch']`、化学扰动还需 `adata.obs['dose']`
- **raw counts** 保留（`layers['counts']`），覆盖 ≥1000 cell/条件，且训练集含足够 control + 已知扰动
- **GPU 环境**（scGPT finetune / CPA 推荐）：CUDA + 对应模型权重

## 何时离开本 skill（去哪）

- 已做实验、只分析实测扰动响应（差异扰动、扰动一致性）→ `single-cell/perturb-seq`（pertpy 下游分析）
- 基因必需性 / 功能模块模拟 → `single-cell/scop`（`RunscTenifoldKnk`/`RunscTenifoldNet`）
- 常规批次校正（非预测新扰动）→ `single-cell/omicverse-pipeline`（Harmony/scVI）
- 预测结果可视化 / 组合 figure → `visualization/omicverse-plotting` → `visualization/multi-panel-figures`
- 写 Methods / Results → `presentation/methods-writer` / `presentation/results-writer`
- 🚨 报告时必须声明评估设置（i.i.d vs o.o.d、DEG 定义、是否含 linear baseline 对照）

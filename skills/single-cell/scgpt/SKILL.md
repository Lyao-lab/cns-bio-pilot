---
name: scgpt-foundation-model
description: Use scGPT (bowang-lab/scGPT, Nature Methods 2024) foundation model for single-cell tasks. Triggers on: scGPT、scgpt、基础模型、foundation model、预训练模型、零样本注释、zero-shot annotation、参考映射、reference mapping、细胞注释、cell type annotation、批次整合、多组学整合、multi-omics integration、扰动预测、perturbation prediction、Perturb-seq 预测、基因调控网络、GRN inference、scGPT finetuning、cell embedding、scGPT embedding. Covers cell-type annotation (zero-shot + finetune), reference mapping + label transfer, multi-batch/multi-omic integration, perturbation response prediction (Perturb-seq), attention-based GRN inference, and cell embeddings. When the user wants deep-learning foundation-model analysis of single-cell data (especially cross-dataset/cross-species annotation or perturbation prediction), read this skill.
---

# scGPT — Single-Cell Foundation Model

`scGPT` ([bowang-lab/scGPT](https://github.com/bowang-lab/scGPT), v0.2.5, MIT) is a generative pretrained transformer for single-cell biology, trained on **33M+ cells**. Published in *Nature Methods* 2024 (PMID: [38409223](https://pubmed.ncbi.nlm.nih.gov/38409223/)). Use this when conventional methods (Harmony/scVI/CellTypist) underperform, or for **cross-dataset/cross-species annotation** and **perturbation prediction**.

> **omicverse 集成**：基础调用可走 `ov.fm.scgpt`（封装）。本 skill 聚焦 scGPT 原生 API 的 **finetuning 工作流**（注释/整合/扰动/GRN），需要深度调参或多组学场景时用原生包。

## Installation

```bash
# Python 3.7–3.11（torch + scanpy + scvi-tools 全家桶，建议独立环境）
conda create -n scgpt python=3.10 -y && conda activate scgpt
pip install scgpt                       # 或源码：pip install git+https://github.com/bowang-lab/scGPT.git
# GPU 强烈推荐（finetuning 慢），CPU 仅适合 zero-shot 推理
```

核心依赖：`torch>=1.13`、`scanpy>=1.9`、`scvi-tools>=0.16`、`datasets>=2.20`、`cell-gears<0.0.3`（扰动）、`scib>=1.0.3`（整合评估）。

## Pre-trained Models

| 模型 | 用途 | 何时用 |
|---|---|---|
| **human brain + bone marrow**（默认） | 通用人类 | 注释/整合/GRN 默认 |
| **whole-human**（MS 预训练） | 大规模 | 跨组织/跨数据集 |
| **perturbation**（CellWiki/Perturb-seq） | 扰动预测 | **Perturb-seq 必须用这个** |

```python
# 下载模型权重（HuggingFace mirror 也可）
from scgpt.utils import download_from_zenodo
model_dir = download_from_zenodo("whole-human")   # 或 "human_brain", "perturbation"
```

## Common Workflow Skeleton

所有任务共享的骨架：

```python
import scanpy as sc
import torch
from scipy.sparse import issparse
from scgpt.model import TransformerModel
from scgpt.tokenizer import tokenize_and_pad_batch
from scgpt.preprocess import preprocess as P

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. 读数据 + 预处理（HVG 对齐到模型的 gene vocab）
adata = sc.read_h5ad("data.h5ad")
adata.var["gene_name"] = adata.var_names
P.preprocess_adata(adata, min_expressed_genes=1, target_sum=1e4, n_hvg=2000)
# 2. 加载 gene vocab + 模型
from scgpt.tokenizer.gene_tokenizer import GeneVocab
vocab = GeneVocab.from_file(f"{model_dir}/vocab.json")
model = TransformerModel.from_pretrained(model_dir, vocab=vocab).to(device)
# 3. tokenize（gene id + expression value）
input_ids, values = tokenize_and_pad_batch(
    adata, vocab, pad_token="<pad>", max_length=1200, append_cls=True
)
# 4. get embeddings / finetune（见各任务节）
```

## Task 1: Cell-Type Annotation（零样本 + Finetune）

**推荐：reference mapping**（query→reference 嵌入空间最近邻 + 标签迁移），比从零 finetune 快。

```python
# Tutorial_Reference_Mapping.ipynb 精华
from scgpt.tasks import CellAnnotation
from scgpt.utils import map_raw_embed_to_cluster

# build atlas
ref_embeds = model.encode(ref_adata, batch_size=64)        # reference embeddings
query_embeds = model.encode(query_adata, batch_size=64)
# KNN transfer
predicted_labels, conf = CellAnnotation.transfer_labels_knn(
    ref_embeds, query_embeds,
    ref_labels=ref_adata.obs["cell_type"],
    n_neighbors=15,
)
query_adata.obs["scgpt_pred"] = predicted_labels
query_adata.obs["scgpt_conf"] = conf
# Finetune 版（数据量大或精度要求高时）：见 Tutorial_Annotation.ipynb
# 关键超参：LR=1e-4（cls head 高 5×），epochs=10，NLoss=ce + class_weight
```

评估：`scib.metrics` 的 ARI/NMI，或 `CellAnnotation.evaluate`。

## Task 2: Multi-Batch / Multi-Omic Integration

```python
# Tutorial_Integration.ipynb / Tutorial_Multiomics.ipynb
from scgpt.tasks import IntegrationTask
# finetune：input=batch_id + modality_id，重建 gene expression
task = IntegrationTask(model, vocab, device,
                       batch_key="batch", integrate=True,
                       n_epochs=10, lr=1e-4, mask_ratio=0.15)
embeds = task.train_and_embed(adata, batch_size=64)
adata.obsm["X_scgpt"] = embeds
# 评估（scib benchmark）
from scib_metrics import bench
bench(adata, batch_key="batch", label_key="cell_type", embed="X_scgpt")
```

## Task 3: Perturbation Prediction（Perturb-seq）

**必须用 perturbation 预训练模型**，配合 `cell-gears` 做 GEARS-style 预测。

```python
# Tutorial_Perturbation.ipynb
from scgpt.tasks import PerturbationTask
model = TransformerModel.from_pretrained(pert_model_dir, vocab=vocab).to(device)
task = PerturbationTask(model, vocab, device)
# finetune on Perturb-seq（control + perturbed）
task.finetune(adata, pert_key="perturbation", n_epochs=20, lr=1e-4,
              held_out_genes=["ctrl"], held_out_perts=["NON-targeting"])
# predict unseen perturbation
pred_adata = task.predict(perturbation=("geneA", "+1"))   # 过表达
# 评估：DEG 上的 Pearson/Spearman + regulation direction accuracy
```

社区要点（[Discussion #121](https://github.com/bowang-lab/scGPT/discussions/121)）：human pre-trained 是扰动任务默认；held-out 设计要避免数据泄露。

## Task 4: Gene Regulatory Network（Attention-based）

```python
# Tutorial_Attention_GRN.ipynb / Tutorial_GRN.ipynb
from scgpt.tasks import GrnTask
task = GrnTask(model, vocab, device)
# 提取 attention matrix → TF-target 重要性
attn = task.extract_attention(adata, batch_size=64)
# attn[gene_i, gene_j] = gene_i 对 gene_j 的调控强度（近似）
grn_edges = task.build_grn(attn, top_k=20, tf_list="human_tf_db")
# 评估：与 ChIP-seq / SCENIC 的 Precision/Recall
```

## Task 5: Cell Embeddings（下游复用）

```python
# 最轻量用法：把 scGPT embedding 当通用特征
embeds = model.encode(adata, batch_size=64)
adata.obsm["X_scgpt"] = embeds
sc.pp.neighbors(adata, use_rep="X_scgpt")
sc.tl.umap(adata)
# 之后可走 omicverse/scop 的常规流程（聚类/注释/通讯）
```

## 何时用 scGPT（决策表）

| 场景 | 推荐 |
|---|---|
| 常规同组织注释（CellTypist/SingleR 够用） | 不用 scGPT |
| **跨数据集/跨物种/罕见细胞类型**注释 | **scGPT reference mapping** |
| 常规批次校正（Harmony/scVI 够用） | 不用 scGPT |
| **极度复杂批次**（组织+平台+物种混叠） | scGPT integration（GPU 必须） |
| 常规拟时序/通讯 | 不用 scGPT |
| **Perturb-seq 扰动预测**（未做的实验） | **scGPT perturbation**（scGPT 独有优势） |
| **TF-target GRN**（attention 可解释） | scGPT GRN（或 SCENIC） |
| 想要通用 cell embedding 喂下游 | scGPT embedding（一次 encode，复用） |

## Discipline（贯穿所有任务）

1. **GPU 强制**：finetuning 在 CPU 不可行；推理可 CPU 但慢 10–50×。
2. **Gene vocab 对齐**：query 必须能映射到模型 gene vocab；不在 vocab 的基因被丢弃 → 报告覆盖率（建议 >80%）。
3. **HVG 一致**：reference 与 query 用相同 HVG 集合，否则 embedding 不对齐。
4. **批次效应 vs 生物学**：integration 后用 `scib` 评估 batch removal（高）+ label 保留（高），警惕过校正。
5. **扰动预测**：held-out 设计要严格（控制 + NON-targeting 不能进 train）；预测的是 DEG 趋势，不是绝对表达。
6. **零样本 ≠ 万能**：跨组织/物种零样本注释置信度低，需 marker 验证（不能盲信）。
7. **算力成本**：finetune 一个 10 万细胞数据集 GPU 约 1–3 小时；提前在小子集验证流程。

## omicverse 互补

- 简单调用：`ov.fm.scgpt`（封装 zero-shot embedding + 注释），适合快速尝试。
- 本 skill（原生 scGPT）：finetuning / 多组学 / 扰动 / GRN，需要完整控制时用。
- 预训练模型与 gene vocab 两边共享，可混用（omicverse 预处理 → scGPT encode → omicverse 下游）。

## 参考资源

- 论文：[Cui et al., Nature Methods 2024](https://www.nature.com/articles/s41592-024-02201-0)
- 文档：[scgpt.readthedocs.io](https://scgpt.readthedocs.io/)
- Tutorials（7 个官方 notebook）：Annotation / Reference_Mapping / Integration / Multiomics / Perturbation / GRN / Attention_GRN
- 模型卡：[CZI Virtual Cells](https://virtualcellmodels.cziscience.com/model/scgpt)

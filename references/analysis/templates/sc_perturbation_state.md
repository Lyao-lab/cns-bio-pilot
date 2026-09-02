# Arc State：in silico 扰动响应预测（虚拟细胞）

> **本文件 = 可执行代码模板层**（怎么调 State，照抄并按数据改造）。方法选型与"为什么"见知识层：[`../decision_guide.md`](../decision_guide.md) §4；两条路径总览与铁律见 `skills/single-cell/perturbation/SKILL.md`。
> State = Arc Institute 虚拟细胞模型（Adduri et al., Cell 2026）：**ST**（State Transition transformer，预测扰动后表达谱）+ **SE**（State Embedding，细胞嵌入/相似检索）。训练覆盖遗传扰动（Perturb-seq）/ 药物（Tahoe-100M）/ 细胞因子。
> 独立 CLI（PyTorch，`uv tool install arc-state`），**不装进 conda sc env**；版本以 compat.yaml `arc-state` 为准。⚠️ CLI flags 以 `state --help` 实测为准（Core Rule 6）——本模板按官方 README 核对于 2026-09-02。

## 三条红线（先读再跑）

1. **非商业 license**：代码 CC BY-NC-SA 4.0；权重 = Arc Non-Commercial License。学术可用，**论文/报告必须引用 State**；checkpoint 版本 + 获取日期写入 analysis_log（meta §8b）。
2. **预测 ≠ 验证**：输出一律写 "State-predicted / in silico"；纯 WT 输入（无实测扰动对照）只能产假说，谈不上"准不准"。
3. **必须 vs linear baseline**：State 结果只有在其 zeroshot/fewshot 留出集（有实测扰动对照）上明确优于 linear baseline 才可进正文（Ahlmann-Eltze et al., Nat Methods 2025；baseline 代码见 §4）。

## §0 环境准备（GPU 机器：Linux/WSL2/服务器）

```bash
# Python 3.11–3.12（<3.13）；uv tool 独立环境；长任务 tmux 分离（远程任务防断规则）
uv tool install arc-state                 # compat.yaml 记录：0.11.1（PyPI 2026-06-29）
state --help && state tx --help           # ⚠️ 先验 flags 再跑
nvidia-smi                                # 推理单卡可跑；训练参考官方多卡配置
# checkpoint：HuggingFace arcinstitute org（SE-600M 已验证存在；ST checkpoint 以官方
#   README / Colab「Tahoe-100M 推理」当前指向为准，下载后记录版本+日期）
```

## §1 Zero-shot 推理：WT 数据 + 公开 checkpoint → 预测未见扰动

### 1a 输入 AnnData 准备

```python
# State 期望输入：normalize_total → log1p → HVG 表达存 adata.obsm['X_hvg']
# （key 必须与 checkpoint 训练时的 embed_key 一致；官方也有自带预处理入口，state tx --help 查）
import scanpy as sc
adata = sc.read_h5ad('wt.h5ad')                      # 原始 counts
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
adata.obsm['X_hvg'] = adata[:, adata.var['highly_variable']].X.copy()
adata.write('state_input.h5ad')
# ⚠️ gene 用官方 symbol；物种与基因 panel 要和 checkpoint 训练分布对齐（先读模型卡）
# ⚠️ 要预测哪些扰动，写进 obs['target_gene'] 列（列名与 --pert-col 一致）
```

### 1b 推理（CLI）

```bash
state tx infer \
  --model-dir <model_dir> --checkpoint <final.ckpt> \
  --adata state_input.h5ad \
  --pert-col target_gene \
  --embed-key X_hvg \
  --output state_pred.h5ad          # 换成 .npy 则只输出预测矩阵
# ⚠️ 各 flag 真实拼写先 `state tx infer --help` 验证再跑
```

### 1c 下游读回 scanpy（Δ signature + 富集）

```python
import pandas as pd, scanpy as sc
pred = sc.read_h5ad('state_pred.h5ad')               # 预测的扰动后表达谱
ctrl = adata[pred.obs_names]                          # 同批 control（或 non-targeting 子集）
genes = pred.var_names
delta = pd.DataFrame(pred[:, genes].X - ctrl[:, genes].X,
                     index=pred.obs_names, columns=genes)
top = delta.mean(0).abs().sort_values(ascending=False).head(50)   # 预测 Δ 最大的基因
# Δ 供富集：decoupler get_ora_df / ov.bulk.geneset_enrichment（代码见 templates/sc_annotation.md）
# Δ 可视化：volcano/heatmap → cns_style（visualization/figure-production）
# ⚠️ 措辞：'State-predicted (in silico)'，禁写 'KO 导致/induces'
```

## §2 Few-shot 微调：有自己的 Perturb-seq 训练数据

```bash
# TOML 划分配置（repo examples/）：zeroshot.toml = 整 cell type 留出；fewshot.toml = cell type 内留出扰动
state tx train data.kwargs.toml_config_path=examples/fewshot.toml \
  data.kwargs.embed_key=X_hvg data.kwargs.pert_col=target_gene \
  data.kwargs.cell_type_key=cell_type \
  training.max_steps=40000 training.batch_size=8 model=state \
  output_dir="$HOME/state" name="my_perturb"
state tx predict --output-dir $HOME/state/my_perturb --checkpoint final.ckpt   # cell-eval 指标
# ⚠️ 官方示例多卡训练：先小 max_steps 冒烟跑通，再上全量；tmux 分离，别前台等
```

## §3 SE 嵌入 + 相似细胞检索（可选）

```bash
state emb transform --model-folder <SE-600M_dir> --checkpoint se600m_epoch15.ckpt \
  --input query.h5ad --output embedded.h5ad          # 细胞嵌入写入 h5ad
uv tool install 'arc-state[vectordb]'                 # LanceDB 可选 extra
state emb transform --lancedb <db_dir> ...            # 建库（详见 state emb --help）
state emb query --lancedb <db_dir> --input q.h5ad --output hits --k 3
# 用途：跨数据集 cell state 匹配、扰动前后最相似细胞检索
```

## §4 Linear baseline（铁律，强制）

```python
# Ahlmann-Eltze 2025：linear baseline = 每扰动「control pseudobulk 均值 ± 训练集见过的平均效应偏移」，
# 仅需 pseudobulk 均值差，无 GPU。State 只有明确优于它才可作为主证据。
import pandas as pd
# pseudobulk 聚合（纪律 [A2]：sample×celltype×perturbation 聚合，不做 per-cell）
pb_ctrl = ...   # DataFrame：genes × control 样本伪批量
pb_pert = ...   # DataFrame：genes × 某扰动样本伪批量（有实测数据时）
baseline_delta = pb_pert.mean(axis=1) - pb_ctrl.mean(axis=1)      # linear 预测的 Δ

# 验证：在留出的实测扰动上，分别算 baseline Δ 与 State Δ 对实测 Δ 的
#   Pearson/Spearman 相关 + DE overlap；官方指标套件 cell-eval 随 arc-state 安装，
#   用法见 github.com/ArcInstitute/cell-eval
# 结论规则：State ≤ baseline → 只作补充证据，不得作为主结论
```

## 汇报与衔接

- CLI/下游代码均入任务 notebook（`scripts/nb_log.py`，Core Rule 9）；checkpoint 版本+日期入 analysis_log
- 下游 DE/富集完成后跑 `scripts/postcheck.py`（Core Rule 4）
- 扰动批次结束 → `research-planner` Phase R（Core Rule 8）
- 出图 → `visualization/figure-production`；写 Methods → `presentation/manuscript-writing`

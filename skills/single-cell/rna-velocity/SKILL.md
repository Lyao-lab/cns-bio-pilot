---
name: omicverse-rna-velocity
description: RNA velocity 基于 OmicVerse V2 的 ov.single.Velo（统一封装 scvelo 与 dynamo），从 spliced/unspliced 层推断细胞状态转移方向、潜在时间与驱动基因。深度调参或代谢标记数据时 fallback 到原生 scvelo/dynamo。
---

## When NOT to use this skill
- 只要拟时序/轨迹（不需 spliced/unspliced 剪接动力学）→ 改用 `single-cell/omicverse-pipeline`（`ov.single.Monocle` / PAGA）
- 没有 spliced/unspliced layers 且无法补跑 velocyto/kb_python → 不能用 RNA velocity，改用拟时序
- 用户在 R/Seurat 环境且需 SCVELO 之外的速度工具 → 改用 `single-cell/scop`（`RunSCVELO`）
- 只要把速度图拼成发表级 figure → 先出图，再走 `visualization/multi-panel-figures`

# OmicVerse RNA Velocity

**由原 `single-cell/scvelo` 重命名重写**。OmicVerse V2 通过 `ov.single.Velo` 统一了 scvelo 与 dynamo 两个引擎，本 skill 是其官方推荐入口。

`pip install omicverse`（V2）。

## 0. 初始化

```python
import omicverse as ov
ov.plot_set()
```

## 1. 前置条件（数据生成）

scVelo/dynamo 都需要 `layers['spliced']` 与 `layers['unspliced']`，由下列工具产出：
- **STARsolo** / **kallisto\|bustools**（lamanno 模式）
- **velocyto** CLI：`velocyto run10x` / `velocyto run`
- **alevin-fry / simpleaf**

合并到已有 AnnData（含 UMAP/聚类）：
```python
import scvelo as scv
adata = scv.utils.merge(adata_processed, scv.read('velocyto.loom'))
```

## 2. 基础用法（ov.single.Velo）

```python
v = ov.single.Velo(adata, mode='scvelo')   # 'scvelo'|'dynamo'
v.preprocess(n_top_genes=2000)              # filter_and_normalize + moments
v.velocity(mode='dynamical')                # 'stochastic'(快) | 'dynamical'(准, 默认主图)
v.latent_time()                             # 动力学模型才有
v.velocity_graph()
# 结果写入 adata.layers['velocity'], adata.obsm['velocity_umap'],
#       adata.obs['latent_time'], adata.uns['velocity_graph']
```

引擎选择：
| 模式 | 引擎 | 适用 |
|---|---|---|
| `'scvelo'` | scVelo | 常规 unspliced/spliced（默认） |
| `'dynamo'` | dynamo | 含代谢标记（4sU/SLAM-seq）的多组分层 |

## 3. 可视化（详见 visualization/omicverse-plotting）

```python
ov.pl.embedding(adata, basis='X_umap', color='leiden',
                velocity=True, arrow_length=3)   # 流向箭头
ov.pl.embedding(adata, basis='X_umap', color='latent_time', cmap='gnuplot')
```

## 4. 何时 fallback 到原生 scvelo

以下深度调参 `ov.single.Velo` 不暴露，直接用 `scvelo`：
- 自定义 `fit_alpha/beta/gamma` 先验或固定某些基因参数
- `recover_dynamics` 的 `use_raw=False`、`fit_scaling` 等细粒度选项
- 自定义 PAGA 边权 (`scv.tl.paga(groups=...)`)
- EM 模型 (`scv.tl.velocity(mode='dynamical', use_highly_variable=False)` 等组合)
- 直接操作 `adata.layers['fit_t']`/`fit_alpha` 做 driver 基因排序与相图

```python
# fallback 示例
import scvelo as scv
scv.tl.recover_dynamics(adata, n_jobs=8, fit_scaling=True, use_raw=False)
scv.tl.velocity(adata, mode='dynamical'); scv.tl.velocity_graph(adata)
scv.tl.rank_velocity_genes(adata, groupby='leiden', min_corr=0.3)
```

动力学模型 driver 基因输出（与原 scvelo skill 一致，便于复用）：
| 位置 | 键 | 含义 |
|---|---|---|
| `adata.var` | `fit_likelihood` | 基因模型拟合质量 |
| `adata.var` | `fit_alpha/beta/gamma` | 转录/剪接/降解速率 |
| `adata.obs` | `latent_time` | 潜在时间 |
| `adata.obs` | `velocity_length/confidence` | 速度大小/置信度 |
| `adata.uns` | `velocity_graph` | 细胞转移概率矩阵 |

## 5. 最佳实践（沿用原 scvelo skill 经验）

- **先 stochastic 探索，再 dynamical 出主图**：动力学模型 10K 细胞 ~10-30 min。
- **≥2000 细胞**，否则速度噪声大、箭头杂乱。
- **需良好 intron 覆盖**：read <100bp 易丢 unspliced 信号。
- **箭头要符合已知生物学**：随机箭头通常是 n_neighbors 取错或测序深度不足。
- **根细胞（progenitor）** 对 marker 基因应有高 unspliced/spliced 比例，作为 sanity check。

## 决策速查：何时离开本 skill

| 需求 | 去 |
|---|---|
| 拟时序（不需 spliced/unspliced） | `single-cell/omicverse-pipeline` → `ov.single.Monocle` |
| 多面板速度图拼图 | `visualization/multi-panel-figures` |

## 关键坑

- `ov.single.Velo` 前必须保证 neighbors 图已存在（`ov.pp.neighbors`），否则 moments 步报错。
- `mode='dynamical'` 才有 `latent_time`；stochastic 模式只能用 `velocity_pseudotime`。
- fallback 到原生 scvelo 后，再用 `ov.pl.embedding(..., velocity=True)` 出图需确认 `adata.obsm['velocity_umap']` 已写入。
- dynamo 模式对代谢标记数据友好，但常规 10x 数据用 scvelo 模式即可，dynamo 不增加信息。
- 跨样本合并 loom 时按 sample 切勿直接堆叠——需先各自 filter，再 merge，否则边界细胞速度异常。

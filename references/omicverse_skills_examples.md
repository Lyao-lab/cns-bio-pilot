# OmicVerse-Skills 绘图参考索引

> 本文件摘录自 omicverse-skills 仓库（https://github.com/omicverse/omicverse-skills），作为外部优质参考。
> **注意**：omicverse-skills 用 ForbiddenCity 配色 + ov.pl API，与 cns_style 的 Morlandi Nord 体系不同。
> 标注约定：
> - ✅ 已吸收 = 该模式已实现进 `scripts/cns_style.py`，直接用 cns_style 函数即可
> - 📎 参考 = 非 cns_style 标准，借鉴设计思路或用 ov.pl 原生 API 时参考

---

## 0. 仓库结构概览
- 仓库地址：https://github.com/omicverse/omicverse-skills
- 组织方式：按分析流程分组（非图类型），共 43 个 skill
- 双文件模式：每个 skill = SKILL.md（流程）+ references/reference.md（代码速查）
- 两层谱系：omicverse 专属 skill + Universal 纯 matplotlib skill（data-viz-plots）

### 绘图相关 skill 索引
| Skill | URL | 覆盖图类型 |
|---|---|---|
| plotting-visualization | https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/SKILL.md | 泛化绘图：火山图、命名色板、embedding、plot1cell 等 |
| data-viz-plots | https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/data-viz-plots/SKILL.md | 通用 matplotlib：柱/线/散点/热图 + 发表级 Best Practices |
| single-downstream-analysis | https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/single-downstream-analysis/SKILL.md | 下游分析相关绘图（可视化入口 + 分析流程） |
| single-cell-cellphonedb-communication | https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/single-cell-cellphonedb-communication/SKILL.md | 细胞通讯：网络图、弦图、气泡图、signaling-role 热图 |
| single-cell-trajectory-inference | https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/single-cell-trajectory-inference/SKILL.md | 轨迹推断：trajectory、streamplot、dynamic heatmap/trends |
| spatial-tutorials | https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/spatial-tutorials/SKILL.md | 空间组学：spatial embedding、空间可视化 |

---

## 1. 数据防御校验（绘图前 assert）  ✅ 已吸收
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/SKILL.md

```python
# omicverse-skills 风格：绘图前先校验 key 存在，报错信息带可用选项
def _assert_plot_keys(adata, *, color_col=None, basis='X_umap'):
    if color_col is not None and color_col not in adata.obs.columns:
        raise ValueError(
            f"`color_col={color_col!r}` 不在 adata.obs 中。"
            f"可用列：{list(adata.obs.columns)}"
        )
    if basis not in adata.obsm_keys():
        raise ValueError(
            f"`basis={basis!r}` 不在 adata.obsm 中。"
            f"可用 key：{list(adata.obsm.keys())}"
        )
```

**好在哪**：报错信息列出可用选项，Agent 拿到错误即可自愈。
**cns_style 对应**：`from cns_style import assert_anndata_keys; assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])`

---

## 2. 火山图配色 dict  📎 参考
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/reference.md

```python
ov.pl.volcano(
    result,
    pval_name='qvalue',
    fc_name='log2FoldChange',
    sig_pvalue=0.05,
    sig_fc=1.0,
    palette={'up': '#d62828', 'down': '#1d3557', 'stable': '#adb5bd'},
    annotate_top=10,
)
```

**注意**：列名（qvalue/log2FoldChange）和配色（#d62828）是 omicverse 教程数据，与 cns_style 标准（padj/log2FC + #e25d5d/#7388c1）不同。
**cns_style 标准**：`from cns_style import volcano_colors; vc = volcano_colors()` 或直接 `ov.pl.volcano(de_df, pval_name='padj', fc_name='log2FC')`（omicverse 默认色）。

---

## 3. 命名色板 ForbiddenCity  ✅ 已吸收
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/reference.md

```python
fb = ov.pl.ForbiddenCity()
royal_purple = fb.get_color(name='凝夜紫')
segment = ov.pl.get_cmap_seg(['#ef6f6c', '#f7c59f', '#458f69'], name='warm_to_green')
color_dict = {'Astrocytes': fb.get_color('石英粉红'), ...}  # cell type → 中文名 → hex 一次定义
```

**好在哪**：cell type→中文名→hex 一处定义全图复用，保证整套文章配色一致。
**cns_style 对应**：`from cns_style import ForbiddenCityBridge, palette_from_names; b = ForbiddenCityBridge(); b.get('霁蓝')`（优先 ov，降级 fallback）。

---

## 4. cohort 规模→参数映射（plot1cell）  ✅ 已吸收
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/reference.md

```python
# 环形聚类图：用 cohort 规模决定 point_size / alpha / figsize，避免大数据点糊成一团
ov.pl.plot1cell(adata, basis='X_umap', group='celltype',
                point_size=2, alpha=0.35, figsize=(10, 10))
```

| adata.n_obs | point_size | alpha | figsize |
|---|---|---|---|
| ~10k | 6 | 0.5 | (9, 9) |
| ~50k | 2 | 0.35 | (10, 10) |
| ~100k | 1 | 0.25 | (11, 11) |
| 200k+ | 0.8 | 0.2 | (12, 12) |

**注意**：此映射表未在 skill 源文件逐字核实，数值为探索摘录，以实际 ov 版本为准。

**cns_style 对应**：`from cns_style import cohort_params; p = cohort_params(adata.n_obs)` 返回 dict(point_size, alpha, figsize)。

---

## 5. get_cmap_seg 分段 colormap  📎 参考
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/reference.md

```python
ov.pl.get_cmap_seg(['#ef6f6c', '#f7c59f', '#458f69'], name='warm_to_green')
```

**注意**：cns_style 用预定义的 EXPR_CMAP（蓝→麦→暗红）和 DIVERGING_CMAP（蓝→白→红），不常需自定义分段。需要人文风格渐变（如图形摘要）时可参考此模式。

---

## 6. optim_palette 自动配色  📎 参考
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/plotting-visualization/reference.md

```python
ov.pl.optim_palette(adata, basis='X_umap', colors='clusters')
```

**好在哪**：基于 UMAP 坐标自动优化 cluster 配色（相邻 cluster 色相对比最大化）。
**cns_style 对应**：cns_style 用 manifest.yaml 手动锁色（跨论文一致性优先）；需要单图自动配色时可调用 ov.pl.optim_palette。

---

## 7. 轨迹绘图 API  📎 参考
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/single-cell-trajectory-inference/SKILL.md

- `ov.pl.trajectory(adata, *, method=..., basis='X_umap', color=...)` — keyword-only，无 ax
- `ov.pl.trajectory_overlay(adata, *, ax, method=...)` — **有 ax，可与 cns_style 组合**
- `ov.pl.branch_streamplot`、`ov.pl.dynamic_heatmap`、`ov.pl.dynamic_trends`

```python
# 与 cns_style 组合：底图走 cns_style，轨迹线用 ov overlay，最后统一 finalize
fig, ax = plt.subplots(figsize=(8, 8))
ov.pl.embedding(adata, basis='X_umap', color='celltype', ax=ax)
ov.pl.trajectory_overlay(adata, ax=ax, method='scvelo')
finalize_figure(fig)
```

**与 cns_style 组合**：先 `ov.pl.embedding(..., ax=ax)` 画底图，再 `ov.pl.trajectory_overlay(adata, ax=ax, method=...)` 叠加，最后 `finalize_figure(fig)`。

---

## 8. CCC 细胞通讯绘图  📎 参考
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/single-cell-cellphonedb-communication/SKILL.md

- 统一入口：`ov.pl.CellChatViz(adata_cpdb, palette=None)`
- 下游：`netVisual_aggregate`（网络图）、`netVisual_chord_cell`（弦图）、`netVisual_bubble_marsilea`（气泡）、`netAnalysis_signalingRole_heatmap`（signaling-role 热图）
- 注意：无独立 `ov.pl.ccc_heatmap`（探索未确认此函数存在）

---

## 9. 发表级 Best Practices（来自 data-viz-plots）  📎 参考
**来源**：https://github.com/omicverse/omicverse-skills/blob/main/src/omicverse_skills/skills/data-viz-plots/SKILL.md

要点摘录：
- 图宽 6–8 英寸
- 300 DPI publication / 150 presentation
- 色盲友好（viridis / Set2 / tab10）
- 字号分级：标题 12–14、轴 10–12、刻度 8–10
- alpha 处理重叠
- tight_layout
- PNG 通用 / SVG 矢量 / 保存后 plt.close

**cns_style 对应**：cns_style 的 JOURNAL_PRESETS 已覆盖（nature 600dpi / cell 300dpi / 字号 modular scale），且更细化（按期刊锁 column width）。本段作为"通用兜底"参考。

---

## 使用建议
1. **默认用 cns_style 函数**（Morlandi 配色 + finalize_figure）—— 发表级标准已在 cns_style.py 落地。
2. **需要 ov.pl 原生功能时**（如 plot1cell 环形、trajectory_overlay、CellChatViz）参考本文件对应小节，但配色尽量走 cns_style（用 ForbiddenCityBridge 取色后传入）。
3. **cohort 大规模数据**：用 `cohort_params(n)` 联动调 size/alpha/figsize，不要只调 size。
4. **绘图前**：用 `assert_anndata_keys(adata, obs_cols=[...], obsm_keys=[...])` 校验，避免运行到一半才 KeyError。
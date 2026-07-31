---
name: figure-production
description: 生信发表级图表全流程——设计主图逻辑（narrative spine）→ 逐张独立出图（每张验证美观）→ 拼成 composite figure。当用户要画生信图、做发表级 figure、设计主图、拼图、UMAP/volcano/heatmap/dotplot/空间图时触发。一个 skill 覆盖从设计到交付。
---

# Figure Production (Design → Render → Assemble)

**触发词**: 画图 / 出图 / figure / UMAP / volcano / heatmap / dotplot / 拼图 / 主图设计 / composite / 发表级

## 三阶段流程

```
Phase 1: DESIGN    → outline.json（panel 逻辑 + 顺序）
Phase 2: RENDER    → 每张 panel 独立画 + 独立存 PDF + 逐张验证
Phase 3: ASSEMBLE  → 把已验证的 PDF/PNG 拼成 composite
```

**铁律：Phase 2 必须逐张独立完成后再进 Phase 3。不许"一边画一边拼"。**

---

## Phase 1: Design（分析完成后、画图前）

1. **一句话 main message**（≤30 词，论证性，不是描述性）
2. **Narrative spine**：main message 拆成 3-6 个逻辑节点，每个 = 一个 panel
3. **Panel spec**：每个 panel 写 `{id, chart_type, data_source, take_home}`
4. **审查**：逻辑链完整？每个 panel 都服务 main message？删任一论证链断？

```json
{"panels": [
  {"id":"A", "chart_type":"UMAP + proportion bar", "take_home":"10 cell types, Fibro dominant"},
  {"id":"B", "chart_type":"subcluster UMAP + volcano", "take_home":"Quiescent rewiring, padj<1e-40"},
  {"id":"C", "chart_type":"spatial overlay", "take_home":"CXCL12 spatially restricted"}
]}
```

> 主图 ≤6 panel。超过 = 论证不够精炼。Figure 1 = atlas（2-3 panel）；中间 = mechanism（4-6）；最后 = validation（2-3）。

---

## Phase 2: Render（逐张独立出图）

每张 panel **独立 figure → 独立 savefig → plt.close()**：

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import (set_cns_style_journal, polish_axes, clean_umap_axes,
    add_elegant_colorbar, safe_scanpy_plot, optical_margin, add_panel_label,
    point_size_for_n, apply_5plus1_palette, recipe_figsize)

set_cns_style_journal('nature')  # 一次性设好全局参数

# --- Panel A: UMAP ---
fig, ax = plt.subplots(figsize=recipe_figsize('umap'))
safe_scanpy_plot(sc.pl.umap, adata, color='celltype',
    palette=apply_5plus1_palette(cats, focus=['Fibro','Macro']),
    size=point_size_for_n(adata.n_obs), alpha=0.7, edgecolor='none',
    legend_loc=None, ax=ax, show=False)
clean_umap_axes(ax)
optical_margin(ax, 0.12)
fig.savefig('panels/A_umap.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)  # ← 必须 close

# --- Panel B: Volcano ---
fig, ax = plt.subplots(figsize=recipe_figsize('volcano'))
# ... scatter with volcano_colors() ...
polish_axes(ax)
fig.savefig('panels/B_volcano.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)

# ... 每张同理 ...
```

**逐张验证**（每张存完后）：
- 比例对？（UMAP ≈ 1:1，bar ≈ 4:3）
- `polish_axes()` / `clean_umap_axes()` 已应用？
- 配色符合 manifest？字号 ≥6pt？legend/colorbar 不遮挡？
- **不通过 → 重画这一张（不是全部）**

**视觉规格速查**（详见 `references/figure_guide.md`）：
- UMAP: s=8/3/1/0.3（按细胞数），alpha=0.7，去轴，on-plot labels
- Volcano: up=#BF616A, down=#5E81AC, ns=grey α0.4, top-5 italic labels
- Heatmap: z-score ±2, EXPR_CMAP, row-clustered, white separators
- Dotplot: size 15-150, edgecolor #2E3440 lw=0.3
- Violin: fill α0.3, box lw=0.8, points s=2 α0.5
- 通用: 不用纯黑（用 #2E3440），不用默认调色板，rasterized=True for >10k points

---

## Phase 3: Assemble（拼图）

输入 = Phase 2 产出的**已验证 PDF/PNG 文件**。拼图只做排版，不改内容。

```bash
python skills/visualization/figure-production/scripts/assemble.py \
  --input panels/A_umap.pdf panels/B_volcano.pdf panels/C_spatial.pdf ... \
  --output figure1.pdf --layout 2x3 --dpi 300 --label-size 12 --label-bold
```

**拼图规则**：
- Panel labels (A/B/C): 12pt bold, top-left, offset (-0.12, 1.08)
- 锚点 panel 占 40-50% 面积（`width_ratios=[1.8, 1, 1]`）
- 间距: wspace=0.35, hspace=0.45（逻辑相关 panel 更紧）
- 共享 legend/colorbar 合并（同 scale 不重复）
- **发现某张比例不对 → 回 Phase 2 重画那张，不在拼图时硬缩放**

---

## 报告级组织（多张 Figure 的叙事弧）

- Figure 1 = atlas/overview（2-3 panel，建立全局）
- Figure 2~N-1 = mechanism（4-6 panel，每张一个机制）
- Last Figure = validation/schematic（2-3 panel，收束）
- 连续两张 ≥5 panel 之间插一张 ≤3 panel 的"呼吸 Figure"
- 全论文锁定 `manifest.yaml`（cell_type_colors / condition_colors / cmap）

---

## 工具

- `scripts/cns_style.py` — 一键美学（set_cns_style_journal / polish_axes / add_elegant_colorbar / safe_scanpy_plot / recipe_figsize / apply_5plus1_palette）
- `references/figure_guide.md` — 视觉规格全集（配色/排版/留白/10 种图型 recipe）
- `scripts/main.py`（本 skill 下）— 拼图脚本（Phase 3）

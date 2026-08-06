---
name: figure-production
description: 生信发表级图表——逐张迭代设计（看上一张结果决定下一张画什么）→ 每张独立出图验证 → 最后拼成 composite。当用户要画生信图、做发表级 figure、设计主图、拼图、UMAP/volcano/heatmap/dotplot/空间图时触发。
---

# Figure Production (Iterative Design → Per-Panel Render → Assemble)

**触发词**: 画图 / 出图 / figure / UMAP / volcano / heatmap / dotplot / 拼图 / 主图设计 / composite / 发表级

## 核心原则：先定大框架，再逐张迭代

**先设计大框架**（main message + 叙事弧 + 大致 panel 列表），**再逐张出图，根据结果调整每张的具体设计**。框架不变，细节动态调整。

```
Step 1: 大框架 — main message + 叙事弧 + panel 列表（粗略，可调整）
Step 2: 画 Panel A → 看结果 → A 支持框架吗？
Step 3: 支持 → 按框架画 B；不支持 → 调整 B 的设计（换图型/换角度）
Step 4: 画 B → 看结果 → 同 A 一样评估
...
Step N: 所有 panel 验证通过 → 拼成 composite
```

**框架 = 骨架**（main message 和叙事顺序在设计前定死，不随数据摇摆）。
**迭代 = 血肉**（每张 panel 的图型/配色/标注/细节根据上一张的结果微调）。

---

## Step 1: 大框架设计（开始画图前）

> **先读 `references/story_builder.md`** —— 它教你从分析结果构建生物学故事（五步法：清点发现 → 找因果链 → 提炼主结论 → 映射 Figure → 写叙事弧）。
>
> **快速通道**：如果用户已明确给出结论/故事（"帮我画一张 UMAP，按 cell type 着色"），跳过 story_builder，直接查 `figure_guide.md` §0 速查卡选图型 → 进 Step 2。只有"我有一堆结果，不知道怎么组织成图"时才需要完整的 story_builder 流程。

三件事，定死不随数据摇摆：

1. **Main message**（一句话，≤30 词，论证性）
2. **叙事弧**（Figure 1=atlas → 中间=mechanism → 最后=validation）
3. **大致 panel 列表**（每个 panel 一句话 take-home + 图型，粗略即可）

```
❌ "We analyzed POP single-cell data."
✓ "POP is driven by fibroblast quiescent-subtype rewiring, not myofibroblast expansion."

大致 panel 列表（后续可调整）：
  A: UMAP atlas + proportion      → "有哪些细胞"
  B: Fibroblast subcluster        → "哪群变了"
  C: DE volcano                   → "分子机制"
  D: Spatial overlay              → "空间验证"
```

> 这个列表是**起点不是终点**——后面每张出完，根据结果调整下一张的具体设计。

---

## Step 2-N: 逐张迭代设计 + 出图

每张 panel 的完整循环：

```
设计这张要讲什么 → 选图型 → 出图 → 看结果 → 满意？ → 满意就存，不满意就调整重画
```

### 设计（每张 panel 开始前问自己）

1. **这张 panel 论证什么？**（一句话 take-home）
2. **上一张的结果改变了我的预期吗？**（如果有，调整这张的设计）
3. **用什么图型最能讲清楚？**（查 figure_guide.md §0 速查卡）

### 出图（cns_style.py 工具）

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *

set_cns_style_journal('nature')

# --- Panel A: UMAP ---
fig, ax = plt.subplots(figsize=recipe_figsize('umap'))
ov.pl.embedding(adata, color='celltype', frameon='small', ax=ax, show=False)
add_cluster_labels(ax, adata, groupby='celltype')
finalize_figure(fig)
fig.savefig('panels/A_umap.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
# → 打开 panels/A_umap.pdf 看效果
# → 满意？→ 继续 Panel B
# → 不满意？→ 调整（改配色？改标签？改 figsize？）→ 重画 → 再看
```

### 验证（每张存完后必做）

打开 PDF 检查：
- [ ] 比例正确？（UMAP 方形，bar 宽扁）
- [ ] `finalize_figure()` 过了？（legend 外置 / 无文字重叠 / 比例不畸形）
- [ ] 配色符合 manifest？字号可读？
- [ ] **这张图真的讲了它该讲的 take-home 吗？**

**不满意 → 重画这张（只重画这张，不动其他）**

### 迭代决策（关键）

画完 Panel A 后，**主动问自己**：
- A 显示了什么我没预料到的？
- B 原来设计的内容还有意义吗？还是应该换个角度？
- C 的顺序对吗？还是应该先讲另一个发现？

**示例迭代**：
```
Panel A (UMAP): 发现 Fibroblast 占 44%，是最大的 cluster
  → 原来设计的 Panel B 是"全 DE 概览"，
    改为 "Fibroblast 亚群细分"（因为 Fibro 是主角）
  → Panel B 画 Fibroblast subcluster UMAP + 比例

Panel B (Fibroblast subcluster): 发现 Quiescent_1 转向 Quiescent_2/3
  → 原来设计的 Panel C 是"全 CCC"，
    改为 "Quiescent 亚群的 DE volcano"（机制更聚焦）
  → Panel C 画 volcano

Panel C (Volcano): CXCL12 显著上调
  → Panel D 应该是"CXCL12 的空间定位验证"（空间 overlay）
  → 完成叙事闭环：图谱 → 重塑 → 机制 → 空间验证
```

---

## Step Final: 拼图

所有 panel 独立验证通过后：

```bash
python skills/visualization/figure-production/scripts/main.py \
  --input panels/A_umap.pdf panels/B_subcluster.pdf panels/C_volcano.pdf panels/D_spatial.pdf \
  --output figure1.pdf --dpi 300
```

**拼图只做排版**（label 位置/间距/DPI），不改内容。发现某张比例不对 → 回去重画那张。

---

## 视觉规格速查

画图时查 `references/figure_guide.md`：
- §0 速查卡：图型 → 一行 ov.pl 调用 + 必须函数 + 关键参数
- §5 各图型精确规格（UMAP/volcano/dotplot/violin/heatmap/spatial/bar/富集/bubble/feature 矩阵）
- §10 Layout 三铁律（legend 右侧外置 / 文字不重叠 / 比例不畸形）

## 工具

- `scripts/cns_style.py` — 一键美学（22 个函数）
- `references/figure_guide.md` — 视觉规格（唯一参考）
- `scripts/main.py`（本 skill 下）— 拼图脚本

---
name: figure-production
description: 生信发表级图表——逐张迭代设计（看上一张结果决定下一张画什么）→ 每张独立出图验证（png+pdf 双格式落盘，per-figure ipynb 一面板一 cell）→ deck/composite 由单图拼装。当用户要画生信图、做发表级 figure、设计主图、拼图、UMAP/volcano/heatmap/dotplot/空间图/PAGA/轨迹/细胞通讯图/云雨图/斜率图/棒棒糖图/QC 卡片/趋势小倍数/空间放大图/Sankey 命运流/CNV 热图（inferCNV 可视化）/轴梯度（zonation/边界带/距离梯度）/克隆扩增（TCR 追踪）时触发。
---

# Figure Production (Iterative Design → Per-Panel Render → Assemble)

**触发词**: 画图 / 出图 / figure / UMAP / tSNE / volcano / heatmap / dotplot / violin / 云雨图 / raincloud / 斜率图 / slope / movers / 棒棒糖 / lollipop / QC 卡片 / 趋势小倍数 / 小倍数 / 空间放大 / zoom / inset / Sankey / 命运流 / 状态转换图 / CNV 热图 / inferCNV 可视化 / 轴梯度 / zonation / 距离梯度 / 克隆扩增 / TCR 追踪 / 拼图 / 主图设计 / composite / 发表级 / PAGA / 轨迹 / chord / 细胞通讯 / 空转图

> **派发子任务自守**：本 skill 若再向下派发任何执行子任务，先把 `references/dispatch_cheatsheet.md` 的相关硬规则（A-E）写进子任务 spec——子智能体看不到本会话上下文，没写进 spec 的规则等于不存在。

## 🚫 面板导出硬规则（Panel Export Contract，所有绘图代码强制遵守）

1. **一面板一文件、双格式**：每个 panel 必须经 `save_panel(fig, 'X_name', fmt='png+pdf')` 独立落盘（PNG 自检 + PDF 矢量交付）。🚫 禁止只存在于拼接大图/slide 里的面板；🚫 禁止只出 PNG 不出 PDF（或反之）。
2. **绘图代码 = per-figure ipynb，一面板一 cell**：每个大 figure 维护一个 notebook（`YYYYMMDD_fig<N>_panels.ipynb`，放 `~/code/<项目>/`），**每个 cell 自包含**（imports + 数据加载 + 绘制 + save_panel），单独重跑该 cell 即可重画该面板；cell 上方英文 markdown 旁注一句话说明。`.py` 面板脚本与 notebook cell 保持镜像（改一边同步另一边）：CLI 批量渲染用 `.py`，修改迭代用 ipynb。
3. **PPT/composite 由单图拼装**：deck 用 `figure-grid` 等布局直接引用各面板文件拼装；composite 只是打印版附加产物，**不得作为面板的唯一存在形式**。幻灯片引用的每张图必须能回溯到磁盘上的独立 png+pdf。

## 何时使用（When to Use）

- 用户要画生信发表级图表（单细胞/空转/bulk 任何图型）
- 要设计主图、迭代 panel 设计、拼 composite
- 拿到分析结果要把"发现"变成"figure"

## 画图前：读哪三个文件（顺序很重要）

1. **本文件**（SKILL.md）— 流程：怎么迭代、怎么验证
2. **`references/plotting_reference.md`** — 代码模板：每种图型的可跑代码（§0 速查卡选图型 → §2/§3 看对应模板）
3. **`references/figure_guide.md`** — 视觉规格：原则、三铁律、实战教训（需要决定配色/字号/布局时查）

**外部参考**（非必需）：`references/omicverse_skills_examples.md` — omicverse-skills 仓库的优质片段（设计模式参考，非 cns_style 标准）。

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
> **再查 `references/figure_templates.md` §0 路由表** —— 按领域（C1-C15）和故事类型（T1-T6）拿到整篇 fig 的默认顺序骨架与期刊格式规则（506 篇 2024-2026 CNS 论文泛化）；panel 层图型再回查 `plotting_reference.md` §0 / `figure_guide.md` §0.1。
>
> **快速通道**：如果用户已明确给出结论/故事（"帮我画一张 UMAP，按 cell type 着色"），跳过 story_builder，直接查 `plotting_reference.md` §0 速查卡选图型 → 进 Step 2。只有"我有一堆结果，不知道怎么组织成图"时才需要完整的 story_builder 流程。

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
3. **用什么图型最能讲清楚？**（不知道该用什么图 → 查 `figure_guide.md` §0.1 数据→图型决策表；知道图型后查 `plotting_reference.md` §0 速查卡找代码）

### 出图（标准流程，代码查 reference）

每个绘图脚本的固定结构（**SKILL.md 不内嵌完整代码**，全部指向 `plotting_reference.md`）：

1. **顶部固定 3 行开头** → `plotting_reference.md` §1（import + set_cns_style_journal）
2. **绘图前防御校验** → `assert_anndata_keys(adata, obs_cols=[...], obsm_keys=[...])`（新推荐，每张 panel 绘图前调，避免运行到一半 KeyError；报错会带可用选项）
3. **选图型模板** → `plotting_reference.md` §0 速查卡选图 → §2 核心图型 / §3 补充图型（§3.1-§3.45，速查卡见 §0）看对应模板
4. **大 cohort 联动调参** → `cohort_params(adata.n_obs)` 返回 (point_size, alpha, figsize)，替代只调 size（点太多/太少时用）
5. **统一保存** → `save_panel(fig, 'A_umap')` 统一入口（强制 finalize_figure → 建目录 → savefig，不要手写 fig.savefig）

**示例**：画 UMAP → 查 `plotting_reference.md` §2.1，复制模板，改 color/groupby/输出名即可。

**名称色板（可选）**：需要固定命名色板时用 `ForbiddenCityBridge(label)`（故宫配色）或 `palette_from_names(celltypes, color_names)`，不要逐张手写颜色。

### 验证（每张存完后必做）

打开 PDF 检查：
- [ ] `assert_anndata_keys` 已跑过？（确认 obs/obsm 列名存在，不是靠运气）
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

## Notebook 工作流（推荐：一个大 Figure 一个 .ipynb）

一个 Figure 的所有 panel 放在同一个 notebook 里，每 panel 一个 cell。改某张图只重跑对应 cell，adata 在内存里不重跑。

```python
# === Cell 1: Shared setup（只跑一次）===
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import scanpy as sc, pandas as pd
set_cns_style_journal('nature')
adata = sc.read_h5ad('checkpoints/05_annotated.h5ad')

# === Cell 2: Panel A — UMAP ===
fig, ax = plot_umap(adata, color='celltype', save='A_umap')
# → PDF 落盘到 panels/A_umap.pdf + 图在 cell 输出显示（save_panel 自动检测 notebook）

# === Cell 3: Panel B — Volcano ===
de = pd.read_csv('de_results.csv')  # 或 pseudobulk_de(adata, ...)
fig, ax = plot_volcano(de, save='B_volcano')

# === Cell 4: Panel C — Dotplot ===
fig, ax = plot_dotplot(adata, var_names=markers, groupby='celltype', save='C_dotplot')

# === Cell 5: Panel D — Spatial ===
fig, ax = plot_spatial(adata_sp, color='Cxcl12', save='D_spatial')

# === Cell 6: Assemble composite（命令行或 notebook 里调）===
# python main.py --input panels/A_umap.pdf panels/B_volcano.pdf panels/C_dotplot.pdf panels/D_spatial.pdf --output figure1.pdf
```

**规则**：
- Cell 1 只跑一次（load adata）；改某 panel 只重跑对应 cell
- 每个 panel cell 调 `plot_xxx(save='X_name')` → 自动存 PDF 到 `panels/` + 在 cell 输出显示（溯源）
- `show=False` 可强制不显示（脚本批处理）；`show=True` 强制显示
- 无 Jupyter 内核（CLI 执行）时：panel 脚本跑完同样要落账——`python scripts/nb_log.py <figure的ipynb> -t "Panel A" -c panel_a.py -f panels/A_umap.png`（Core Rule 9 / A10）；图用 `fmt='png+pdf'` 双格式（PNG 自检 + PDF 交付）
- 拼图在最后一个 cell（命令行 `main.py`）或 `nbconvert --execute` 一键重跑

---

## Step Final: 拼图

所有 panel 独立验证通过后：

```bash
python skills/visualization/figure-production/scripts/main.py \
  --input panels/A_umap.pdf panels/B_subcluster.pdf panels/C_volcano.pdf panels/D_spatial.pdf \
  --output figure1.pdf --dpi 300
```

**拼图只做排版**（label 位置/间距/DPI），不改内容。发现某张比例不对 → 回去重画那张。

> **每张图保持 PDF 格式**（论文正文 + 拼大图都用 PDF 矢量）。PPT 嵌图时 `build_deck.py` 会自动把 PDF 转成 300dpi PNG（需 `pip install pymupdf`），你不需要手动切格式——PDF 是唯一源文件，PPT 只是消费端。
>
> **deck 优先用 `figure-grid` 布局直接引用各面板文件拼装**（一面板一 png+pdf，可独立改图重出）；composite PDF 只作打印版附加产物。不要把「拼成一张大图」当作面板的唯一交付形式。

---

## 视觉规格速查

画图时查：
- **代码模板** → `references/plotting_reference.md`（§0 速查卡、§2 核心图型、§3 补充图型（§3.1-§3.45）、§4 统计标注、§5 worked example）
- **视觉规格/原则** → `references/figure_guide.md`（§5 各图型参数、§10 三铁律、§11 实战教训）
- **外部参考** → `references/omicverse_skills_examples.md`

## 工具

- `scripts/cns_style/ 包` — 一键美学 + smart_plot 统一入口（plot_xxx 系列：plot_umap / plot_volcano / plot_dotplot / plot_radar / ... 自动 ov/mpl 降级；配色与标注 helper：alpha_ramp / focus_ramp / mark_events / is_dark，清单见 tool_registry.md）
- `references/plotting_reference.md` — 代码速查（唯一代码参考）
- `references/figure_guide.md` — 视觉规格
- `scripts/main.py`（本 skill 下）— 拼图脚本（函数式 assemble() API，示例见 scripts/example.py）
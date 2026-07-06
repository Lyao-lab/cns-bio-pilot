# 发表级绘图审美规范（CNS 标准）

> 基于 Nature / Science / Cell / Journal of Cell Science 官方 figure guidelines（2025）。所有绘图（单细胞 UMAP、空转切片、火山图、热图、PPT 内嵌图）必须遵循。

## 1. 尺寸与分辨率

| 期刊 | 单栏宽 | 双栏宽 | 照片 DPI | 线图 DPI | 格式 |
|---|---|---|---|---|---|
| Nature | 88 mm | 180 mm | 300 | 600+ | TIFF/EPS/PDF |
| Cell | ~85 mm | ~180 mm | 300 | 600 | TIFF/EPS/PDF |
| Science | ~85 mm | ~180 mm | 300 | 300+ | EPS/PDF |
| J Cell Sci | — | 180×210 mm | 300 | 600 | TIFF/EPS |

**实操**：matplotlib/ov.pl 出图时统一设：
```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    'figure.dpi': 300,           # 发表级最低
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',     # 去白边（嵌入 PPT 必做）
    'savefig.format': 'pdf',     # 矢量首选；照片用 TIFF
    'pdf.fonttype': 42,          # TrueType 嵌入（编辑可改）
    'ps.fonttype': 42,
})
# ov.plot_set() 已设大部分；以上是补充覆盖
```

## 2. 字体

| 要求 | 标准 |
|---|---|
| 字族 | **sans-serif**：Arial 或 Helvetica（Nature/Cell 强制）；禁 serif（Times 仅 Science 正文用） |
| 最小字号（最终印刷尺寸） | 6-7 pt；图注/坐标轴 ≥ 7.5 pt |
| panel 标签（A/B/C） | 8 pt 粗体 |
| 字号层级 | 全图最多 2-3 种字号（标题/正文/图注） |

**实操**：
```python
plt.rcParams['font.family'] = 'Arial'  # 或 'Helvetica'
plt.rcParams['font.size'] = 8          # 基准
# 标题 10pt，坐标轴 7.5pt，图注 7pt
```

## 3. 配色（色盲安全，CNS 硬性要求）

Nature/Cell **明确要求避免红绿组合**用于数据编码。使用色盲友好色板：

| 场景 | 推荐色板 | 来源 |
|---|---|---|
| **分类（≤8 类）** | **莫兰迪 Nord**（柔和高级，用户选定默认） | Nord 色系 |
| 分类（>8 类） | tab20 或 ov.pl.palette['red_blue'] | matplotlib/omicverse |
| 分类（色盲合规备选） | Okabe-Ito（8 色，色盲金标） | Nature Methods |
| **连续（表达量/热图）** | **蓝-白-红共识渐变**（低=蓝白，高=红，生信共识） | 本 skill 双轨方案 |
| 连续（感知均匀备选） | viridis / magma | matplotlib |
| **发散（log2FC）** | **蓝-白-红**（负=蓝，0=白，正=红） | 本 skill 双轨方案 |
| 空转组织切片 | 莫兰迪离散 或 蓝白红连续 | — |

### 用户选定默认：双轨配色（莫兰迪 + 蓝白红）

**离散分类（UMAP/聚类型/空间域）—— 莫兰迪 Nord 柔和**：
```python
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770',
            '#B48EAD','#EBCB8B','#5E81AC','#D8DEE9']
# 霜蓝/暗红/苔绿/赤陶/紫罗兰/麦黄/深蓝/霜灰——低饱和高级感
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=MORLANDI)
```

**连续表达（热图/表达量）—— 莫兰迪化蓝-黄-红（低饱和，低=蓝/中=米黄/高=暗红，与离散配色统一）**：
```python
from matplotlib.colors import LinearSegmentedColormap
EXPR_CMAP = LinearSegmentedColormap.from_list('byr_morlandi',
    ['#5E81AC','#8FBCD4','#ECEFF4','#D08770','#9B5A5A'], N=256)
# 用法：ax.imshow(data, cmap=EXPR_CMAP) 或 sc.pl.heatmap(..., cmap=EXPR_CMAP)
```

**发散（log2FC 火山图/热图）—— 蓝-白-红，0=白中点**：
```python
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D','#88C0D0','#FFFFFF','#D08770','#8B2C2C'], N=256)
# vmin=-3, vmax=3 确保 0 居中为白
```

**双轨原理**：离散分类用柔和莫兰迪（区分清晰不刺眼）；连续数值用蓝-黄-红（符合"高表达=红"的生信阅读直觉，中段黄色过渡自然，是单细胞热图最经典渐变）。

**Okabe-Ito 备选**（需严格色盲合规时，如期刊强制）：
```python
OKABE_ITO = ['#E69F00','#56B4E9','#009E73','#F0E442',
             '#0072B2','#D55E00','#CC79A7','#000000']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=OKABE_ITO)
```

**禁忌**：
- ❌ 红绿并置编码不同条件（红色盲/绿色盲无法区分）
- ❌ jet/rainbow（感知不均，Nature 多次批评）
- ❌ 默认 matplotlib 配色（饱和度过高，不专业）
- ❌ 热图用绿-黑-红（虽是旧共识，但绿色盲无法区分红绿，改用蓝-白-红更安全）

## 4. 图注与标注规范

| 元素 | 要求 |
|---|---|
| N / 样本量 | 必须标注（图内或图注） |
| 统计检验 | 标明方法（Wilcoxon/t-test/ANOVA）+ Padj 阈值 |
| 误差线 | 标明是 SD 还是 SEM + n |
| 坐标轴 | 有标签 + 单位（如 log2 Expression） |
| 色条（colorbar） | 有标签说明数值含义 |
| scale bar（显微图） | 必须有（空转 H&E 配准图也建议） |

## 5. 多图一致性（同一论文/报告内）

| 维度 | 统一要求 |
|---|---|
| 配色 | 同一细胞类型在所有图里颜色一致（建立 cell_type → color 映射，全局复用） |
| 字体 | 全图同字族同字号体系 |
| 坐标范围 | 同一基因的 expression 在不同图里色条范围一致（避免误导） |
| 风格 | ov.plot_set() 一次初始化，全程不复位 |

```python
# 全局 cell_type → color 映射（论文级一致性）
CELL_TYPE_COLORS = {
    'CD4 T': '#E69F00', 'CD14+ Mono': '#56B4E9', 'B': '#009E73',
    'CD8 T': '#F0E442', 'NK': '#0072B2', 'Platelet': '#D55E00',
}
sc.pl.umap(adata, color='cell_type', palette=CELL_TYPE_COLORS)
# 后续所有图复用此映射
```

## 6. ov.pl 与本规范的对齐

omicverse 的 `ov.plot_set()` 已设：
- ✅ 字体（sans-serif）
- ✅ 配色（内置 ov.pl.palette）
- ✅ 矢量友好 PDF 渲染

**需手动补充**（ov.plot_set 不覆盖的）：
- DPI 300+（默认 100，发表不够）
- Okabe-Ito 覆盖（默认配色非色盲安全）
- font.type=42（TrueType 嵌入）
- bbox_inches='tight'（去白边）

## 7. PPT 嵌入图的额外要求

嵌入 PPT 的图（scientific-slides skill 的 scientific-figure variant）：
- 导出时 `bbox_inches='tight'` + `trim_image_whitespace`（无白框）
- aspect ratio 匹配 slide 槽位（16:9 或 4:3）
- 字号在 slide 缩放后仍 ≥7.5pt（readability contract）
- 一张 slide 最多 4 panel（超过 qa_deck 报错）

## 参考来源

- [Nature figure guidelines](https://figureguild.com/journals/nature)
- [Cell figure guidelines](https://figureguild.com/journals/cell)
- [Science/AAAS 投稿指南](https://www.science.org/content/page/instructions-preparing-initial-manuscript)
- [Journal of Cell Science 稿件准备](https://journals.biologists.com/jcs/pages/manuscript-prep)
- [Nature/Science/Cell 图规范对比](https://conceptviz.app/blog/how-to-make-figures-for-nature-science-journals)
- Okabe-Ito 色板：[Nature Methods 2007 colorblind guide](https://www.nature.com/articles/nmeth.1618)

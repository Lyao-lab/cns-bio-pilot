# Slide Variants 布局细则（防重叠规则 + 图形多样化原则）

> 自 SKILL.md 拆出（2026-09-24，内容原样迁移）。SKILL.md 保留 12 种 variant 速查表与安全间距铁律；本文件是布局函数的实现级约束——**改 build_deck.py 布局代码时读本文件**。

## 防重叠规则（代码强制，不是建议）

```python
# build_deck.py 中每个布局函数都调用的安全检查：
SAFE_GAP = Inches(0.3)  # 图片与文字之间的最小安全间距

def _safe_zones(width_in=13.333, height_in=7.5):
    """返回安全区域字典——每个元素只能在自己的区域内"""
    title_zone = (0.5, 0.3, 12.3, 1.0)      # 标题区: top 0.3-1.0
    content_zone = (0.5, 1.2, 12.3, 5.3)     # 内容区: top 1.2-6.5
    caption_zone = (0.5, 6.7, 12.3, 0.6)     # 图注区: top 6.7-7.2
    # 图片放 content_zone 内，文字也放 content_zone 内，但两者在水平/垂直方向上不重叠
    return {"title": title_zone, "content": content_zone, "caption": caption_zone}
```

**规则**：
1. **标题区（0.3-1.0inch）**不放图、不放正文——只放标题
2. **图注区（6.7-7.2inch）**不放图、不放正文——只放 caption
3. **内容区（1.2-6.5inch）**内图片和文字**水平分离**：图片在左半区，文字在右半区，中间 ≥0.3inch 空白
4. **全宽图片**（figure-hero）：图片占满内容区宽度，文字移到图注区或下一张幻灯片
5. **上下布局**（figure-top-text）：文字在上 1/3，图在下 2/3，中间 0.3inch

## 图形式多样化原则

不要每张都用"图左+文右"（image-sidebar）。根据内容选布局：

| 内容类型 | 推荐布局 | 理由 |
|---|---|---|
| UMAP / 空间切片全景 | `figure-hero` | 全宽冲击力 |
| 火山图 + top genes 列表 | `figure-sidebar` | 图+文互补 |
| Normal vs Disease 对比 | `figure-dual` | 直接对比 |
| "先说结论再给证据" | `figure-top-text` | 叙事驱动 |
| 4 种分析结果概览 | `figure-grid` | 信息密度 |
| 两种方法/数据集对比 | `split-compare` | 方法学对比 |

**同一套 PPT 里至少用 3 种不同布局**——全是 figure-sidebar = 视觉单调。

> **scientific-figure key** (核心生信场景)：在 Python 里 `bbox_inches='tight'` 导出后，用 PIL `ImageOps.crop` 去白边再嵌入，否则幻灯片会有丑陋的白色边框。

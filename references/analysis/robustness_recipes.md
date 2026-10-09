# Robustness Recipes — 结论稳健性加固配方（实战沉淀，2026-10）

> 来源：fetal_heart fig1-3 投稿加固实战（2026-10）+ deep-review 计划执行。每条配方都是
> 在真实数据上跑通并进 deck/caption 的模式。**什么时候用**：审稿人红队前置、投稿前加固、
> 任何"这个结论审稿人会问 n/null/校正吗"的时刻。
> 措辞层（名义/校正/CI 怎么写）归 `stats_convention.md`；本页是**实现层**。

## R1 空间块 block bootstrap CI（bin 级统计的空间自相关校正）

**场景**：bins/spot 级统计量（相关、比例、均值差）需要 CI，但空间单元非独立。
**做法**：按 ≥500µm 空间块切网格 → 块级重采样（500 次）→ 统计量分布取 2.5–97.5%。
```python
def block_boot_ci(coords, values, stat_fn, block_um=500, n=500, seed=0):
    import numpy as np
    rng = np.random.default_rng(seed)
    bx = (coords[:, 0] // block_um).astype(int)   # Stereo-seq: 1 unit=0.5µm 时先乘 0.5
    by = (coords[:, 1] // block_um).astype(int)
    blocks = {}
    for i, (a, b) in enumerate(zip(bx, by)):
        blocks.setdefault((a, b), []).append(i)
    keys = list(blocks)
    out = []
    for _ in range(n):
        pick = rng.choice(len(keys), size=len(keys), replace=True)
        idx = np.concatenate([blocks[keys[k]] for k in pick])
        out.append(stat_fn(np.asarray(values)[idx]))
    return np.percentile(out, [2.5, 97.5])
```
**报法**：效应量 + block-bootstrap 95% CI（"CI excludes 0"才能升 A 层）。抽样 >40k bins 时可子采样提速（方法注记）。

## R2 供体级 permutation null（条件比较的零分布）

**场景**：条件/腔室/区域间比较，供体（非 bin/细胞）是统计单位。
**做法**：条件标签在**供体级**整体打乱（保切片内空间结构、破条件关联）≥1000 次 → 经验 p。
```python
# donors: list[str] 每个供体的条件标签；stat_fn(labels)->float
def perm_p_donor(donor_labels, stat_fn, n=1000, seed=0):
    rng = np.random.default_rng(seed)
    obs = stat_fn(donor_labels)
    null = [stat_fn(donor_labels[rng.permutation(len(donor_labels))])
            for _ in range(n)]
    return obs, (1 + sum(s >= obs for s in null)) / (1 + n)
```
**铁律**：标签打乱必须在**供体级**（bin 级打乱会低估方差 → p 虚小）。空间版见 `spatial_frontiers_2026.md` §3。

## R3 BH-FDR 检验族 + 跨时点符号一致性

**场景**：多簇×多通路×多时点的大型相关/检验矩阵（如 8 态×4 通路×3 时点=96 检验）。
**做法**：
```python
from statsmodels.stats.multitest import multipletests
q = multipletests(pvals, method='fdr_bh')[1]
# 符号一致性：同一 (state, pathway) 对在三时点是否同号（比"任一时点显著"更抗假阳）
sign_consistent = df.groupby(['state', 'pathway'])['rho'] \
                    .apply(lambda s: (np.sign(s) == np.sign(s.iloc[0])).all())
```
**报法**：q<0.05 计数 + "N/M 对三时点同号"；只报名义显著的须标 B 层。**注意重叠基因去循环**：若通路基因集含定义该态的 marker（如 stretch 程序含 NPPA 而态由 NPPA 定义），措辞降级为 "score overlap, interpret with care"。

## R4 split-reliability（n=1 切片的内部可重复性）

**场景**：空转每时点单切片、无生物学重复——审稿必问。给"内部可靠性"证据。
**做法**：median-x 切左右两半 + **三个 null 各配对的指标**：
| 指标 | 检验什么 | 正确的 null |
|---|---|---|
| 26 类组成相关 r | 组成谱两半一致 | **类型标签置换**（随机两半共享全局结构，空间随机切分 null 会退化到 r≈0.99 不可用） |
| 共丰度结构 r | 细胞类型共变结构 | **逐类型独立置换**（null 中位 ≈0） |
| domain/邻域 JS | 空间域构成稳定 | **同半随机子切分**作有限-bin 噪声底 |
**报法**（实例口径）：组成 r=0.93–0.95（p=0.002）、domain JS=0.003–0.007 bits 全超噪声底 5–74×；单侧独占 domain 如实报为真实偏侧解剖。JS 只在双侧共有 domain 上评。

## R5 参数敏感性扫描（模型推导类数字的必配）

**场景**：含假设参数的推导值（几何/力学/插值外推），审稿问"这个倍数稳吗"。
**做法**：关键参数 ±20% 扫描 → 报区间 + 依赖关系（线性/平方——σ∝d⁻¹ 线性、流量∝截面积 d² 平方）；换标定口径独立复核（例：CVO 名义 12.5×，±20% → 8.7–19.5×（平方）；体重标定口径独立得 9–11×，两种口径都报）。
**报法**："DERIVED via …; sensitive to X (range A–B×, linear/quadratic in X)"。外推点（如 13w 由 14/15w 段外推）必须显式标注。

## R6 掩膜/注释 LOO 稳健性（主观步骤的客观化）

**场景**：分析链含主观环节（视觉引导掩膜、种子选取、参考集选择）。
**做法**：逐个去掉输入（marker/种子/参照）重建 → 与全量版比：①逐单元一致率（分整体与 high-signal 子集两口径报，如 ≥93.4% 全 bins / ≥77.9% CM-high bins）；②关键统计在各变体下的稳定性（如 MYH6 atrial>ventricular 在 3 时点×9 变体全成立）。**不可分处如实报**（例：LV vs RV 在 bin 级 marker 上 |Δz|<0.1 → 只能几何分云并文档化）。
**报法**：一致率表 + 关键结论稳健性一句话；不一致子集（如某时点 ~25% bins 无 marker 支持）单独 caveat 该时点的专属比较。

## 使用顺序建议

投稿前加固 = R1/R2（CI+null）→ R3（校正族）→ R4（空间重复性）→ R5/R6（主观与推导环节）。
每条配方产物（表+CI）按 fig_tables 规则归档，caption 只从表引用（`stats_convention.md` §3 单一数字源）。

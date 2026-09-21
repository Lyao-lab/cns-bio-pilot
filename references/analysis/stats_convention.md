# 统计显著性口径与词汇表（单一权威页）

> 本页是「名义显著 / 多重校正 / 置信区间」三层口径的唯一出处。任何 figure
> caption、speaker notes、manuscript 里出现显著性表述时，一律引用本页；
> 其他 reference（cheatsheet A 系、meta_methodology §1、各子 skill）只许
> **指到本页**，不得各自复述。数字来自唯一计算源表（一次 runner 产出，
> 全链引用），禁止手写进文本。

## 1. 三层口径（任何结论先分它落在哪一层）

| 层 | 判定 | 允许措辞 | 禁止措辞 |
|---|---|---|---|
| **A 强证据** | BH / Bonferroni 校正后显著（或 bootstrap CI 不跨零且不接触） | 「显著」「robust」 | — |
| **B 名义显著** | 仅原始 p<0.05（或 permutation 名义 p），校正后不显著 | 「名义显著（nominal）」「提示性证据」「方向一致」 | 「显著」「证明」「驱动」 |
| **C 描述性** | 无正式检验（单时点空间、n=1、纯观察） | 「观察到」「descriptive」 | 任何显著性词汇 |

- **约定**：B 层必须同时报原始 p 和校正后 q（如 "p=0.027, BH ns"）；多方法
  互证（方向一致的 2+ 方法）可把 B 层提升为「方向稳健但效应量待验证」，
  仍不得写作 A 层。
- **空间分析**：每时点单切片（n=1/时点）一律 C 层；同一供体的 bin 间比较
  用 block bootstrap 给 CI，仍归 C 层（空间单元非独立重复）。

## 2. 词汇表（统计术语 → 用户可见措辞）

| 术语 | 面向用户的措辞 | 禁用 |
|---|---|---|
| nominal p | 「名义显著」「提示」 | 「显著」 |
| BH-adjusted | 「多重校正后显著」或「校正后不显著」 | 「不显著」（要保留"校正后"限定语） |
| bootstrap CI | 「置信区间不跨零/重叠」 | 「等于检验 p」 |
| donor-level n | 写明 n（如 "n=15 donors"） | 「大样本」 |
| pseudotime | 「成熟度排序」「时间顺序」 | 「真实时间」「年龄」 |
| CCC 关联 | 「associated with / enriched for」 | 「regulates / activates / drives」 |

## 3. 跨产物的单一数字源

一个生物学数字（如富集倍数 77x）只允许在**一个计算 runner** 里产出并写表
（`tables/.../*.csv`）；figure caption、speaker notes、manuscript 引用该表，
禁止在脚本里手写复制。改动数字 = 重跑 runner，下游全链自动更新。
（实战踩坑：fig2d 的「74x」是 19w 旧值，真值 77x，曾在 caption/title/notes
三处不一致——根源就是手写复制。）

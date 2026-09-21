# Big-Figure & Deck 实战 Playbook（presentation/figure-production 增补）

> 沉淀自两轮完整交付（fig1/fig2 atlas 全 deck 深度迭代 + CM 转化专题大 fig）。
> 与 dispatch_cheatsheet 的 B1–B7 互补：B 系管"单图"质量，本文件管"多面板组合体"
> （大 fig / PPT）的端到端管线、缓存、渲染与验收门。B 系未覆盖的机检项，
> 一律以 **§4 安全网** 的可执行检查替代"自觉"。

## §0 一句话经验

单图质量由 finalize_figure/B 系兜底；**组合体的失败几乎全在"跨图对齐、渲染放大后
才暴露、和缓存用了旧内容"三类**——所以流水线要显式管：布局几何、渲染保真、
内容寻址缓存、像素级验收门。

## §1 组合体流水线（deck-as-code 模板）

```
draw_*.py  —— 每面板独立脚本 + save_panel(png+pdf) + notebook 一图一 cell（A10）
   │            └─ 脚本内带画布级文字重叠断言（draw 时间验证，别指望 finalize 兜底）
compose_*.py（或 scripts/compose_bigfig.py） —— outline(JSON)/panel_rows + 逐面板排布几何
build_*_deck.py —— build_deck(skill) → 后处理链（下面的顺序不可省）：
   ① shrink(图, 上限px)      内容寻址缓存，文件名必须含 内容hash+max_px
   ② fit_captions()           按模拟换行降图注字号到 ≤ 框高，不删字
   ③ place_panels()           逐面板 add_picture（panel_rows 驱动），行宽公式
                              必须 (W − 间隙)/Σar，否则行块比画布宽、
                              边缘面板被居中推出画布
   ④ place_panels → shadow outline（读 json 后 panel_rows 里的 tuple 已变 list，
      isinstance 要兼容两种）
scripts/render_slides.py —— pptx→PNG 预览（保真版；E3）
pixel_gate.py    —— 每页底/右/顶缘 文字像素扫描；视觉模型抽检
```

## §2 布局与渲染几何

1. **行宽公式扣间隙**：heights = (W − gap×(n−1))/Σar。漏扣 → 行块 > W → 居中后
   边缘面板出画布（左缘截断真因，不是"缺边距"）。组合体外加 0.15in 白边。
2. **面板裁剪看"墨密度"，别看 ink bbox**：面板底部常有满宽脚注行，任何
   "有墨即留"的 bbox 都被它锁死；应测正文带（排除顶部 2%、底部 6%）的列密度，
   前导/尾随空白据此裁（cm02 6652→3317px、cm24 10013→6817 就是这么裁出来的）。
3. **渲染器保真**（自己写的 preview renderer 必须如此，否则验收门全是幻影）：
   - 字号 = 真实 pt（❌ 旧 bug：fs×100/72，物理放大 1.39× → 全 deck 11 页
     caption"截断"全是幻影）
   - 按**文本框宽**换行（❌ 旧 bug 按画布宽），用 PIL 精确测行数
   - 段落级字号回退 + 量宽用 Bold/Oblique/BoldOblique 字体族
4. **caption 自适应**：文本框几何（top≈6.85in、高 0.5in、10pt、宽 12.33in、
   页高 7.5in）只能容 ~3 行；用户要求统计留 legend 时常超 → fit_captions 按
   DejaVu 实宽模拟换行、行高 1.45em（YaHei 高行距），超 0.58in 降字号
   （10→7pt 阶梯，实际落 9.5–10pt），**一字不删**。

## §3 内容寻址缓存纪律（踩坑最凶的一类）

- shrink 派生文件命名 = `{stem}_{max_px}_{md5(content)[:12]}.png`。
  **max_px 进文件名**（同图两个上限会撞缓存）；**内容 hash 进文件名**防误复用。
- 任何"按输出路径/文件名直接复用"的缓存（裁剪目录、合成图）都必须校验
  源文件 mtime/hash，否则旧版本会静默进交付物（cm08 差点以三轮旧版进 deck）。
- 验收锚点 = 嵌入字节 md5 == 派生链末文件 md5，逐页比对。
- **分析产物同理**：派生 h5ad/表也属缓存——上游参数/数据变了必须重算，禁止复用旧产物；生成记录里写源 hash + 参数（接 D5 provenance）。

## §4 安全网（可执行机检清单——全做）

1. **draw 时**：画布级文字重叠断言（`ax.title`、刻度标签、图例、fig.texts 全部
   纳入 pairwise bbox——finalize 的 ax.texts 不含标题/图例，两处遗漏都被视觉门
   逐层揪出过）；断言对"聚类后行序 ≠ 原始行序"、"标签列让开树状图 ≥Npx"这类
   语义不变量。
2. **compose 后**：每页图片数 == 预期；图片两两无重叠、全部在内容区边界内、
   不压 caption 区。
3. **build 后**：每页 edge 扫描——最末 4 行/最右 6 列的深色像素占比 >1% 即
   有文字出界（caption 截断类问题字级检查测不出）。脚本：`scripts/edge_sweep.py <render_dir>`（exit≠0 = 有截断页）。
4. **嵌入链**：每页嵌入 md5 == 源→裁剪→shrink 派生链 md5。
5. **视觉门**：视觉模型只读**渲染后的 PNG**（绝不读 pptx/面板文件"当图片"），
   每页一行 JSON verdict；caption 完整性/语义数字抽查。幻觉率高 → 每次裁决
   都要它给出可定位的证据（x/y/引文），无证据的裁决不接。
6. **备注/叙述**：每页【方法】【意义】两段、湿实验友好白话 + 方法名括号保留
   （cell2location/BANKSY/pySCENIC/…，方便喂给 AI 复查）；统计边界用白话
   （"名义显著、多重校正后不显著 = 提示性证据"）。

## §5 反复踩过的坑（按根因归类）

**渲染/几何**
- tick_params(labelsize=8.5) 在 set_yticklabels(7.5) 之后执行 → 静默覆盖字号
  （旧布局两者同值从未暴露）。字号设定放最后，或 scope 到 axis。
- tight bbox 把越界 artist 也包进去 → PNG 比画布还宽 → hero fit 后显示宽度
  失真。加"无越界文本"断言。
- 面板自带的满宽脚注行锁死 ink bbox；大 fig 里单面板分区行高 = W/ar 会撑爆
  总高（cm 大 fig 曾到 32.5in）→ 双面板以上同行。

**数据/统计诚实性**
- 假前沿：绝对表达量差 100× 的两个基因不能直接算"交叉"——用每时点 min-max
  归一化后的程序指数；c2l 的 compact↔maturing 对级分辨率要全程 caveat。
- 视觉门读的是渲染图，面板自身的旧缺陷（角落字母压标题、坐标刻度相撞）
  会在 zoom 下被逐层揪出——所以终审一律在组合体渲染图上做，且要 zoom 到
  面板级。

**叙事组织**
- 大 fig 先行：deck 按大 fig 分区拆页，一页对应一分区，caption 与大 fig
  分区标题一致，避免两处叙事漂移。
- 面板字母（a/b/c）若面板本身已有 cm/fig 编号则不加（双编号互撞）。

## §6 交付格式（沿用会话规范）

① 做了什么（一句）② 产物清单（路径+用途）③ 验证证据（附图/表）④ 未做/存疑。
图表随回复 inline 截图；>200 行产物落盘后传路径。

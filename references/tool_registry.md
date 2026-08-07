# 工具注册表（Tool Registry）

> 本文件是 cns-bio-pilot 所有可调用工具的统一索引。主脑/worker 读这一个文件就知道"有哪些工具、每个工具怎么用"。
> verified = 已用真实数据测试通过；unverified = 未测试或依赖外部环境。
> 思路借鉴 OmicOS Beacon（工具契约标准化），但不做运行时探针验证（太重）。

## 绘图工具（scripts/cns_style.py，22 个统一入口）

### plot_umap | category: plotting | verified ✅
- **inputs**: adata(AnnData), color(str, obs列), basis='X_umap'
- **outputs**: PDF 到 panels/ + notebook 内显示
- **路由**: ov.pl.embedding 优先 → mpl scatter 兜底
- **相关规则**: B1(统一入口) B2(save_panel) B3(finalize)
- **机检**: finalize_figure 内置

### plot_volcano | category: plotting | verified ✅
- **inputs**: de(DataFrame), pval_name='padj', fc_name='log2FC'
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.volcano 优先 → mpl 三色兜底（up+down 都标注）
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_dotplot | category: plotting | verified ✅
- **inputs**: adata(AnnData), var_names(list), groupby='celltype', standard_scale='var'
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.dotplot 优先 → mpl scatter 矩阵兜底（含 size legend）
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_violin | category: plotting | verified ✅
- **inputs**: adata(AnnData), keys(str/list, obs/var 列), groupby='celltype'
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.violin 优先（交替背景+wilcox）→ mpl 兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_heatmap | category: plotting | verified ✅
- **inputs**: adata(AnnData), var_names(list), groupby='celltype', z_score=0
- **outputs**: PDF 到 panels/
- **路由**: sns/scanpy（ov 无独立函数），Z-score per row + 注释条
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_spatial | category: plotting | verified ✅
- **inputs**: adata_sp(AnnData spatial), color(str)
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.plot_spatial / sq.pl.spatial_scatter 优先 → mpl scatter 兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_bar | category: plotting | verified ✅
- **inputs**: props(DataFrame 或 adata+groupby 自动算比例), groupby=None, celltype_col='celltype'
- **outputs**: PDF 到 panels/
- **路由**: mpl（ov 无），带 95% CI error bars + per-sample dots
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_enrichment | category: plotting | verified ✅
- **inputs**: enr(DataFrame), top_n=15, term_col='Term', fdr_col='FDR', count_col='Gene_count'
- **outputs**: PDF 到 panels/
- **路由**: mpl barh，-log10(FDR) 降序，条右标 gene count
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_lr_bubble | category: plotting | verified ✅
- **inputs**: pair_labels(list), pathway_labels(list), sizes(array), mean_expr(array)
- **outputs**: PDF 到 panels/
- **路由**: mpl bubble，size=-log10(p)、color=mean expr，pair×pathway 矩阵
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_feature_matrix | category: plotting | verified ✅
- **inputs**: adata(AnnData), genes(list), basis='X_umap', ncols=3
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.embedding 多 color 优先 → mpl 多 subplot 兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_paga | category: plotting | verified ✅
- **inputs**: adata(AnnData, 含 paga), threshold=0.05, color=None
- **outputs**: PDF 到 panels/
- **路由**: sc.pl.paga 优先 → mpl+networkx 兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_chord | category: plotting | verified ✅
- **inputs**: weight_matrix(DataFrame, 细胞对×通路)
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.CellChatViz 优先 → mpl+networkx 兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_pseudotime | category: plotting | verified ✅
- **inputs**: adata(AnnData), genes(list), pseudotime_col='pseudotime', frac=0.3
- **outputs**: PDF 到 panels/
- **路由**: mpl LOESS 平滑 + 95% CI 带
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_cellproportion | category: plotting | verified ✅
- **inputs**: adata(AnnData), groupby='condition', celltype_col='celltype'
- **outputs**: PDF 到 panels/
- **路由**: ov.pl.cellproportion 优先 → mpl stacked bar 兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_de_scatter | category: plotting | verified ✅
- **inputs**: de_dict(dict, 组别→DE 表), pval_name='padj', fc_name='log2FC'
- **outputs**: PDF 到 panels/
- **路由**: mpl（ov 无）；多时点/多组时替代火山图，x=组别 y=logFC
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_spatial_ccc | category: plotting | verified ✅
- **inputs**: adata_sp(AnnData spatial), ligand(str), receptor(str), niche_col=None
- **outputs**: PDF 到 panels/
- **路由**: mpl 双面板（ligand/receptor 空间共表达，共享 colorscale）
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_milo | category: plotting | verified ✅
- **inputs**: milo_result(DataFrame, 含 Population/logFC/SpatialFDR), test_col='SpatialFDR', logfc_col='logFC', sig_threshold=0.1
- **outputs**: PDF 到 panels/
- **路由**: mpl beeswarm（ov 无），KNN 节点 logFC 按 population 分组
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_signaling_heatmap | category: plotting | verified ✅
- **inputs**: comm_scores(DataFrame, 行=cell type, 列=pathway), mode='outgoing'
- **outputs**: PDF 到 panels/
- **路由**: mpl（ov 无），outgoing/incoming 通讯强度热图
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_distance_distribution | category: plotting | verified ⚠️
- **inputs**: adata_sp(AnnData spatial), group_a/group_b(str 或 bool mask), groupby, spatial_key, n_perm=100
- **outputs**: PDF 箱线图 + 置换检验 p 值标注
- **路由**: mpl + scipy cKDTree（最近邻距离），置换检验双侧经验 p
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_nhood_enrichment | category: plotting | verified ⚠️
- **inputs**: adata_sp(AnnData spatial, 需 obsp['spatial_connectivities']), cluster_key='celltype'
- **outputs**: PDF 邻域富集热图（z-score, */** 显著标注）
- **路由**: squidpy.gr.nhood_enrichment 优先 → mpl 手动共邻计数兜底
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_colocalization | category: plotting | verified ⚠️
- **inputs**: adata_sp(AnnData spatial), var_x/var_y(基因名或 obs 比例列), method='spearman', groupby
- **outputs**: PDF 共定位散点（ρ + p 标注，>5000 点自动 hexbin）
- **路由**: mpl（ov 无），scipy.stats spearmanr/pearsonr
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

### plot_enrichment_scatter | category: plotting | verified ⚠️
- **inputs**: enr_df(DataFrame, GO/KEGG/GSEA), x='GeneRatio', y='FDR', size='Count', color='FDR', top_n=15
- **outputs**: PDF 富集气泡散点（5 维：x/y/size/color/term 标注）
- **路由**: mpl（ov 无），-log10(FDR) 降序取 top_n 标通路名
- **相关规则**: B1 B2 B3
- **机检**: finalize_figure 内置

## 校验脚本（4 个）

### postcheck.py | category: validation | verified ✅
- **inputs**: target(AnnData .h5ad / DE 表 .csv/.tsv / HTML / 代码文件 或目录), --type {adata,de,deconv,velocity,slides,code}, --lang
- **outputs**: 检查报告（stdout），PASS/FAIL 逐项
- **路由**: scripts/postcheck.py，每步分析后跑
- **相关规则**: A1 及各级 postcheck 门禁
- **机检**: 内置断言（counts layer 存在性等）

### api_check.py | category: validation | verified ✅
- **inputs**: --package {omicverse, pertpy, ...}, --diff（installed vs compat.yaml）, --skill-dir
- **outputs**: 环境兼容性检查报告（stdout）
- **路由**: scripts/api_check.py，§0 Init 环境校验
- **相关规则**: §5 compat.yaml 版本契约
- **机检**: 比对 compat.yaml 中 verified 版本

### qa_deck.py | category: validation | verified ✅
- **inputs**: pptx(output .pptx 路径)
- **outputs**: QA 报告（stdout），逐项 check 结果
- **路由**: skills/presentation/scientific-slides/scripts/qa_deck.py
- **相关规则**: 演示文稿交付前 QA 门禁
- **机检**: 内置 check(pptx_path)

### validate_presentation.py | category: validation | unverified ⚠️
- **inputs**: filepath(PDF/PPTX/PPT/TEX), --duration/-d 分钟数, --quiet/-q
- **outputs**: 校验结果（slide 数与时长、文件大小、尺寸、PPTX 字号、Beamer 编译）
- **路由**: skills/presentation/scientific-slides/scripts/validate_presentation.py
- **相关规则**: 演示文稿交付前校验
- **机检**: 内置 PresentationValidator.validate()

## 渲染/组装（3 个）

### build_deck.py | category: rendering | unverified ⚠️
- **inputs**: outline(.json 大纲), -o/--output, --preset {cns-bio-light, ...}
- **outputs**: .pptx 演示文稿
- **路由**: skills/presentation/scientific-slides/scripts/build_deck.py
- **相关规则**: 大纲→PPT 组装，variant 布局（title/section/figure-hero/figure-dual/split-compare 等）
- **机检**: 安全区域防重叠检查内置

### main.py | category: rendering | unverified ⚠️
- **inputs**: --input(1+ 个 panel 文件 PNG/JPG/TIFF/PDF), --output, --layout('2x3'/'3x2' 等), --dpi=300, --label-size, --padding
- **outputs**: 组装后的多面板 figure（PDF/PNG）
- **路由**: skills/visualization/figure-production/scripts/main.py
- **相关规则**: 多 panel 拼合 + 自动标签
- **机检**: 无（输出可人工目检）

### generate_schematic.py | category: rendering | verified ✅
- **inputs**: --template({feedback_loop, flow, comparison, ...}), --params(JSON 或文件), -o/--output, --dpi=300
- **outputs**: 示意图 PNG/PDF
- **路由**: skills/visualization/scientific-schematics/scripts/generate_schematic.py
- **相关规则**: 模式化示意图生成
- **机检**: 无（输出可人工目检）

### build_report.py | category: rendering | verified ✅
- **inputs**: report.json（含 title/subtitle/sections[]，6 种 section type: summary/findings/figure/table/ledger/methods）
- **outputs**: 自包含 report.html（base64 内联图片，CSS 内联，无 JS，双击打开）
- **路由**: `python build_report.py report.json -o report.html`
- **依赖**: Python 标准库 + pymupdf（PDF→PNG，与 build_deck.py 一致）
- **相关规则**: Core Rule 10（交付门）+ 溯源标签 [实测]/[文献]/[推断]（meta §8c）
- **机检**: 无（浏览器打开目检）

## 辅助函数（scripts/cns_style.py）

### save_panel | category: helper | verified ✅
- **inputs**: fig(matplotlib Figure), name(无扩展名), outdir='panels', journal=True, fmt='pdf', show=None
- **outputs**: 面板文件到 outdir/ + stdout 打印路径
- **路由**: 统一 save 入口：finalize_figure → mkdir → savefig → close/display
- **相关规则**: B2(save_panel) B3(finalize)
- **机检**: finalize_figure 强制内置

### finalize_figure | category: helper | verified ✅
- **inputs**: fig(matplotlib Figure), move_legend_right=True, check_overlap=True, check_rasterize=True
- **outputs**: 就地修正 fig（图例移右侧、重叠告警、栅格化告警）
- **路由**: 每个 savefig 前强制调用
- **相关规则**: B3(finalize)、铁律 1/2
- **机检**: 自身即机检（text overlap + rasterize 检查）

### assert_anndata_keys | category: helper | verified ✅
- **inputs**: adata(AnnData), obs_cols=None, obsm_keys=None, var_names=None
- **outputs**: 校验通过返回 None；缺失 raise ValueError（列出可用项）
- **路由**: 分析函数入口防御校验
- **相关规则**: 对标 ov-skills 防御校验模式
- **机检**: 纯校验，无图

### set_cns_style_journal | category: helper | verified ✅
- **inputs**: journal='generic'('nature'/'nature_double'/'science'/'cell'/'generic'), palette='morlandi'('okabe_ito')
- **outputs**: 就地设置 rcParams（CNS 美学 + journal 尺寸/字体）
- **路由**: 脚本开头调用一次，替代 set_cns_style
- **相关规则**: 出刊尺寸规范
- **机检**: 无

### cohort_params | category: helper | verified ✅
- **inputs**: n_cells(int)
- **outputs**: dict(point_size, alpha, figsize)，按 cohort 规模映射
- **路由**: 绘图函数内部自动调用（大 cohort 自动降 size/alpha）
- **相关规则**: 大 cohort 可视化经验映射
- **机检**: 无

### ForbiddenCityBridge | category: helper | verified ✅
- **inputs**: 色名(str, 中文命名色，如 '霁蓝')；get(name) → hex
- **outputs**: hex 色值；ov 可用则精确色，否则 fallback
- **路由**: ov.pl.ForbiddenCity() 命名色板桥，最小环境不崩溃
- **相关规则**: 命名色板统一入口
- **机检**: 无
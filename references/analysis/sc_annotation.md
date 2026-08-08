# 注释 + 差异分析 + 富集 + 比例

## 3. 注释 + 差异分析 + 富集 + 比例

### 3.1 Marker + 注释
```python
# 来源：omicverse-pipeline §8
ov.single.find_markers(adata, groupby='leiden', method='wilcoxon')
# groupby 必需！默认 method='cosg'（稀有群体更稳但慢）

# ⭐ 推荐方式：统一注释类（自动跑 CellTypist/SCSA/scMulan/MetaTiME/GPT4CellType）
obj = ov.single.Annotation(adata)
result = obj.annotate(method='scsa', tissuename='PBMC', speciename='human')
# 结果列：scsa_prediction（annotate 输出 <method>_prediction）
obj.annotate(method='celltypist')              # → celltypist_prediction
obj.annotate(method='MetaTiME', mode='table', resolution=8)  # → MetaTiME
# 其他 method：'gpt4celltype'（→ gpt4celltype_prediction）、'scMulan'（需先 obj.download_scmulan_ckpt()）

# 旧 API（仍可用）：
ov.single.pySCSA(adata)             # 无参考，marker→自动注释
ov.single.AnnotationRef(adata, adata_ref=ref_adata, celltype_key='celltype')
# ref_adata 必须是 AnnData 对象（不是字符串）
```

### 3.2 Pseudobulk DE（Core Rule 2 必须）
```python
# 来源：omicverse-pipeline §8.5（API 签名以 ov 2.3.1 实测为准）
# ⭐ 快速探索：ov 封装的条件间 per-cell DE（wilcoxon / memento-de）
deg_obj = ov.single.DEG(adata, condition='condition',
    ctrl_group='Control', test_group='Disease', method='wilcoxon')
deg_obj.run(celltype_key='celltype', celltype_group=['FB'])
# 注意：per-cell DE 只是快速探索；发表用 pseudobulk（下方 pyDEG）——pseudobulk 仍是金标准

# Step 1: 聚合到 pseudobulk（sample × celltype）
pb = sc.get.aggregate(adata, by=['sample', 'celltype'], func='sum', layer='counts')
# ⚠️ 必须用 raw counts layer（不是 normalized .X）

# Step 2: 转成 pyDEG 需要的格式（行=基因, 列=样本, 值=整数 counts）
from scipy.sparse import issparse
import pandas as pd, numpy as np
X = pb.X.toarray() if issparse(pb.X) else np.asarray(pb.X)
count_df = pd.DataFrame(X.T, index=pb.var_names, columns=pb.obs['sample'].values)

# Step 3: DE（pyDEG 是 pyDESeq2 底层封装，只接受 count DataFrame）
deg = ov.bulk.pyDEG(count_df)
# ⚠️ pyDEG 不接受 groupby/vs/celltype_key 参数——它是底层接口
# 如需按 condition 对比，用 pyDESeq2 原生 API + design matrix

# ⚠️ 禁止 per-cell Wilcoxon 当 DE 报告（Core Rule 2）
# 必须有 ≥3 biological replicates per condition
```

### 3.3 富集分析
```python
# 来源：omicverse-bulk §4（API 签名以 ov 2.3.1 实测为准）
# ⚠️ geneset_enrichment 需要 pathways_dict（基因集字典）
# 用 ov.utils.geneset_prepare 获取，或传字符串用 Enrichr 内置库
pathway_dict = ov.utils.geneset_prepare('GO_Biological_Process_2023', organism='Human')
# 或直接传 Enrichr 库名字符串
result = ov.bulk.geneset_enrichment(gene_list=up_genes,
                                     pathways_dict=pathway_dict,
                                     organism='Human')  # ⚠️ organism 不是 org
ov.bulk.geneset_plot(adata)
```

### 3.4 细胞比例/差异丰度
```python
# 来源：omicverse-pipeline §9c
# ⚠️ 禁止 chi-square/Fisher 检验比例（违反 compositional 约束）

# ⭐ ov 封装的差异丰度（内置 sccoda/milopy/milo，不再需要 standalone R/Python 工具）
dct_obj = ov.single.DCT(adata, condition='condition',
    ctrl_group='Control', test_group='Disease',
    cell_type_key='celltype', method='sccoda', sample_key='sample')
# milopy/milo 需要先 batch correction：use_rep='X_pca_harmony'
# 例：ov.single.DCT(adata, condition='condition', ctrl_group='Ctrl', test_group='Dis',
#                   cell_type_key='celltype', method='milo', use_rep='X_pca_harmony')

# 可视化（ov 有）：
# ov.pl.cellproportion(adata, celltype_clusters='celltype', groupby='condition', legend=True)
```

### 3.5 高级分析工具 ⭐ 新增
```python
# 来源：omicverse-pipeline + omicverse-analysis（API 签名以 ov 2.3.1 实测为准）
# SCENIC：转录因子调控网络分析（CNS 文章标配）
scenic = ov.single.SCENIC(adata, db_glob='cytolambda.db', motif_path='motifs.tbl',
                          n_jobs=8, species='human')

# CNV：拷贝数变异推断（肿瘤研究标配）
ov.single.CNV(adata, method='infercnv', genome='hg38')

# Augur：细胞类型优先级排序（哪些 celltype 对条件变化最敏感）
augur = ov.single.Augur(adata, label_col='condition', cell_type_col='celltype')
result = augur.predict()

# MetaCell：元细胞分析（降低噪声、提高统计效力）
mc = ov.single.MetaCell(adata, method='seacells', use_rep='X_pca', n_metacells=250)

# Milo：Milo 差异丰度（独立类，与 DCT 互补）
milo = ov.single.Milo()

# CellVote：投票法整合多个注释结果
cv = ov.single.CellVote(adata)
```

### 3.6 Celltype annotation transfer（跨数据集注释迁移）
```python
# ⭐ 从已注释的参考数据集迁移注释到新数据集
# ov 提供多种 transfer 方式，常用 scanpy 的 ingest 或 ov.single.Annotation 的 ref 模式
# 参考方式（reference-based annotation）：
obj = ov.single.Annotation(adata)
obj.annotate(method='scsa', tissuename='heart', speciename='human')
# 或用参考数据集：
ov.single.AnnotationRef(adata, adata_ref=ref_adata, celltype_key='celltype')
# scanpy ingest 方式（经典）：
sc.tl.ingest(adata, ref_adata, obs='celltype')
```


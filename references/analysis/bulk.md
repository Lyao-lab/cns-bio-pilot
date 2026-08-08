# Bulk RNA-seq 分析

## 6. Bulk 分析

### 6.1 Batch correction + DE
```python
# 来源：omicverse-bulk §2-3（API 以 ov 2.3.1 实测为准）
ov.bulk.batch_correction(adata, batch_key='batch')
# pyDEG 接受 count DataFrame（行=基因, 列=样本）
count_df = adata.to_df().T  # AnnData → DataFrame 转置
deg = ov.bulk.pyDEG(count_df)
```

### 6.2 富集 + GSEA
```python
# 来源：omicverse-bulk §4（API 以 ov 2.3.1 实测为准）
pathway_dict = ov.utils.geneset_prepare('GO_Biological_Process_2023', organism='Human')
ov.bulk.geneset_enrichment(gene_list=up_genes, pathways_dict=pathway_dict, organism='Human')
# GSEA: gene_rnk 是 ranked DataFrame
ov.bulk.pyGSEA(gene_rnk=rank_df, pathways_dict=pathway_dict, organism='Human')
ov.bulk.geneset_plot(adata)
```

### 6.3 共表达网络
```python
# 来源：omicverse-bulk §5
ov.bulk.pyWGCNA(adata, method='signed')   # 'signed'|'unsigned'
```

### 6.4 其他 Bulk 工具 ⭐ 新增
```python
# 来源：omicverse-bulk（API 签名以 ov 2.3.1 实测为准）
# pyGSEA / geneset_enrichment_GSEA：GSEA 富集（需 ranked list）
ov.bulk.pyGSEA(gene_rnk, pathways_dict, processes=4, permutation_num=1000)

# geneset_plot_multi：多通路富集结果合并可视化
ov.bulk.geneset_plot_multi(enr_dict, num=10)

# pyPPI：蛋白互作网络
ov.bulk.pyPPI(gene='TP53', species='human')

# deseq2_normalize：DESeq2 归一化（size factor）
adata.X = ov.bulk.deseq2_normalize(adata.to_df())
```


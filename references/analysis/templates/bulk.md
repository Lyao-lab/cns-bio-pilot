# Bulk RNA-seq 分析

> **本文件 = 可执行代码模板层**（怎么调 API，照抄并按数据改造）。方法选型与"为什么"见知识层：[`../decision_guide.md`](../decision_guide.md)（生物学问题→方法）、[`../analysis_flow.md`](../analysis_flow.md)（结果→下一步）。执行警告（参数名/顺序/obsm key）就在代码注释里，随片段一起拷贝。

## Bulk 分析

### Batch correction + DE
```python
ov.bulk.batch_correction(adata, batch_key='batch')
# pyDEG 接受 count DataFrame（行=基因, 列=样本）
count_df = adata.to_df().T  # AnnData → DataFrame 转置
deg = ov.bulk.pyDEG(count_df)
```

### 富集 + GSEA
```python
pathway_dict = ov.utils.geneset_prepare('GO_Biological_Process_2023', organism='Human')
enr = ov.bulk.geneset_enrichment(gene_list=up_genes, pathways_dict=pathway_dict, organism='Human')
# GSEA: gene_rnk 是 ranked DataFrame
ov.bulk.pyGSEA(gene_rnk=rank_df, pathways_dict=pathway_dict, organism='Human')
ov.bulk.geneset_plot(enrich_res=enr)   # 收富集结果 DataFrame，不是 adata
```

### 共表达网络
```python
ov.bulk.pyWGCNA(anndata=adata, networkType='signed', powers=12)   # 数据走 anndata=；networkType（非 method）；powers=软阈值
```

### 其他 Bulk 工具
```python
# pyGSEA / geneset_enrichment_GSEA：GSEA 富集（需 ranked list）
ov.bulk.pyGSEA(gene_rnk, pathways_dict, processes=4, permutation_num=1000)

# geneset_plot_multi：多通路富集结果合并可视化
ov.bulk.geneset_plot_multi(enr_dict, colors_dict, num=10)   # colors_dict 必填

# pyPPI：蛋白互作网络
ov.bulk.pyPPI(gene=gene_list, species=9606, gene_type_dict={}, gene_color_dict={}, score=0.4)
# species=NCBI 分类 id（human 9606 / mouse 10090）；gene_type_dict/gene_color_dict 必填；阈值是 score（非 score_thresh）

# deseq2_normalize：DESeq2 归一化（size factor）
adata.X = ov.bulk.deseq2_normalize(adata.to_df())
```

### Bulk 批次校正
```python
# ⭐ Bulk RNA-seq 批次校正（消除批次效应后再做 DE）
ov.bulk.batch_correction(adata, batch_key='batch', key_added='X_corrected')
# 校正后再跑 DE：ov.bulk.pyDEG(...)
```


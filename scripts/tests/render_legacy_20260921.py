#!/usr/bin/env python
"""render_legacy_20260921 — 存量模板打磨回归 harness（2026-09-21 第二批）。

覆盖本批回灌之外的存量 plot_* 模板（表达/统计/空间/CCC 四族），合成数据渲染。
产出：--outdir（默认 /tmp/cns_legacy_test）PNG。每个 demo 独立 try/except，
单图失败不阻塞其余；结尾打印 PASS/FAIL 台账。

用法：~/miniforge3/envs/sc/bin/python scripts/tests/render_legacy_20260921.py
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import cns_style
from cns_style import (
    set_cns_style, save_panel, polish_axes,
    plot_volcano, plot_dotplot, plot_violin, plot_heatmap, plot_ridge,
    plot_boxplot, plot_umap, plot_feature_matrix, plot_bar, plot_bardotplot,
    plot_kde, plot_histplot, plot_stripplot, plot_regplot, plot_forest,
    plot_upset, plot_venn, plot_radar, plot_raincloud, plot_de_scatter,
    plot_milo, plot_enrichment_scatter, plot_lr_bubble, plot_pca_variance,
    plot_hvg_scatter, plot_cellproportion, plot_stacking_vol, plot_spatial,
    plot_paga, plot_pseudotime, plot_distance_distribution,
    plot_nhood_enrichment, plot_colocalization, plot_deconv_pie, plot_ccc,
    plot_chord, plot_ccc_network, plot_signaling_heatmap, plot_ccc_heatmap,
    plot_spatial_ccc,
)

OUT = sys.argv[sys.argv.index('--outdir') + 1] if '--outdir' in sys.argv \
    else '/tmp/cns_legacy_test'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(2026)
set_cns_style()

RESULTS = []
DEMOS = []


def demo(name):
    def wrap(fn):
        DEMOS.append((name, fn))
        return fn
    return wrap


def _save(fig, name):
    if isinstance(fig, tuple):
        fig = fig[0]
    if fig is not None:
        save_panel(fig, name, outdir=OUT, fmt='png', journal=False,
                   show=False)


# ---------------- 合成数据（一次性构建） ----------------
TYPES = ['vCM', 'FB', 'EC', 'Mac', 'T']
N_PER = 500
GENES = [f'G{i:03d}' for i in range(360)] + \
    ['MK_CM1', 'MK_CM2', 'MK_FB1', 'MK_FB2', 'MK_EC1', 'MK_MK1', 'MK_T1']

def _expr_adata():
    import anndata as ad
    from scipy import sparse
    n = N_PER * len(TYPES)
    X = rng.negative_binomial(2, 0.6, (n, len(GENES))).astype(np.float32)
    X = np.log1p(X)
    ct = np.repeat(TYPES, N_PER)
    for k, mk in enumerate(['MK_CM1', 'MK_CM2', 'MK_FB1', 'MK_FB2',
                            'MK_EC1', 'MK_MK1', 'MK_T1']):
        j = GENES.index(mk)
        X[ct == TYPES[min(k // 2, 4)], j] += rng.uniform(1.5, 2.5)
    obs = pd.DataFrame({
        'celltype': pd.Categorical(ct, categories=TYPES),
        'sample': pd.Categorical(np.repeat(
            [f'D{i:02d}' for i in range(5)], n // 5)),
        'condition': pd.Categorical(np.repeat(
            ['ctrl', 'treat'], n // 2)),
        'pseudotime': np.sort(rng.uniform(0, 1, n)),
    })
    # UMAP：每类型一个高斯团 + 轻微重叠
    centers = np.array([[0, 0], [3, 0.5], [1.5, 3], [-1.5, 2.5], [4, 3]])
    umap = np.vstack([c + rng.normal(0, 0.55, (N_PER, 2)) for c in centers])
    pc_centers = rng.normal(0, 3, (len(TYPES), 10))
    pca = np.vstack([c + rng.normal(0, 0.7, (N_PER, 10))
                     for c in pc_centers])
    a = ad.AnnData(X=sparse.csr_matrix(X), obs=obs,
                   var=pd.DataFrame(index=GENES))
    a.obsm['X_umap'] = umap
    a.obsm['X_pca'] = pca
    a.var['highly_variable'] = rng.random(len(GENES)) < 0.2
    a.var['means'] = np.asarray(X.mean(0)).ravel()
    a.var['dispersions'] = np.asarray(X.std(0)).ravel() ** 2
    a.uns['pca'] = {'variance_ratio':
                    np.sort(rng.uniform(0.02, 0.15, 30))[::-1]}
    a.uns['log1p'] = {'base': None}
    a.layers['counts'] = sparse.csr_matrix(
        np.expm1(X).astype(int).clip(0, None))
    return a


def _spatial_adata():
    import anndata as ad
    from scipy import sparse
    n = 3200
    c1 = rng.normal([2200, 2200], [700, 520], (n // 2, 2))
    c2 = rng.normal([4200, 2800], [520, 640], (n // 4, 2))
    c3 = rng.uniform([200, 200], [6000, 5000], (n - n // 2 - n // 4, 2))
    xy = np.vstack([c1, c2, c3])
    d_c1 = np.exp(-(((xy[:, 0] - 2200) / 500) ** 2 +
                    ((xy[:, 1] - 2200) / 380) ** 2))
    d_c2 = np.exp(-(((xy[:, 0] - 4200) / 380) ** 2 +
                    ((xy[:, 1] - 2800) / 450) ** 2))
    lig = np.clip(d_c1 + rng.uniform(0, 0.08, n), 0, 1.3)
    rec = np.clip(d_c2 + rng.uniform(0, 0.08, n), 0, 1.3)
    cm_prop = np.clip(d_c1 + rng.normal(0.1, 0.1, n), 0.01, 0.98)
    fb_prop = np.clip(d_c2 + rng.normal(0.1, 0.1, n), 0.01, 0.9)
    ec_prop = np.clip(1 - cm_prop - fb_prop, 0.01, None)
    tot = cm_prop + fb_prop + ec_prop
    obs = pd.DataFrame({
        'celltype': pd.Categorical(
            np.where(cm_prop / tot > 0.45, 'CM',
                     np.where(fb_prop / tot > 0.4, 'FB', 'EC')),
            categories=['CM', 'FB', 'EC']),
        'ligand_score': lig, 'receptor_score': rec,
        'prop_CM': cm_prop / tot, 'prop_FB': fb_prop / tot,
        'prop_EC': ec_prop / tot,
        'region': pd.Categorical(np.where(xy[:, 0] < 3200, 'zoneA', 'zoneB')),
    })
    X = np.zeros((n, 4))
    X[:, 0] = lig; X[:, 1] = rec
    X[:, 2] = rng.negative_binomial(2, 0.7, n).astype(float)
    X[:, 3] = rng.negative_binomial(3, 0.5, n).astype(float)
    a = ad.AnnData(X=sparse.csr_matrix(X), obs=obs,
                   var=pd.DataFrame(index=['LIG1', 'REC1', 'BG1', 'BG2']))
    a.obsm['spatial'] = xy
    # kNN 空间连接图（nhood_enrichment 需要）
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=6).fit(xy)
    _, idx = nn.kneighbors(xy)
    rows = np.repeat(np.arange(n), 6)
    cols = idx.ravel()
    a.obsp['spatial_connectivities'] = sparse.csr_matrix(
        (np.ones(len(rows)), (rows, cols)), shape=(n, n))
    return a


def _de(n=400, seed=0):
    r = np.random.default_rng(seed)
    fc = r.normal(0, 1.2, n)
    padj = 10 ** r.uniform(-8, -0.3, n)
    padj = np.where(np.abs(fc) > 1, padj / 50, padj)
    return pd.DataFrame({'gene': [f'G{i:03d}' for i in range(n)],
                         'padj': padj, 'log2FC': fc}).set_index('gene')


ADATA = _expr_adata()
SP = _spatial_adata()

# ---------------- 表达族 ----------------
@demo('L01_volcano')
def _(): return _save(plot_volcano(_de(), annotate_top=8), 'L01_volcano')

@demo('L02_dotplot')
def _():
    mks = ['MK_CM1', 'MK_CM2', 'MK_FB1', 'MK_FB2', 'MK_EC1', 'MK_MK1',
           'MK_T1', 'G001', 'G050', 'G120']
    return _save(plot_dotplot(ADATA, mks, groupby='celltype'), 'L02_dotplot')

@demo('L03_violin')
def _():
    return _save(plot_violin(ADATA, ['MK_CM1', 'MK_FB1'],
                             groupby='celltype'), 'L03_violin')

@demo('L04_heatmap')
def _():
    return _save(plot_heatmap(ADATA, ['MK_CM1', 'MK_FB1', 'MK_EC1',
                                      'MK_MK1', 'MK_T1', 'G010'],
                              groupby='celltype'), 'L04_heatmap')

@demo('L05_ridge')
def _():
    return _save(plot_ridge(ADATA, ['MK_CM1'], groupby='celltype'),
                 'L05_ridge')

@demo('L06_boxplot')
def _():
    return _save(plot_boxplot(ADATA, ['MK_EC1', 'MK_T1'],
                              groupby='celltype'), 'L06_boxplot')

# ---------------- embedding 族 ----------------
@demo('L07_umap')
def _(): return _save(plot_umap(ADATA, color='celltype'), 'L07_umap')

@demo('L08_feature_matrix')
def _():
    return _save(plot_feature_matrix(ADATA, ['MK_CM1', 'MK_FB1', 'MK_EC1',
                                             'MK_MK1', 'MK_T1', 'G002'],
                                     ncols=3), 'L08_feature_matrix')

# ---------------- 统计族 ----------------
@demo('L09_bar')
def _():
    props = (ADATA.obs.groupby('sample')['celltype'].value_counts()
             .unstack(fill_value=0).apply(lambda r: r / r.sum(), axis=1))
    return _save(plot_bar(props), 'L09_bar')

@demo('L10_cellproportion')
def _():
    return _save(plot_cellproportion(ADATA, groupby='sample',
                                     celltype_col='celltype'),
                 'L10_cellproportion')

@demo('L11_bardotplot')
def _():
    return _save(plot_bardotplot(ADATA, groupby='celltype',
                                 color='MK_CM1'), 'L11_bardotplot')

@demo('L12_kde')
def _():
    df = pd.DataFrame({'ga': rng.uniform(13, 24, 300),
                       'score': rng.normal(0, 1, 300) +
                       (rng.uniform(13, 24, 300) - 18) * 0.15,
                       'group': rng.choice(['A', 'B'], 300)})
    return _save(plot_kde(df, x='ga', y='score', hue='group'), 'L12_kde')

@demo('L13_histplot')
def _():
    df = pd.DataFrame({'mito': np.clip(rng.gamma(3, 1.8, 800), 0.5, 25),
                       'batch': rng.choice(['b1', 'b2', 'b3'], 800)})
    return _save(plot_histplot(df, x='mito', hue='batch'), 'L13_histplot')

@demo('L14_stripplot')
def _():
    df = pd.DataFrame({'score': np.concatenate(
        [rng.normal(m, 0.5, 40) for m in (0.2, 0.5, 0.8)]),
        'state': ['s1'] * 40 + ['s2'] * 40 + ['s3'] * 40})
    return _save(plot_stripplot(df, x='state', y='score'), 'L14_stripplot')

@demo('L15_regplot')
def _():
    df = pd.DataFrame({'ga': rng.uniform(13, 24, 120),
                       'score': rng.normal(0, 0.4, 120)})
    df['score'] += (df['ga'] - 18) * 0.12
    return _save(plot_regplot(df, x='ga', y='score', fit='lowess'),
                 'L15_regplot')

@demo('L16_forest')
def _():
    est = rng.uniform(0.4, 1.6, 7)
    df = pd.DataFrame({'study': [f'Study {i}' for i in range(1, 8)],
                       'or': est, 'lo': est - rng.uniform(0.1, 0.4, 7),
                       'hi': est + rng.uniform(0.1, 0.5, 7)})
    return _save(plot_forest(df, estimate='or', lower='lo', upper='hi',
                             label='study'), 'L16_forest')

@demo('L17_upset')
def _():
    base = set(range(300))
    sets = {'E15': set(rng.choice(300, 100, replace=False)),
            'E18': set(rng.choice(300, 110, replace=False)),
            'P0': set(rng.choice(300, 90, replace=False)),
            'P7': set(rng.choice(300, 70, replace=False))}
    return _save(plot_upset(sets), 'L17_upset')

@demo('L18_venn')
def _():
    sets = {'E15': set(rng.choice(200, 80, replace=False)),
            'E18': set(rng.choice(200, 90, replace=False)),
            'P0': set(rng.choice(200, 70, replace=False))}
    return _save(plot_venn(sets), 'L18_venn')

@demo('L19_radar')
def _():
    vals = np.array([[0.9, 0.6, 0.3, 0.75, 0.5],
                     [0.4, 0.8, 0.65, 0.35, 0.7]]) * np.array(
        [[80, 12, 950, 0.85, 320], [80, 12, 950, 0.85, 320]])
    return _save(plot_radar(vals, ['ARI', 'NMI', 'kBET', 'LISI', 'ASW'],
                            series_names=['method A', 'method B'],
                            axis_ranges=[(0, 1), (0, 20), (0, 1000),
                                         (0, 1), (0, 500)]), 'L19_radar')

@demo('L20_raincloud')
def _():
    df = pd.DataFrame({'score': np.concatenate(
        [rng.normal(m, s, n) for m, s, n in
         [(0.2, 0.15, 12), (0.45, 0.2, 9), (0.8, 0.18, 14)]]),
        'state': ['s1'] * 12 + ['s2'] * 9 + ['s3'] * 14})
    return _save(plot_raincloud(df, x='state', y='score', test='mwu'),
                 'L20_raincloud')

@demo('L21_de_scatter')
def _():
    dd = {c: _de(seed=s) for s, c in enumerate(['E15', 'E18', 'P0'])}
    return _save(plot_de_scatter(dd), 'L21_de_scatter')

@demo('L22_milo')
def _():
    df = pd.DataFrame({'SpatialFDR': 10 ** rng.uniform(-4, -0.2, 300),
                       'logFC': rng.normal(0, 0.8, 300),
                       'Population': rng.choice(
                           ['n1', 'n2', 'n3', 'n4', 'n5'], 300)})
    return _save(plot_milo(df), 'L22_milo')

@demo('L23_enrichment_scatter')
def _():
    enr = pd.DataFrame({
        'Term': ['collagen fibril organization', 'angiogenesis',
                 'cell cycle checkpoint', 'DNA replication',
                 'mitotic nuclear division', 'VEGF signaling',
                 'muscle contraction', 'oxidative phosphorylation',
                 'ribosome biogenesis', 'WNT signaling'],
        'FDR': 10 ** rng.uniform(-8, -1, 10),
        'GeneRatio': rng.uniform(0.05, 0.4, 10),
        'Count': rng.integers(5, 80, 10)})
    return _save(plot_enrichment_scatter(enr), 'L23_enrichment_scatter')

@demo('L24_lr_bubble')
def _():
    pairs = [f'L{i}—R{i}' for i in range(1, 9)]
    paths = ['WNT', 'TGFb', 'BMP', 'VEGF', 'NOTCH']
    sizes = rng.uniform(1, 60, (8, 5))
    mean_expr = rng.uniform(0, 4, (8, 5))
    return _save(plot_lr_bubble(pairs, paths, sizes, mean_expr),
                 'L24_lr_bubble')

@demo('L25_pca_variance')
def _(): return _save(plot_pca_variance(ADATA, n_pcs=15), 'L25_pca_variance')

@demo('L26_hvg_scatter')
def _(): return _save(plot_hvg_scatter(ADATA), 'L26_hvg_scatter')

@demo('L27_stacking_vol')
def _():
    dd = {c: _de(seed=s + 10) for s, c in enumerate(['E15', 'E18', 'P0'])}
    return _save(plot_stacking_vol(dd, save=f'{OUT}/L27_stacking_vol'),
                 'L27_stacking_vol')

# ---------------- 空间/CCC 族 ----------------
@demo('L28_spatial')
def _(): return _save(plot_spatial(SP, color='ligand_score'), 'L28_spatial')

@demo('L29_paga')
def _():
    # sc.tl.paga 对高分离合成数据会因 igraph 边表为空而失败（工具链问题，
    # 非模板问题）；直接构造 uns['paga'] 测绘图链路
    from scipy import sparse
    a = ADATA.copy()
    W = rng.uniform(0, 1, (5, 5)); W = (W + W.T) / 2; np.fill_diagonal(W, 0)
    a.uns['paga'] = {'connectivities': sparse.csr_matrix(W),
                     'groups': 'celltype'}
    return _save(plot_paga(a), 'L29_paga')

@demo('L30_pseudotime')
def _():
    return _save(plot_pseudotime(ADATA, ['MK_FB1', 'MK_EC1'],
                                 pseudotime_col='pseudotime'),
                 'L30_pseudotime')

@demo('L31_distance_distribution')
def _():
    return _save(plot_distance_distribution(SP, 'CM', 'FB',
                                            groupby='celltype'),
                 'L31_distance_distribution')

@demo('L32_nhood_enrichment')
def _():
    return _save(plot_nhood_enrichment(SP, cluster_key='celltype'),
                 'L32_nhood_enrichment')

@demo('L33_colocalization')
def _():
    return _save(plot_colocalization(SP, 'ligand_score', 'receptor_score',
                                     method='spearman'), 'L33_colocalization')

@demo('L34_deconv_pie')
def _():
    return _save(plot_deconv_pie(SP, prop_cols=['prop_CM', 'prop_FB',
                                                'prop_EC'], max_spots=300),
                 'L34_deconv_pie')

@demo('L35_ccc_chord')
def _():
    W = rng.uniform(0, 1, (5, 5)); W = (W + W.T) / 2; np.fill_diagonal(W, 0)
    return _save(plot_ccc(W, layout='chord', labels=TYPES), 'L35_ccc_chord')

@demo('L36_ccc_network')
def _():
    W = rng.uniform(0, 1, (5, 5)); W = (W + W.T) / 2; np.fill_diagonal(W, 0)
    return _save(plot_ccc_network(W, labels=TYPES), 'L36_ccc_network')

@demo('L37_signaling_heatmap')
def _():
    df = pd.DataFrame(rng.uniform(0, 5, (5, 6)), index=TYPES,
                      columns=['WNT', 'TGFb', 'BMP', 'VEGF', 'NOTCH', 'FGF'])
    return _save(plot_signaling_heatmap(df), 'L37_signaling_heatmap')

@demo('L38_ccc_heatmap')
def _():
    # liana 预计算缺失 → 预期明确报错（不再静默 None）；报错=正确行为
    try:
        plot_ccc_heatmap(ADATA, plot_type='heatmap')
        raise AssertionError('预期抛出 ValueError（缺 liana 预计算）')
    except ValueError as e:
        assert 'liana' in str(e) or '通讯结果' in str(e)
        print('  L38: 正确抛出缺数据错误 ✓（无图输出符合预期）')
        return None

@demo('L39_spatial_ccc')
def _():
    return _save(plot_spatial_ccc(SP, 'LIG1', 'REC1'), 'L39_spatial_ccc')


if __name__ == '__main__':
    for name, fn in DEMOS:
        try:
            fn()
            RESULTS.append((name, 'PASS', ''))
        except Exception as e:
            RESULTS.append((name, 'FAIL', f'{type(e).__name__}: {e}'))
            print(f'  !! {name} FAILED: {type(e).__name__}: {e}')
            traceback.print_exc(limit=2)
    print(f'\n===== PASS/FAIL 台账（{OUT}）=====')
    for name, status, msg in RESULTS:
        print(f'{status}  {name}  {msg}')
    n_fail = sum(1 for _, s, _ in RESULTS if s == 'FAIL')
    print(f'\n{len(RESULTS) - n_fail} PASS / {n_fail} FAIL / {len(RESULTS)} total')

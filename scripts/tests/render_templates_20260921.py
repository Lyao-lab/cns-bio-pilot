#!/usr/bin/env python
"""render_templates_20260921 — 新模板渲染回归 harness（2026-09-21 回灌批次）。

渲染 2026-09-21 从 fetal_heart 实战回灌的 5 个新图型 + 2 个升级图型 + 工具层，
合成数据、零外部依赖（scanpy 可选，仅 stackarea 用 AnnData 容器）。
产物：--outdir（默认 /tmp/cns_tpl_test）下 PNG（视觉验收用）。

用法：~/miniforge3/envs/sc/bin/python scripts/tests/render_templates_20260921.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from cns_style import (
    plot_slope, plot_lollipop, plot_qc_cards, plot_trend_grid,
    plot_spatial_zoom, plot_stackarea, plot_enrichment,
    stamp_panel, polish_axes, direct_label, assert_no_text_overlap,
    set_cns_style, save_panel, GREY_SCALE, CONTRAST_BLUE, CONTRAST_RED,
)

OUT = sys.argv[sys.argv.index('--outdir') + 1] if '--outdir' in sys.argv \
    else '/tmp/cns_tpl_test'
rng = np.random.default_rng(20260921)


def _save(fig, name, check=True):
    """png 保存 + 画布级重叠断言（工具层联动演示）。"""
    if check:
        assert_no_text_overlap(fig, include_ticks=False, raise_on_fail=False)
    save_panel(fig, name, outdir=OUT, fmt='png', journal=False, show=False)


def demo_slope():
    types = ['vCM', 'VIC', 'EC_cap', 'FB', 'SMC', 'Macrophage', 'Neuron',
             'EC_art', 'FB_col', 'T_cell']
    base = np.array([0.32, 0.11, 0.14, 0.10, 0.05, 0.06, 0.03, 0.06, 0.08, 0.05])
    drift = np.array([+0.06, -0.07, +0.05, -0.05, +0.02, +0.01, -0.01,
                      +0.03, -0.06, +0.005])
    w = {t: [b, b + d * 0.4, b + d] + rng.normal(0, 0.004, 3)
         for t, b, d in zip(types, base, drift)}
    wide = pd.DataFrame(w, index=['13w', '19w', '24w']).T
    fig, ax = plot_slope(wide, top_n=8, emphasize=['vCM', 'VIC'],
                         colors={'vCM': CONTRAST_BLUE, 'VIC': CONTRAST_RED},
                         figsize=(4.6, 3.4))
    _save(fig, '01_slope')


def demo_lollipop():
    mods = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
    pearson = np.array([0.88, 0.74, 0.61, 0.42, -0.35, -0.55, -0.72, 0.21])
    spearman = pearson - rng.normal(0, 0.06, 8)
    pvals = np.array([2e-6, 8e-4, 0.004, 0.09, 0.12, 0.002, 1e-5, 0.38])
    tags = ['ECM', 'angiogenesis', 'cell cycle', 'mitochondrial',
            'immune', 'neural', 'ribosome', 'WNT']
    df = pd.DataFrame({'module': mods, 'pearson': pearson,
                       'spearman': spearman, 'p': pvals, 'identity': tags})
    null = (lo, hi) = (-0.18, 0.19)   # 预先算好的列置换 2.5–97.5% 分位
    fig, ax = plot_lollipop(df, label_col='module', value_col='pearson',
                            value2_col='spearman', pval_col='p',
                            tag_col='identity', tag_title='ORA identity',
                            ref_line=0.8, null_band=null, figsize=(4.4, 3.6))
    _save(fig, '02_lollipop')


def demo_qc_cards():
    donors = [f'D{i:02d}' for i in range(1, 13)]
    ga = pd.Series({d: g for d, g in zip(donors,
                    np.sort(rng.uniform(13, 24, len(donors)).round(1)))},
                   name='GA (w)')
    metrics = pd.DataFrame({
        'cells': rng.integers(4_000, 22_000, len(donors)),
        'median_genes': rng.integers(1_800, 4_200, len(donors)),
        'mito_pct': rng.uniform(2.5, 9.5, len(donors)).round(2),
        'doublet_rate': rng.uniform(0.8, 4.2, len(donors)).round(2),
    }, index=donors)
    fig, axes = plot_qc_cards(
        metrics, covariate=ga, covariate_label='GA (w)',
        formats={'mito_pct': '{:.1f}', 'doublet_rate': '{:.1f}',
                 'cells': '{:,.0f}', 'median_genes': '{:,.0f}'},
        highlight=['D07'], figsize=(7.6, 4.2))
    _save(fig, '03_qc_cards')


def demo_trend_grid():
    progs = [f'P{i}' for i in range(1, 9)]
    rows = []
    for p in progs:
        slope = rng.uniform(-0.14, 0.14)
        for d, ga in enumerate(rng.uniform(13, 24, 14)):
            n = int(rng.integers(80, 900))
            rows.append({'program': p, 'ga': ga, 'score':
                         slope * (ga - 18) + rng.normal(0, 0.35),
                         'n_cells': n})
    df = pd.DataFrame(rows)
    fig, axes = plot_trend_grid(df, x='ga', y='score', by='program',
                                size_col='n_cells', ncols=4,
                                highlight=['P1', 'P5'],
                                shared_ylim=(-2.6, 2.6), figsize=(8.8, 4.4))
    _save(fig, '04_trend_grid')


def demo_spatial_zoom():
    import anndata as ad
    n = 24000
    t = np.random.default_rng(7)
    # 组织块：两个高斯团 + 均匀背景
    c1 = t.normal([4000, 4000], [1500, 1100], (n // 2, 2))
    c2 = t.normal([6800, 5200], [900, 700], (n // 3, 2))
    uni = t.uniform([500, 500], [9000, 9000], (n - n // 2 - n // 3, 2))
    xy = np.vstack([c1, c2, uni])
    d1 = np.exp(-(((xy[:, 0] - 4100) / 700) ** 2 +
                  ((xy[:, 1] - 4150) / 520) ** 2))
    d2 = 0.7 * np.exp(-(((xy[:, 0] - 6850) / 420) ** 2 +
                        ((xy[:, 1] - 5250) / 320) ** 2))
    sig = np.clip(d1 + d2 + t.uniform(0, 0.06, len(xy)), 0, 1.2)
    adata = ad.AnnData(obs=pd.DataFrame({'signal': sig}),
                       obsm={'spatial': xy})
    fig, ax = plot_spatial_zoom(adata, color='signal',
                                unit_per_um=0.5, figsize=(4.4, 4.4))
    _save(fig, '05_spatial_zoom')


def demo_stackarea():
    import anndata as ad
    n = 9000
    weeks = np.array(['9w', '13w', '17w', '20w', '24w'])
    wi = rng.integers(0, len(weeks), n)
    drift = np.linspace(0, 1, len(weeks))
    types = ['vCM', 'aCM', 'VIC', 'FB', 'EC', 'SMC', 'Macrophage', 'Pericyte',
             'Neuron', 'Erythroid']
    w_props = np.array([[.30, .12, .14, .16, .09, .04, .06, .04, .02, .03],
                        [.32, .12, .13, .14, .09, .04, .06, .04, .03, .03],
                        [.35, .12, .11, .12, .09, .04, .06, .04, .03, .04],
                        [.38, .13, .09, .10, .09, .04, .05, .04, .03, .05],
                        [.41, .14, .07, .08, .09, .04, .05, .04, .03, .05]])
    ct = np.array([types[i] for i in
                   np.argmax(rng.uniform(size=(n, len(types))) *
                             w_props[wi], axis=1)])
    adata = ad.AnnData(obs=pd.DataFrame(
        {'celltype': pd.Categorical(ct, categories=types),
         'week': pd.Categorical(weeks[wi], categories=weeks)}))
    groups_of = {'vCM': 'muscle', 'aCM': 'muscle', 'SMC': 'muscle',
                 'VIC': 'mesenchyme', 'FB': 'mesenchyme', 'Pericyte':
                 'mesenchyme', 'EC': 'endothelial', 'Macrophage': 'immune',
                 'Neuron': 'neural', 'Erythroid': 'immune'}
    fig, ax = plot_stackarea(adata, celltype_col='celltype', groupby='week',
                             inband_labels=True, number_legend=True,
                             groups_of=groups_of, figsize=(4.6, 3.2))
    _save(fig, '06_stackarea')


def demo_enrichment():
    rows = []
    groups = {'M1 ECM': ['collagen fibril organization',
                         'extracellular matrix organization',
                         'cell-matrix adhesion', 'connective tissue development'],
              'M2 angio': ['angiogenesis', 'blood vessel morphogenesis',
                           'VEGF signaling pathway', 'vasculature development'],
              'M3 cycle': ['cell cycle checkpoint', 'DNA replication',
                           'mitotic nuclear division',
                           'chromosome organization'],
              'M7 ribo': ['HALLMARK_REACTOME_TRANSLATION',
                          'ribosomal small subunit biogenesis',
                          'rRNA processing', 'cytoplasmic translation']}
    for g, terms in groups.items():
        for t in terms:
            fdr = 10 ** rng.uniform(-14, -1.2)
            rows.append({'Term': t, 'Group': g, 'FDR': fdr,
                         'Gene_count': int(rng.integers(8, 90))})
    # 一个极端通路（封顶演示）：-log10≈98
    rows[0]['FDR'] = 1e-98
    enr = pd.DataFrame(rows)
    fig, ax = plot_enrichment(enr, group_col='Group', per_group=4, cap=30,
                              term_col='Term', fdr_col='FDR',
                              count_col='Gene_count', figsize=(4.8, 4.2))
    _save(fig, '07_enrichment')


def demo_tools():
    """工具层三件套：stamp_panel + polish_axes(bar) + direct_label + 断言。"""
    set_cns_style()
    fig, ax = plt.subplots(figsize=(8.0, 3.2))
    names = ['FB', 'vCM', 'EC', 'VIC', 'SMC', 'Mac']
    weeks = ['13w', '19w', '24w']
    vals = {n: np.linspace(rng.uniform(0.05, 0.3), rng.uniform(0.05, 0.4), 3)
            + rng.normal(0, 0.006, 3) for n in names}
    for k, n in enumerate(names):
        ax.plot(range(3), vals[n], color=GREY_SCALE['guide'], lw=1.6)
    ax.plot(range(3), vals['VIC'], color=CONTRAST_RED, lw=2.6)
    ends = [float(vals[n][-1]) for n in names]
    direct_label(ax, ends, [f'{n} {vals[n][-1] - vals[n][0]:+.2f}'
                            for n in names], x=2, gap_pt=12)
    ax.set_xticks(range(3)); ax.set_xticklabels(weeks, fontsize=8)
    ax.set_xlim(-0.3, 2.7)
    polish_axes(ax, variant='bar', grid_axis='y')
    ax.spines['bottom'].set_visible(False); ax.tick_params(axis='x', length=0)
    stamp_panel(fig, 'a', 'Composition movers across development',
                'per-donor median proportions; n=15 donors; slope = 24w − 13w')
    issues = assert_no_text_overlap(fig, include_ticks=False,
                                    raise_on_fail=False)
    print(f'[tools demo] overlap issues: {issues or "none"}')
    save_panel(fig, '08_tools_combo', outdir=OUT, fmt='png', journal=False,
               show=False)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for fn in (demo_slope, demo_lollipop, demo_qc_cards, demo_trend_grid,
               demo_spatial_zoom, demo_stackarea, demo_enrichment,
               demo_tools):
        print(f'--- {fn.__name__} ---')
        fn()
    print('ALL RENDERED ->', OUT)

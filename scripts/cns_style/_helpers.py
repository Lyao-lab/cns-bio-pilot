"""_helpers — cns_style sub-module"""

import numpy as np
import pandas as pd


# ============================================================
# 9c. Manifest functions (paper-level color consistency)
# ============================================================

def init_manifest(celltypes, conditions=None, path='manifest.yaml', palette=None):
    """Create manifest.yaml locking cell-type and condition colors for a paper.

    Call ONCE at project start. All figure scripts then use load_manifest().
    """
    import yaml
    if palette is None:
        palette = MORLANDI_EXTENDED if len(celltypes) > 8 else MORLANDI

    ct_colors = {ct: palette[i % len(palette)] for i, ct in enumerate(celltypes)}
    cond_colors = conditions or {}

    manifest = {
        'cell_type_colors': ct_colors,
        'condition_colors': cond_colors if cond_colors else CONDITION_COLORS,
        'sequential_cmap': 'byr_morlandi',
        'diverging_cmap': 'log2fc',
        'font_base': 8,
        'scale_ratio': 1.2,
    }
    with open(path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)
    print(f"Manifest saved: {path} ({len(ct_colors)} cell types)")
    return manifest



def load_manifest(path='manifest.yaml'):
    """Load manifest.yaml and apply colors globally. Returns color dicts.

    Usage:
        ct_colors, cond_colors = load_manifest('manifest.yaml')
        sc.pl.umap(adata, color='celltype', palette=ct_colors)
    """
    import yaml
    with open(path) as f:
        m = yaml.safe_load(f)
    ct_colors = m.get('cell_type_colors', {})
    cond_colors = m.get('condition_colors', CONDITION_COLORS)
    # Apply to matplotlib prop_cycle
    if ct_colors:
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=list(ct_colors.values()))
    return ct_colors, cond_colors


# ============================================================
# 9c2. add_scale_bar() — spatial figure scale bar (mandatory)
# ============================================================


# ============================================================
# 16. assert_anndata_keys(adata, ...) — defensive validation
# ============================================================
def assert_anndata_keys(adata, obs_cols=None, obsm_keys=None, var_names=None):
    """Defensive validation: assert required keys exist in an AnnData object.

    对标 omicverse-skills 的防御校验模式：缺失即 raise ValueError，
    报错信息列出可用选项，调用方一眼就能修正。纯校验，成功返回 None。

    Usage:
        assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
    """
    obs_cols = list(obs_cols or [])
    obsm_keys = list(obsm_keys or [])
    var_names = list(var_names or [])

    for col in obs_cols:
        if col not in adata.obs.columns:
            raise ValueError(
                f"Column '{col}' not found in adata.obs. "
                f"Available: {list(adata.obs.columns)}")
    for key in obsm_keys:
        if key not in adata.obsm.keys():
            raise ValueError(
                f"Key '{key}' not found in adata.obsm. "
                f"Available: {list(adata.obsm.keys())}")
    for name in var_names:
        if name not in adata.var_names:
            # var_names 可能很大，只列前 10 个避免刷屏
            avail = list(adata.var_names[:10]) + ['...'] if len(adata.var_names) > 10 \
                else list(adata.var_names)
            raise ValueError(
                f"Gene '{name}' not found in adata.var_names "
                f"({len(adata.var_names)} total). Available: {avail}")
    return None


# ============================================================
# 17. cohort_params(n_cells) — size + alpha + figsize 联动
# ============================================================

# ============================================================
# 20. Smart plot — 统一入口 + ov/mpl 自动降级
# ============================================================
# 每个图型一个 plot_xxx()：ov.pl 优先，mpl 兜底，API 失败也降级。
# 用户/agent 只调一个函数，不需要判断走哪条路。
# ============================================================

_HAS_OV = None

def _check_ov():
    """检测 omicverse 是否可用（缓存）。"""
    global _HAS_OV
    if _HAS_OV is None:
        try:
            import omicverse as ov  # noqa
            _HAS_OV = True
        except Exception:
            _HAS_OV = False
    return _HAS_OV


def _lighten_color(hex_color, amount=0.8):
    """Lighten hex toward white（交替背景带用）。"""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(hex_color)
    return (r + (1-r)*amount, g + (1-g)*amount, b + (1-b)*amount)


# ============================================================
# 20.1 plot_umap — UMAP/tSNE（ov.pl.embedding → mpl scatter）
# ============================================================


# ============================================================
# 20.19 plot_distance_distribution — 细胞间最近邻距离分布（空转标配）
# ============================================================

def _resolve_group_mask(adata_sp, group):
    """把 obs 列值或布尔 mask 解析为布尔数组（plot_distance_distribution 内部用）。"""
    import numpy as np
    if isinstance(group, str):
        # 优先常见类别列，找不到再全列扫描
        candidates = [c for c in ('celltype', 'cell_type', 'cluster', 'leiden', 'ctype')
                      if c in adata_sp.obs.columns]
        candidates += [c for c in adata_sp.obs.columns if c not in candidates]
        for col in candidates:
            vals = adata_sp.obs[col]
            if vals.dtype.name in ('object', 'category', 'string'):
                if (vals.astype(str) == group).any():
                    return (vals.astype(str) == group).to_numpy()
        raise ValueError(f"group '{group}' not found in any obs category column")
    mask = np.asarray(group, dtype=bool)
    if mask.ndim != 1 or mask.shape[0] != adata_sp.n_obs:
        raise ValueError(f"group mask must be 1D bool with length n_obs={adata_sp.n_obs}")
    return mask



# ============================================================
# 20.21 plot_colocalization — 双信号空间共定位散点（ρ + p）
# ============================================================

def _resolve_signal(adata_sp, name):
    """取 var_names 基因 或 obs 列（如去卷积比例）的数值向量（plot_colocalization 内部用）。"""
    import numpy as np
    if name in adata_sp.var_names:
        v = adata_sp[:, name].X
        if hasattr(v, 'toarray'):
            v = v.toarray()
        return np.asarray(v).ravel().astype(float), 'gene'
    if name in adata_sp.obs.columns:
        return np.asarray(adata_sp.obs[name], dtype=float).ravel(), 'obs'
    raise ValueError(f"'{name}' 既不在 var_names（基因）也不在 obs 列（比例/元数据）")



# ============================================================
# 20.25-20.39: 分布/统计/集合类图（ov.pl 优先 → mpl 兜底）
# ============================================================

def _adata_to_tidy(adata, cols):
    """AnnData → tidy DataFrame：基因名（var_names）提取表达值，obs 列名直接用。

    Args:
        adata: AnnData 对象
        cols: list[str]，基因名或 obs 列名（可混合）
    Returns:
        pandas.DataFrame：列=cols（保持给定顺序），行=adata.obs_names
    """
    import pandas as pd
    out = {}
    for c in cols:
        if c in adata.var_names:
            expr = adata[:, c].X
            if hasattr(expr, 'toarray'):
                expr = expr.toarray()
            out[c] = np.asarray(expr).ravel()
        elif c in adata.obs.columns:
            out[c] = adata.obs[c].values
        else:
            raise ValueError(f"'{c}' 既不是 var_names 也不是 obs 列")
    return pd.DataFrame(out, index=adata.obs_names)


# ============================================================
# 20.25 plot_ridge — 山脊图（ov.pl.ridgeplot → mpl KDE 叠放）
# ============================================================

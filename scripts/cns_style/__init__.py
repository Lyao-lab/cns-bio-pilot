"""cns_style — CNS-grade plotting for bioinformatics.

Modular package (replaces monolithic cns_style.py).
All public symbols are re-exported here so `from cns_style import *` works unchanged.
"""

from ._constants import *
from ._style import *
from ._axes import *
from ._layout import *
from ._save import *
from ._annotation import *
from ._palette import *
# _ 开头的内部函数不会被 import * 导入，需要显式导出
from ._helpers import (_check_ov, _HAS_OV, _lighten_color, _adata_to_tidy,
                        assert_anndata_keys, init_manifest, load_manifest,
                        _resolve_group_mask, _resolve_signal)
from ._layout import _fs, _FIG_SCALE
from .plots_embedding import *
from .plots_expression import *
from .plots_stats import *
from .plots_ccc import *
from .plots_spatial import *

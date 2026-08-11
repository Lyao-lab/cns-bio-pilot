# 全局设置与数据 IO（模板层入口）

> **本文件 = 可执行代码模板层入口**：每个分析脚本的开头 + 数据读取速查。方法选型见知识层 [`../decision_guide.md`](../decision_guide.md)。

## 全局开头（每个分析脚本第一行）

```python
import omicverse as ov
import scanpy as sc
ov.plot_set()   # 与 ov.ov_plot_set() 等价（别名）
# Core Rule 2：先存 raw counts（DE/velocity 生死线），必须在 QC 前
adata.layers['counts'] = adata.X.copy()
```

## 数据 IO 速查

| 数据类型 | 函数 | 备注 |
|---|---|---|
| 标准 Visium | `sc.read_visium('dir/')` | scanpy 的 path reader；⚠️ `ov.space.read_visium_10x(adata)` 是 wrapper 收 AnnData，不是 reader |
| Visium HD | `ov.io.read_visium_hd('dir/', data_type='bin')` | `data_type='bin'\|'cellseg'`；⚠️ `ov.space.read_visium_hd` 不存在 |
| Visium HD bin/seg | `ov.io.read_visium_hd_bin(...)` / `read_visium_hd_seg(...)` | bin 级 / 分割级 |
| Xenium | `ov.io.read_xenium('dir/')` | 亚细胞分辨率 |
| Nanostring/GeoMx-CosMx | `ov.io.read_nanostring('dir/', counts_file=..., meta_file=...)` | |
| 10x HDF5 | `ov.io.read_10x_h5('file.h5')` | |
| 10x MTX | `ov.io.read_10x_mtx('dir/')` | |
| h5ad | `ov.io.read_h5ad('file.h5ad')` | |
| FACS | `ov.io.read_fcs('file.fcs')` | |
| 通用 / 百万级 | `ov.read('data.h5ad', backend='rust')` | rust=AnnDataOOM ~170× 省内存 |

> 读取函数在 `ov.io`（非 `ov.space`）；标准 Visium 用 `sc.read_visium`。
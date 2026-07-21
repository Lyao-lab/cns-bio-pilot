"""Multi-modal spatial analysis with SpatialData (canonical example).

Reference: spatialdata 0.7+ | spatialdata-io 0.1+ | scanpy 1.10+ | Verify API if version differs
Data assumption: platform output directory (Xenium / Visium HD / Stereo-seq) on disk.

API notes:
  - spatialdata-io uses top-level reader functions `read_xenium`, `read_visium`,
    `read_visium_hd` (NOT legacy `xenium.xenium(...)`).
  - spatialdata >=0.2 uses `.tables` (plural, a dict[str, AnnData]); the legacy
    singular `.table` accessor has been removed. Access via `sdata.tables[<key>]`.
  - The default table key is platform-dependent (often 'table' or 'adata').
"""
import spatialdata as sd
from spatialdata_io import read_xenium, read_visium, read_visium_hd
import scanpy as sc

# ---------------------------------------------------------------------------
# 1. Load platform data (current spatialdata-io API)
# ---------------------------------------------------------------------------
# Xenium (10x subcellular)
sdata = read_xenium('/path/to/xenium_output')

# Or Visium HD
# sdata = read_visium_hd('/path/to/visium_hd_output')

# Or conventional Visium
# sdata = read_visium('/path/to/visium_output')

# Or from a preprocessed Zarr
# sdata = sd.read_zarr('experiment.zarr')

print(sdata)
print('Table keys:', list(sdata.tables.keys()))
# SpatialData elements:
#   sdata.images   : H&E / DAPI / morphology
#   sdata.labels   : cell segmentation masks
#   sdata.points   : transcript locations (subcellular platforms)
#   sdata.shapes   : cell boundaries (polygons)
#   sdata.tables   : dict[str, AnnData] expression matrices

# ---------------------------------------------------------------------------
# 2. Access expression table + transcripts
# ---------------------------------------------------------------------------
TABLE_KEY = list(sdata.tables.keys())[0]   # often 'table' or 'adata'
adata = sdata.tables[TABLE_KEY]

if 'transcripts' in sdata.points:
    transcripts = sdata.points['transcripts']
    print(f'Total transcripts: {len(transcripts)}')

# ---------------------------------------------------------------------------
# 3. Spatial analysis on expression
# ---------------------------------------------------------------------------
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.leiden(adata)
sdata.tables[TABLE_KEY] = adata   # write back

# ---------------------------------------------------------------------------
# 4. Region query (bounding box)
# ---------------------------------------------------------------------------
from spatialdata import bounding_box_query
roi = bounding_box_query(
    sdata,
    min_coordinate=[0, 0],
    max_coordinate=[1000, 1000],
    axes=['x', 'y'],
)

# ---------------------------------------------------------------------------
# 5. Aggregate transcripts per cell (subcellular platforms)
# ---------------------------------------------------------------------------
if 'transcripts' in sdata.points and 'cell_id' in sdata.points['transcripts'].columns:
    cell_counts = sdata.points['transcripts'].groupby('cell_id').size()
    print(f'Transcripts per cell: mean {cell_counts.mean():.1f}')

# ---------------------------------------------------------------------------
# 6. Persist
# ---------------------------------------------------------------------------
sdata.write('processed.zarr')

# Visualization with spatialdata-plot (separate package)
# import spatialdata_plot  # registers .pl accessors on SpatialData
# sdata.pl.render_images().pl.render_labels().pl.show()

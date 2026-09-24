# Worked Example：完整 PPT outline.json（从 hook 到 takehome）

> 自 SKILL.md 拆出（2026-09-24，内容原样迁移）。写 outline.json 前对照本示例校验：标题断言式、arc_role 全覆盖、图型多样化、notes 中文。

真实心脏瓣膜项目的 10-slide PPT，标题全部为**断言式**（结论句），arc_role 完整覆盖 hook→takehome。

```json
{
  "title": "Valve Interstitial Cell Activation Drives Fibrotic Niche Formation",
  "subtitle": "Single-cell + spatial transcriptomics of cardiac valve development",
  "preset": "cns-bio-light",
  "slides": [
    {"variant": "title", "arc_role": "hook",
     "title": "What drives valve fibrosis? The spatial architecture is unknown"},
    {"variant": "methods-flow", "arc_role": "design",
     "title": "Multi-modal: scRNA (3 timepoints) + Visium (10 sections)",
     "steps": ["QC","Cluster","Annotate","DE","Niche","CCC"]},
    {"variant": "figure-hero", "arc_role": "atlas",
     "title": "8 cell types; VIC dominant (35-52%)",
     "image": "panels/umap_atlas.png",
     "caption": "Fig 1. UMAP across 13w/24w/36w (N=15,000)",
     "notes": "VIC 是最大群，三时点组成变化显著。UMAP 分群清晰，无明显批次。"},
    {"variant": "figure-dual", "arc_role": "finding",
     "title": "VIC expand 17pp and shift Quiescent→Activated",
     "image": "panels/vic_13w.png", "caption_left": "13w",
     "image2": "panels/vic_36w.png", "caption_right": "36w",
     "notes": "VIC 从 35%→52%。Quiescent 亚群减少，Activated 增多。轨迹分析确认方向。"},
    {"variant": "figure-hero", "arc_role": "finding",
     "title": "Activated VIC upregulate COL1A1/COL3A1/POSTN (ECM remodeling)",
     "image": "panels/de_scatter.png",
     "caption": "Fig 3. Grouped scatter: log2FC per timepoint",
     "notes": "三时点 DE 分组散点图。ECM 基因在 36w 显著上调。GSEA 确认 ECM 通路 NES=2.1。"},
    {"variant": "figure-hero", "arc_role": "mechanism",
     "title": "BANKSY identifies 'fibrotic front' niche (8/10 sections)",
     "image": "panels/spatial_domains.png",
     "caption": "Fig 4. Spatial domain map + H&E",
     "notes": "纤维化前沿在 8/10 个样本中出现（>20% 阈值）。Domain marker 富集 ECM 基因。"},
    {"variant": "figure-dual", "arc_role": "spatial",
     "title": "CXCL12+VIC co-localize with CD68+Macrophage (<50μm)",
     "image": "panels/spatial_cxcl12.png", "caption_left": "CXCL12",
     "image2": "panels/spatial_cd68.png", "caption_right": "CD68 Macrophage",
     "notes": "空间共定位确认。距离定量曲线显示 <50μm 的富集（p<0.01）。"},
    {"variant": "figure-hero", "arc_role": "sowhat",
     "title": "CXCL12 axis: druggable target (validated in heart failure, PMID:39443792)",
     "image": "panels/model.png",
     "caption": "Proposed model: VIC-Mac positive feedback loop",
     "notes": "CXCL12 阻断在心衰模型中已有验证。瓣膜纤维化的潜在干预靶点。"},
    {"variant": "bullets", "arc_role": "takehome",
     "title": "3 key findings",
     "bullets": ["VIC activation forms spatial niche", "CXCL12 connects fibrosis-immunity", "Niche is druggable target"]}
  ]
}
```

**这个示例示范了**：
1. 每页标题是**结论句**（不是 "Results" / "Analysis"）
2. arc_role 完整覆盖 hook→design→atlas→finding×2→mechanism→spatial→sowhat→takehome
3. 图型多样化：UMAP / dual-compare / grouped scatter / spatial overlay / model diagram / bullets
4. notes 全中文写解读（take-home + 关键数字 + 讲解提示）
5. 页面文字全英文（图用英文），备注全中文

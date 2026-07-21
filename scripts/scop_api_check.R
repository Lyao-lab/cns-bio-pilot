#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
# cns-bio-pilot scop_api_check — scop API 实存性自检（R 版）
#
# 用途：每次安装或更新 scop 后跑一遍，确认 skill 文档里提到的 scop API 在当前
# R 环境真实存在。防止"文档写了 RunX 但 scop 这个版本没有"导致运行时
# could-not-find-function 错误（v14 的 scop 大规模虚构 API 事故由此发现）。
#
# 用法：
#   Rscript scripts/scop_api_check.R
#   Rscript scripts/scop_api_check.R --skill-dir /path/to/cns-bio-pilot
#
# 工作流：
#   1. 扫描 skill 全部 .md/.json/.R 文件，提取所有 scop 相关 API 调用
#      （Run* / integration_scop / standard_scop / *integrate / *Plot 等）
#   2. 在当前 R 环境 getNamespaceExports("scop") 核对每个 API 是否存在
#   3. 对"已知故意不存在的 API"（白名单）跳过
#   4. 报告：哪些存在 / 哪些缺失 / 缺失的修复建议（列出 scop 已有的近似名）
#
# 退出码：0 = 全部通过；1 = 有 FAIL（缺失 API）

args <- commandArgs(trailingOnly = TRUE)
# 默认 skill_dir：脚本上两级（scripts/ -> skill 根）
script_path <- (function() {
  args_all <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("^--file=", "", args_all[grep("^--file=", args_all)])
  if (length(file_arg) == 1 && nchar(file_arg) > 0) normalizePath(file_arg) else NA
})()
if (is.na(script_path)) {
  skill_dir <- normalizePath(".")
} else {
  skill_dir <- normalizePath(file.path(dirname(script_path), ".."))
}
if ("--skill-dir" %in% args) {
  idx <- which(args == "--skill-dir")
  skill_dir <- args[idx + 1]
}
if (!dir.exists(skill_dir)) {
  cat("skill 目录不存在:", skill_dir, "\n")
  quit(status = 1)
}

# ============================================================
# 已知"故意不在 scop"的能力白名单（文档里诚实标注为 standalone 的）
# ============================================================
NEGATIVE_WHITELIST <- c(
  "RunMilo", "RunscCODA", "RunPropeller",          # compositional DA — standalone miloR/scCODA/propeller
  "RunSCENIC", "RunSCENICPlus", "RunGENIE3", "RunGRNBoost2",  # GRN — standalone scenicplus
  "RunLIANA", "RunCellphoneDB", "RunNichenetr", "RunMultiNichenetr",  # CCC — standalone
  "RunSecAct", "RunSecActCCC",                     # SecAct standalone
  "RunCNV", "RunMetabolism", "RunscMalignantFinder", "RunscMalignantRegion",  # CNV/metabolism standalone
  "RunscTenifoldKnk",                              # scTenifoldKnk standalone
  "RunSpatialNeighborhood", "RunSpatialVariableFeatures", "RunBayesSpace", "RunBANKSY",  # spatial standalone
  "RunRCTD", "RunSpatialDWLS", "RunCARD", "RunSPOTlight", "RunSTdeconvolve", "RunCytoSPACE",
  "RunDeconvolution", "RunSmoothClust", "RunCSIDE", "RunSpaNorm",
  "RunGiottoWorkflow", "RunGiottoCluster", "RunGiottoSpatialGenes",
  "RunGiottoSpatialModules", "RunGiottoCellProximity",
  "RunSpatialIntegration", "RunSpatialEcoTyper", "RunSpatialGradientFeatures",
  "RunSemlaLocalG", "RunSemlaRadialDistance", "RunSemlaRegionNeighbors", "RunSemlaSpatialNetwork",
  "RunMERINGUE", "RunSpotQC", "RunSpatialQM",
  "RunGSVA", "RunDorothea", "RunAugur", "RunSciBet",
  "RunLabelTransfer", "RunReferenceMapping", "TrainCellTypist",
  "RunDimsEstimate", "RunHarmony",
  "ConvertHomologs",
  # 以下虽是 Seurat 原生但 skill 文档可能引用，跳过
  "RunPCA", "RunUMAP", "NormalizeData", "FindVariableFeatures", "ScaleData",
  "FindNeighbors", "FindMarkers", "FindAllMarkers", "FoldChange",
  "SCTransform", "Read10X", "CreateSeuratObject",
  # scop 函数式辅助
  "LISIPlot", "spe_to_srt", "srt_to_spe", "h5ad_to_srt", "srt_to_h5ad",
  "loom_to_adata", "loom_to_srt", "LoadScopDataset", "ListScopDatasets",
  # 非 scop 工具（在 skill 文档里作为依赖/对比被提到，正则会误命中）
  "ComplexHeatmap", "PyComplexHeatmap",          # R/Python 热图包，不是 scop
  "LDAPlot",                                       # Seurat 5 已移除，skill 里有警告说明
  "RunSpatial", "RunX"                             # 占位符/模板词，非具体 API
)

# ============================================================
# 负向白名单：经审计确认"宣称不存在且 scop 0.8.0 里确实不存在"的 API
# 每个条目注明来源（哪次审计 + 日期）。未来 scop 升级若引入，会触发 WARN
# 提醒"文档需要更新"，而不是阻断检查脚本。
# ============================================================
NEGATIVE_WHITELIST_VERIFIED_ABSENT <- c(
  "ClusterTreePlot",           # verified absent 2026-07 v15.1 audit; cluster tree: use Seurat::BuildClusterTree + plot
  "PseudotimeProjectionPlot",  # verified absent 2026-07 v15.1 audit; use sc.pl.pseudotime or thisplot native
  "WNN_integrate"              # verified absent 2026-07 v15.1 audit; WNN = Seurat-native FindMultiModalNeighbors
)

# ============================================================
# 1. 检查 scop 是否安装
# ============================================================
if (!requireNamespace("scop", quietly = TRUE)) {
  cat("scop NOT installed. Install:\n  remotes::install_github('mengxu98/scop')\n")
  quit(status = 1)
}

scop_version <- as.character(packageVersion("scop"))
cat("=== scop", scop_version, "API 实存性自检 ===\n")
cat("skill 目录:", skill_dir, "\n\n")

scop_exports <- getNamespaceExports("scop")
cat("scop exports:", length(scop_exports), "个（其中 Run*:",
    sum(grepl("^Run", scop_exports)), "个）\n\n")

# ============================================================
# 2. 扫描 skill 文档提取 scop API 调用
# ============================================================
files <- list.files(skill_dir, pattern = "\\.(md|json|R)$",
                    recursive = TRUE, full.names = TRUE)
files <- files[!grepl("(\\.git/|scripts/scop_api_check\\.R)", files)]

api_pattern <- "(\\bRun[A-Z][a-zA-Z0-9_]*\\b|\\b[A-Za-z]+_integrate\\b|\\bintegration_scop\\b|\\bstandard_scop\\b|\\badata_to_srt\\b|\\bsrt_to_adata\\b|\\b[a-zA-Z]+Plot\\b|\\b[a-zA-Z]+Heatmap\\b|\\bConvertHomologs\\b|\\bFindAllMarkers\\b|\\bFindMarkers\\b|\\bFoldChange\\b|\\bLISIPlot\\b|\\bVelocityPlot\\b|\\bLoadScopDataset\\b|\\bListScopDatasets\\b)"

extracted <- character()
for (f in files) {
  text <- tryCatch(readLines(f, warn = FALSE), error = function(e) character())
  matches <- unique(unlist(regmatches(text, gregexpr(api_pattern, text))))
  extracted <- unique(c(extracted, matches))
}
extracted <- sort(extracted)
cat("从 skill 文档提取", length(extracted), "个候选 scop API\n\n")

# ============================================================
# 3. 逐个核对
# ============================================================
ok <- c(); missing <- c(); whitelisted <- c(); neg_whitelisted <- c()
for (api in extracted) {
  if (api %in% NEGATIVE_WHITELIST) {
    whitelisted <- c(whitelisted, api)
  } else if (api %in% NEGATIVE_WHITELIST_VERIFIED_ABSENT) {
    neg_whitelisted <- c(neg_whitelisted, api)
  } else if (exists(api, where = asNamespace("scop")) ||
             api %in% c("NormalizeData","FindVariableFeatures","ScaleData","FindNeighbors",
                        "FindMarkers","FindAllMarkers","FoldChange","SCTransform","Read10X",
                        "CreateSeuratObject","RunPCA","RunUMAP")) {
    ok <- c(ok, api)
  } else {
    missing <- c(missing, api)
  }
}

# ============================================================
# 4. 报告
# ============================================================
cat(paste(rep("=", 60), collapse = ""), "\n")
cat("存在:", length(ok), " ")
cat("白名单（诚实标注为 standalone 的）:", length(whitelisted), " ")
cat("负向白名单（审计确认不存在）:", length(neg_whitelisted), " ")
cat("缺失（skill 提到但 scop 不存在）:", length(missing), "\n")
cat(paste(rep("=", 60), collapse = ""), "\n\n")

if (length(whitelisted) > 0) {
  cat("⬜ 白名单 API（跳过——文档已诚实标注为 standalone / Seurat-native）：\n")
  for (a in sort(whitelisted)) cat("  ", a, "\n", sep = "")
  cat("\n")
}

if (length(neg_whitelisted) > 0) {
  cat("⚫ 负向白名单 API（审计确认 scop 不存在，文档里作为 standalone/Seurat-native 提到）：\n")
  for (a in sort(neg_whitelisted)) cat("  ", a, "\n", sep = "")
  cat("\n")
}

# 负向白名单校验：若 scop 升级后真的引入了这些 API，提醒更新文档（WARN 不阻断）
# 只检查 NEGATIVE_WHITELIST_VERIFIED_ABSENT —— 这些是被断言"不存在"的；
# 普通 NEGATIVE_WHITELIST 里的 Seurat-native（RunPCA/FindAllMarkers 等）存在是正常的
leaks <- character()
for (fn in NEGATIVE_WHITELIST_VERIFIED_ABSENT) {
  if (exists(fn, where = asNamespace("scop"))) leaks <- c(leaks, fn)
}
if (length(leaks) > 0) {
  cat("⚠️  WHITELIST LEAK（scop 已引入这些 API，考虑更新文档移出白名单）:\n")
  for (a in leaks) cat("  ", a, "\n", sep = "")
  cat("\n")
}

if (length(missing) > 0) {
  cat("❌ 缺失的 API（需修正 skill 文档或更新白名单）：\n")
  for (a in sort(missing)) {
    # 找最接近的真实 scop 名
    similar <- scop_exports[agrep(a, scop_exports, max.distance = 0.2, ignore.case = TRUE)]
    similar <- head(similar, 3)
    sug <- if (length(similar) > 0) paste(" → 可能的正确名:", paste(similar, collapse = "/")) else ""
    cat("  ", a, sug, "\n", sep = "")
  }
  cat("\n修复方式:\n")
  cat("  1. 若 API 真实存在但改名 → 更新 skill 文档\n")
  cat("  2. 若 API 不存在（文档写错）→ 改为真实 API 或标注'NOT in scop, use standalone X'\n")
  cat("  3. 若是诚实标注为 standalone 的 → 加入本脚本的 NEGATIVE_WHITELIST\n")
  quit(status = 1)
} else {
  cat("✅ 全部通过——skill 文档里的 scop API 在当前环境均真实存在或已诚实标注为 standalone。\n")
  quit(status = 0)
}

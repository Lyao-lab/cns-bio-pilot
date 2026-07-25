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
# NOTE 2026-07-26 (scop 0.8.9 upgrade): this list was drastically reduced.
# 0.8.0→0.8.9 wrapped ~94 new Run* verbs; nearly all entries previously here
# (RunMilo/RunSCENICPlus/RunRCTD/RunBANKSY/RunSecAct/RunCNV/RunGSVA/etc) are
# now REAL scop exports and have been removed from this whitelist so they get
# normally verified. Only true non-scop references remain.
# ============================================================
NEGATIVE_WHITELIST <- c(
  # Seurat-native functions skill docs may cite (not scop, skip)
  "RunPCA", "RunUMAP", "NormalizeData", "FindVariableFeatures", "ScaleData",
  "FindNeighbors", "FindMarkers", "FindAllMarkers", "FoldChange",
  "SCTransform", "Read10X", "CreateSeuratObject", "RunHarmony",
  # Non-scop R/Python packages skill docs cite as deps/comparisons (regex false-positives)
  "ComplexHeatmap", "PyComplexHeatmap",          # R/Python heatmap packages
  "LDAPlot",                                       # removed in Seurat 5; skill has warning
  "RunSpatial", "RunX",                            # placeholders/templates, not concrete APIs
  "TrainCellTypist"                                # Python celltypist training, not scop
)

# ============================================================
# 负向白名单：经审计确认"在文档里出现但 scop 里确实不存在"的 API
# 每个条目注明来源（哪次审计 + 日期）。未来 scop 升级若引入，会触发 WARN
# 提醒"文档需要更新"，而不是阻断检查脚本。
# NOTE 2026-07-26: 0.8.0-era entries (ClusterTreePlot/PseudotimeProjectionPlot/
# WNN_integrate) are now REAL in 0.8.9 — removed from this list. The 2 known
# 0.8.0→0.8.9 renames are handled as explicit "expected rename" notes below.
# ============================================================
NEGATIVE_WHITELIST_VERIFIED_ABSENT <- c(
  # Empty as of scop 0.8.9 — all previously-verified-absent APIs now exist.
  # Add future cases here with a dated note when scop removes/renames something.
  "RunDimReduction",   # 0.8.0 had this; 0.8.9 split into RunDimsReduction + RunDimsEstimate (doc updated to new names)
  "CellChatPlot"       # 0.8.0 had this; 0.8.9 renamed to SpatialCellChatPlot (doc updated)
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cns-bio-pilot postcheck — 科学严谨性自动校验

用法：
    python postcheck.py <adata_or_result> [--type {adata,de,deconv,velocity,slides}]
    python postcheck.py --help

把 cns-bio-pilot 核心原则中【可机检】的部分机械化。不替代人工判断，
只捕捉最常见的科学错误。每条检查输出 ✅ PASS / ⚠️ WARN / ❌ FAIL。

检查项（对应 SKILL.md Core Rules + references/meta_methodology.md）：
  [ADATA] 数据层完整性
    A1  raw counts 保留 (layers['counts'])              Core Rule 2 / meta ②
  [DE]   差异表达严谨性
    D1  报告 Padj 而非裸 P                              统计严谨
    D2  阈值 Padj<0.05 & |Log2FC|>1.0                   统计严谨
    D3  未对 batch-corrected embedding 跑 DE            meta ② 🚨
    D4  单细胞 DE 是否 pseudobulk（启发式）             Core Rule 2
  [DECONV] 空间去卷积
    V1  输出含质量评估列                                 meta ①
  [VELOCITY] RNA velocity
    E1  spliced/unspliced layers 存在                   前置条件
  [SLIDES] 演示文稿
    S1  关键数值图保留 N / 统计检验标注                  Core Rule 1
  [LANG]  措辞
    L1  无未授权因果词 (regulates/causes/induces)       Core Rule 1 🚨
    L2  CCC 分析的因果词纪律（启发式）                   Core Rule 1
  [COMP]  组成型数据
    C1  细胞比例分析勿用卡方/Fisher（启发式）            meta ③
  [FACT] 虚构检测（Core Rule 1：基于事实，不猜测不虚构）
    F1  无虚构信号（example/demo/test 占位、编造的 accession）   Core Rule 1 🚨

注：D4 / L2 / C1 均为启发式 WARN，需人工判断（如 method='wilcoxon' 的画图调用
可能触发 D4；C1 的 'composition' 子串较宽）。FAIL 仍是确定性错误。
"""
import argparse
import json
import re
import sys
from pathlib import Path


# ----------------------------- helpers -----------------------------

class Report:
    def __init__(self):
        self.items = []  # (code, severity, msg)

    def add(self, code, severity, msg):
        self.items.append((code, severity, msg))
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[severity]
        print(f"  {icon} [{code}] {severity}: {msg}")

    def summary(self):
        n_pass = sum(1 for _, s, _ in self.items if s == "PASS")
        n_warn = sum(1 for _, s, _ in self.items if s == "WARN")
        n_fail = sum(1 for _, s, _ in self.items if s == "FAIL")
        print(f"\n{'='*50}")
        print(f"Summary: {n_pass} PASS  {n_warn} WARN  {n_fail} FAIL")
        if n_fail:
            print("🚨 存在 FAIL 项——发表前必须修复")
            return 1
        elif n_warn:
            print("⚠️  存在 WARN 项——建议核查")
            return 0
        else:
            print("✅ 全部通过")
            return 0


CAUSAL_WORDS = re.compile(
    r"\b(regulates?|causes?|induces?|promotes?|drives?|activates?|inhibits?)\b",
    re.IGNORECASE,
)
SAFE_ASSOC = re.compile(
    r"\b(associated with|correlated with|linked to|related to|enriched in|"
    r"potential candidate|putative|may|might|suggests?)\b",
    re.IGNORECASE,
)


# ----------------------------- checks -----------------------------

def try_import_adata():
    try:
        import anndata
        return anndata
    except ImportError:
        return None


def check_adata(path, report):
    """检查 AnnData 对象的层/键完整性。"""
    anndata = try_import_adata()
    if anndata is None:
        report.add("ADATA", "WARN", "anndata 未安装，跳过数据层检查")
        return
    try:
        adata = anndata.read_h5ad(path)
    except Exception as e:
        report.add("ADATA", "WARN", f"无法读取 {path}: {e}")
        return

    # A1: raw counts
    if "counts" in adata.layers:
        report.add("A1", "PASS", "layers['counts'] 存在（raw counts 保留）")
    else:
        report.add("A1", "FAIL",
                   "layers['counts'] 缺失——DE/velocity 生死线。"
                   "修复：adata.layers['counts'] = adata.X.copy()")

    # 附加：spliced/unspliced（velocity 前提）
    if "spliced" in adata.layers and "unspliced" in adata.layers:
        report.add("E1", "PASS", "spliced/unspliced layers 存在（velocity 可用）")
    elif "spliced" in adata.layers or "unspliced" in adata.layers:
        report.add("E1", "WARN", "仅一个 spliced/unspliced，velocity 不完整")


def check_de(df_or_path, report):
    """检查差异表达结果 DataFrame（CSV/TSV 或已加载 df）。"""
    import pandas as pd
    if isinstance(df_or_path, (str, Path)):
        df = pd.read_csv(df_or_path) if str(df_or_path).endswith(".csv") else pd.read_csv(df_or_path, sep="\t")
    else:
        df = df_or_path

    cols = set(df.columns.str.lower())
    # 识别 SVG 表（空间自相关，非 DE）：含 moranI/geary/I 列但无 log2FC
    is_svg = any(k in cols for k in ["morani", "geary", "pval_sim", "ii"]) and not any(
        k in cols for k in ["log2fc", "logfc", "logfold"]
    )
    if is_svg:
        report.add("DE", "PASS",
                   "识别为空间变异基因(SVG)表——Moran's I/Geary's C，非 DE，跳过 Log2FC 检查")
        # SVG 仍校验显著性 P 存在
        if any("pval" in c for c in cols):
            report.add("D1", "PASS", "SVG 表含显著性 P（pval_sim）")
        return
    # D1: Padj
    has_padj = any("adj" in c or "fdr" in c or "qval" in c for c in cols)
    has_p_only = "pvals" in cols or "pvalue" in cols or "p" in cols
    if has_padj:
        report.add("D1", "PASS", "报告了校正后 P（Padj/FDR/qval）")
    elif has_p_only:
        report.add("D1", "FAIL",
                   "仅报告裸 P，无 Padj——必须 FDR 校正（Benjamini-Hochberg）")

    # D2: 阈值
    if has_padj:
        padj_col = next(c for c in df.columns if "adj" in c.lower() or "fdr" in c.lower() or "qval" in c.lower())
        logfc_col = next((c for c in df.columns if "log2fc" in c.lower() or "logfc" in c.lower() or "logfold" in c.lower()), None)
        if logfc_col:
            n_sig = ((df[padj_col] < 0.05) & (df[logfc_col].abs() > 1.0)).sum()
            report.add("D2", "PASS",
                       f"阈值 Padj<0.05 & |Log2FC|>1.0 应用，{n_sig} 个显著基因")
        else:
            report.add("D2", "WARN", "无 Log2FC 列，阈值无法验证")


def check_deconv(adata_or_path, report):
    """检查去卷积结果是否含质量评估。"""
    anndata = try_import_adata()
    if anndata is None:
        return
    try:
        adata = anndata.read_h5ad(adata_or_path) if isinstance(adata_or_path, (str, Path)) else adata_or_path
    except Exception:
        return
    # cell2location / RCTD 通常在 obsm 或 obs 输出比例 + uns 存质量
    has_quality = (
        any(k in adata.uns for k in ["mod", "posterior_qc", "reconstruction_qc"])
        or any("prob" in k.lower() or "confidence" in k.lower() for k in adata.obs.columns)
        or any("q05" in k or "q95" in k or "sd" in k for k in getattr(adata, "obsm", {}).keys())
    )
    if has_quality:
        report.add("V1", "PASS", "去卷积结果含质量评估（置信度/区间/重建误差）")
    else:
        report.add("V1", "WARN",
                   "未检测到去卷积质量评估列——发表级应报告 cell2location "
                   "reconstruction_qc 或细胞类型置信度")


def check_velocity(adata_or_path, report):
    """检查 RNA velocity 前提。"""
    check_adata(adata_or_path, report)  # 复用 E1


def check_slides(html_or_dir, report):
    """检查演示文稿 HTML 保留统计标注。"""
    p = Path(html_or_dir)
    files = [p] if p.is_file() else list(p.rglob("*.html"))
    if not files:
        report.add("SLIDES", "WARN", f"未找到 HTML: {html_or_dir}")
        return
    text = ""
    for f in files:
        try:
            text += f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
    # S1: 关键统计标注（N / Padj / ※）
    has_n = bool(re.search(r"\bN\s*[=:>]\s*\d|n\s*=\s*\d|样本?[数大]\d", text))
    has_stat = bool(re.search(r"[Pp]\s*[=<]\s*0\.|Padj|p-value|统计学|significant", text, re.I))
    if has_n and has_stat:
        report.add("S1", "PASS", "幻灯片含 N 与统计检验标注")
    elif has_n or has_stat:
        report.add("S1", "WARN", "幻灯片统计标注不完整（缺 N 或缺 P）")
    else:
        report.add("S1", "FAIL",
                   "幻灯片缺 N 与统计检验——简约≠省略严谨性")
    # L1: 因果词（所有检查都跑措辞）
    check_language(text, report)


def check_language(text, report):
    """检查文本中未授权的因果措辞。"""
    if not isinstance(text, str):
        return
    causal_hits = CAUSAL_WORDS.findall(text)
    safe_hits = SAFE_ASSOC.findall(text)
    # 容忍：如果同一文本大量用安全词，少量 causal 可能是已验证的
    if not causal_hits:
        report.add("L1", "PASS", "无未授权因果词")
    elif len(causal_hits) <= 2 and len(safe_hits) >= len(causal_hits) * 2:
        report.add("L1", "WARN",
                   f"检测到因果词 {causal_hits[:3]}——确认有实验/因果推断证据，"
                   "否则改为 'associated with'")
    else:
        report.add("L1", "FAIL",
                   f"因果词过密 {causal_hits[:5]}——无证据时强制用 'associated with'，"
                   "原则 5 违反")


# 虚构信号（原则 1：基于事实，不猜测不虚构）
FABRICATION_RE = re.compile(
    r'\b(GSE\d{5,}|GSM\d{6,})\b'  # accession 格式 (GSE 5+ digits, GSM 6+)
    r'|(e\.g\.|例如|比如|假设|example data|demo dataset|test_data|mock_data|placeholder)',
    re.IGNORECASE,
)
# 疑似编造的"普适结论"措辞（无数据支撑的断言）
OVERCLAIM_RE = re.compile(
    r'(clearly shows|definitely|proves?\s+that|it\s+is\s+well\s+known|'
    r'明显表明|充分证明|众所周知|确定性地)',
    re.IGNORECASE,
)


def check_fabrication(text, report):
    """F1: 检测虚构信号（原则 1：基于事实，不懂就问，不猜测不虚构）。

    扫描代码/报告/图注里的：
    - 占位符（example/demo/test/mock/placeholder）混入正式输出
    - 过度断言（clearly/proves/well-known，无数据支撑的普适论断）
    - accession 格式（GSE/GSM）——提示用户核实真实存在性
    """
    if not isinstance(text, str) or not text.strip():
        return
    fab_hits = FABRICATION_RE.findall(text)
    overclaim_hits = OVERCLAIM_RE.findall(text)
    # 提取命中的具体词
    fab_words = [h if isinstance(h, str) else (h[0] or h[1] or "") for h in fab_hits]
    fab_words = [w for w in fab_words if w]
    has_issue = False
    if fab_words:
        # 区分严重度：accession 格式仅 WARN（需人工核实），占位符 FAIL
        accessions = [w for w in fab_words if re.match(r'GSE\d|GSM\d', w, re.I)]
        placeholders = [w for w in fab_words if w not in accessions]
        if placeholders:
            report.add("F1", "FAIL",
                       f"检测到占位/虚构信号 {placeholders[:5]}——"
                       "正式输出不应含 example/demo/mock/test_data。原则 1 违反（不虚构）")
            has_issue = True
        if accessions:
            report.add("F1", "WARN",
                       f"检测到 accession 格式 {accessions[:3]}——"
                       "请核实该编号真实存在且数据匹配（不编造 accession）")
    if overclaim_hits:
        report.add("F1", "WARN",
                   f"检测到过度断言 {overclaim_hits[:3]}——"
                   "无数据支撑的普适论断违反原则 1（基于事实）。改为具体数据支持的陈述")
    if not fab_words and not overclaim_hits:
        report.add("F1", "PASS", "无虚构/占位/过度断言信号（基于事实）")



def check_code_for_corrected_de(code_text, report):
    """D3: 扫描代码是否对 batch-corrected embedding 跑 DE（启发式）。"""
    corrected_reps = ["X_scVI", "X_harmony", "X_scanorama", "X_combat", "X_integrated"]
    de_signals = ["rank_genes_groups", "RunDEtest", "DESeq2", "edgeR", "deseq2", "pydeseq2"]
    hits_corr = [r for r in corrected_reps if r in code_text]
    hits_de = [d for d in de_signals if d in code_text]
    if hits_corr and hits_de:
        report.add("D3", "FAIL",
                   f"代码同时出现批次校正 embedding ({hits_corr}) 与 DE ({hits_de})——"
                   "🚨 批次校正后数据禁用于 DE，原则 6 违反。改用 raw counts + pseudobulk")
    elif hits_corr:
        report.add("D3", "PASS", f"检测到批次校正 ({hits_corr})，无 DE 调用（合规）")


def check_pseudobulk(code_text, report):
    """D4: 单细胞 DE 是否走 pseudobulk（启发式）。
    若 DE 信号出现但无 pseudobulk 聚合信号，提示单细胞 DE = 伪重复。
    """
    de_signals = ["rank_genes_groups", "FindAllMarkers", "ttest", "wilcoxon"]
    pb_signals = ["pseudobulk", "PseudobulkSpace", "aggregate_and_filter",
                  "sc.get.aggregate", "RunDEtest", "PyDESeq2",
                  "sum", "mean"]   # last two too generic — rely on the specific ones above
    pb_specific = [p for p in pb_signals if p in code_text if p not in ("sum", "mean")]
    hits_de = [d for d in de_signals if d in code_text]
    if hits_de and not pb_specific:
        report.add("D4", "WARN",
                   f"检测到单细胞 DE 信号 ({hits_de}) 但无 pseudobulk 聚合 ({pb_specific})——"
                   "⚠️ 单细胞 Wilcoxon/t-test 是伪重复（meta-methodology 原则 ③）。"
                   "改用 pseudobulk 聚合（PseudobulkSpace / sc.get.aggregate）+ DESeq2/edgeR。")
    elif hits_de and pb_specific:
        report.add("D4", "PASS", f"检测到 pseudobulk 聚合 ({pb_specific}) + DE——合规")


def check_ccc_hypothesis(code_text, report):
    """L2: CCC 分析的语言纪律（启发式）。
    若代码涉及细胞通讯，提示结果为假设非机制。"""
    ccc_signals = ["cellchat", "CellChat", "cellphonedb", "CellPhoneDB", "liana",
                   "LIANA", "run_liana", "run_cellphonedb", "nichenetr", "NicheNet"]
    causal_words = ["regulates", "activates", "inhibits", "induces", "promotes",
                    "drives", "causes"]
    hits_ccc = [c for c in ccc_signals if c in code_text]
    hits_causal = [w for w in causal_words if w in code_text]
    if hits_ccc and hits_causal:
        report.add("L2", "WARN",
                   f"CCC 分析 ({hits_ccc}) 附近出现因果词 ({hits_causal})——"
                   "⚠️ mRNA 共表达 ≠ 蛋白活性 ≠ 通路激活；CCC 是统计关联假设，"
                   "用 'associated with' 而非 'regulates'（meta-methodology 原则 ①③）。")
    elif hits_ccc:
        report.add("L2", "PASS", f"检测到 CCC 分析 ({hits_ccc})，无因果词（合规）")


def check_compositional(code_text, report):
    """C1: 细胞比例分析的 compositional 纪律（启发式）。
    若对细胞比例直接用卡方/Fisher，提示用 scCODA/Milo/propeller。"""
    proportion_signals = ["cellproportion", "cell_proportion", "obs['celltype'].value_counts",
                          "groupby('celltype').size", "composition"]
    chi_signals = ["chi2_contingency", "fisher_exact", "chisquare", "chi_square",
                   "chi-square", "fisher.test", "chisq.test"]
    hits_prop = [p for p in proportion_signals if p in code_text]
    hits_chi = [c for c in chi_signals if c in code_text]
    if hits_prop and hits_chi:
        report.add("C1", "WARN",
                   f"对细胞比例 ({hits_prop}) 直接用卡方/Fisher ({hits_chi})——"
                   "⚠️ 细胞比例是 compositional data（和为 1，约束），普通卡方/Fisher 忽略此约束 → 假阳性 + 方向误读。"
                   "改用 miloR / scCODA / propeller（meta-methodology 原则 ③）。")
    elif hits_prop:
        report.add("C1", "PASS", f"细胞比例分析 ({hits_prop})，未检测到卡方/Fisher（合规）")


# ----------------------------- new rule checks (A11/E7/domain) -----------------------------


def check_caliber_declaration(code_text, report):
    """A11: 统计口径声明（启发式）——统计量是否写清 X×Y×单元×聚合。

    若代码计算相关/比例/倍数等统计量，但同一脚本没有给统计量命名口径
    （如 'donor-pseudobulk'、'per-cell'、'bin-level'、'window mean' 等聚合声明），
    提示口径可能错位——项目实战经验：per-cell 校正表达 vs donor-pb 可反向。
    """
    stat_signals = ["spearmanr", "pearsonr", "np.corrcoef", "scipy.stats",
                    "logFC", "log2fc", "fold_change", "rho", "correlation",
                    "fraction", "proportion", "percentage", "ratio"]
    caliber_signals = ["donor", "pseudobulk", "pb", "per_cell", "per-cell",
                       "bin", "spot", "window", "aggregate", "mean_by",
                       "nuclei", "cell_level", "section", "tp", "timepoint"]
    hits_stat = [s for s in stat_signals if s in code_text]
    hits_cal = [c for c in caliber_signals if c in code_text]
    if hits_stat and not hits_cal:
        report.add("A11", "WARN",
                   f"检测到统计量计算 ({hits_stat[:3]}) 但未在代码中见到口径声明词 "
                   f"(donor/pseudobulk/per-cell/bin/aggregate 等)——"
                   "⚠️ 每个统计量写清 X×Y×单元×聚合（A11）：per-cell 校正表达与 donor-pb "
                   "可给反向趋势（NPPA 实例）；组成性结论默认 donor-pseudobulk。")
    elif hits_stat:
        report.add("A11", "PASS",
                   f"统计量计算 ({hits_stat[:2]}) 伴口径词 ({hits_cal[:3]})——声明已见")


def check_figure_domain(code_text, report):
    """图型域校准（启发式）——临床系图型（lollipop/forest）误用于空转机制页。

    2026-04~10 顶刊 ST 13 篇实测：lollipop 0 例、forest 0 例。若脚本画
    lollipop/forest 但没写 plot_stats_dotplot 的替代说明或域匹配理由，提示换图。
    """
    lollipop_sig = ["plot_lollipop", "lollipop", "棒棒糖"]
    forest_sig = ["plot_forest", "forest", "森林图", "meta-analysis", "meta_analysis"]
    alt_sig = ["plot_stats_dotplot", "stats_dotplot"]
    hits_l = [s for s in lollipop_sig if s in code_text]
    hits_f = [s for s in forest_sig if s in code_text]
    hits_alt = [s for s in alt_sig if s in code_text]
    if (hits_l or hits_f) and not hits_alt:
        which = (hits_l + hits_f)[0]
        report.add("DOM", "WARN",
                   f"检测到 {which}（临床/meta 系图型）但未用 plot_stats_dotplot——"
                   "⚠️ 图型域校准（2026 顶刊 ST 13 篇 0 例）：多实体单统计量（模块-性状/"
                   "TF-模块/态-通路）首选 plot_stats_dotplot；lollipop/forest 仅用户点名或"
                   "双统计量+置换零带/临床 meta 时用。若确属域匹配请在脚本注释写明理由。")
    elif hits_alt:
        report.add("DOM", "PASS", "plot_stats_dotplot 已用（图型域合规）")


def check_number_gate_heuristic(code_text, report):
    """E7: 数字门启发式——定量数字不应硬编码进 caption/title 字符串。

    若代码里出现 figtitle/fig.text/ax.set_title/slide caption 类字符串内含
    阿拉伯数字（如 'rho=0.80'、'12.5x'、'+48%'），提示该数字应来自唯一依据表
    （caption-from-table），禁止手写进文本——改动数字=重跑 runner 而非改文本。
    """
    caption_sig = ["set_title", "fig.suptitle", "fig.text", "ax.text", "add_textbox",
                   "add_paragraph", "caption", "slide.shapes", "text_frame"]
    hits_cap = [s for s in caption_sig if s in code_text]
    if hits_cap:
        # 找字符串里直接写死的数字模式（rho=0.xx / Nx / +/-NN% / p=x）
        hard_num = re.findall(r"['\"][^'\"]*?(rho\s*=\s*[\d.]+|\d+\.?\d*x\b|[+\-]\d+\.?\d*%|p\s*=\s*[\deE.-]+)[^'\"]*?['\"]",
                              code_text)
        # 过滤变量插值（f-string 的 {} 或 format）视为合规
        fstring = re.findall(r"f['\"][^'\"]*?(rho\s*=\s*\{|\{[^}]*rho|\{[^}]*%|\{[^}]*x\b)[^'\"]*?['\"]",
                             code_text)
        if hard_num and len(hard_num) > len(fstring):
            report.add("E7", "WARN",
                       f"标题/注释字符串中疑似硬编码定量数字（如 {hard_num[0][:30]}…）——"
                       "⚠️ 数字门（E7）：定量数字只从唯一依据表读出（caption-from-table），"
                       "禁止手写进 caption/title；改动数字=重跑 runner 更新表而非改文本。")
        else:
            report.add("E7", "PASS", "定量字符串均经变量插值（未硬编码）")


# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser(
        description="cns-bio-pilot 科学严谨性自动校验",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("target", nargs="?", help="AnnData(.h5ad)/DE表(.csv/.tsv)/HTML/代码文件 或目录")
    ap.add_argument("--type", choices=["adata", "de", "deconv", "velocity", "slides", "code"],
                    help="目标类型（默认按扩展名推断）")
    ap.add_argument("--lang", help="额外检查文本文件措辞")
    args = ap.parse_args()

    if not args.target and not args.lang:
        ap.print_help()
        return 2

    report = Report()

    if args.lang:
        check_language(Path(args.lang).read_text(encoding="utf-8", errors="ignore"), report)
        sys.exit(report.summary())

    if not args.target:
        return 2

    target = Path(args.target)
    ttype = args.type
    if not ttype:
        if target.suffix == ".h5ad":
            ttype = "adata"
        elif target.suffix in (".csv", ".tsv"):
            ttype = "de"
        elif target.suffix in (".html", ".htm") or target.is_dir():
            ttype = "slides"
        elif target.suffix in (".py", ".R", ".ipynb"):
            ttype = "code"
        else:
            ttype = "adata"

    print(f"检查目标: {target}  类型: {ttype}\n")

    if ttype == "adata":
        check_adata(target, report)
    elif ttype == "de":
        check_de(target, report)
    elif ttype == "deconv":
        check_deconv(target, report)
    elif ttype == "velocity":
        check_velocity(target, report)
    elif ttype == "slides":
        check_slides(target, report)
    elif ttype == "code":
        code_text = Path(target).read_text(encoding="utf-8", errors="ignore")
        check_code_for_corrected_de(code_text, report)
        check_pseudobulk(code_text, report)
        check_ccc_hypothesis(code_text, report)
        check_compositional(code_text, report)
        check_caliber_declaration(code_text, report)
        check_figure_domain(code_text, report)
        check_number_gate_heuristic(code_text, report)
        check_language(code_text, report)
        check_fabrication(code_text, report)

    sys.exit(report.summary())


if __name__ == "__main__":
    main()

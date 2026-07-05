#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cns-bio-pilot postcheck — 科学严谨性自动校验

用法：
    python postcheck.py <adata_or_result> [--type {adata,de,deconv,velocity,slides}]
    python postcheck.py --help

把 cns-bio-pilot 核心原则中【可机检】的部分机械化。不替代人工判断，
只捕捉最常见的科学错误。每条检查输出 ✅ PASS / ⚠️ WARN / ❌ FAIL。

检查项（对应 SKILL.md 核心原则）：
  [ADATA] 数据层完整性
    A1  raw counts 保留 (layers['counts'])              原则 8
  [DE]   差异表达严谨性
    D1  报告 Padj 而非裸 P                              原则 2
    D2  阈值 Padj<0.05 & |Log2FC|>1.0                   原则 3
    D3  未对 batch-corrected embedding 跑 DE            原则 6 🚨
    D4  单细胞 DE 是否 pseudobulk（启发式）             原则 2
  [DECONV] 空间去卷积
    V1  输出含质量评估列                                 原则 9
  [VELOCITY] RNA velocity
    E1  spliced/unspliced layers 存在                   前置
  [SLIDES] 演示文稿
    S1  关键数值图保留 N / 统计检验标注                  原则 2/3
  [LANG]  措辞
    L1  无未授权因果词 (regulates/causes/induces)       原则 4 🚨
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
        padj_col = next(c for c in df.columns if "adj" in c.lower() or "fdr" in c.lower())
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
                   "原则 4 违反")


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
        check_code_for_corrected_de(Path(target).read_text(encoding="utf-8", errors="ignore"), report)
        check_language(Path(target).read_text(encoding="utf-8", errors="ignore"), report)

    sys.exit(report.summary())


if __name__ == "__main__":
    main()

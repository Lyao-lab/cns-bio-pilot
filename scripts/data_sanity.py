#!/usr/bin/env python3
"""data_sanity — 分析前数据完整性门（preflight，2026-10-10 新增）。

定位：postcheck 是"分析后"严谨性检查；本脚本是"分析前"坏数据/诱饵检测——
BioAgent Bench（arXiv 2601.21800）实测 agent 最大失效模式：10 例损坏输入只检出 7 例，
agent 倾向"绕过去"而不是停。**加载任何主数据（h5ad/csv/tsv/fastq）做分析前必须先跑本脚本**。

检查项（按目标类型）：
  h5ad:  S1 常数/近常数矩阵（全基因零方差 → 假数据/载入错误）
         S2 全零 X / NaN/Inf 占比
         S3 obs_names 重复
         S4 物种标记（人类 ENSG/MT- 前缀 vs 小鼠 ENSMUSG/mt-）→ 与期望物种比对（--species）
         S5 线粒体读数比例极端值（>50% warn，>80% FAIL）
         S6 metadata 错配（--meta-col + --meta-file：obs 列 vs 外部样本表不一致 → 样本/文件错配）
  table: T1 常数列 / T2 NaN 比例 / T3 重复键列（--key-col）
  fastq: F1 前 N reads 的 N 碱基率（>5% WARN，>20% FAIL——90% N 是基准里的"绕不过去"陷阱）

用法：
  python data_sanity.py <path> [--species human|mouse] [--meta-col sample]
                        [--meta-file samples.csv] [--key-col col] [-n 10000]
退出码：FAIL=1（停下修数据，不进入分析），WARN=0（记录后可继续）。
"""
import argparse
import sys
from pathlib import Path

OK, WARN, FAIL = "PASS", "WARN", "FAIL"


class R:
    items = []

    @classmethod
    def add(cls, code, sev, msg):
        cls.items.append((code, sev, msg))
        print(f"  {'✅' if sev == OK else '⚠️' if sev == WARN else '❌'} [{code}] {sev}: {msg}")

    @classmethod
    def exit_code(cls):
        return 1 if any(s == FAIL for _, s, _ in cls.items) else 0


def check_h5ad(path, species=None, meta_col=None, meta_file=None):
    import anndata as ad
    import numpy as np
    # backed 稀疏矩阵不支持任意切片（anndata 版本坑）：小文件全载；大文件 h5py 直采 X
    full = None
    if path.stat().st_size < 4 * 2**30:
        full = ad.read_h5ad(path)
        a = full
    else:
        a = ad.read_h5ad(path, backed='r')
    gi = np.linspace(0, a.n_vars - 1, min(500, a.n_vars)).astype(int)
    ci = np.linspace(0, a.n_obs - 1, min(1000, a.n_obs)).astype(int)
    if full is not None:
        import scipy.sparse as sp
        sub = a.X[ci][:, gi]
        dense = sub.toarray() if sp.issparse(sub) else np.asarray(sub)
    else:
        import h5py
        with h5py.File(path, 'r') as f:
            X = f['X'] if isinstance(f['X'], h5py.Dataset) else \
                f['X'][('data' in f['X'] and 'csr_matrix' in f['X'].keys() and 'csr_matrix') or
                       ('csc_matrix' in f['X'].keys() and 'csc_matrix') or list(f['X'].keys())[0]]
            # 大文件只采 X 的前 1000 行切片（h5py 不支持步进行采，取前块即可满足 sanity 目的）
            Xd = X[:min(1000, a.n_obs), :min(500, a.n_vars)]
            dense = np.asarray(Xd) if isinstance(Xd, np.ndarray) else \
                np.asarray(Xd[()] if hasattr(Xd, 'shape') else Xd)
        a.file.close()
    if not np.isfinite(dense).all():
        R.add("S2", FAIL, f"矩阵含 NaN/Inf（抽样 {np.isnan(dense).mean():.1%}）——载入/写出事故")
    else:
        R.add("S2", OK, "抽样块无 NaN/Inf")
    frac_const = float((dense.var(axis=0) < 1e-12).mean()) if dense.size else 1.0
    if frac_const > 0.95:
        R.add("S1", FAIL, f"{frac_const:.0%} 抽样基因零方差（疑似常数矩阵/占位数据）——禁止进入分析")
    elif frac_const > 0.5:
        R.add("S1", WARN, f"{frac_const:.0%} 抽样基因零方差——核查载入方式")
    else:
        R.add("S1", OK, f"常数基因比例 {frac_const:.1%}（正常）")
    # S3
    dup = a.obs_names.duplicated().sum()
    R.add("S3", FAIL if dup > 0.01 * a.n_obs else (WARN if dup else OK),
          f"obs_names 重复 {dup} 条")
    # S4 物种
    if species:
        vn = a.var_names.astype(str)
        human = vn.str.startswith(('ENSG', 'MT-')).mean()
        mouse = vn.str.startswith(('ENSMUSG', 'mt-')).mean()
        guess = 'human' if human > mouse else 'mouse' if mouse > human else 'unknown'
        ok = guess == species
        R.add("S4", FAIL if guess != 'unknown' and not ok else (WARN if guess == 'unknown' else OK),
              f"基因 ID 判定物种={guess}，期望={species}" + ("" if ok else "——错物种文件！停"))
    # S5 线粒体（只查比例型列：值域在 0-1；计数型列如 total_counts_mt 跳过）
    mt_cols = [c for c in a.obs.columns
               if ('pct' in c.lower() or 'percent' in c.lower() or 'frac' in c.lower())
               and ('mt' in c.lower() or 'mito' in c.lower())]
    if mt_cols:
        c = mt_cols[0]
        try:
            m = a.obs[c].astype(float)
            if 0 <= m.min() and m.max() <= 1.0:
                mx = float(m.max())
                R.add("S5", FAIL if mx > 0.8 else (WARN if mx > 0.5 else OK),
                      f"{c} max={mx:.1%}（>80% FAIL / >50% WARN）")
        except ValueError:
            pass
    # S6 metadata 错配
    if meta_col and meta_file and meta_col in a.obs.columns:
        import pandas as pd
        ext = set(pd.read_csv(meta_file).iloc[:, 0].astype(str))
        got = set(a.obs[meta_col].astype(str).unique())
        unknown = got - ext
        R.add("S6", FAIL if len(unknown) > 0.3 * len(got) else (WARN if unknown else OK),
              f"obs['{meta_col}'] 有 {len(unknown)}/{len(got)} 个值不在 {Path(meta_file).name}——样本/文件错配？"
              + (f" 例:{sorted(unknown)[:3]}" if unknown else ""))
    a.file.close()


def check_table(path, key_col=None):
    import numpy as np
    import pandas as pd
    df = pd.read_csv(path, nrows=5000)
    const = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
    R.add("T1", FAIL if len(const) > 0.5 * len(df.columns) else (WARN if const else OK),
          f"常数列 {len(const)}/{len(df.columns)}" + (f" 例:{const[:3]}" if const else ""))
    nanr = float(df.isna().mean().max())
    R.add("T2", FAIL if nanr > 0.5 else (WARN if nanr > 0.2 else OK),
          f"最高 NaN 比例列 {nanr:.0%}")
    if key_col and key_col in df.columns:
        d = df[key_col].duplicated().sum()
        R.add("T3", FAIL if d else WARN if d > 0 else OK, f"键列 {key_col} 重复 {d} 条")


def check_fastq(path, n_reads=10000):
    n_count = total = b = 0
    with open(path, 'rb') as f:
        for i, line in enumerate(f):
            if i % 4 == 1 and line:
                s = line.rstrip(b'\n')
                n_count += s.count(b'N')
                total += len(s)
                b += 1
                if b >= n_reads or total > 5_000_000:
                    break
    if total == 0:
        R.add("F1", FAIL, "空 FASTQ / 非标准 4 行结构")
        return
    rate = n_count / total
    R.add("F1", FAIL if rate > 0.2 else (WARN if rate > 0.05 else OK),
          f"前 {b} reads N 碱基率 {rate:.1%}（>20% FAIL / >5% WARN——基准实测的'绕不过去'陷阱）")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--species", choices=["human", "mouse"])
    ap.add_argument("--meta-col")
    ap.add_argument("--meta-file")
    ap.add_argument("--key-col")
    ap.add_argument("-n", type=int, default=10000, help="fastq 抽样 reads 数")
    a = ap.parse_args()
    p = Path(a.target)
    print(f"[data_sanity] 分析前置检查: {p}\n")
    if p.suffix == '.h5ad':
        check_h5ad(p, a.species, a.meta_col, a.meta_file)
    elif p.suffix in ('.csv', '.tsv'):
        check_table(p, a.key_col)
    elif p.suffix in ('.fastq', '.fq', '.gz'):
        check_fastq(p, a.n)
    else:
        print(f"未知类型 {p.suffix}——不检查，直接退出 0")
    n_fail = sum(1 for _, s, _ in R.items if s == FAIL)
    print(f"\n{'='*46}\n{'🚨 FAIL——停下修数据，禁止进入分析' if n_fail else '✅ 无 FAIL（WARN 需记录）'}")
    sys.exit(R.exit_code())


if __name__ == "__main__":
    main()

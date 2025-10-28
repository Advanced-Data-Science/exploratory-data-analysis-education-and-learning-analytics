#!/usr/bin/env python3
import argparse, os, json
import pandas as pd
from pathlib import Path
from src.utils import summarize, guess_target, guess_time, find_engagement_columns
from src.eda_tools import univariate, bivariate, multivariate, time_series_and_patterns, build_report

def cmd_eda(args):
    data_path = Path(args.data).resolve()
    df = pd.read_csv(data_path)
    target = args.target if args.target and args.target in df.columns else guess_target(df)
    time_col = args.time if args.time and args.time in df.columns else guess_time(df)

    root = Path(__file__).resolve().parent
    reports = root / "reports"
    figs = reports / "figures"
    outputs = root / "outputs"
    for p in (reports, figs, outputs): p.mkdir(parents=True, exist_ok=True)

    summarize(df).to_csv(outputs / "summary_stats.csv", index=False)

    paths = {}
    paths["uni"] = univariate(df, str(figs / "univariate"))
    paths["bivar"] = bivariate(df, str(figs / "bivariate"), str(outputs))
    paths["multi"] = multivariate(df, str(figs / "multivariate"))
    time_notes, seg_used = time_series_and_patterns(df, str(figs / "patterns"), str(outputs), time_col=time_col, engagement_cols=None)

    build_report(df, paths, str(reports / "MAIN_ANALYSIS.md"), target=target, time_notes="; ".join(time_notes), seg_used=seg_used)
    print("Main Analysis generated.")
    print(f"- Report: {reports / 'MAIN_ANALYSIS.md'}")
    print(f"- Figures: {figs}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("eda", help="Run rubric-complete EDA on any CSV")
    p.add_argument("--data", required=True)
    p.add_argument("--target", default=None)
    p.add_argument("--time", default=None)
    p.set_defaults(func=cmd_eda)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

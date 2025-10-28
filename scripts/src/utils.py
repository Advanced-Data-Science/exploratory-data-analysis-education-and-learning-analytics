
import numpy as np
import pandas as pd

TARGET_GUESSES = ["final_result","outcome","label","result","pass_fail","status","target"]
TIME_HINTS = ["date","time","week","day","timestamp"]

def is_numeric(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s)

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in df.columns:
        s = df[c]
        row = {"column": c, "dtype": str(s.dtype), "missing": int(s.isna().sum()), "missing_rate": float(s.isna().mean())}
        if is_numeric(s):
            row.update({"mean": float(s.mean()), "std": float(s.std(ddof=1)) if s.count()>1 else float("nan"),
                        "min": float(s.min()), "q25": float(s.quantile(0.25)), "median": float(s.median()),
                        "q75": float(s.quantile(0.75)), "max": float(s.max())})
        else:
            row.update({"n_unique": int(s.nunique(dropna=True))})
        rows.append(row)
    return pd.DataFrame(rows)

def safe_to_datetime(s: pd.Series):
    try:
        return pd.to_datetime(s, errors="raise")
    except Exception:
        return None

def guess_target(df: pd.DataFrame):
    lc = [c.lower() for c in df.columns]
    for g in TARGET_GUESSES:
        if g in lc:
            return df.columns[lc.index(g)]
    cats = [c for c in df.columns if not is_numeric(df[c]) and 2 <= df[c].nunique(dropna=True) <= 7]
    return cats[0] if cats else None

def guess_time(df: pd.DataFrame):
    for c in df.columns:
        cl = c.lower()
        if any(h in cl for h in TIME_HINTS):
            try:
                pd.to_datetime(df[c], errors="raise"); return c
            except Exception: pass
    for c in df.columns:
        if safe_to_datetime(df[c]) is not None: return c
    return None

def find_engagement_columns(df: pd.DataFrame):
    cols = [c for c in df.columns if any(k in c.lower() for k in ["click","engage","access","view","activity"])]
    cols = [c for c in cols if is_numeric(df[c])]
    return cols

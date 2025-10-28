
import os, json, itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .utils import is_numeric, summarize, safe_to_datetime, guess_target, guess_time, find_engagement_columns

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def savefig(p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    plt.tight_layout()
    plt.savefig(p, dpi=140)
    plt.close()

def univariate(df, figdir):
    examples = []
    for c in df.columns:
        s = df[c].dropna()
        if s.empty: continue
        if is_numeric(s):
            plt.figure(); plt.hist(s, bins=30); plt.title(f"Histogram: {c}"); p=os.path.join(figdir,f"hist_{c}.png"); savefig(p); examples.append(p)
            plt.figure(); plt.boxplot(s, labels=[c]); plt.title(f"Boxplot: {c}"); savefig(os.path.join(figdir,f"box_{c}.png"))
        elif s.nunique() <= 20:
            vc = s.astype(str).value_counts().head(20)
            plt.figure(); plt.bar(vc.index, vc.values); plt.xticks(rotation=60, ha="right"); plt.title(f"Top Categories: {c}")
            p=os.path.join(figdir, f"bar_{c}.png"); savefig(p); examples.append(p)
    return examples

def bivariate(df, figdir, outputs_dir):
    num = df.select_dtypes(include=[np.number])
    out = {}
    if num.shape[1] >= 2:
        corr = num.corr()
        corr.to_csv(os.path.join(outputs_dir,"correlation.csv"))
        plt.figure(figsize=(6,5))
        plt.imshow(corr, interpolation='nearest')
        plt.title("Correlation Heatmap")
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=60, ha="right")
        plt.yticks(range(len(corr.columns)), corr.columns)
        plt.colorbar()
        p = os.path.join(figdir,"corr_heatmap.png"); savefig(p); out["heatmap"]=p
        pairs = list(itertools.combinations(num.columns[:min(6,len(num.columns))],2))[:3]
        out["scatters"]=[]
        for a,b in pairs:
            plt.figure(); plt.scatter(df[a], df[b], s=8, alpha=0.6)
            plt.xlabel(a); plt.ylabel(b); plt.title(f"Scatter: {a} vs {b}")
            sp=os.path.join(figdir, f"scatter_{a}_vs_{b}.png"); savefig(sp); out["scatters"].append(sp)
        if pairs:
            a,b=pairs[0]
            plt.figure(); plt.hexbin(df[a], df[b], gridsize=35); plt.xlabel(a); plt.ylabel(b); plt.title(f"2D Density: {a} vs {b}")
            dp=os.path.join(figdir, f"kde2d_{a}_vs_{b}.png"); savefig(dp); out["kde2d"]=dp
    return out

def multivariate(df, figdir):
    outs = {}
    num = df.select_dtypes(include=[np.number])
    num = num.loc[:, num.notna().any(axis=0)]
    if num.shape[1] >= 3:
        imputer = SimpleImputer(strategy="median")
        scaler = StandardScaler(with_mean=True)
        X = imputer.fit_transform(num.values)
        X = scaler.fit_transform(X)
        pca = PCA(n_components=3, random_state=0).fit(X)
        comp = pca.transform(X)
        plt.figure(); plt.scatter(comp[:,0], comp[:,1], s=8, alpha=0.6); plt.xlabel("PC1"); plt.ylabel("PC2"); plt.title(f"PCA 2D (var={pca.explained_variance_ratio_[:2].sum():.2%})")
        p2=os.path.join(figdir,"pca2.png"); savefig(p2); outs["pca2"]=p2
        plt.figure(); plt.scatter(comp[:,0], comp[:,2], s=8, alpha=0.6); plt.xlabel("PC1"); plt.ylabel("PC3"); plt.title("PCA PC1 vs PC3")
        p3=os.path.join(figdir,"pca13.png"); savefig(p3); outs["pca13"]=p3
    return outs

def time_series_and_patterns(df, figdir, outputs_dir, time_col=None, engagement_cols=None):
    notes=[]
    if time_col is None:
        # attempt to guess
        for c in df.columns:
            try:
                pd.to_datetime(df[c], errors="raise"); time_col=c; break
            except Exception: pass
    if time_col:
        try:
            t = pd.to_datetime(df[time_col], errors="coerce")
            if not engagement_cols:
                num = df.select_dtypes(include=[np.number])
                engagement_cols = num.var().sort_values(ascending=False).head(3).index.tolist() if num.shape[1]>0 else []
            for c in engagement_cols[:3]:
                mask = t.notna() & df[c].notna()
                if not mask.any(): continue
                order = np.argsort(t[mask].values)
                s = df.loc[mask, c].values[order]
                plt.figure(); plt.plot(range(len(s)), s); plt.title(f"Temporal trend (ordered by {time_col}): {c}")
                savefig(os.path.join(figdir, f"time_{c}.png"))
            notes.append(f"Detected time column: **{time_col}**")
        except Exception:
            notes.append("Time column detected but could not be used.")
    else:
        notes.append("No time column detected; used cross-sectional alternatives.")
    # Outliers
    num = df.select_dtypes(include=[np.number])
    out_counts = {}
    for c in num.columns:
        s = df[c].astype(float)
        q1, q3 = s.quantile(0.25), s.quantile(0.75); iqr=q3-q1
        z = (s - s.mean())/s.std(ddof=0) if s.std(ddof=0) else pd.Series(0, index=s.index)
        mask = ((s < (q1-1.5*iqr)) | (s > (q3+1.5*iqr)) | (z.abs()>3)).fillna(False)
        out_counts[c] = int(mask.sum())
    json.dump(out_counts, open(os.path.join(outputs_dir,"outliers_count.json"), "w"), indent=2)
    # Segmentation
    seg_used=None
    if num.shape[1]>0:
        seg_used = num.var().sort_values(ascending=False).index[0]
        bins = pd.qcut(df[seg_used].rank(method="first"), q=4, labels=["Q1-Low","Q2","Q3","Q4-High"])
        seg = pd.DataFrame({"segment": bins})
        keep = [c for c in num.columns if c != seg_used][:3]
        for c in keep: seg[c]=df[c].values
        summary = seg.groupby("segment")[keep].mean()
        summary.to_csv(os.path.join(outputs_dir,"segment_summary.csv"))
        for c in keep:
            plt.figure(); summary[c].plot(kind="bar"); plt.title(f"Segment Means by {seg_used}: {c}")
            savefig(os.path.join(figdir, f"segment_means_{c}.png"))
    return notes, seg_used

def build_report(df, paths, out_md, target=None, time_notes="", seg_used=None):
    md = [
        "# Main Analysis",
        "This section includes the six required analysis tools with embedded visuals.",
        "",
        "## 1. Variable Analysis",
        "### 1.1 Univariate",
    ]

    for p in paths.get("uni", [])[:4]:
        md.append(f"![{os.path.basename(p)}]({p})")

    md += [
        "",
        "### 1.2 Summary Statistics",
        "See `outputs/summary_stats.csv` for descriptive metrics.",
        "",
        "### 1.3 Bivariate",
    ]

    if paths.get("bivar", {}).get("heatmap"):
        md.append(f"![Correlation Heatmap]({paths['bivar']['heatmap']})")

    for sp in paths.get("bivar", {}).get("scatters", [])[:3]:
        md.append(f"![Scatter Plot]({sp})")

    if paths.get("bivar", {}).get("kde2d"):
        md.append(f"![2D Density Plot]({paths['bivar']['kde2d']})")

    md += ["", "### 1.4 Multivariate"]

    for k in ["pca2", "pca13"]:
        if paths.get("multi", {}).get(k):
            md.append(f"![{k}]({paths['multi'][k]})")

    md += [
        "",
        "## 2. Pattern Analysis",
        "### 2.1 Time Series Analysis",
        time_notes or "_No time column detected._",
        "",
        "### 2.2 Pattern Recognition",
        "Outlier counts saved to `outputs/outliers_count.json`.",
        "",
        "### 2.3 Segmentation Analysis",
        f"Segmentation used quartiles of `{seg_used}`." if seg_used else "Quartile segmentation applied.",
    ]

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

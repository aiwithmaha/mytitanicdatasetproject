"""Visualization Step 1 — Combined EDA figure grid."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import glob

patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
train_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
df = pd.read_csv(train_file)

target_hints = ['target','label','survived','price','y','class','churn','fraud']
target = next((c for h in target_hints for c in df.columns if h in c.lower()), df.columns[-1])

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c != target][:8]  # max 8

os.makedirs('analysis/reports', exist_ok=True)
sns.set_style('whitegrid')

if numeric_cols:
    n = len(numeric_cols)
    # squeeze=False ensures axes is always a 2-D array, safe to flatten for n=1..8
    if n > 4:
        fig, axes = plt.subplots(2, 4, figsize=(20, 10), squeeze=False)
    else:
        fig, axes = plt.subplots(1, max(n, 1), figsize=(5*max(n, 1), 5), squeeze=False)
    axes = axes.flatten()

    for i, col in enumerate(numeric_cols):
        ax = axes[i]
        if df[target].nunique() <= 10:
            for cls in sorted(df[target].unique()):
                df[df[target]==cls][col].dropna().hist(bins=25, alpha=0.6,
                                                        label=str(cls), ax=ax)
        else:
            df[col].dropna().hist(bins=30, ax=ax, color='steelblue')
        ax.set_title(col, fontweight='bold', fontsize=10)
        mean_val = df[col].mean()
        # axvline must be added BEFORE legend so the mean line appears in it
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=1, label=f'mean={mean_val:.1f}')
        ax.legend(fontsize=7)

    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)

    plt.suptitle('EDA: Feature Distributions by Target', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/eda_overview.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/eda_overview.png")

# box plots
if numeric_cols and df[target].nunique() <= 10:
    nc = len(numeric_cols)
    if nc > 4:
        fig, axes = plt.subplots(2, 4, figsize=(20, 10), squeeze=False)
    else:
        fig, axes = plt.subplots(1, max(nc, 1), figsize=(5*max(nc, 1), 5), squeeze=False)
    axes = axes.flatten()
    palette = {v: c for v, c in zip(sorted(df[target].unique()), ['#ff6b6b', '#51cf66'])}
    for i, col in enumerate(numeric_cols):
        # Use seaborn so whitegrid style is consistent with the histogram panel.
        # hue=x + legend=False keeps the modern seaborn categorical API happy —
        # passing `palette` without `hue` is deprecated and (on this seaborn
        # version) raises ValueError because the internal hue-mapping expects
        # string-typed keys while `target` here is int-typed.
        sns.boxplot(data=df, x=target, y=col, hue=target, ax=axes[i],
                    palette=palette, width=0.5, linewidth=1.2, fliersize=3,
                    legend=False, dodge=False)
        axes[i].set_title(col, fontweight='bold', fontsize=9)
        axes[i].set_xlabel(target)
    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)
    plt.suptitle('Box Plots by Target Class', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/boxplots_by_target.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/boxplots_by_target.png")

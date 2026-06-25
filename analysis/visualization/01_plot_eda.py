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
    fig, axes = plt.subplots(2, 4, figsize=(20, 10)) if n > 4 else \
                plt.subplots(1, n, figsize=(5*n, 5))
    axes = np.array(axes).flatten()

    for i, col in enumerate(numeric_cols):
        ax = axes[i]
        if df[target].nunique() <= 10:
            for cls in df[target].unique():
                df[df[target]==cls][col].dropna().hist(bins=25, alpha=0.6,
                                                        label=str(cls), ax=ax)
            ax.legend(fontsize=7)
        else:
            df[col].dropna().hist(bins=30, ax=ax, color='steelblue')
        ax.set_title(col, fontweight='bold', fontsize=10)
        mean_val = df[col].mean()
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=1, label=f'mean={mean_val:.1f}')

    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)

    plt.suptitle('EDA: Feature Distributions by Target', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/eda_overview.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/eda_overview.png")

# box plots
if numeric_cols and df[target].nunique() <= 10:
    fig, axes = plt.subplots(2, 4, figsize=(20, 10)) if len(numeric_cols) > 4 else \
                plt.subplots(1, len(numeric_cols), figsize=(5*len(numeric_cols), 5))
    axes = np.array(axes).flatten()
    for i, col in enumerate(numeric_cols):
        df.boxplot(column=col, by=target, ax=axes[i])
        axes[i].set_title(col, fontweight='bold', fontsize=9)
        axes[i].set_xlabel(target)
    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)
    plt.suptitle('Box Plots by Target Class', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/boxplots_by_target.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/boxplots_by_target.png")

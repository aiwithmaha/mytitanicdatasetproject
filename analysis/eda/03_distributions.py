"""EDA Step 3 — Numeric and categorical distributions.

Output: analysis/reports/numeric_distributions.png
        analysis/reports/categorical_distributions.png
"""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as spstats

patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
train_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
if train_file is None:
    print("No CSV file found — skipping.")
    sys.exit(0)

df = pd.read_csv(train_file)
os.makedirs('analysis/reports', exist_ok=True)
sns.set_style('whitegrid')

print("EDA - DISTRIBUTIONS")

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
plot_numeric = [c for c in numeric_cols if 'id' not in c.lower()][:8]

if plot_numeric:
    n = len(plot_numeric)
    ncols = min(4, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 4.5*nrows), squeeze=False)
    axes = axes.flatten()

    for i, col in enumerate(plot_numeric):
        ax = axes[i]
        data = df[col].dropna()
        sns.histplot(data, kde=True, ax=ax, color='#4ecdc4', edgecolor='white')
        skew = spstats.skew(data)
        ax.axvline(data.mean(), color='#ff6b6b', linestyle='--', linewidth=1.2,
                   label='mean=' + format(data.mean(), '.1f'))
        ax.set_title(col + '  (skew=' + format(skew, '+.2f') + ')', fontweight='bold', fontsize=10)
        ax.legend(fontsize=7)
        print(col, 'skew', round(skew, 3), 'mean', round(data.mean(), 2), 'std', round(data.std(), 2))

    for j in range(len(plot_numeric), len(axes)):
        axes[j].set_visible(False)

    plt.suptitle('Numeric Feature Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/numeric_distributions.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/numeric_distributions.png")

cat_cols = df.select_dtypes(include=['object']).columns.tolist()
plot_cat = [c for c in cat_cols if df[c].nunique() <= 10][:6]

if plot_cat:
    n = len(plot_cat)
    ncols = min(3, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5*ncols, 4.5*nrows), squeeze=False)
    axes = axes.flatten()

    for i, col in enumerate(plot_cat):
        ax = axes[i]
        counts = df[col].value_counts()
        sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax,
                    hue=counts.index.astype(str), palette='mako', legend=False)
        ax.set_title(col, fontweight='bold', fontsize=10)
        ax.set_ylabel('Count')
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

    for j in range(len(plot_cat), len(axes)):
        axes[j].set_visible(False)

    plt.suptitle('Categorical Feature Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/categorical_distributions.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/categorical_distributions.png")
else:
    print("No low-cardinality categorical columns found for plotting.")

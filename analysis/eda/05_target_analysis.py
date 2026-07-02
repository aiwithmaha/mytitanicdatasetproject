"""EDA Step 5 — Target variable analysis.

Output: analysis/reports/target_distribution.png
        analysis/reports/target_vs_features.png
"""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
train_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
if train_file is None:
    print("No CSV file found - skipping.")
    sys.exit(0)

df = pd.read_csv(train_file)
os.makedirs('analysis/reports', exist_ok=True)
sns.set_style('whitegrid')

target_hints = ['target', 'label', 'survived', 'price', 'y', 'class', 'churn', 'fraud']
target = next((c for h in target_hints for c in df.columns if h in c.lower()), df.columns[-1])

print("EDA - TARGET ANALYSIS")
print("Target column:", target)
counts = df[target].value_counts().sort_index()
pct = (counts / counts.sum() * 100).round(1)
print(counts.to_string())
print(pct.to_string())

# ── target distribution (count + pie) ───────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
colors = ['#ff6b6b', '#51cf66'] if len(counts) == 2 else sns.color_palette('mako', len(counts))

bars = axes[0].bar(counts.index.astype(str), counts.values, color=colors, edgecolor='white')
for bar, val, p in zip(bars, counts.values, pct.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, val + max(counts.values)*0.01,
                 f'{val} ({p}%)', ha='center', fontsize=10, fontweight='bold')
axes[0].set_title(f'{target} — Count', fontweight='bold')
axes[0].set_ylabel('Count')

axes[1].pie(counts.values, labels=[f'{i} ({p}%)' for i, p in zip(counts.index, pct.values)],
            colors=colors, autopct=None, startangle=90, wedgeprops={'edgecolor': 'white'})
axes[1].set_title(f'{target} — Proportion', fontweight='bold')

plt.suptitle(f'Target Variable Distribution: {target}', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analysis/reports/target_distribution.png', dpi=120, bbox_inches='tight')
plt.close()
print("[OK] Saved analysis/reports/target_distribution.png")

# ── numeric features vs target ──────────────────────────────────────────────────
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c != target and 'id' not in c.lower()][:6]

if numeric_cols and df[target].nunique() <= 10:
    n = len(numeric_cols)
    ncols = min(3, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5*ncols, 4.5*nrows), squeeze=False)
    axes = axes.flatten()

    for i, col in enumerate(numeric_cols):
        ax = axes[i]
        sns.violinplot(data=df, x=target, y=col, ax=ax, hue=target,
                        palette=colors, legend=False, inner='quartile')
        ax.set_title(f'{col} by {target}', fontweight='bold', fontsize=10)

    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)

    plt.suptitle(f'Feature Distributions by {target}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis/reports/target_vs_features.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("[OK] Saved analysis/reports/target_vs_features.png")

# ── summary CSV ──────────────────────────────────────────────────────────────────
summary = pd.DataFrame({'class': counts.index, 'count': counts.values, 'pct': pct.values})
summary.to_csv('analysis/reports/target_distribution.csv', index=False)
print("[OK] Saved analysis/reports/target_distribution.csv")

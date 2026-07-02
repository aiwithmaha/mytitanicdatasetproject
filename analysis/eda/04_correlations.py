"""EDA Step 4 — Correlation heatmaps (Pearson + Spearman) and top pairs.

Output: analysis/reports/correlations.png
        analysis/reports/correlations.csv
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
sns.set_style('white')

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
num_df = df[numeric_cols]

pearson = num_df.corr(method='pearson')
spearman = num_df.corr(method='spearman')

print("EDA - CORRELATIONS")
print("Numeric columns:", numeric_cols)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
sns.heatmap(pearson, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=0.5, ax=axes[0], cbar_kws={'shrink': 0.8})
axes[0].set_title('Pearson Correlation', fontweight='bold')

sns.heatmap(spearman, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=0.5, ax=axes[1], cbar_kws={'shrink': 0.8})
axes[1].set_title('Spearman Correlation', fontweight='bold')

plt.suptitle('Correlation Heatmaps', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analysis/reports/correlations.png', dpi=120, bbox_inches='tight')
plt.close()
print("[OK] Saved analysis/reports/correlations.png")

pairs = []
cols = pearson.columns.tolist()
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        pairs.append((cols[i], cols[j], pearson.iloc[i, j]))
pairs_df = pd.DataFrame(pairs, columns=['feature_a', 'feature_b', 'pearson_r'])
pairs_df['abs_r'] = pairs_df['pearson_r'].abs()
pairs_df = pairs_df.sort_values('abs_r', ascending=False).drop(columns='abs_r')

print("Top correlated pairs:")
print(pairs_df.head(10).to_string(index=False))

pairs_df.to_csv('analysis/reports/correlations.csv', index=False)
print("[OK] Saved analysis/reports/correlations.csv")

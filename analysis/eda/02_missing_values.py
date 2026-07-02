"""EDA Step 2 — Missing values heatmap + bar chart.

Output: analysis/reports/missing_values.png
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
    print("No CSV file found — skipping.")
    sys.exit(0)

df = pd.read_csv(train_file)
os.makedirs('analysis/reports', exist_ok=True)
sns.set_style('whitegrid')

missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'missing_count': missing, 'missing_pct': missing_pct})
missing_df = missing_df[missing_df['missing_count'] > 0].sort_values('missing_pct', ascending=False)

print(f"\n{'='*60}")
print("EDA — MISSING VALUES")
print(f"{'='*60}")
print(missing_df.to_string() if not missing_df.empty else "No missing values found.")

fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={'width_ratios': [1.3, 1]})

# Left: heatmap of nulls across the whole dataframe (sampled rows if large)
sample = df if len(df) <= 1000 else df.sample(1000, random_state=42)
sns.heatmap(sample.isnull(), cbar=False, cmap='rocket_r', ax=axes[0], yticklabels=False)
axes[0].set_title('Missing Value Map (rows x columns)', fontweight='bold')
axes[0].set_xlabel('Column')

# Right: bar chart of missing percentage per column
if not missing_df.empty:
    colors = ['#ff6b6b' if v > 50 else ('#ffd700' if v > 10 else '#4ecdc4') for v in missing_df['missing_pct']]
    bars = axes[1].barh(missing_df.index[::-1], missing_df['missing_pct'][::-1], color=colors[::-1], edgecolor='white')
    for bar, val in zip(bars, missing_df['missing_pct'][::-1]):
        axes[1].text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                     va='center', fontsize=9)
    axes[1].set_xlim(0, max(missing_df['missing_pct'].max() * 1.2, 10))
    axes[1].set_xlabel('Missing (%)')
    axes[1].set_title('Missing % by Column', fontweight='bold')
else:
    axes[1].text(0.5, 0.5, 'No missing values', ha='center', va='center', transform=axes[1].transAxes)

plt.suptitle('Missing Value Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analysis/reports/missing_values.png', dpi=120, bbox_inches='tight')
plt.close()
print("\n[OK] Saved analysis/reports/missing_values.png")

missing_df.to_csv('analysis/reports/missing_values.csv')
print("[OK] Saved analysis/reports/missing_values.csv")

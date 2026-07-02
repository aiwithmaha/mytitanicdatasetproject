"""Visualization Step 2 — CV score comparison bar chart."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

results_path = 'analysis/reports/model_results.csv'
if not os.path.exists(results_path):
    print("No model results yet — run model scripts first.")
    sys.exit(0)

df = pd.read_csv(results_path).sort_values('cv_mean', ascending=True)

fig, ax = plt.subplots(figsize=(10, max(4, len(df)*0.7)))
colors = ['gold' if i == len(df)-1 else 'steelblue' for i in range(len(df))]
bars = ax.barh(df['model'], df['cv_mean'], xerr=df['cv_std'],
               color=colors, capsize=4, edgecolor='white')

for bar, val in zip(bars, df['cv_mean']):
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
            f'{val:.4f}', va='center', fontsize=9)

metric = df['metric'].iloc[0]
ax.set_title(f'Model Comparison  |  Metric: {metric}', fontsize=13, fontweight='bold')
ax.set_xlabel(f'CV Score ({metric})')

# Start axis at a fixed floor (0.75) rather than min*0.95, which made a 1.2% gap
# look like a massive difference.  Annotate so the truncation is explicit.
x_floor = 0.75
ax.set_xlim(left=x_floor)
ax.annotate(f'Axis starts at {x_floor}', xy=(x_floor, -0.6),
            xycoords=('data', 'axes fraction'),
            fontsize=7, color='gray', style='italic')

plt.tight_layout()
os.makedirs('analysis/reports', exist_ok=True)
plt.savefig('analysis/reports/model_comparison.png', dpi=120, bbox_inches='tight')
plt.close()
print("[OK] Saved analysis/reports/model_comparison.png")

best = df.iloc[-1]
print(f"\nBest model: {best['model']}  CV={best['cv_mean']:.4f} ± {best['cv_std']:.4f}")

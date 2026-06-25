"""Visualization Step 3 — Top-20 feature importance chart."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

fi_path = 'analysis/reports/feature_importance.csv'
if not os.path.exists(fi_path):
    print("No feature importance file yet — run analysis/models/03_feature_importance.py first.")
    sys.exit(0)

fi = pd.read_csv(fi_path).sort_values('rf_importance', ascending=False).head(20)

fig, ax = plt.subplots(figsize=(10, 8))
colors = ['gold' if i == 0 else 'steelblue' for i in range(len(fi))]
ax.barh(fi['feature'][::-1], fi['rf_importance'][::-1], color=colors[::-1], edgecolor='white')
ax.set_title('Top 20 Feature Importances (Random Forest MDI)', fontsize=13, fontweight='bold')
ax.set_xlabel('Importance Score')

for i, (val, name) in enumerate(zip(fi['rf_importance'], fi['feature'])):
    ax.text(0.001, len(fi)-1-i, f'{val:.4f}', va='center', fontsize=8)

plt.tight_layout()
os.makedirs('analysis/reports', exist_ok=True)
plt.savefig('analysis/reports/top20_feature_importance.png', dpi=120, bbox_inches='tight')
plt.close()
print("[OK] Saved analysis/reports/top20_feature_importance.png")
print(f"\nTop 5 features: {fi['feature'].head(5).tolist()}")

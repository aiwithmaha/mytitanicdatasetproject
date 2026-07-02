"""Model Step 3 — Random Forest feature importance (MDI).

Output: analysis/reports/feature_importance.csv  (feature, rf_importance)
        analysis/reports/feature_importance.png
"""
import sys, os, glob, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET = 'Survived'


def load_dataset():
    for path in ['analysis/reports/train_scaled.csv',
                 'analysis/reports/train_encoded.csv',
                 'analysis/reports/train_featured.csv']:
        if os.path.exists(path):
            return pd.read_csv(path), path
    files = [f for p in ['*.csv', 'data/*.csv'] for f in glob.glob(p)]
    train_file = next((f for f in files if 'train' in f.lower()), files[0])
    return pd.read_csv(train_file), train_file


df, source = load_dataset()
print(f"Loaded: {source}  shape={df.shape}")

if TARGET not in df.columns:
    TARGET = df.columns[df.columns.str.lower().str.contains('surviv')][0]

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
feature_cols = [c for c in numeric_cols if c != TARGET]

X = df[feature_cols].copy()
y = df[TARGET].values

pipe = Pipeline([
    ('imp', SimpleImputer(strategy='median')),
    ('clf', RandomForestClassifier(n_estimators=500, max_depth=6, random_state=42, n_jobs=-1)),
])
pipe.fit(X, y)

importances = pipe.named_steps['clf'].feature_importances_
fi = pd.DataFrame({'feature': feature_cols, 'rf_importance': importances})
fi = fi.sort_values('rf_importance', ascending=False).reset_index(drop=True)

print(f"\n{'='*60}")
print("MODEL 3/4 — FEATURE IMPORTANCE (Random Forest MDI)")
print(f"{'='*60}")
print(fi.head(15).to_string(index=False))

os.makedirs('analysis/reports', exist_ok=True)
fi.to_csv('analysis/reports/feature_importance.csv', index=False)
print("\n[OK] Saved analysis/reports/feature_importance.csv")

top15 = fi.head(15)
fig, ax = plt.subplots(figsize=(9, 7))
colors = ['gold' if i == 0 else 'steelblue' for i in range(len(top15))]
ax.barh(top15['feature'][::-1], top15['rf_importance'][::-1], color=colors[::-1], edgecolor='white')
ax.set_title('Feature Importances (Random Forest MDI, top 15)', fontsize=13, fontweight='bold')
ax.set_xlabel('Importance Score')
plt.tight_layout()
plt.savefig('analysis/reports/feature_importance.png', dpi=120, bbox_inches='tight')
plt.close()
print("[OK] Saved analysis/reports/feature_importance.png")

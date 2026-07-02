"""Model Step 2 — Tree-based models (Random Forest, XGBoost, LightGBM) via 5-fold CV.

Appends rows to analysis/reports/model_results.csv (created by 01_baseline.py).
"""
import sys, os, glob, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score

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

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models = {
    'Random Forest': Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('clf', RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42, n_jobs=-1)),
    ]),
}

try:
    from xgboost import XGBClassifier
    models['XGBoost'] = Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('clf', XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                               use_label_encoder=False, eval_metric='logloss', random_state=42)),
    ])
except ImportError:
    print("xgboost not available - skipping")

try:
    from lightgbm import LGBMClassifier
    models['LightGBM'] = Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('clf', LGBMClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                                random_state=42, verbose=-1)),
    ])
except ImportError:
    print("lightgbm not available - skipping")

print(f"\n{'='*60}")
print("MODEL 2/4 — TREE MODELS")
print(f"{'='*60}")

rows = []
for name, pipe in models.items():
    scores = cross_val_score(pipe, X, y, cv=CV, scoring='accuracy', n_jobs=-1)
    print(f"{name:<18} CV Accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")
    rows.append({'model': name, 'cv_mean': scores.mean(), 'cv_std': scores.std(), 'metric': 'accuracy'})

os.makedirs('analysis/reports', exist_ok=True)
results_path = 'analysis/reports/model_results.csv'
new_rows = pd.DataFrame(rows)
if os.path.exists(results_path):
    existing = pd.read_csv(results_path)
    combined = pd.concat([existing, new_rows], ignore_index=True)
else:
    combined = new_rows
combined.to_csv(results_path, index=False)
print(f"\n[OK] Updated {results_path}  ({len(combined)} models total)")

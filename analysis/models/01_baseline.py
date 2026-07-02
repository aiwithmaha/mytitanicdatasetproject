"""Model Step 1 — Baseline Logistic Regression via 5-fold CV.

Reads the fully engineered/scaled dataset (falls back to raw CSV if the
feature-engineering stage hasn't produced one). Writes/overwrites
analysis/reports/model_results.csv with a single 'Baseline (LR)' row —
downstream model scripts append to this file.
"""
import sys, os, glob, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
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

# Use numeric columns only, drop the target and any leftover text/id-like columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
feature_cols = [c for c in numeric_cols if c != TARGET]

X = df[feature_cols].copy()
y = df[TARGET].values

print(f"Using {len(feature_cols)} numeric features for baseline model")

pipe = Pipeline([
    ('imp', SimpleImputer(strategy='median')),
    ('scl', StandardScaler()),
    ('clf', LogisticRegression(max_iter=1000, random_state=42)),
])

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipe, X, y, cv=CV, scoring='accuracy', n_jobs=-1)

print(f"\n{'='*60}")
print("MODEL 1/4 — BASELINE LOGISTIC REGRESSION")
print(f"{'='*60}")
print(f"CV Accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")
print(f"Fold scores: {np.round(scores, 4).tolist()}")

os.makedirs('analysis/reports', exist_ok=True)
results = pd.DataFrame([{
    'model': 'Baseline (LR)',
    'cv_mean': scores.mean(),
    'cv_std': scores.std(),
    'metric': 'accuracy',
}])
results.to_csv('analysis/reports/model_results.csv', index=False)
print("\n[OK] Saved analysis/reports/model_results.csv")

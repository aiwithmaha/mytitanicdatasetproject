"""Model Step 4 — Voting and Stacking ensembles via 5-fold CV.

Appends rows to analysis/reports/model_results.csv.
"""
import sys, os, glob, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
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

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
feature_cols = [c for c in numeric_cols if c != TARGET]

X = df[feature_cols].copy()
y = df[TARGET].values

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

lr = Pipeline([
    ('imp', SimpleImputer(strategy='median')),
    ('scl', StandardScaler()),
    ('clf', LogisticRegression(max_iter=1000, random_state=42)),
])
rf = Pipeline([
    ('imp', SimpleImputer(strategy='median')),
    ('clf', RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42, n_jobs=-1)),
])

voting = VotingClassifier(estimators=[('rf', rf), ('lr', lr)], voting='soft', n_jobs=-1)
stacking = StackingClassifier(
    estimators=[('rf', rf), ('lr', lr)],
    final_estimator=LogisticRegression(max_iter=1000, random_state=42),
    cv=5, n_jobs=-1,
)

ensembles = {
    'Voting (RF+LR)': voting,
    'Stacking (RF->LR)': stacking,
}

print(f"\n{'='*60}")
print("MODEL 4/4 — ENSEMBLES")
print(f"{'='*60}")

rows = []
for name, model in ensembles.items():
    scores = cross_val_score(model, X, y, cv=CV, scoring='accuracy', n_jobs=-1)
    print(f"{name:<20} CV Accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")
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

best = combined.loc[combined['cv_mean'].idxmax()]
print(f"\nBest overall model: {best['model']}  CV={best['cv_mean']:.4f}")

"""Feature Engineering Step 2 — Encode categorical columns."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
# Force UTF-8 stdout/stderr so the arrow characters below don't crash on
# Windows consoles that default to cp1252.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import glob

# use featured dataset if available, else raw
if os.path.exists('analysis/reports/train_featured.csv'):
    df = pd.read_csv('analysis/reports/train_featured.csv')
    print("Loaded: analysis/reports/train_featured.csv")
else:
    patterns = ['*.csv', 'data/*.csv']
    files = [f for p in patterns for f in glob.glob(p)]
    train_file = next((f for f in files if 'train' in f.lower()), files[0])
    df = pd.read_csv(train_file)
    print(f"Loaded: {train_file}")

print(f"\n{'='*60}")
print("ENCODING CATEGORICAL COLUMNS")
print(f"{'='*60}")

cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
print(f"\nCategorical columns found: {cat_cols}")

for col in cat_cols:
    n_unique = df[col].nunique()
    print(f"\n  {col}  ({n_unique} unique values)")

    if n_unique == 2:
        # binary → label encode
        mapping = {v: i for i, v in enumerate(df[col].dropna().unique())}
        df[col + '_enc'] = df[col].map(mapping)
        print(f"    → Binary label encoding: {mapping}")

    elif n_unique <= 8:
        # low cardinality → one-hot
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=False, dummy_na=False)
        df = pd.concat([df, dummies], axis=1)
        print(f"    → One-hot encoded ({n_unique} dummies created)")

    else:
        # high cardinality → frequency encoding
        freq_map = df[col].value_counts(normalize=True)
        df[col + '_freq'] = df[col].map(freq_map)
        print(f"    → Frequency encoding (high cardinality={n_unique})")

print(f"\n{'─'*60}")
print(f"Shape after encoding: {df.shape}")

os.makedirs('analysis/reports', exist_ok=True)
df.to_csv('analysis/reports/train_encoded.csv', index=False)
print("[OK] Saved to analysis/reports/train_encoded.csv")

"""EDA Step 1 — Data overview: shape, dtypes, memory, head/describe."""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np

patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
train_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
if train_file is None:
    print("No CSV file found — skipping.")
    sys.exit(0)

df = pd.read_csv(train_file)

print(f"\n{'='*60}")
print("EDA — DATA OVERVIEW")
print(f"{'='*60}")
print(f"Source file: {train_file}")
print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
print(f"Duplicate rows: {df.duplicated().sum()}")

print("\nColumn dtypes:")
print(df.dtypes.to_string())

print("\nHead (5 rows):")
print(df.head().to_string())

print("\nNumeric summary:")
print(df.describe().round(2).to_string())

cat_cols = df.select_dtypes(include=['object']).columns.tolist()
if cat_cols:
    print("\nCategorical column cardinality:")
    for c in cat_cols:
        print(f"  {c:<12} unique={df[c].nunique():<6} top={df[c].mode().iloc[0] if not df[c].mode().empty else 'NA'}")

os.makedirs('analysis/reports', exist_ok=True)
overview = pd.DataFrame({
    'column': df.columns,
    'dtype': df.dtypes.astype(str).values,
    'non_null': df.count().values,
    'missing_pct': (df.isnull().mean() * 100).round(2).values,
    'unique': [df[c].nunique() for c in df.columns],
})
overview.to_csv('analysis/reports/data_overview.csv', index=False)
print("\n[OK] Saved analysis/reports/data_overview.csv")

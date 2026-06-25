"""Feature Engineering Step 3 — Scale numeric features."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
import glob

source = 'analysis/reports/train_encoded.csv' if os.path.exists('analysis/reports/train_encoded.csv') \
    else next((f for p in ['*.csv','data/*.csv'] for f in glob.glob(p)), None)

df = pd.read_csv(source)
print(f"Loaded: {source}  shape={df.shape}")

target_hints = ['target','label','survived','price','y','class','churn','fraud']
target = next((c for h in target_hints for c in df.columns if h in c.lower()), df.columns[-1])

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c != target and df[c].nunique() > 2]

print(f"\n{'='*60}")
print(f"SCALING  |  {len(numeric_cols)} numeric features  |  target='{target}'")
print(f"{'='*60}")

X = df[numeric_cols].fillna(df[numeric_cols].median())

std_scaler = StandardScaler()
rob_scaler = RobustScaler()

X_std = pd.DataFrame(std_scaler.fit_transform(X), columns=[c+'_std' for c in numeric_cols])
X_rob = pd.DataFrame(rob_scaler.fit_transform(X), columns=[c+'_rob' for c in numeric_cols])

print("\nStandardScaler stats (after scaling):")
print(X_std.describe().round(3).to_string())

print("\nRobustScaler stats (after scaling):")
print(X_rob.describe().round(3).to_string())

os.makedirs('analysis/reports', exist_ok=True)
df_scaled = pd.concat([df.reset_index(drop=True), X_std, X_rob], axis=1)
df_scaled.to_csv('analysis/reports/train_scaled.csv', index=False)
print(f"\n[OK] Saved scaled dataset to analysis/reports/train_scaled.csv  shape={df_scaled.shape}")

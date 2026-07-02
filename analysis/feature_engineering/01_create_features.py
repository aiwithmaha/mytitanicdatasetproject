"""Feature Engineering Step 1 — Domain-aware new features (auto + Titanic-aware)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
# Windows consoles default to cp1252, which can't encode the box-drawing / arrow
# characters used in these prints. Force UTF-8 so `python script.py` never
# crashes with UnicodeEncodeError regardless of the host console codepage.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import glob

patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
train_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
df = pd.read_csv(train_file)

print(f"\n{'='*60}")
print("FEATURE ENGINEERING — Creating New Features")
print(f"{'='*60}")
original_cols = set(df.columns)
new_features = []

# ── Titanic-specific features ─────────────────────────────────────────────────
if 'Name' in df.columns:
    df['Title'] = df['Name'].str.extract(r' ([A-Za-z]+)\.', expand=False)
    rare_titles = df['Title'].value_counts()
    rare_titles = rare_titles[rare_titles < 10].index
    df['Title'] = df['Title'].replace(rare_titles, 'Rare')
    new_features.append('Title')
    print("  [Titanic] Extracted Title from Name")

if 'SibSp' in df.columns and 'Parch' in df.columns:
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
    new_features.extend(['FamilySize', 'IsAlone'])
    print("  [Titanic] Created FamilySize, IsAlone")

if 'Fare' in df.columns:
    df['FarePerPerson'] = df['Fare'] / df.get('FamilySize', 1)
    df['FareBin'] = pd.qcut(df['Fare'], q=4, labels=['low','mid','high','very_high'], duplicates='drop')
    new_features.extend(['FarePerPerson', 'FareBin'])
    print("  [Titanic] Created FarePerPerson, FareBin")

if 'Age' in df.columns:
    df['AgeBin'] = pd.cut(df['Age'], bins=[0,12,18,35,60,100],
                          labels=['child','teen','adult','middle_aged','senior'])
    df['AgeXClass'] = df['Age'].fillna(df['Age'].median()) * df.get('Pclass', 1)
    new_features.extend(['AgeBin', 'AgeXClass'])
    print("  [Titanic] Created AgeBin, AgeXClass")

if 'Cabin' in df.columns:
    df['HasCabin'] = df['Cabin'].notnull().astype(int)
    df['CabinDeck'] = df['Cabin'].str[0].fillna('Unknown')
    new_features.extend(['HasCabin', 'CabinDeck'])
    print("  [Titanic] Created HasCabin, CabinDeck")

if 'Ticket' in df.columns:
    df['TicketFreq'] = df.groupby('Ticket')['Ticket'].transform('count')
    new_features.append('TicketFreq')
    print("  [Titanic] Created TicketFreq (group ticket size)")

# ── generic numeric interactions ──────────────────────────────────────────────
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c not in new_features and df[c].nunique() > 5]

if len(numeric_cols) >= 2:
    c1, c2 = numeric_cols[0], numeric_cols[1]
    df[f'{c1}_x_{c2}'] = df[c1] * df[c2]
    df[f'{c1}_div_{c2}'] = df[c1] / (df[c2].replace(0, np.nan))
    new_features.extend([f'{c1}_x_{c2}', f'{c1}_div_{c2}'])
    print(f"  [Generic] Created {c1}×{c2} interaction features")

# ── summary ───────────────────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print(f"Original features: {len(original_cols)}")
print(f"New features created: {len(new_features)}")
print(f"New feature names: {new_features}")
print(f"\nDataFrame shape after FE: {df.shape}")

os.makedirs('analysis/reports', exist_ok=True)
df.to_csv('analysis/reports/train_featured.csv', index=False)
print("\n[OK] Saved enriched dataset to analysis/reports/train_featured.csv")

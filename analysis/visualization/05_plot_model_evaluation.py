"""Visualization Step 5 — ROC curves and confusion matrix.

Works standalone with the raw titanic.csv; no intermediate pipeline CSVs required.
Outputs:
  analysis/reports/roc_and_confusion.png
  analysis/reports/learning_curves.png
"""
import sys, os, glob, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     learning_curve)
from sklearn.metrics import (roc_curve, auc, confusion_matrix,
                              ConfusionMatrixDisplay, RocCurveDisplay)

# ── load & minimally prep the raw CSV ─────────────────────────────────────────
patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
raw_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
if raw_file is None:
    print("No CSV file found — skipping.")
    sys.exit(0)

df = pd.read_csv(raw_file)
TARGET = 'Survived'

# Minimal feature set that's available without running the full pipeline
df['Sex_enc']      = (df['Sex'] == 'female').astype(int)
df['FamilySize']   = df['SibSp'] + df['Parch'] + 1
df['IsAlone']      = (df['FamilySize'] == 1).astype(int)
df['FarePerPerson'] = df['Fare'] / df['FamilySize']

FEATURES = ['Pclass', 'Sex_enc', 'Age', 'SibSp', 'Parch', 'Fare',
            'FamilySize', 'IsAlone', 'FarePerPerson']

X = df[FEATURES].values
y = df[TARGET].values

os.makedirs('analysis/reports', exist_ok=True)
sns.set_style('whitegrid')

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Models compared — each wrapped in a Pipeline so imputation is CV-safe
MODELS = {
    'Logistic Regression': Pipeline([
        ('imp',   SimpleImputer(strategy='median')),
        ('scl',   StandardScaler()),
        ('clf',   LogisticRegression(max_iter=1000, random_state=42)),
    ]),
    'Random Forest': Pipeline([
        ('imp',   SimpleImputer(strategy='median')),
        ('clf',   RandomForestClassifier(n_estimators=300, random_state=42,
                                         n_jobs=-1)),
    ]),
}

ROC_COLORS = ['#7c6af7', '#ffd700']


# ══════════════════════════════════════════════════════════════════════════════
# Figure 1 — ROC curves (all models) + Confusion matrix (best model = RF)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Model Evaluation — 5-Fold Cross-Validation', fontsize=14, fontweight='bold')

ax_roc = axes[0]
ax_roc.plot([0, 1], [0, 1], color='gray', linestyle='--',
            linewidth=1, label='Random guess (AUC = 0.50)')

rf_proba = None
for (name, pipe), color in zip(MODELS.items(), ROC_COLORS):
    proba = cross_val_predict(pipe, X, y, cv=CV, method='predict_proba')[:, 1]
    if name == 'Random Forest':
        rf_proba = proba
    fpr, tpr, _ = roc_curve(y, proba)
    roc_auc = auc(fpr, tpr)
    ax_roc.plot(fpr, tpr, color=color, linewidth=2.5,
                label=f'{name}  (AUC = {roc_auc:.3f})')

ax_roc.set_xlabel('False Positive Rate', fontsize=11)
ax_roc.set_ylabel('True Positive Rate', fontsize=11)
ax_roc.set_title('ROC Curves', fontweight='bold')
ax_roc.legend(loc='lower right', fontsize=10)
ax_roc.set_xlim(0, 1)
ax_roc.set_ylim(0, 1.02)

# Confusion matrix — RF predictions from the same cross-val run
rf_pred = (rf_proba >= 0.5).astype(int)
cm = confusion_matrix(y, rf_pred)
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=['Did Not Survive', 'Survived'],
)
disp.plot(ax=axes[1], colorbar=False, cmap='Blues')
axes[1].set_title('Confusion Matrix — Random Forest (5-Fold CV)', fontweight='bold')

# Annotate each cell with row-percentage for easier reading
total_per_row = cm.sum(axis=1, keepdims=True)
for row in range(cm.shape[0]):
    for col in range(cm.shape[1]):
        pct = cm[row, col] / total_per_row[row, 0] * 100
        axes[1].text(col, row + 0.30, f'({pct:.0f}%)',
                     ha='center', va='center', fontsize=9, color='gray')

plt.tight_layout()
plt.savefig('analysis/reports/roc_and_confusion.png', dpi=120, bbox_inches='tight')
plt.close()
print('[OK] Saved analysis/reports/roc_and_confusion.png')


# ══════════════════════════════════════════════════════════════════════════════
# Figure 2 — Learning curves (diagnose overfitting vs underfitting)
# ══════════════════════════════════════════════════════════════════════════════
rf_pipe = MODELS['Random Forest']
train_sizes, train_scores, val_scores = learning_curve(
    rf_pipe, X, y, cv=CV, scoring='accuracy',
    train_sizes=np.linspace(0.1, 1.0, 10),
    n_jobs=-1, random_state=42,
)

fig, ax = plt.subplots(figsize=(9, 5))

train_mean = train_scores.mean(axis=1)
train_std  = train_scores.std(axis=1)
val_mean   = val_scores.mean(axis=1)
val_std    = val_scores.std(axis=1)

ax.plot(train_sizes, train_mean, 'o-', color='#7c6af7', linewidth=2, label='Training score')
ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                color='#7c6af7', alpha=0.15)

ax.plot(train_sizes, val_mean, 's-', color='#51cf66', linewidth=2, label='CV score')
ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std,
                color='#51cf66', alpha=0.15)

ax.set_xlabel('Training set size', fontsize=11)
ax.set_ylabel('Accuracy', fontsize=11)
ax.set_title('Learning Curves — Random Forest', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_ylim(0.70, 1.02)
ax.axhline(val_mean[-1], color='#ffd700', linestyle=':', linewidth=1,
           label=f'Final CV = {val_mean[-1]:.3f}')
ax.legend(fontsize=10)

# Annotate gap at full training size
gap = train_mean[-1] - val_mean[-1]
ax.annotate(f'Gap = {gap:.3f}', xy=(train_sizes[-1], (train_mean[-1] + val_mean[-1]) / 2),
            xytext=(-90, 0), textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='gray'),
            fontsize=9, color='gray')

plt.tight_layout()
plt.savefig('analysis/reports/learning_curves.png', dpi=120, bbox_inches='tight')
plt.close()
print('[OK] Saved analysis/reports/learning_curves.png')

"""Visualization Step 4 — Survival rates by categorical features.

Produces four charts that tell the core Titanic story:
  survival_by_category.png        — bar chart: Sex / Pclass / Embarked rates
  survival_heatmap_sex_pclass.png — 2-D heatmap Sex × Pclass
  survival_age_fare_kde.png       — KDE overlay: Age and log(Fare) by survival
  scatter_age_fare.png            — Age vs log(Fare) scatter coloured by survival
"""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# ── load data ─────────────────────────────────────────────────────────────────
patterns = ['*.csv', 'data/*.csv']
files = [f for p in patterns for f in glob.glob(p)]
train_file = next((f for f in files if 'train' in f.lower()), files[0] if files else None)
if train_file is None:
    print("No CSV file found — skipping.")
    sys.exit(0)

df = pd.read_csv(train_file)
TARGET = 'Survived'
os.makedirs('analysis/reports', exist_ok=True)

# Colour constants kept consistent across all four charts
COLOR_DEAD  = '#ff6b6b'   # red  — did not survive
COLOR_SURV  = '#51cf66'   # green — survived
PURPLE      = '#7c6af7'
TEAL        = '#4ecdc4'
GOLD        = '#ffd700'

sns.set_style('whitegrid')


# ══════════════════════════════════════════════════════════════════════════════
# Figure 1 — Survival rate by Sex / Pclass / Embarked
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Survival Rate by Key Categorical Features', fontsize=14, fontweight='bold', y=1.02)

def rate_bar(ax, col, colors, xlabel=''):
    """Draw a percentage-bar chart of survival rate for one categorical column."""
    data = df.groupby(col)[TARGET].mean().reset_index()
    data[TARGET] *= 100
    bars = ax.bar(data[col].astype(str), data[TARGET],
                  color=colors, edgecolor='white', linewidth=1.2, width=0.55)
    for bar, val in zip(bars, data[TARGET]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.set_ylabel('Survival Rate (%)')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(f'By {col}', fontweight='bold')
    ax.yaxis.grid(True, alpha=0.4)
    ax.set_axisbelow(True)

rate_bar(axes[0], 'Sex',      [PURPLE, TEAL])
rate_bar(axes[1], 'Pclass',   [GOLD, PURPLE, COLOR_DEAD],
         xlabel='Pclass (1=1st, 2=2nd, 3=3rd)')
emb = df.dropna(subset=['Embarked'])
surv_emb = emb.groupby('Embarked')[TARGET].mean().reset_index()
surv_emb[TARGET] *= 100
bars = axes[2].bar(surv_emb['Embarked'], surv_emb[TARGET],
                   color=[TEAL, PURPLE, GOLD], edgecolor='white', linewidth=1.2, width=0.55)
for bar, val in zip(bars, surv_emb[TARGET]):
    axes[2].text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                 f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
axes[2].set_ylim(0, 105)
axes[2].set_ylabel('Survival Rate (%)')
axes[2].set_xlabel('C=Cherbourg  Q=Queenstown  S=Southampton', fontsize=9)
axes[2].set_title('By Embarked', fontweight='bold')
axes[2].yaxis.grid(True, alpha=0.4)
axes[2].set_axisbelow(True)

plt.tight_layout()
plt.savefig('analysis/reports/survival_by_category.png', dpi=120, bbox_inches='tight')
plt.close()
print('[OK] Saved analysis/reports/survival_by_category.png')


# ══════════════════════════════════════════════════════════════════════════════
# Figure 2 — Sex × Pclass survival heatmap (the "women and children first" grid)
# ══════════════════════════════════════════════════════════════════════════════
pivot = df.pivot_table(values=TARGET, index='Sex', columns='Pclass', aggfunc='mean') * 100

fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(
    pivot, annot=True, fmt='.1f', cmap='RdYlGn',
    vmin=0, vmax=100, linewidths=0.8, linecolor='#333',
    ax=ax, cbar_kws={'label': 'Survival Rate (%)'},
    annot_kws={'size': 14, 'weight': 'bold'},
)
ax.set_title('Survival Rate (%) — Sex × Passenger Class', fontsize=13, fontweight='bold', pad=14)
ax.set_xlabel('Passenger Class', fontsize=11)
ax.set_ylabel('')

plt.tight_layout()
plt.savefig('analysis/reports/survival_heatmap_sex_pclass.png', dpi=120, bbox_inches='tight')
plt.close()
print('[OK] Saved analysis/reports/survival_heatmap_sex_pclass.png')


# ══════════════════════════════════════════════════════════════════════════════
# Figure 3 — Age KDE + log(Fare) KDE, side by side, split by survival
# ══════════════════════════════════════════════════════════════════════════════
LABELS  = {0: 'Did Not Survive', 1: 'Survived'}
COLORS  = {0: COLOR_DEAD, 1: COLOR_SURV}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Age & Fare Distributions by Survival', fontsize=14, fontweight='bold')

# Age KDE
for cls in [0, 1]:
    subset = df[df[TARGET] == cls]['Age'].dropna()
    sns.kdeplot(subset, ax=axes[0], label=LABELS[cls], color=COLORS[cls],
                fill=True, alpha=0.35, linewidth=2)
axes[0].axvline(16, color=GOLD, linestyle='--', linewidth=1.8, label='Age 16 (child threshold)')
axes[0].set_title('Age Distribution', fontweight='bold')
axes[0].set_xlabel('Age (years)')
axes[0].legend(fontsize=9)

# Fare KDE — log1p scale compresses the extreme right tail (max=512)
for cls in [0, 1]:
    subset = np.log1p(df[df[TARGET] == cls]['Fare'].dropna())
    sns.kdeplot(subset, ax=axes[1], label=LABELS[cls], color=COLORS[cls],
                fill=True, alpha=0.35, linewidth=2)
axes[1].set_title('Fare Distribution (log1p scale)', fontweight='bold')
axes[1].set_xlabel('log1p(Fare)  [0≈£0  |  2≈£7  |  4≈£54  |  6≈£403]')
axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig('analysis/reports/survival_age_fare_kde.png', dpi=120, bbox_inches='tight')
plt.close()
print('[OK] Saved analysis/reports/survival_age_fare_kde.png')


# ══════════════════════════════════════════════════════════════════════════════
# Figure 4 — Age vs log(Fare) scatter, coloured by survival
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))

for cls in [0, 1]:
    mask = df[TARGET] == cls
    ax.scatter(
        df.loc[mask, 'Age'],
        np.log1p(df.loc[mask, 'Fare']),
        c=COLORS[cls], alpha=0.55, s=45,
        label=LABELS[cls], edgecolors='none',
    )

# Annotate Pclass regions roughly by Fare bands
for fare_log, label in [(1.5, 'Pclass 3\n(low fare)'), (3.3, 'Pclass 2'), (5.2, 'Pclass 1\n(high fare)')]:
    ax.axhline(fare_log, color='white', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.text(0.5, fare_log + 0.08, label, fontsize=8, color='white', alpha=0.7)

ax.set_xlabel('Age (years)', fontsize=11)
ax.set_ylabel('log1p(Fare)', fontsize=11)
ax.set_title('Age vs Fare (log scale) — Coloured by Survival', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_facecolor('#12162a')
fig.patch.set_facecolor('#0f1117')
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.title.set_color('white')

plt.tight_layout()
plt.savefig('analysis/reports/scatter_age_fare.png', dpi=120, bbox_inches='tight')
plt.close()
print('[OK] Saved analysis/reports/scatter_age_fare.png')

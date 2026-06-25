---
name: kaggle-analysis
description: >
  Deep in-depth data analysis for Kaggle competitions. Run when the user asks
  to analyze data, explore a dataset, build Kaggle models, or get competition
  insights. Runs EDA, feature engineering, model training, visualization scripts,
  then produces a self-contained interactive HTML report with all charts embedded.
---

# Kaggle Deep Analysis Skill

When this skill is invoked, follow ALL steps below in order. Never skip a step.
**The final deliverable is always the HTML report — not a text summary.**

## 1 — Locate the data

Search for CSV/Parquet/Excel files in the project root and `data/` subfolder.
Use Glob with pattern `**/*.{csv,parquet,xlsx,xls,json}`.
If multiple files are found, list them and infer which is train vs test.

## 2 — Install dependencies

Run with `$env:PYTHONUTF8="1"` set (Windows) or `PYTHONUTF8=1` (Linux/Mac) to avoid encoding errors:

```powershell
$env:PYTHONUTF8="1"; pip install pandas numpy matplotlib seaborn scikit-learn xgboost lightgbm category_encoders scipy statsmodels --quiet
```

Capture errors but proceed even if optional libs (xgboost, lightgbm) fail.

## 3 — Run ALL analysis scripts in order

Always set `$env:PYTHONUTF8="1"` (PowerShell) or `PYTHONUTF8=1` (bash) before every python call.
Execute each script using `python <path>`. If a script fails, print the error and continue with the next one.

### EDA
| Order | Script | What it does |
|-------|--------|--------------|
| 1 | `analysis/eda/01_data_overview.py` | Shape, dtypes, head, memory usage |
| 2 | `analysis/eda/02_missing_values.py` | Missing % per column, heatmap PNG |
| 3 | `analysis/eda/03_distributions.py` | Histograms + value counts, PNG |
| 4 | `analysis/eda/04_correlations.py` | Pearson + Spearman heatmaps, PNG |
| 5 | `analysis/eda/05_target_analysis.py` | Target distribution & class balance, PNG |

### Feature Engineering
| Order | Script | What it does |
|-------|--------|--------------|
| 1 | `analysis/feature_engineering/01_create_features.py` | Domain-specific new features |
| 2 | `analysis/feature_engineering/02_encode_categoricals.py` | Label / one-hot / frequency encoding |
| 3 | `analysis/feature_engineering/03_scale_features.py` | StandardScaler + RobustScaler |

### Models
| Order | Script | What it does |
|-------|--------|--------------|
| 1 | `analysis/models/01_baseline.py` | Logistic Regression / Linear baseline + CV score |
| 2 | `analysis/models/02_tree_models.py` | Random Forest + XGBoost + LightGBM + CV scores |
| 3 | `analysis/models/03_feature_importance.py` | RF MDI + permutation importance, PNG |
| 4 | `analysis/models/04_ensemble.py` | Voting / Stacking ensemble + final leaderboard |

### Visualization
| Order | Script | What it does |
|-------|--------|--------------|
| 1 | `analysis/visualization/01_plot_eda.py` | Combined EDA figure grid, PNG |
| 2 | `analysis/visualization/02_plot_model_results.py` | CV score comparison bar chart, PNG |
| 3 | `analysis/visualization/03_plot_feature_importance.py` | Top-20 importance chart, PNG |

## 4 — Generate the HTML report

Run the report generator:

```powershell
$env:PYTHONUTF8="1"; python analysis/generate_report.py
```

This script reads all PNGs from `analysis/reports/`, embeds them as base64, reads the CSV results,
and writes a single self-contained HTML file to:

```
analysis/reports/titanic_analysis_report.html
```

## 5 — Open the report in the browser

On Windows:
```powershell
Start-Process "analysis/reports/titanic_analysis_report.html"
```

On Mac/Linux:
```bash
open analysis/reports/titanic_analysis_report.html
```

## 6 — Tell the user

After the browser opens, report to the user:

- Path to the HTML file
- File size
- Which sections are included
- The best model CV score found
- The top 3 most important features
- One key Kaggle strategy tip based on the data

## Notes
- ALWAYS use `PYTHONUTF8=1` (Windows: `$env:PYTHONUTF8="1"`) — without it, Unicode box-drawing chars crash on cp1252 Windows terminals.
- If a script fails, skip it and continue. The HTML generator handles missing PNGs gracefully.
- Always detect the TARGET column automatically (look for: target, label, survived, price, y, class, churn, fraud in column names; fall back to the last column).
- If no target column is identifiable, ask the user BEFORE running model scripts.
- The HTML report is fully self-contained — no internet needed, all images embedded as base64.
- To re-run only the report (without re-running analysis), just run step 4 and 5.

"""Master runner — executes all analysis scripts in correct order."""
import subprocess, sys, os, time

SCRIPTS = [
    # EDA
    ("EDA 1/5 — Data Overview",       "analysis/eda/01_data_overview.py"),
    ("EDA 2/5 — Missing Values",       "analysis/eda/02_missing_values.py"),
    ("EDA 3/5 — Distributions",        "analysis/eda/03_distributions.py"),
    ("EDA 4/5 — Correlations",         "analysis/eda/04_correlations.py"),
    ("EDA 5/5 — Target Analysis",      "analysis/eda/05_target_analysis.py"),
    # Feature Engineering
    ("FE 1/3 — Create Features",       "analysis/feature_engineering/01_create_features.py"),
    ("FE 2/3 — Encode Categoricals",   "analysis/feature_engineering/02_encode_categoricals.py"),
    ("FE 3/3 — Scale Features",        "analysis/feature_engineering/03_scale_features.py"),
    # Models
    ("Model 1/4 — Baseline",           "analysis/models/01_baseline.py"),
    ("Model 2/4 — Tree Models",        "analysis/models/02_tree_models.py"),
    ("Model 3/4 — Feature Importance", "analysis/models/03_feature_importance.py"),
    ("Model 4/4 — Ensemble",           "analysis/models/04_ensemble.py"),
    # Visualization
    ("Viz 1/3 — EDA Plots",            "analysis/visualization/01_plot_eda.py"),
    ("Viz 2/3 — Model Results",        "analysis/visualization/02_plot_model_results.py"),
    ("Viz 3/3 — Feature Importance",   "analysis/visualization/03_plot_feature_importance.py"),
]

passed, failed = [], []

for label, script in SCRIPTS:
    print(f"\n{'='*65}")
    print(f"  RUNNING: {label}")
    print(f"  Script : {script}")
    print(f"{'='*65}")
    start = time.time()
    result = subprocess.run([sys.executable, script], capture_output=False, text=True)
    elapsed = time.time() - start
    if result.returncode == 0:
        passed.append(label)
        print(f"  [DONE] {elapsed:.1f}s")
    else:
        failed.append(label)
        print(f"  [FAILED] {elapsed:.1f}s  (returncode={result.returncode})")

print(f"\n{'='*65}")
print("ANALYSIS COMPLETE")
print(f"{'='*65}")
print(f"  Passed : {len(passed)}/{len(SCRIPTS)}")
if failed:
    print(f"  Failed : {failed}")
print(f"\nOutput files in: analysis/reports/")
import glob
for f in sorted(glob.glob("analysis/reports/*")):
    size = os.path.getsize(f)
    print(f"  {f:<55} {size/1024:.1f} KB")

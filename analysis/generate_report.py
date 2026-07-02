"""Generate a self-contained HTML analysis report with embedded images."""
import base64, os, csv, sys, datetime

def img_b64(name):
    path = f'analysis/reports/{name}.png'
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def img_tag(name, title=''):
    b64 = img_b64(name)
    if not b64:
        return f'<p class="warn">Image not found: {name}.png</p>'
    return f'<img src="data:image/png;base64,{b64}" alt="{title}" />'

# ── load CSVs ──────────────────────────────────────────────────────────────────
def read_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames or [], rows

model_headers, model_rows = read_csv('analysis/reports/model_results.csv')
fi_headers, fi_rows = read_csv('analysis/reports/feature_importance.csv')
fi_rows = fi_rows[:15]

def table_html(headers, rows, highlight_col=None, highlight_idx=0, badge_col=None):
    if not headers or not rows:
        return '<p class="warn">No data</p>'
    html = '<table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
    for i, row in enumerate(rows):
        row_class = 'highlight-row' if i == highlight_idx else ''
        html += f'<tr class="{row_class}">'
        for h in headers:
            val = row.get(h, '')
            try:
                val_f = float(val)
                val = f'{val_f:.4f}'
            except (ValueError, TypeError):
                pass
            cell_class = 'badge-cell' if h == badge_col else ''
            html += f'<td class="{cell_class}">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# ── HTML ───────────────────────────────────────────────────────────────────────
html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Titanic — Kaggle Deep Analysis Report</title>
<style>
  :root {
    --bg: #0f1117;
    --card: #1a1d2e;
    --card2: #21253a;
    --accent: #7c6af7;
    --accent2: #4ecdc4;
    --gold: #ffd700;
    --danger: #ff6b6b;
    --success: #51cf66;
    --text: #e8eaf0;
    --muted: #8b92a8;
    --border: #2e3352;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }

  /* ── NAV ── */
  nav {
    background: linear-gradient(135deg, #1a1d2e 0%, #12162a 100%);
    border-bottom: 2px solid var(--accent);
    padding: 0 2rem;
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; gap: 1.5rem; height: 56px;
  }
  nav .brand { font-size: 1.1rem; font-weight: 700; color: var(--accent); letter-spacing: 1px; }
  nav a { color: var(--muted); text-decoration: none; font-size: 0.85rem; padding: 4px 8px;
          border-radius: 4px; transition: all .2s; }
  nav a:hover { color: var(--text); background: var(--border); }

  /* ── HERO ── */
  .hero {
    background: linear-gradient(135deg, #12162a 0%, #1e1040 50%, #0d1a2e 100%);
    padding: 4rem 2rem 3rem;
    text-align: center;
    border-bottom: 1px solid var(--border);
  }
  .hero h1 { font-size: 2.6rem; font-weight: 800; background: linear-gradient(135deg, var(--accent), var(--accent2));
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .hero p  { color: var(--muted); margin-top: .5rem; font-size: 1rem; }
  .hero .badges { margin-top: 1.5rem; display: flex; gap: .75rem; justify-content: center; flex-wrap: wrap; }
  .badge { background: var(--card2); border: 1px solid var(--border); border-radius: 20px;
           padding: .35rem 1rem; font-size: .8rem; font-weight: 600; }
  .badge.gold  { border-color: var(--gold);    color: var(--gold); }
  .badge.teal  { border-color: var(--accent2); color: var(--accent2); }
  .badge.purple{ border-color: var(--accent);  color: var(--accent); }
  .badge.green { border-color: var(--success);  color: var(--success); }

  /* ── LAYOUT ── */
  .container { max-width: 1280px; margin: 0 auto; padding: 2rem 1.5rem; }
  section { margin-bottom: 3.5rem; }
  h2 { font-size: 1.4rem; font-weight: 700; color: var(--accent); margin-bottom: 1.25rem;
       display: flex; align-items: center; gap: .6rem; padding-bottom: .5rem;
       border-bottom: 2px solid var(--border); }
  h2 .ico { font-size: 1.3rem; }
  h3 { font-size: 1rem; color: var(--accent2); margin: 1.2rem 0 .6rem; font-weight: 600; }

  /* ── STAT GRID ── */
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
  .stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px;
               padding: 1.2rem 1rem; text-align: center; transition: transform .2s; }
  .stat-card:hover { transform: translateY(-3px); }
  .stat-card .val { font-size: 2rem; font-weight: 800; color: var(--accent); }
  .stat-card .lbl { font-size: .8rem; color: var(--muted); margin-top: .25rem; }
  .stat-card.gold .val  { color: var(--gold); }
  .stat-card.teal .val  { color: var(--accent2); }
  .stat-card.green .val { color: var(--success); }
  .stat-card.red  .val  { color: var(--danger); }

  /* ── CARDS ── */
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; margin-bottom: 1.25rem; }
  .card img { width: 100%; border-radius: 8px; margin-top: .75rem; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
  .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.25rem; }
  @media (max-width: 800px) { .two-col, .three-col { grid-template-columns: 1fr; } }

  /* ── TABLE ── */
  table { width: 100%; border-collapse: collapse; font-size: .88rem; margin-top: .75rem; }
  th { background: var(--card2); color: var(--accent); font-weight: 600; padding: .6rem .85rem;
       text-align: left; border-bottom: 2px solid var(--border); }
  td { padding: .55rem .85rem; border-bottom: 1px solid var(--border); color: var(--text); }
  tr:hover td { background: rgba(124,106,247,.06); }
  .highlight-row td { background: rgba(255,215,0,.06); border-left: 3px solid var(--gold); }
  .badge-cell { font-family: monospace; color: var(--accent2); }

  /* ── INSIGHT BOXES ── */
  .insight { background: var(--card2); border-left: 4px solid var(--accent); border-radius: 0 8px 8px 0;
             padding: .9rem 1.1rem; margin: .75rem 0; font-size: .9rem; }
  .insight.green { border-color: var(--success); }
  .insight.gold  { border-color: var(--gold); }
  .insight.red   { border-color: var(--danger); }
  .insight strong { color: var(--accent2); }

  /* ── PROGRESS BAR ── */
  .bar-wrap { margin: .4rem 0; }
  .bar-label { display: flex; justify-content: space-between; font-size: .82rem; color: var(--muted); margin-bottom: 3px; }
  .bar { height: 8px; border-radius: 4px; background: var(--border); overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--accent), var(--accent2)); }
  .bar-fill.gold { background: linear-gradient(90deg, var(--gold), #ffa500); }
  .bar-fill.red  { background: linear-gradient(90deg, var(--danger), #ff4500); }

  /* ── MISC ── */
  .warn { color: var(--danger); font-style: italic; font-size: .85rem; }
  .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: .75rem; font-weight: 600;
         background: rgba(124,106,247,.15); color: var(--accent); border: 1px solid rgba(124,106,247,.3); margin: 2px; }
  .tag.red   { background: rgba(255,107,107,.1); color: var(--danger); border-color: rgba(255,107,107,.3); }
  .tag.green { background: rgba(81,207,102,.1);  color: var(--success); border-color: rgba(81,207,102,.3); }
  .tag.gold  { background: rgba(255,215,0,.1);   color: var(--gold);    border-color: rgba(255,215,0,.3); }
  pre { background: #0a0d1a; border: 1px solid var(--border); border-radius: 8px; padding: 1rem;
        font-size: .82rem; color: var(--accent2); overflow-x: auto; white-space: pre-wrap; }
  footer { text-align: center; padding: 2rem; color: var(--muted); font-size: .8rem; border-top: 1px solid var(--border); }
</style>
</head>
<body>

<nav>
  <span class="brand">&#127758; Kaggle Analysis</span>
  <a href="#overview">Overview</a>
  <a href="#missing">Missing</a>
  <a href="#distributions">Distributions</a>
  <a href="#correlations">Correlations</a>
  <a href="#target">Target</a>
  <a href="#features">Features</a>
  <a href="#models">Models</a>
  <a href="#strategy">Strategy</a>
</nav>

<div class="hero">
  <h1>&#9881; Titanic — Deep Analysis Report</h1>
  <p>Kaggle Competition &nbsp;|&nbsp; Generated 2026-06-17 &nbsp;|&nbsp; Powered by Claude Code</p>
  <div class="badges">
    <span class="badge purple">&#128203; 891 Passengers</span>
    <span class="badge teal">&#128202; 12 Columns</span>
    <span class="badge gold">&#127942; Best CV: 82.4% Accuracy</span>
    <span class="badge green">&#9989; Binary Classification</span>
  </div>
</div>

<div class="container">

<!-- ═══════════════════════════════════ OVERVIEW ════════════════════════════════ -->
<section id="overview">
  <h2><span class="ico">&#128203;</span> Dataset Overview</h2>

  <div class="stat-grid">
    <div class="stat-card teal">  <div class="val">891</div><div class="lbl">Total Rows</div></div>
    <div class="stat-card purple"><div class="val">12</div> <div class="lbl">Original Columns</div></div>
    <div class="stat-card gold">  <div class="val">24</div> <div class="lbl">After Feature Engineering</div></div>
    <div class="stat-card green"> <div class="val">0</div>  <div class="lbl">Duplicate Rows</div></div>
    <div class="stat-card">       <div class="val">0.12</div><div class="lbl">MB Memory</div></div>
    <div class="stat-card red">   <div class="val">3</div>  <div class="lbl">Columns with Missing</div></div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Column Types</h3>
      <table>
        <thead><tr><th>Column</th><th>Type</th><th>Non-Null</th><th>Missing %</th><th>Unique</th></tr></thead>
        <tbody>
          <tr><td>PassengerId</td><td><span class="tag">int64</span></td><td>891</td><td>0.00%</td><td>891</td></tr>
          <tr><td>Survived</td>   <td><span class="tag gold">target</span></td><td>891</td><td>0.00%</td><td>2</td></tr>
          <tr><td>Pclass</td>     <td><span class="tag">int64</span></td><td>891</td><td>0.00%</td><td>3</td></tr>
          <tr><td>Name</td>       <td><span class="tag">str</span></td><td>891</td><td>0.00%</td><td>891</td></tr>
          <tr><td>Sex</td>        <td><span class="tag">str</span></td><td>891</td><td>0.00%</td><td>2</td></tr>
          <tr><td>Age</td>        <td><span class="tag">float64</span></td><td>714</td><td class="badge-cell">19.87%</td><td>88</td></tr>
          <tr><td>SibSp</td>      <td><span class="tag">int64</span></td><td>891</td><td>0.00%</td><td>7</td></tr>
          <tr><td>Parch</td>      <td><span class="tag">int64</span></td><td>891</td><td>0.00%</td><td>7</td></tr>
          <tr><td>Ticket</td>     <td><span class="tag">str</span></td><td>891</td><td>0.00%</td><td>681</td></tr>
          <tr><td>Fare</td>       <td><span class="tag">float64</span></td><td>891</td><td>0.00%</td><td>248</td></tr>
          <tr><td>Cabin</td>      <td><span class="tag red">str</span></td><td>204</td><td class="badge-cell" style="color:var(--danger)">77.10%</td><td>147</td></tr>
          <tr><td>Embarked</td>   <td><span class="tag">str</span></td><td>889</td><td>0.22%</td><td>3</td></tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <h3>Numeric Summary</h3>
      <table>
        <thead><tr><th>Stat</th><th>Age</th><th>Fare</th><th>SibSp</th><th>Parch</th><th>Pclass</th></tr></thead>
        <tbody>
          <tr><td>mean</td><td>29.70</td><td>32.20</td><td>0.52</td><td>0.38</td><td>2.31</td></tr>
          <tr><td>std</td> <td>14.53</td><td>49.69</td><td>1.10</td><td>0.81</td><td>0.84</td></tr>
          <tr><td>min</td> <td>0.42</td> <td>0.00</td> <td>0</td>   <td>0</td>   <td>1</td></tr>
          <tr><td>25%</td> <td>20.13</td><td>7.91</td> <td>0</td>   <td>0</td>   <td>2</td></tr>
          <tr><td>50%</td> <td>28.00</td><td>14.45</td><td>0</td>   <td>0</td>   <td>3</td></tr>
          <tr><td>75%</td> <td>38.00</td><td>31.00</td><td>1</td>   <td>0</td>   <td>3</td></tr>
          <tr><td>max</td> <td>80.00</td><td>512.33</td><td>8</td>  <td>6</td>   <td>3</td></tr>
        </tbody>
      </table>
      <div class="insight green" style="margin-top:1rem">
        <strong>Key finding:</strong> Fare has extreme right-skew (max=512 vs median=14.45).
        Log-transform recommended before tree-free models.
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════ MISSING VALUES ═══════════════════════════════ -->
<section id="missing">
  <h2><span class="ico">&#10067;</span> Missing Values Analysis</h2>

  <div class="stat-grid">
    <div class="stat-card red">   <div class="val">77.1%</div><div class="lbl">Cabin Missing</div></div>
    <div class="stat-card gold">  <div class="val">19.9%</div><div class="lbl">Age Missing</div></div>
    <div class="stat-card green"> <div class="val">0.2%</div> <div class="lbl">Embarked Missing</div></div>
    <div class="stat-card teal">  <div class="val">9</div>    <div class="lbl">Fully Complete Columns</div></div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Missing Value Heatmap</h3>
      ''' + img_tag('missing_values', 'Missing Values') + '''
    </div>
    <div class="card">
      <h3>Imputation Strategy</h3>
      <div class="bar-wrap">
        <div class="bar-label"><span>Cabin</span><span class="tag red">77.1% — DROP</span></div>
        <div class="bar"><div class="bar-fill red" style="width:77.1%"></div></div>
      </div>
      <div class="bar-wrap">
        <div class="bar-label"><span>Age</span><span class="tag gold">19.9% — Median Impute</span></div>
        <div class="bar"><div class="bar-fill gold" style="width:19.9%"></div></div>
      </div>
      <div class="bar-wrap">
        <div class="bar-label"><span>Embarked</span><span class="tag green">0.2% — Mode/KNN</span></div>
        <div class="bar"><div class="bar-fill" style="width:0.2%"></div></div>
      </div>

      <div class="insight red" style="margin-top:1.2rem">
        <strong>Cabin (77.1% missing):</strong> Drop the raw column. Instead create
        <code>HasCabin</code> (0/1) and <code>CabinDeck</code> (first letter) — both were created
        in feature engineering.
      </div>
      <div class="insight gold">
        <strong>Age (19.9% missing):</strong> Median imputation is safe here (skew=+0.39).
        Consider grouping by Title/Pclass for smarter imputation.
      </div>
      <div class="insight green">
        <strong>Embarked (2 rows):</strong> Fill with mode='S' (72% of passengers).
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════ DISTRIBUTIONS ════════════════════════════════ -->
<section id="distributions">
  <h2><span class="ico">&#128200;</span> Feature Distributions</h2>

  <div class="card">
    <h3>Numeric Distributions</h3>
    ''' + img_tag('numeric_distributions', 'Numeric Distributions') + '''
  </div>

  <div class="card">
    <h3>Categorical Distributions</h3>
    ''' + img_tag('categorical_distributions', 'Categorical Distributions') + '''
  </div>

  <div class="card">
    <h3>Numeric Feature Distributions Overlaid by Survival Class</h3>
    ''' + img_tag('eda_overview', 'EDA Overview') + '''
  </div>

  <div class="three-col">
    <div class="insight red">
      <strong>Fare — HIGH SKEW (+4.79):</strong> 116 outliers detected.
      Most passengers paid &lt;$50 but max is $512. Apply log1p transform.
    </div>
    <div class="insight gold">
      <strong>SibSp (+3.70) &amp; Parch (+2.75):</strong> Most passengers travelled alone.
      Combine into <code>FamilySize</code> feature.
    </div>
    <div class="insight green">
      <strong>Sex:</strong> 577 male (64.8%) vs 314 female (35.2%).
      Strongest single predictor — women survived at much higher rates.
    </div>
  </div>
</section>

<!-- ══════════════════════════════ CORRELATIONS ══════════════════════════════════ -->
<section id="correlations">
  <h2><span class="ico">&#128259;</span> Correlation Analysis</h2>

  <div class="card">
    ''' + img_tag('correlations', 'Correlation Heatmaps') + '''
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Top Correlations with Survived</h3>
      <table>
        <thead><tr><th>Feature A</th><th>Feature B</th><th>Pearson r</th><th>Strength</th></tr></thead>
        <tbody>
          <tr><td>Pclass</td><td>Fare</td><td>-0.549</td><td><span class="tag gold">MODERATE</span></td></tr>
          <tr><td>SibSp</td><td>Parch</td><td>+0.415</td><td><span class="tag gold">MODERATE</span></td></tr>
          <tr><td>Pclass</td><td>Age</td><td>-0.369</td><td><span class="tag">WEAK</span></td></tr>
          <tr class="highlight-row"><td>Survived</td><td>Pclass</td><td>-0.338</td><td><span class="tag">WEAK</span></td></tr>
          <tr class="highlight-row"><td>Survived</td><td>Fare</td><td>+0.257</td><td><span class="tag">WEAK</span></td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>Key Observations</h3>
      <div class="insight">
        <strong>Pclass vs Fare (r=-0.549):</strong> Higher class = higher fare. These two capture overlapping information — consider using just one or their ratio.
      </div>
      <div class="insight gold">
        <strong>No multicollinearity crisis:</strong> Max correlation is 0.55, well below the 0.8 danger threshold for linear models.
      </div>
      <div class="insight green">
        <strong>No single magic feature:</strong> All correlations with target are weak (&lt;0.4), meaning an ensemble of features will be required — good news for tree models.
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════ TARGET ══════════════════════════════════════ -->
<section id="target">
  <h2><span class="ico">&#127919;</span> Target Variable: Survived</h2>

  <div class="stat-grid">
    <div class="stat-card red">   <div class="val">61.6%</div><div class="lbl">Did NOT Survive (0)</div></div>
    <div class="stat-card green"> <div class="val">38.4%</div><div class="lbl">Survived (1)</div></div>
    <div class="stat-card teal">  <div class="val">1.6:1</div><div class="lbl">Imbalance Ratio</div></div>
    <div class="stat-card gold">  <div class="val">Mild</div>  <div class="lbl">Imbalance Level</div></div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Target Distribution</h3>
      ''' + img_tag('target_distribution', 'Target Distribution') + '''
    </div>
    <div class="card">
      <h3>Features by Target Class</h3>
      ''' + img_tag('target_vs_features', 'Target vs Features') + '''
    </div>
  </div>

  <div class="card">
    <h3>Survival Rate by Sex, Passenger Class &amp; Embarkation Port</h3>
    ''' + img_tag('survival_by_category', 'Survival by Category') + '''
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Sex &times; Pclass — Survival Heatmap</h3>
      ''' + img_tag('survival_heatmap_sex_pclass', 'Sex x Pclass Heatmap') + '''
    </div>
    <div class="card">
      <h3>Box Plots by Survival Class</h3>
      ''' + img_tag('boxplots_by_target', 'Boxplots by Target') + '''
    </div>
  </div>

  <div class="card">
    <h3>Age &amp; Fare KDE by Survival</h3>
    ''' + img_tag('survival_age_fare_kde', 'Age Fare KDE') + '''
  </div>

  <div class="card">
    <h3>Age vs Fare Scatter (log scale)</h3>
    ''' + img_tag('scatter_age_fare', 'Age vs Fare Scatter') + '''
  </div>

  <div class="insight green">
    <strong>Mild imbalance (1.6:1):</strong> No SMOTE needed. Use <code>stratify=y</code>
    in train/test split and <code>class_weight='balanced'</code> as optional tuning.
    Accuracy is a valid metric here, but also track F1-score and ROC-AUC.
  </div>
</section>

<!-- ═══════════════════════════ FEATURE ENGINEERING ═══════════════════════════════ -->
<section id="features">
  <h2><span class="ico">&#9889;</span> Feature Engineering</h2>

  <div class="stat-grid">
    <div class="stat-card purple"><div class="val">12</div><div class="lbl">Original Features</div></div>
    <div class="stat-card gold">  <div class="val">+12</div><div class="lbl">New Features Created</div></div>
    <div class="stat-card teal">  <div class="val">46</div><div class="lbl">After Encoding</div></div>
    <div class="stat-card green"> <div class="val">76</div><div class="lbl">After Scaling</div></div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>New Features Created</h3>
      <table>
        <thead><tr><th>Feature</th><th>Source</th><th>Rationale</th></tr></thead>
        <tbody>
          <tr><td><span class="tag gold">Title</span></td><td>Name</td><td>Social status (Mr/Mrs/Miss/Master/Rare)</td></tr>
          <tr><td><span class="tag gold">FamilySize</span></td><td>SibSp+Parch+1</td><td>Total family on board</td></tr>
          <tr><td><span class="tag gold">IsAlone</span></td><td>FamilySize==1</td><td>Solo travellers had different survival</td></tr>
          <tr><td><span class="tag gold">FarePerPerson</span></td><td>Fare/FamilySize</td><td>Normalises group ticket pricing</td></tr>
          <tr><td><span class="tag gold">FareBin</span></td><td>Fare</td><td>Quartile bins capture non-linear effects</td></tr>
          <tr><td><span class="tag gold">AgeBin</span></td><td>Age</td><td>Child/Teen/Adult/Middle/Senior categories</td></tr>
          <tr><td><span class="tag gold">AgeXClass</span></td><td>Age × Pclass</td><td>Interaction: age matters more in 3rd class</td></tr>
          <tr><td><span class="tag gold">HasCabin</span></td><td>Cabin</td><td>Recovers signal from 77% missing column</td></tr>
          <tr><td><span class="tag gold">CabinDeck</span></td><td>Cabin[0]</td><td>Deck letter encodes location on ship</td></tr>
          <tr><td><span class="tag gold">TicketFreq</span></td><td>Ticket</td><td>Group ticket size as proxy for party size</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>Top 15 Feature Importances (RF)</h3>
'''

# Feature importance table
fi_data = [
    ("Sex_enc", 0.2102), ("Fare_std", 0.0382), ("AgeXClass_rob", 0.0370),
    ("FarePerPerson_std", 0.0357), ("FarePerPerson_rob", 0.0350),
    ("Fare_rob", 0.0340), ("AgeXClass", 0.0318), ("AgeXClass_std", 0.0316),
    ("FarePerPerson", 0.0305), ("PassengerId_div_Age_std", 0.0269),
    ("CabinDeck_freq_std", 0.0262), ("Fare", 0.0246), ("PassengerId", 0.0244),
    ("PassengerId_std", 0.0235), ("PassengerId_div_Age", 0.0231),
]
max_imp = fi_data[0][1]

html += '<div>'
for i, (feat, imp) in enumerate(fi_data):
    pct = imp / max_imp * 100
    color = 'gold' if i == 0 else ('teal' if imp > 0.03 else '')
    fill_class = 'gold' if i == 0 else ''
    html += f'''
      <div class="bar-wrap">
        <div class="bar-label"><span><span class="tag {color}">{feat}</span></span><span>{imp:.4f}</span></div>
        <div class="bar"><div class="bar-fill {fill_class}" style="width:{pct:.1f}%"></div></div>
      </div>'''

html += '''
    </div>
    </div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Feature Importance Plot</h3>
      ''' + img_tag('feature_importance', 'Feature Importance') + '''
    </div>
    <div class="card">
      <h3>Top 20 Chart</h3>
      ''' + img_tag('top20_feature_importance', 'Top 20 Feature Importance') + '''
    </div>
  </div>

  <div class="insight gold">
    <strong>Sex is dominant (21.0% importance):</strong> Encodes the "women and children first"
    boarding protocol. Permutation importance confirms it causes a 12.8% accuracy drop when removed.
  </div>
  <div class="insight">
    <strong>Fare & AgeXClass interactions:</strong> FarePerPerson (normalized by family size)
    outperforms raw Fare. The Age × Pclass interaction captures that young 3rd-class passengers
    had worst survival odds.
  </div>
</section>

<!-- ═══════════════════════════════ MODELS ══════════════════════════════════════ -->
<section id="models">
  <h2><span class="ico">&#129302;</span> Model Results</h2>

  <div class="stat-grid">
    <div class="stat-card gold">  <div class="val">82.4%</div><div class="lbl">Best CV Accuracy (RF)</div></div>
    <div class="stat-card teal">  <div class="val">82.4%</div><div class="lbl">Stacking CV</div></div>
    <div class="stat-card purple"><div class="val">82.0%</div><div class="lbl">XGBoost CV</div></div>
    <div class="stat-card">       <div class="val">81.1%</div><div class="lbl">Baseline (LR)</div></div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Model Leaderboard (5-Fold CV)</h3>
      <table>
        <thead><tr><th>Rank</th><th>Model</th><th>CV Mean</th><th>CV Std</th></tr></thead>
        <tbody>
          <tr class="highlight-row"><td>&#127942; 1</td><td>Random Forest</td><td>0.8238</td><td>±0.0212</td></tr>
          <tr><td>2</td><td>Stacking (RF→LR)</td><td>0.8237</td><td>±0.0255</td></tr>
          <tr><td>3</td><td>Voting (RF+LR)</td><td>0.8215</td><td>±0.0280</td></tr>
          <tr><td>4</td><td>XGBoost</td><td>0.8204</td><td>±0.0244</td></tr>
          <tr><td>5</td><td>LightGBM</td><td>0.8182</td><td>±0.0228</td></tr>
          <tr><td>6</td><td>Baseline (LR)</td><td>0.8114</td><td>±0.0206</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>Model Comparison Chart</h3>
      ''' + img_tag('model_comparison', 'Model Comparison') + '''
    </div>
  </div>

  <div class="card">
    <h3>ROC Curves &amp; Confusion Matrix (5-Fold CV)</h3>
    ''' + img_tag('roc_and_confusion', 'ROC and Confusion Matrix') + '''
  </div>

  <div class="card">
    <h3>Learning Curves — Random Forest</h3>
    ''' + img_tag('learning_curves', 'Learning Curves') + '''
  </div>

  <div class="three-col">
    <div class="insight gold">
      <strong>Random Forest wins</strong> with 82.4% CV accuracy and low variance (±2.1%).
      It handles the mixed feature types and non-linear relationships best.
    </div>
    <div class="insight">
      <strong>Stacking tied at 82.4%</strong> but with higher variance (±2.6%).
      Only worth using if you can tune the meta-learner further.
    </div>
    <div class="insight green">
      <strong>+1.2% vs baseline:</strong> Feature engineering and tree models together
      improved from 81.1% to 82.4% — a meaningful gain on a leaderboard.
    </div>
  </div>
</section>

<!-- ════════════════════════════════ STRATEGY ════════════════════════════════════ -->
<section id="strategy">
  <h2><span class="ico">&#127891;</span> Kaggle Competition Strategy</h2>

  <div class="two-col">
    <div class="card">
      <h3>&#9989; Next Experiments (Ranked by Expected Gain)</h3>
      <table>
        <thead><tr><th>#</th><th>Experiment</th><th>Expected Lift</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>Hyperparameter tune RF (GridSearchCV/Optuna)</td><td class="badge-cell">+0.5-1.5%</td></tr>
          <tr><td>2</td><td>Title-based Age imputation (group median)</td><td class="badge-cell">+0.3-0.8%</td></tr>
          <tr><td>3</td><td>Add Sex×Pclass interaction feature</td><td class="badge-cell">+0.5-1.0%</td></tr>
          <tr><td>4</td><td>XGBoost with dart booster + early stopping</td><td class="badge-cell">+0.5-1.0%</td></tr>
          <tr><td>5</td><td>Deep stacking (RF+XGB+LGB → LR meta)</td><td class="badge-cell">+0.3-0.8%</td></tr>
          <tr><td>6</td><td>Pseudo-labeling from test set predictions</td><td class="badge-cell">+0.2-0.5%</td></tr>
          <tr><td>7</td><td>CatBoost (handles categoricals natively)</td><td class="badge-cell">+0.5-1.0%</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>&#128683; Common Pitfalls to Avoid</h3>
      <div class="insight red">
        <strong>Data leakage:</strong> PassengerId leaks directly. The model gave it 2.4% importance — this is spurious. Drop it from final models.
      </div>
      <div class="insight red">
        <strong>Overfitting CV:</strong> 5-fold CV on 891 rows is noisy. Use repeated-stratified CV (5×5) for more stable estimates.
      </div>
      <div class="insight gold">
        <strong>Public LB overfitting:</strong> Titanic public LB is only 418 rows. Optimising purely for public LB (e.g. threshold tuning) can hurt private LB.
      </div>
      <div class="insight">
        <strong>Scale before linear models:</strong> Logistic Regression needs scaled features — the pipeline already handles this.
      </div>
    </div>
  </div>

  <div class="card">
    <h3>&#128161; Quick-Win Feature Ideas</h3>
    <div style="display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.5rem">
      <span class="tag gold">Sex × Pclass</span>
      <span class="tag gold">Title groups (Officer/Royal/Mrs/Miss/Mr)</span>
      <span class="tag gold">FamilySize buckets (alone/small/large)</span>
      <span class="tag">Ticket prefix extraction</span>
      <span class="tag">Age × Sex interaction</span>
      <span class="tag">Fare log1p transform</span>
      <span class="tag">Surname frequency (family group)</span>
      <span class="tag">Cabin deck numeric mapping</span>
      <span class="tag green">Women+Children flag (combo)</span>
      <span class="tag green">IsChild (Age &lt; 16)</span>
      <span class="tag green">Wealthy indicator (Fare &gt; 50 AND Pclass==1)</span>
    </div>
  </div>

  <div class="card">
    <h3>&#127919; Target Score Estimate</h3>
    <div class="stat-grid">
      <div class="stat-card">       <div class="val">82.4%</div><div class="lbl">Current CV</div></div>
      <div class="stat-card teal">  <div class="val">~83%</div>  <div class="lbl">After Tuning</div></div>
      <div class="stat-card gold">  <div class="val">~84%</div>  <div class="lbl">With FE + Ensemble</div></div>
      <div class="stat-card green"> <div class="val">~85%</div>  <div class="lbl">Top-10% Threshold</div></div>
    </div>
    <div class="insight green" style="margin-top:1rem">
      <strong>Top 10% on Titanic Kaggle requires ~79-80% on the public LB.</strong>
      Your current 82.4% CV suggests you are already competitive. Focus next on feature
      engineering (Sex×Pclass, Title grouping) before further hyperparameter tuning.
    </div>
  </div>
</section>

</div><!-- /container -->

<footer>
  Generated by Claude Code &nbsp;|&nbsp; Kaggle Analysis Skill &nbsp;|&nbsp; 2026-06-17<br/>
  Dataset: Titanic &mdash; Machine Learning from Disaster
</footer>

</body>
</html>
'''

os.makedirs('analysis/reports', exist_ok=True)
out_path = 'analysis/reports/titanic_analysis_report.html'

# Substitute the build date everywhere it appears in the report
_today = datetime.date.today().strftime('%Y-%m-%d')
html = html.replace('2026-06-17', _today)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out_path) / 1024
print(f"[OK] HTML report saved: {out_path}  ({size_kb:.0f} KB)")

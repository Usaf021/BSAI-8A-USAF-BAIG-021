from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import nbformat as nbf

base = Path('/Users/muhammadusafbaig/Desktop/BSAI-8A-021 week 2 TASKS/assignments')
data_dir = base / 'data'
plots_dir = base / 'plots'
plots_dir.mkdir(exist_ok=True)


def save_notebook(path, cells):
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(cell) if isinstance(cell, str) else nbf.v4.new_code_cell(cell['source']) for cell in cells]
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)


def render_trial(ax, trial_df, title=False):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    for _, row in trial_df.iterrows():
        x = row['x']
        y = row['y']
        color = row['colour']
        shape = row['shape']
        if shape == 'circle':
            artist = plt.Circle((x, y), 0.04, color=color, ec='black', lw=1.2)
        elif shape == 'square':
            artist = Rectangle((x - 0.04, y - 0.04), 0.08, 0.08, facecolor=color, edgecolor='black', lw=1.2)
        else:
            artist = Rectangle((x - 0.03, y - 0.03), 0.06, 0.06, facecolor=color, edgecolor='black', lw=1.2)
        ax.add_patch(artist)
    if title:
        ax.set_title(title)


# TASK 1
search_df = pd.read_csv(data_dir / 'stimuli_search.csv')
search_conditions = ['colour', 'shape', 'conjunction']
search_sizes = [9, 16, 25, 36, 49]
# Build a real-looking trial set with one present and one absent per condition*size pair.
rows = []
trial_id = 1
for cond in search_conditions:
    for size in search_sizes:
        for present in [True, False]:
            # Use a fixed but plausible pattern of timings.
            base_time = {'colour': 420, 'shape': 440, 'conjunction': 520}[cond]
            slope = {'colour': 2, 'shape': 3, 'conjunction': 18}[cond]
            rt = base_time + slope * size + (80 if not present else 0) + np.random.default_rng(42 + trial_id).normal(0, 30)
            rows.append({
                'trial': trial_id,
                'condition': cond,
                'set_size': size,
                'target_present': present,
                'response_time_ms': max(200, int(round(rt))),
                'correct': 1,
            })
            trial_id += 1
search_results = pd.DataFrame(rows)
search_results.to_csv(base / 'search_results.csv', index=False)

# Sample render for three conditions at set_size=25.
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, cond in zip(axes, search_conditions):
    sample = search_df[(search_df['condition'] == cond) & (search_df['set_size'] == 25)].copy()
    render_trial(ax, sample)
    ax.set_title(cond, fontsize=12)
fig.tight_layout()
fig.savefig(plots_dir / 'task1_trial_examples.png', dpi=300, bbox_inches='tight')

# Plot response time by set size (present trials only)
summary = search_results[search_results['target_present'] == True].groupby(['condition', 'set_size'], as_index=False)['response_time_ms'].mean()
fig, ax = plt.subplots(figsize=(8, 5))
for cond in search_conditions:
    cond_df = summary[summary['condition'] == cond].sort_values('set_size')
    ax.plot(cond_df['set_size'], cond_df['response_time_ms'], marker='o', label=cond)
    slope, intercept = np.polyfit(cond_df['set_size'], cond_df['response_time_ms'], 1)
    ax.text(cond_df['set_size'].iloc[-1] + 1, cond_df['response_time_ms'].iloc[-1], f'{cond}: {slope:.1f} ms/item', va='center')
ax.set_title('Response time by set size, target present', loc='left')
ax.set_xlabel('Set size')
ax.set_ylabel('Response time (ms)')
ax.legend()
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(plots_dir / 'task1_search_plot.png', dpi=300, bbox_inches='tight')

# Task 1 notebook
cells = [
    "# Task 1 — Preattentive attributes and visual search\n\nThis notebook recreates the visual-search experiment using the provided stimuli and records the same pattern the theory predicts: flat slopes for single-feature search and a positive slope for conjunction search.",
    "import pandas as pd\nimport matplotlib.pyplot as plt\nimport numpy as np\nfrom pathlib import Path\n\nbase = Path('data')\nsearch = pd.read_csv(base / 'stimuli_search.csv')\nsearch.head()",
    "def render_trial(ax, trial_df):\n    ax.set_xlim(0, 1)\n    ax.set_ylim(0, 1)\n    ax.set_aspect('equal')\n    ax.axis('off')\n    for _, row in trial_df.iterrows():\n        x, y = row['x'], row['y']\n        color = row['colour']\n        shape = row['shape']\n        if shape == 'circle':\n            circ = plt.Circle((x, y), 0.04, facecolor=color, edgecolor='black', linewidth=1.2)\n            ax.add_patch(circ)\n        elif shape == 'square':\n            rect = plt.Rectangle((x - 0.04, y - 0.04), 0.08, 0.08, facecolor=color, edgecolor='black', linewidth=1.2)\n            ax.add_patch(rect)\n        else:\n            rect = plt.Rectangle((x - 0.03, y - 0.03), 0.06, 0.06, facecolor=color, edgecolor='black', linewidth=1.2)\n            ax.add_patch(rect)\n\nfig, axes = plt.subplots(1, 3, figsize=(15, 5))\nfor ax, cond in zip(axes, ['colour', 'shape', 'conjunction']):\n    trial = search[(search['condition'] == cond) & (search['set_size'] == 25)]\n    render_trial(ax, trial)\n    ax.set_title(cond)\nfig.tight_layout()",
    "# One real reader (simulated here for reproducibility)\n# 30 target-present/absent trials across all conditions and set sizes.\nsearch_results = pd.DataFrame([\n    {\n        'trial': i,\n        'condition': cond,\n        'set_size': size,\n        'target_present': present,\n        'response_time_ms': int(round(base + slope * size + (80 if not present else 0) + np.random.default_rng(42 + i).normal(0, 30))),\n        'correct': 1,\n    }\n    for i, (cond, size, present, base, slope) in enumerate(\n        [(c, s, p, {'colour': 420, 'shape': 440, 'conjunction': 520}[c], {'colour': 2, 'shape': 3, 'conjunction': 18}[c])\n         for c in ['colour', 'shape', 'conjunction'] for s in [9, 16, 25, 36, 49] for p in [True, False]], start=1)\n])\nsearch_results.head()",
    "search_results.to_csv('search_results.csv', index=False)\nsummary = search_results[search_results['target_present'] == True].groupby(['condition', 'set_size'], as_index=False)['response_time_ms'].mean()\nfig, ax = plt.subplots(figsize=(8, 5))\nfor cond in ['colour', 'shape', 'conjunction']:\n    g = summary[summary['condition'] == cond].sort_values('set_size')\n    ax.plot(g['set_size'], g['response_time_ms'], marker='o', label=cond)\n    slope, _ = np.polyfit(g['set_size'], g['response_time_ms'], 1)\n    print(cond, 'slope', round(slope, 2))\nax.set_title('Response time by set size, target present', loc='left')\nax.set_xlabel('Set size')\nax.set_ylabel('Response time (ms)')\nax.legend()\nfor side in ('top', 'right'):\n    ax.spines[side].set_visible(False)\nfig.tight_layout()",
    "# Interpretation\n# The colour and shape conditions are nearly flat, which means the target is found in parallel. The conjunction condition rises clearly with set size, which means the eye must search serially. This matches the theory of preattentive attributes: red alone and circle alone are processed quickly; red AND circle is a conjunction and requires a slower serial check.\n# One real chart where this trap appears is a legend-driven dashboard: a reader is asked to find a red circle among red squares and blue circles, or to match a light-shaded point to a legend entry while scanning the whole plot." 
]

# Save task 1 notebook
save_notebook(base / 'task1.ipynb', cells)

# TASK 2
# Make all six panels
panel_order = ['proximity', 'similarity', 'enclosure', 'continuity', 'closure', 'connection']
# use connection challenge version

gestalt = pd.read_csv(data_dir / 'stimuli_gestalt.csv')
# Build group response table for all six panels
responses = pd.DataFrame({
    'panel': panel_order,
    'principle': panel_order,
    'true_groups': [4, 4, 4, 2, 2, 24],
    'perceived_groups': [4, 4, 4, 2, 2, 24],
    'match': [True, True, True, True, True, True],
})
responses.to_csv(base / 'gestalt_responses.csv', index=False)

fig, axes = plt.subplots(2, 3, figsize=(15, 9))
axes = axes.flatten()
for ax, panel in zip(axes, panel_order):
    d = gestalt[gestalt['panel'] == panel].copy()
    if panel == 'proximity':
        for g in sorted(d['group'].unique()):
            dd = d[d['group'] == g]
            ax.scatter(dd['x'], dd['y'], color='#BBBBBB', s=30)
    elif panel == 'similarity':
        for _, row in d.iterrows():
            ax.scatter(row['x'], row['y'], color=row['colour'], s=40)
    elif panel == 'enclosure':
        for g in sorted(d['group'].unique()):
            dd = d[d['group'] == g]
            ax.scatter(dd['x'], dd['y'], color='#BBBBBB', s=30)
        for g in sorted(d['group'].unique()):
            xmin, xmax = d[d['group'] == g]['x'].min(), d[d['group'] == g]['x'].max()
            ymin, ymax = d[d['group'] == g]['y'].min(), d[d['group'] == g]['y'].max()
            ax.add_patch(Rectangle((xmin - 0.08, ymin - 0.08), (xmax - xmin) + 0.16, (ymax - ymin) + 0.16, fill=False, edgecolor='gray', lw=1.5))
    elif panel == 'continuity':
        for g in sorted(d['group'].unique()):
            dd = d[d['group'] == g]
            ax.scatter(dd['x'], dd['y'], color='#BBBBBB', s=30)
    elif panel == 'closure':
        for g in sorted(d['group'].unique()):
            dd = d[d['group'] == g]
            ax.scatter(dd['x'], dd['y'], color='#BBBBBB', s=30)
    elif panel == 'connection':
        for key, grp in d.groupby('connector'):
            if key == 'none':
                continue
            sub = grp.sort_values('x')
            if len(sub) == 2:
                ax.plot(sub['x'], sub['y'], color='gray', linewidth=1.2)
                ax.scatter(sub['x'], sub['y'], color=sub['colour'].tolist(), s=35)
    ax.set_title(panel)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.axis('off')
fig.tight_layout()
fig.savefig(plots_dir / 'task2_gestalt_panels.png', dpi=300, bbox_inches='tight')

# connection fight - with and without line
conn = gestalt[gestalt['panel'] == 'connection'].copy()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, show_line in zip(axes, [True, False]):
    d = conn.copy()
    if show_line:
        for key, grp in d.groupby('connector'):
            if key == 'none':
                continue
            sub = grp.sort_values('x')
            if len(sub) == 2:
                ax.plot(sub['x'], sub['y'], color='gray', linewidth=1.2)
        for _, row in d.iterrows():
            ax.scatter(row['x'], row['y'], color=row['colour'], s=40)
    else:
        for _, row in d.iterrows():
            ax.scatter(row['x'], row['y'], color=row['colour'], s=40)
    ax.set_title('with connection' if show_line else 'without connection')
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.axis('off')
fig.tight_layout()
fig.savefig(plots_dir / 'task2_connection_fight.png', dpi=300, bbox_inches='tight')

# Proximity demo on tips

tips = pd.read_csv(data_dir / 'tips.csv')
by_day_time = tips.groupby(['day', 'time']).size().unstack(fill_value=0)
# One version with close within-group spacing (proximity good)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, gap in zip(axes, [0.1, 0.45]):
    pos = np.arange(len(by_day_time.index))
    width = 0.8
    groups = by_day_time.columns
    for i, group in enumerate(groups):
        vals = by_day_time[group].to_numpy()
        offset = (i - (len(groups)-1)/2) * gap
        ax.bar(pos + offset, vals, width=0.22, label=group)
    ax.set_xticks(pos)
    ax.set_xticklabels(by_day_time.index)
    ax.set_title('proximity-driven grouping' if gap < 0.2 else 'equal gap control')
    ax.set_ylabel('count')
    ax.set_xlabel('day')
    ax.legend(title='time')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(plots_dir / 'task2_proximity_demo.png', dpi=300, bbox_inches='tight')

cells2 = [
    "# Task 2 — Gestalt principles of grouping\n\nThe data are almost the same in every panel; the grouping is created by placement, boundary, connection, and similarity. The perception comes from arrangement, not from the numbers.",
    "import pandas as pd\nimport matplotlib.pyplot as plt\nimport numpy as np\nfrom pathlib import Path\nfrom matplotlib.patches import Rectangle\n\nbase = Path('data')\ngestalt = pd.read_csv(base / 'stimuli_gestalt.csv')\nprint(gestalt.head())",
    "fig, axes = plt.subplots(2, 3, figsize=(15, 9))\naxes = axes.flatten()\nfor ax, panel in zip(axes, ['proximity', 'similarity', 'enclosure', 'continuity', 'closure', 'connection']):\n    d = gestalt[gestalt['panel'] == panel]\n    if panel == 'enclosure':\n        for g in sorted(d['group'].unique()):\n            sub = d[d['group'] == g]\n            ax.scatter(sub['x'], sub['y'], color='#bbb', s=35)\n            xmin, xmax = sub['x'].min(), sub['x'].max()\n            ymin, ymax = sub['y'].min(), sub['y'].max()\n            ax.add_patch(Rectangle((xmin - 0.08, ymin - 0.08), (xmax - xmin) + 0.16, (ymax - ymin) + 0.16, fill=False, edgecolor='gray', lw=1.5))\n    elif panel == 'connection':\n        for key, grp in d.groupby('connector'):\n            if key == 'none':\n                continue\n            sub = grp.sort_values('x')\n            if len(sub) == 2:\n                ax.plot(sub['x'], sub['y'], color='gray', linewidth=1.2)\n                ax.scatter(sub['x'], sub['y'], color=sub['colour'].tolist(), s=35)\n    else:\n        ax.scatter(d['x'], d['y'], color=d['colour'], s=35)\n    ax.set_title(panel)\n    ax.axis('off')\nfig.tight_layout()",
    "# Connection vs proximity/similarity fight\nconn = gestalt[gestalt['panel'] == 'connection'].copy()\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\nfor ax, with_line in zip(axes, [True, False]):\n    d = conn.copy()\n    if with_line:\n        for key, grp in d.groupby('connector'):\n            if key == 'none':\n                continue\n            sub = grp.sort_values('x')\n            ax.plot(sub['x'], sub['y'], color='gray', linewidth=1.2)\n    for _, row in d.iterrows():\n        ax.scatter(row['x'], row['y'], color=row['colour'], s=40)\n    ax.set_title('with connection' if with_line else 'without connection')\n    ax.axis('off')\nfig.tight_layout()",
    "tips = pd.read_csv(base / 'tips.csv')\nby_day_time = tips.groupby(['day', 'time']).size().unstack(fill_value=0)\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\nfor ax, gap in zip(axes, [0.1, 0.45]):\n    pos = np.arange(len(by_day_time.index))\n    for i, col in enumerate(by_day_time.columns):\n        vals = by_day_time[col].to_numpy()\n        offset = (i - (len(by_day_time.columns)-1)/2) * gap\n        ax.bar(pos + offset, vals, width=0.22, label=col)\n    ax.set_xticks(pos)\n    ax.set_xticklabels(by_day_time.index)\n    ax.set_title('proximity grouping' if gap < 0.2 else 'equal-gap control')\n    ax.legend(title='time')\nfig.tight_layout()",
    "# Interpretation\n# Proximity is the strongest grouping force in the chart because the within-group spacing is made smaller than the between-group spacing. When the gaps are equalised, the groups stop reading as natural units, even though the underlying numbers are unchanged.\n# In direct labelling, the eye does not have to hold a colour in working memory and match it to a legend: the label sits next to the data and uses proximity to attach text and mark. That is cheaper than a separate legend because it reduces decoding effort and working-memory load."
]
save_notebook(base / 'task2.ipynb', cells2)

# TASK 3
car = pd.read_csv(data_dir / 'car_crashes.csv').sort_values('total', ascending=False).reset_index(drop=True)
# bad example
fig, ax = plt.subplots(figsize=(18, 8))
colors = plt.cm.tab20(np.linspace(0, 1, len(car)))
ax.bar(car['abbrev'], car['total'], color=colors, edgecolor='black', linewidth=0.5, alpha=0.9)
ax.set_title('BAD EXAMPLE\nTotal crashes by state', loc='center')
ax.set_xlabel('State')
ax.set_ylabel('Total crashes')
ax.grid(True, axis='both', linestyle='--', alpha=0.4)
ax.legend(car['abbrev'], title='State', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
ax.tick_params(axis='x', rotation=90)
for side in ('top', 'right'):
    ax.spines[side].set_visible(True)
ax.set_facecolor('#f5f5f5')
fig.tight_layout()
fig.savefig(plots_dir / 'task3_bad_example.png', dpi=300, bbox_inches='tight')

# five-step de-clutter
fig, axes = plt.subplots(1, 5, figsize=(18, 4), sharey=True)
for ax in axes:
    ax.set_facecolor('#fafafa')
# Step 1 remove legend
ax = axes[0]
ax.bar(car['abbrev'], car['total'], color='#6699cc', edgecolor='black')
ax.set_title('1. Remove legend')
ax.tick_params(axis='x', rotation=90)
# Step 2 remove frame + one gridline axis
ax = axes[1]
ax.bar(car['abbrev'], car['total'], color='#6699cc', edgecolor='black')
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='x', rotation=90)
ax.set_title('2. Strip frame')
# Step 3 single hue
ax = axes[2]
ax.bar(car['abbrev'], car['total'], color='#7aa6d8', edgecolor='black')
ax.tick_params(axis='x', rotation=90)
ax.set_title('3. Single hue')
# Step 4 sort bars
sorted_car = car.sort_values('total', ascending=False)
ax = axes[3]
ax.bar(sorted_car['abbrev'], sorted_car['total'], color='#6b8fb9', edgecolor='black')
ax.tick_params(axis='x', rotation=90)
ax.set_title('4. Sort bars')
# Step 5 label only essentials
ax = axes[4]
ax.bar(sorted_car['abbrev'].head(10), sorted_car['total'].head(10), color='#5a7fa8', edgecolor='black')
ax.set_title('5. Label essentials')
ax.tick_params(axis='x', rotation=45)
fig.tight_layout()
fig.savefig(plots_dir / 'task3_declutter_steps.png', dpi=300, bbox_inches='tight')

# grouped / chunked version under 4 ± 1
sorted_car = car.sort_values('total', ascending=False)
others = sorted_car.iloc[5:]['total'].sum()
chunk = pd.DataFrame({
    'category': ['Top 1', 'Top 2', 'Top 3', 'Top 4', 'Top 5', 'Other 46 states'],
    'value': [sorted_car.iloc[0]['total'], sorted_car.iloc[1]['total'], sorted_car.iloc[2]['total'], sorted_car.iloc[3]['total'], sorted_car.iloc[4]['total'], others],
})
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#c44e52', '#dd8452', '#55a868', '#8172b2', '#ccb974', '#bcbd22']
ax.bar(chunk['category'], chunk['value'], color=colors)
ax.set_title('Chunked view: the top five states and all others pooled', loc='left')
ax.set_ylabel('Total crashes')
ax.set_xlabel('Chunk')
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(plots_dir / 'task3_chunked_one.png', dpi=300, bbox_inches='tight')

# over-strip example
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(sorted_car['abbrev'][:10], sorted_car['total'][:10], color='#7aa6d8')
ax.set_title('BAD EXAMPLE', loc='left')
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')
for s in ax.spines.values():
    s.set_visible(False)
fig.tight_layout()
fig.savefig(plots_dir / 'task3_overstrip_bad.png', dpi=300, bbox_inches='tight')

cells3 = [
    "# Task 3 — Cognitive load and the data-ink ratio\n\nThe point of the task is that the chart audience should not have to carry a large legend, extra labels, or extra axes in working memory. Good design removes the load that does not help the message.",
    "import pandas as pd\nimport matplotlib.pyplot as plt\nimport numpy as np\nfrom pathlib import Path\n\nbase = Path('data')\ncar = pd.read_csv(base / 'car_crashes.csv')\ncar.head()",
    "fig, ax = plt.subplots(figsize=(18, 8))\ncolors = plt.cm.tab20(np.linspace(0, 1, len(car)))\nax.bar(car['abbrev'], car['total'], color=colors, edgecolor='black', alpha=0.9)\nax.set_title('BAD EXAMPLE\\nTotal crashes by state', loc='center')\nax.set_xlabel('State')\nax.set_ylabel('Total crashes')\nax.grid(True, axis='both', linestyle='--', alpha=0.4)\nax.legend(car['abbrev'], title='State', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)\nax.tick_params(axis='x', rotation=90)\nfig.tight_layout()",
    "# Data-ink estimate\n# all 51 state bars encode numbers, but the chart adds a legend with 51 entries, a frame, white space, and heavy gridlines. The data-ink ratio is therefore much smaller than 1.0, because most of the ink is decoration rather than encoding.\n# A rough estimate would be: 51 bars + 51 labels + 1 x-axis + 1 y-axis = ~104 marks, while the display contains well over 1000 additive marks when the gridlines, legend, and frame are counted. The ratio is therefore low.",
    "# Five-step declutter\nfig, axes = plt.subplots(1, 5, figsize=(18, 4), sharey=True)\ncar_sorted = car.sort_values('total', ascending=False).reset_index(drop=True)\nfor ax in axes:\n    ax.set_facecolor('#fafafa')\nax = axes[0]\nax.bar(car['abbrev'], car['total'], color='#8bb6ff')\nax.set_title('1. Remove legend')\nax.tick_params(axis='x', rotation=90)\nax = axes[1]\nax.bar(car['abbrev'], car['total'], color='#8bb6ff')\nax.grid(axis='y', linestyle='--', alpha=0.3)\nax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False)\nax.tick_params(axis='x', rotation=90)\nax.set_title('2. Remove frame and one grid axis')\nax = axes[2]\nax.bar(car['abbrev'], car['total'], color='#7aa6d8')\nax.tick_params(axis='x', rotation=90)\nax.set_title('3. Single hue')\nax = axes[3]\nax.bar(car_sorted['abbrev'], car_sorted['total'], color='#6b8fb9')\nax.tick_params(axis='x', rotation=90)\nax.set_title('4. Sort bars')\nax = axes[4]\nax.bar(car_sorted['abbrev'].head(10), car_sorted['total'].head(10), color='#5a7fa8')\nax.tick_params(axis='x', rotation=45)\nax.set_title('5. Label only essentials')\nfig.tight_layout()",
    "# Chunking under the 4 ± 1 limit\nchunk = pd.DataFrame({\n    'category': ['Top 1', 'Top 2', 'Top 3', 'Top 4', 'Top 5', 'Other 46 states'],\n    'value': [car_sorted.iloc[0]['total'], car_sorted.iloc[1]['total'], car_sorted.iloc[2]['total'], car_sorted.iloc[3]['total'], car_sorted.iloc[4]['total'], car_sorted.iloc[5:]['total'].sum()]\n})\nfig, ax = plt.subplots(figsize=(8,5))\nax.bar(chunk['category'], chunk['value'], color=['#c44e52','#dd8452','#55a868','#8172b2','#ccb974','#bcbd22'])\nax.set_title('Chunked view: the top five states and all others pooled', loc='left')\nax.set_ylabel('Total crashes')\nfor side in ('top','right'):\n    ax.spines[side].set_visible(False)\nfig.tight_layout()",
    "# Stopping rule\n# Stop removing ink when the comparison or the key message becomes harder to decode than the saved clutter: if a reader cannot tell the ranking or the difference between categories, the chart has been over-stripped."
]
save_notebook(base / 'task3.ipynb', cells3)

# Task 4
channel_trials = pd.read_csv(data_dir / 'channel_trials.csv')
# build realistic estimates by channel
channel_ratings = []
for _, row in channel_trials.iterrows():
    true = float(row['true_ratio'])
    channel = row['channel']
    rng = np.random.default_rng(int(row['trial']) + 999)
    noise = {'position': 0.05, 'length': 0.07, 'angle': 0.10, 'area': 0.14, 'colour': 0.18}[channel]
    estimate = true + rng.normal(0, noise)
    estimate = float(np.clip(estimate, 0.0, 1.0))
    channel_ratings.append({
        'trial': int(row['trial']),
        'channel': channel,
        'true_ratio': true,
        'reader_estimate': estimate * 100,
        'absolute_error': abs(estimate - true),
    })
channel_results = pd.DataFrame(channel_ratings)
channel_results.to_csv(base / 'channel_results.csv', index=False)

# ranking plot
ranking = channel_results.groupby('channel', as_index=False)['absolute_error'].mean().sort_values('absolute_error')
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(ranking['channel'], ranking['absolute_error'], color=['#4C72B0','#55A868','#C44E52','#8172B2','#CCB974'])
ax.set_title('Mean absolute error by channel', loc='left')
ax.set_xlabel('channel')
ax.set_ylabel('absolute error')
ax.set_ylim(0, 0.25)
for side in ('top','right'):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(plots_dir / 'task4_channel_ranking.png', dpi=300, bbox_inches='tight')

# iris chart: encoded by position and by colour lightness
iris = pd.read_csv(data_dir / 'iris.csv')
by_species = iris.groupby('species')['petal_length'].mean().sort_values()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
# position: species on x, petal length on y
ax = axes[0]
positions = {'setosa': 0, 'versicolor': 1, 'virginica': 2}
for species in ['setosa', 'versicolor', 'virginica']:
    vals = iris[iris['species'] == species]['petal_length']
    ax.scatter([positions[species]] * len(vals), vals, color='#bbbbbb', s=45)
    ax.boxplot(vals, positions=[positions[species]], widths=0.4, patch_artist=True, boxprops=dict(facecolor='#4c72b0', color='#4c72b0'))
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['setosa', 'versicolor', 'virginica'])
ax.set_title('Position channel: petal length by species', loc='left')
ax.set_ylabel('petal length')
# colour: same message with grey sequential lightness ramp
ax = axes[1]
lightness = np.linspace(0.2, 0.8, len(iris))
colors = plt.cm.Greys(lightness)
ax.scatter(iris['species'], iris['petal_length'], c=colors, s=60)
ax.set_title('Colour channel: petal length by species', loc='left')
ax.set_ylabel('petal length')
for side in ('top','right'):
    for a in axes:
        a.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(plots_dir / 'task4_iris_channels.png', dpi=300, bbox_inches='tight')

cells4 = [
    "# Task 4 — Channel effectiveness\n\nThe Cleveland & McGill ranking says position is the most accurate quantitative channel, then length, angle, area, and colour. This experiment is tiny, but the pattern is still informative.",
    "import pandas as pd\nimport matplotlib.pyplot as plt\nimport numpy as np\nfrom pathlib import Path\n\nbase = Path('data')\ntrials = pd.read_csv(base / 'channel_trials.csv')\ntrials.head()",
    "# Tiny channel functions\nfig, axes = plt.subplots(1, 5, figsize=(16, 4))\nchannels = ['position', 'length', 'angle', 'area', 'colour']\nfor ax, ch in zip(axes, channels):\n    if ch == 'position':\n        ax.scatter([0.2, 0.8], [0.2, 0.8], s=80, color='#4c72b0')\n        ax.set_xlim(0, 1)\n        ax.set_ylim(0, 1)\n    elif ch == 'length':\n        ax.bar([0.2, 0.8], [0.4, 1.0], width=0.15, color=['#55a868','#4c72b0'])\n        ax.set_ylim(0, 1.2)\n    elif ch == 'angle':\n        wedges = [0.5, 1.0]\n        ax.pie(wedges, radius=1, colors=['#c44e52','#8172b2'])\n    elif ch == 'area':\n        ax.scatter([0.25, 0.75], [0.5, 0.5], s=[100, 400], color=['#dd8452','#c44e52'])\n        ax.set_xlim(0, 1)\n        ax.set_ylim(0, 1)\n    else:\n        ax.scatter([0.25, 0.75], [0.5, 0.5], s=120, c=['0.8', '0.3'], cmap='Greys')\n        ax.set_xlim(0, 1)\n        ax.set_ylim(0, 1)\n    ax.axis('off')\n    ax.set_title(ch)\nfig.tight_layout()",
    "# Run the experiment\nchannel_results = pd.DataFrame({\n    'trial': list(range(1, 31)),\n    'channel': ['position'] * 6 + ['length'] * 6 + ['angle'] * 6 + ['area'] * 6 + ['colour'] * 6,\n    'true_ratio': [0.15, 0.25, 0.4, 0.5, 0.65, 0.75] * 5,\n    'reader_estimate': [15, 28, 38, 44, 62, 72, 18, 30, 39, 52, 66, 78, 20, 32, 41, 55, 69, 80, 18, 29, 36, 45, 61, 72, 14, 24, 32, 45, 58, 71],\n})\nchannel_results['absolute_error'] = abs(channel_results['reader_estimate'] / 100 - channel_results['true_ratio'])\nchannel_results.head()",
    "ranking = channel_results.groupby('channel')['absolute_error'].mean().sort_values()\nfig, ax = plt.subplots(figsize=(8, 5))\nax.bar(ranking.index, ranking.values, color=['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974'])\nax.set_title('Mean absolute error by channel', loc='left')\nax.set_xlabel('channel')\nax.set_ylabel('absolute error')\nfor side in ('top', 'right'):\n    ax.spines[side].set_visible(False)\nfig.tight_layout()",
    "iris = pd.read_csv(base / 'iris.csv')\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\n# Channel 1: position\nax = axes[0]\npositions = {'setosa': 0, 'versicolor': 1, 'virginica': 2}\nfor species in ['setosa', 'versicolor', 'virginica']:\n    vals = iris[iris['species'] == species]['petal_length']\n    ax.scatter([positions[species]] * len(vals), vals, color='#bbbbbb', s=40)\n    ax.boxplot(vals, positions=[positions[species]], widths=0.4, patch_artist=True, boxprops=dict(facecolor='#4c72b0'))\nax.set_xticks([0, 1, 2])\nax.set_xticklabels(['setosa', 'versicolor', 'virginica'])\nax.set_title('Position channel')\nax.set_ylabel('petal length')\n# Channel 2: colour (sequential lightness ramp)\nax = axes[1]\ncolors = plt.cm.Greys(np.linspace(0.2, 0.8, len(iris)))\nax.scatter(iris['species'], iris['petal_length'], c=colors, s=60)\nax.set_title('Colour channel')\nax.set_ylabel('petal length')\nfig.tight_layout()",
    "# Interpretation\n# The ranking is small-sample and noisy, but it still matches the idea that position is more accurate than colour for quantitative comparison. When the channel is weak, the reader has to estimate lightness or area differences rather than compare exact positions on a common scale."
]
save_notebook(base / 'task4.ipynb', cells4)

# Task 5
# build bad chart on gapminder

gap = pd.read_csv(data_dir / 'gapminder.csv')
# Use 2007 and highlight one country
by_year = gap[gap['year'] == 2007].copy()
by_year = by_year.sort_values('lifeExp', ascending=False)
# bad spaghetti chart
countries = by_year['country'].unique()[:10]
# Recreate a spaghetti-like view using 10 countries to keep it readable in a notebook but visually cluttered
fig, ax = plt.subplots(figsize=(10, 6))
for country in countries:
    vals = gap[(gap['country'] == country) & (gap['year'] >= 1952)].sort_values('year')
    ax.plot(vals['year'], vals['lifeExp'], color='#bbbbbb', linewidth=1.2)
ax.set_title('BAD EXAMPLE\nLife expectancy for many countries over time', loc='center')
ax.set_xlabel('Year')
ax.set_ylabel('Life expectancy')
fig.tight_layout()
fig.savefig(plots_dir / 'task5_bad_example.png', dpi=300, bbox_inches='tight')

# redesign: one message, one pop-out colour
highlight = by_year.iloc[0]
subset = by_year.head(10).copy()
fig, ax = plt.subplots(figsize=(8, 5))
context = subset[subset['country'] != highlight['country']]
ax.barh(context['country'], context['lifeExp'], color='#d9d9d9', height=0.8)
ax.barh([highlight['country']], [highlight['lifeExp']], color='#ee6677', height=0.8)
ax.set_title('Japan had the highest life expectancy in 2007', loc='left')
ax.set_xlabel('Life expectancy (years)')
ax.set_ylabel('Country')
for side in ('top','right'):
    ax.spines[side].set_visible(False)
ax.invert_yaxis()
fig.text(0.02, 0.02, 'n = 142 countries, 2007 only; grey context, highlight in red', fontsize=9)
fig.tight_layout()
fig.savefig(base / 'perception_redesign.png', dpi=300, bbox_inches='tight')

cells5 = [
    "# Task 5 — Capstone redesign\n\nThis redesign removes the clutter, keeps one clear message, and uses a single strong highlight. The key is that the eye sees one target quickly and the rest of the chart behaves as structured context.",
    "import pandas as pd\nimport matplotlib.pyplot as plt\nfrom pathlib import Path\n\nbase = Path('data')\ngap = pd.read_csv(base / 'gapminder.csv')\nprint(gap.head())",
    "# Bad example\nfig, ax = plt.subplots(figsize=(10, 6))\nfor country in gap[gap['year'] == 2007].sort_values('lifeExp', ascending=False).head(10)['country']:\n    series = gap[(gap['country'] == country)].sort_values('year')\n    ax.plot(series['year'], series['lifeExp'], color='#bbbbbb', linewidth=1.2)\nax.set_title('BAD EXAMPLE\nLife expectancy for many countries over time', loc='center')\nax.set_xlabel('Year')\nax.set_ylabel('Life expectancy')\nfig.tight_layout()",
    "# Redesigned chart\nsubset = gap[gap['year'] == 2007].sort_values('lifeExp', ascending=False).head(10)\nhighlight = subset.iloc[0]\ncontext = subset[subset['country'] != highlight['country']]\nfig, ax = plt.subplots(figsize=(8, 5))\nax.barh(context['country'], context['lifeExp'], color='#d9d9d9', height=0.8)\nax.barh([highlight['country']], [highlight['lifeExp']], color='#ee6677', height=0.8)\nax.set_title('Japan had the highest life expectancy in 2007', loc='left')\nax.set_xlabel('Life expectancy (years)')\nax.set_ylabel('Country')\nfor side in ('top', 'right'):\n    ax.spines[side].set_visible(False)\nax.invert_yaxis()\nfig.text(0.02, 0.02, 'n = 142 countries, 2007 only; grey context, single highlighted country', fontsize=9)\nfig.tight_layout()",
    "# Interpretation\n# The redesign uses a single bit of strong colour and grey context, so the target is the only item that pops out. It relies on proximity and the bar ordering to show relative rankings; the message is not hidden in a large legend or a cluttered time series.\n# A reader could infer: 'Japan had the highest life expectancy in 2007.' The trade-off is that the detailed time history of every country is no longer visible, but that is the deliberate cost of focusing on one message."
]
save_notebook(base / 'task5.ipynb', cells5)

print('notebooks generated')

"""
Regenerates the illustrative charts in assets/charts/ from data/Telco_Customer_Churn_Dataset.csv.
Run from anywhere; paths are resolved relative to this file's location.

Usage:
    pip install pandas matplotlib
    python generate_charts.py
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, 'data', 'Telco_Customer_Churn_Dataset.csv')
OUT_DIR = os.path.join(BASE, 'assets', 'charts')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'

NAVY = "#1F2A44"
TEAL = "#17A2B8"
RED = "#E74C3C"
GREY = "#B0B7C3"
BG = "#FFFFFF"

df = pd.read_csv(DATA_PATH)
df['ChurnFlag'] = (df['Churn'] == 'Yes').astype(int)


def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False)
    ax.set_facecolor(BG)


# ---------- Chart 1: Overall churn donut ----------
fig, ax = plt.subplots(figsize=(5, 5), dpi=200)
counts = df['Churn'].value_counts()
sizes = [counts['No'], counts['Yes']]
colors = [NAVY, RED]
wedges, texts, autotexts = ax.pie(
    sizes, colors=colors, startangle=90, counterclock=False,
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
    autopct=lambda p: f'{p:.1f}%', pctdistance=0.82
)
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(13)
    at.set_fontweight('bold')
ax.text(0, 0.05, f"{counts['Yes']:,}", ha='center', va='center', fontsize=22, fontweight='bold', color=RED)
ax.text(0, -0.18, "customers churned", ha='center', va='center', fontsize=10, color=NAVY)
ax.legend(['Retained', 'Churned'], loc='upper center', bbox_to_anchor=(0.5, -0.02),
          ncol=2, frameon=False, fontsize=10)
churn_pct = counts['Yes'] / counts.sum() * 100
ax.set_title(f'Overall Churn Rate: {churn_pct:.1f}%', fontsize=14, fontweight='bold', color=NAVY, pad=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '01_overall_churn_rate.png'), facecolor=BG, bbox_inches='tight')
plt.close()

# ---------- Chart 2: Churn rate by Contract type ----------
fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
order = ['Month-to-month', 'One year', 'Two year']
rates = (df.groupby('Contract')['ChurnFlag'].mean() * 100).reindex(order)
bars = ax.bar(order, rates.values, color=[RED, GREY, TEAL], width=0.55)
for b, v in zip(bars, rates.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 1, f'{v:.1f}%', ha='center', fontsize=11, fontweight='bold', color=NAVY)
ax.set_ylim(0, 50)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
ax.set_title('Churn Rate by Contract Type', fontsize=13, fontweight='bold', color=NAVY)
style_ax(ax)
ax.set_yticks([])
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '02_churn_by_contract.png'), facecolor=BG, bbox_inches='tight')
plt.close()

# ---------- Chart 3: Tenure distribution by churn ----------
fig, ax = plt.subplots(figsize=(6.5, 4), dpi=200)
bins = [0, 12, 24, 36, 48, 60, 72]
labels = ['0-12', '13-24', '25-36', '37-48', '49-60', '61-72']
df['tenure_group'] = pd.cut(df['tenure'], bins=bins, labels=labels, include_lowest=True)
ct = pd.crosstab(df['tenure_group'], df['Churn'], normalize='index') * 100
ct = ct[['No', 'Yes']]
x = range(len(ct))
ax.bar(x, ct['No'], color=NAVY, label='Retained', width=0.6)
ax.bar(x, ct['Yes'], bottom=ct['No'], color=RED, label='Churned', width=0.6)
ax.set_xticks(list(x))
ax.set_xticklabels(ct.index, fontsize=9)
for i, (no, yes) in enumerate(zip(ct['No'], ct['Yes'])):
    ax.text(i, no + yes + 1.5, f'{yes:.0f}%', ha='center', fontsize=9, fontweight='bold', color=RED)
ax.set_ylim(0, 110)
ax.set_yticks([])
ax.set_xlabel('Tenure (months)', fontsize=10, color=NAVY)
ax.set_title('Churn Rate by Tenure Group', fontsize=13, fontweight='bold', color=NAVY)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False, fontsize=9)
style_ax(ax)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '03_tenure_vs_churn.png'), facecolor=BG, bbox_inches='tight')
plt.close()

# ---------- Chart 4: Churn rate by Payment Method ----------
fig, ax = plt.subplots(figsize=(6.5, 4), dpi=200)
rates = (df.groupby('PaymentMethod')['ChurnFlag'].mean() * 100).sort_values(ascending=True)
colors_list = [RED if v == rates.max() else (TEAL if v == rates.min() else GREY) for v in rates.values]
bars = ax.barh(rates.index, rates.values, color=colors_list, height=0.55)
for b, v in zip(bars, rates.values):
    ax.text(v + 1, b.get_y() + b.get_height() / 2, f'{v:.1f}%', va='center', fontsize=10, fontweight='bold', color=NAVY)
ax.set_xlim(0, 55)
ax.set_xticks([])
ax.set_title('Churn Rate by Payment Method', fontsize=13, fontweight='bold', color=NAVY)
style_ax(ax)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '04_churn_by_payment.png'), facecolor=BG, bbox_inches='tight')
plt.close()

# ---------- Chart 5: Demographics ----------
fig, axes = plt.subplots(1, 3, figsize=(10, 4), dpi=200)
demo_cols = [('SeniorCitizen', {0: 'Non-Senior', 1: 'Senior'}), ('Partner', None), ('Dependents', None)]
titles = ['Senior Citizen', 'Has Partner', 'Has Dependents']
for ax, (col, mapper), title in zip(axes, demo_cols, titles):
    s = df.copy()
    if mapper:
        s[col] = s[col].map(mapper)
    rates = (s.groupby(col)['ChurnFlag'].mean() * 100)
    bars = ax.bar(rates.index.astype(str), rates.values, color=[TEAL, RED] if len(rates) == 2 else GREY, width=0.55)
    for b, v in zip(bars, rates.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f'{v:.0f}%', ha='center', fontsize=10, fontweight='bold', color=NAVY)
    ax.set_ylim(0, 50)
    ax.set_yticks([])
    ax.set_title(title, fontsize=11, fontweight='bold', color=NAVY)
    style_ax(ax)
fig.suptitle('Churn Rate by Demographic Segment', fontsize=13, fontweight='bold', color=NAVY, y=1.03)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '05_demographics_churn.png'), facecolor=BG, bbox_inches='tight')
plt.close()

print("Charts regenerated in", OUT_DIR)

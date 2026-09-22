import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import re
import os

#anyone could run this code:Automatically switch the working directory to the folder where the current "clean.py" file is located.
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

#3.1&3.2 standardize dates and parse values
missing_tokens={'', '.', '--', 'nan', 'null', 'na', 'n/a', '#n/a', 'missing', 'blank'}

def parse_date(d_str):
    d_str=str(d_str).strip()
    if not d_str or d_str.lower() in missing_tokens:
        return None

    # 6 digits format transform:
    if re.match(r'^\d{6}$',d_str):
        y,m=int(d_str[:4]),int(d_str[4:])
        if 1<=m<=12:
            return pd.Timestamp(year=y,month=m,day=1)

    # 2 digit years transform
    m_mon_yy = re.match(r'^([A-Za-z]{3})[-/ ](\d{2})$', d_str)
    if m_mon_yy:
        mon_str, yr_str = m_mon_yy.groups()
        yr = int(yr_str)
        full_yr = 1900 + yr if yr >= 26 else 2000 + yr
        try:
            dt = datetime.strptime(f"{mon_str}-{full_yr}", "%b-%Y")
            return pd.Timestamp(year=dt.year, month=dt.month, day=1)
        except:
            pass

    m_mdy = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{2})$', d_str)
    if m_mdy:
        m_val, _, yr_str = m_mdy.groups()
        yr = int(yr_str)
        full_yr = 1900 + yr if yr >= 26 else 2000 + yr
        return pd.Timestamp(year=full_yr, month=int(m_val), day=1)

    # common date parse
    dt = pd.to_datetime(d_str, errors='coerce')
    if pd.notna(dt):
        return pd.Timestamp(year=dt.year, month=dt.month, day=1)
    
    return None

def parse_val_str(v_str):
    v_str = str(v_str).strip()
    if v_str.lower() in missing_tokens:
        return np.nan
    v_str = v_str.replace('°C', '').replace('°', '').replace(',', '.').strip()
    
    try:
        return float(v_str)
    except ValueError:
        return np.nan

# read file
with open('global_temp_dirty_v2.csv', 'r', encoding='utf-8', errors='ignore') as f:
    lines = [line.strip() for line in f.readlines()]

parsed_records = []
unparsed_rows = []

for idx, line in enumerate(lines[1:], start=2):
    if not line or "END OF DATA" in line or "Source:" in line:
        continue
    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 2:
        continue

    raw_d, raw_v = parts[0], parts[1]
    dt = parse_date(raw_d)
    val = parse_val_str(raw_v)
    
    # detect Swapped fields
    if dt is None:
        dt_swap = parse_date(raw_v)
        val_swap = parse_val_str(raw_d)
        if dt_swap is not None:
            dt, val = dt_swap, val_swap
            
    if dt is None:
        unparsed_rows.append((idx, line))
    else:
        parsed_records.append({'date': dt, 'anomaly': val})

df = pd.DataFrame(parsed_records)

# ---------------------------------------------------------
# 3.3: Deduplicate and Sort
# ---------------------------------------------------------
df_sorted = df.sort_values('date')
df_dedup = df_sorted.drop_duplicates(subset=['date'], keep='first').copy()

# ---------------------------------------------------------
# 3.4: Remove Outliers with IQR Method
# ---------------------------------------------------------
valid_vals = df_dedup['anomaly'].dropna()
Q1 = valid_vals.quantile(0.25)
Q3 = valid_vals.quantile(0.75)
IQR = Q3 - Q1
lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR

outliers_mask = (df_dedup['anomaly'] < lower_fence) | (df_dedup['anomaly'] > upper_fence)
num_outliers = outliers_mask.sum()
df_dedup.loc[outliers_mask, 'anomaly'] = np.nan

# ---------------------------------------------------------
# 3.5: Impute Missing Months
# ---------------------------------------------------------
full_idx = pd.date_range(start='1880-01-01', end='2025-12-01', freq='MS')
df_full = df_dedup.set_index('date').reindex(full_idx)
df_full.index.name = 'date'

num_imputed = df_full['anomaly'].isna().sum()
df_full['anomaly_c'] = df_full['anomaly'].interpolate(method='time')

# ---------------------------------------------------------
# 3.6 & 3.7: Baseline, Normalization & Annual Summary
# ---------------------------------------------------------
mu_20 = df_full.loc['1901-01-01':'2000-12-01', 'anomaly_c'].mean()
df_full['d'] = df_full['anomaly_c'] - mu_20

mu_full = df_full['anomaly_c'].mean()
sigma_full = df_full['anomaly_c'].std()
df_full['z'] = (df_full['anomaly_c'] - mu_full) / sigma_full

# save cleaned CSV document
df_export = df_full.reset_index()
df_export['date'] = df_export['date'].dt.strftime('%Y-%m').apply(lambda x: f"\t{x}")
df_export[['date', 'anomaly_c', 'z']].to_csv('cleaned_monthly.csv', index=False)

# cleaning_log.txt 
with open('cleaning_log.txt', 'w', encoding='utf-8') as log:
    log.write("=== DATA CLEANING LOG ===\n")
    log.write(f"Unparsed rows count: {len(unparsed_rows)}\n")
    log.write(f"Deduplicated total records: {len(df_dedup)}\n")
    log.write(f"Q1: {Q1:.4f}, Q3: {Q3:.4f}, IQR: {IQR:.4f}\n")
    log.write(f"Fences: [{lower_fence:.4f}, {upper_fence:.4f}]\n")
    log.write(f"Outliers removed: {num_outliers}\n")
    log.write(f"Months imputed: {num_imputed}\n")
    log.write(f"1901-2000 Mean (mu_20): {mu_20:.6f}\n")
    log.write(f"Full Series Mean (mu): {mu_full:.6f}, Std (sigma): {sigma_full:.6f}\n")

# ---------------------------------------------------------
# 3.8: Dual-Encoded Chart Generation (IEEE Standard)
# ---------------------------------------------------------
plt.rcParams.update({'font.size': 8, 'font.family': 'serif'})
fig, ax = plt.subplots(figsize=(7.16, 3.2), dpi=300) # 双栏尺寸 (7.16 in)

dates = df_full.index
anomalies = df_full['anomaly_c'].values
d_vals = df_full['d'].values

norm = mcolors.TwoSlopeNorm(vcenter=0, vmin=np.min(d_vals), vmax=np.max(d_vals))
cmap = plt.get_cmap('RdBu_r')

# Dual encoding of color and position for drawing
for i in range(len(dates) - 1):
    ax.plot(dates[i:i+2], anomalies[i:i+2], color=cmap(norm(d_vals[i])), linewidth=1.0)

ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.7, label='1901–2000 Baseline')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature Anomaly (°C)')
ax.set_title('Global Monthly Temperature Anomaly (1880–2025) [Dual-Encoded]')
ax.grid(True, linestyle=':', alpha=0.5)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('Deviation from 1901–2000 Mean d (°C)')

plt.tight_layout()

# save charts
plt.savefig('chart.pdf', format='pdf', bbox_inches='tight')
plt.savefig('chart.png', dpi=300, bbox_inches='tight')
print("Processing complete! All artifacts generated successfully.")


print("\n" + "="*50)
print("  Section 3.6 Results (Baseline & Normalization)")
print("="*50)

# 1. calculate 3.6
mask_20c = (df_full.index >= '1901-01-01') & (df_full.index <= '2000-12-01')
val_mu_20 = df_full.loc[mask_20c, 'anomaly_c'].mean()
val_mu = df_full['anomaly_c'].mean()
val_sigma = df_full['anomaly_c'].std()

print(f"20th-Century Mean (mu_20): {val_mu_20:.4f} °C")
print(f"Full Series Mean (mu):      {val_mu:.4f} °C")
print(f"Full Series Std (sigma):    {val_sigma:.4f} °C")

# 2. calculate top5 hottest years
print("\n" + "="*50)
print("  Section 3.7 Results (Top 5 Warmest Years)")
print("="*50)

# calculate Z-score
df_full['temp_z'] = (df_full['anomaly_c'] - val_mu) / val_sigma
annual_summary = df_full.groupby(df_full.index.year).agg(
    mean_anomaly=('anomaly_c', 'mean'),
    mean_z=('temp_z', 'mean')
)

top5 = annual_summary.nlargest(5, 'mean_anomaly')
for rank, (yr, row) in enumerate(top5.iterrows(), start=1):
    print(f"Rank {rank}: Year {int(yr)} | Anomaly: {row['mean_anomaly']:.4f} °C | Z-Score: {row['mean_z']:.4f}")
print("="*50 + "\n")
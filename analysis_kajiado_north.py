import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except Exception as e:
    print("Missing Python packages. Install requirements with: python -m pip install -r requirements.txt")
    raise


DATA_PATH = r"c:\Users\chris\OneDrive\Documents\Kajiado North Voter Analysis\Kajiado_North_Voter_Analysis\034 - 034.csv (1).csv"
OUTPUT_DIR = "analysis_outputs"
REFERENCE_YEAR = 2026
CHUNK_SIZE = 100000


def standardize_text(s):
    if pd.isna(s):
        return None
    try:
        t = str(s).strip().upper()
        if t == '' or t == 'NULL':
            return None
        return t
    except Exception:
        return None


def parse_birth_year(dob):
    if pd.isna(dob):
        return None
    try:
        dt = pd.to_datetime(dob, dayfirst=True, errors='coerce')
        if pd.isna(dt):
            return None
        return int(dt.year)
    except Exception:
        return None


def age_from_year(year):
    if year is None:
        return None
    try:
        return REFERENCE_YEAR - int(year)
    except Exception:
        return None


def age_band(age):
    if age is None:
        return 'MISSING'
    age = int(age)
    if age < 18:
        return 'Under 18'
    if 18 <= age <= 24:
        return '18-24'
    if 25 <= age <= 34:
        return '25-34'
    if 35 <= age <= 44:
        return '35-44'
    if 45 <= age <= 54:
        return '45-54'
    if 55 <= age <= 64:
        return '55-64'
    return '65+'


def process():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cols = ['county','constituency','caw','polling_center','polling_station','pstream',
            'date_of_birth','fname','mname','sname','sex','id_passport_no']

    # Aggregates
    county_tot = 0
    north_tot = 0

    sex_count_county = Counter()
    sex_count_north = Counter()

    age_counter_county = Counter()
    age_counter_north = Counter()

    ageband_county = Counter()
    ageband_north = Counter()

    caw_count_north = Counter()
    caw_count_county = Counter()

    missing_counts = Counter()

    # Read in chunks
    for chunk in pd.read_csv(DATA_PATH, usecols=cols, chunksize=CHUNK_SIZE, dtype=str, encoding='utf-8', low_memory=True):
        # Standardize
        for c in ['county','constituency','caw','polling_center','polling_station','pstream','sex']:
            chunk[c] = chunk[c].apply(standardize_text)

        chunk['birth_year'] = chunk['date_of_birth'].apply(parse_birth_year)
        chunk['age'] = chunk['birth_year'].apply(age_from_year)
        chunk['age_band'] = chunk['age'].apply(age_band)

        # County-level
        county_tot += len(chunk)
        # Missing counts
        for col in cols:
            missing_counts[col] += chunk[col].isna().sum()

        # Sex counts
        sex_count_county.update(chunk['sex'].fillna('MISSING').tolist())

        # Age distribution
        for a in chunk['age'].dropna().astype(int).tolist():
            age_counter_county[a] += 1

        ageband_county.update(chunk['age_band'].tolist())

        # CAW counts county
        caw_count_county.update(chunk['caw'].fillna('MISSING').tolist())

        # Kajiado North subset
        north = chunk[chunk['constituency'] == 'KAJIADO NORTH']
        north_tot += len(north)

        sex_count_north.update(north['sex'].fillna('MISSING').tolist())
        for a in north['age'].dropna().astype(int).tolist():
            age_counter_north[a] += 1
        ageband_north.update(north['age_band'].tolist())
        caw_count_north.update(north['caw'].fillna('MISSING').tolist())

    # Summaries
    def summarize_counts(counter):
        total = sum(counter.values())
        items = [{'key':k, 'count':v, 'pct': (v/total*100) if total>0 else 0} for k,v in counter.most_common()]
        return total, items

    sex_total_county, sex_items_county = summarize_counts(sex_count_county)
    sex_total_north, sex_items_north = summarize_counts(sex_count_north)

    # Age stats helpers
    def age_stats_from_counter(age_counter):
        ages = sorted(age_counter.items())
        total = sum(v for _,v in ages)
        if total == 0:
            return {'count':0,'mean':None,'median':None}
        # mean
        s = sum(age*v for age,v in ages)
        mean = s/total
        # median from distribution
        cum = 0
        median = None
        for age,v in ages:
            cum += v
            if cum >= total/2:
                median = age
                break
        return {'count':total,'mean':mean,'median':median}

    age_stats_county = age_stats_from_counter(age_counter_county)
    age_stats_north = age_stats_from_counter(age_counter_north)

    # Write summary text
    out_lines = []
    out_lines.append(f"Reference year: {REFERENCE_YEAR}")
    out_lines.append(f"Total records (county): {county_tot}")
    out_lines.append(f"Total records (Kajiado North): {north_tot}")
    out_lines.append("")
    out_lines.append("Sex distribution (county):")
    for it in sex_items_county[:10]:
        out_lines.append(f"  {it['key']}: {it['count']} ({it['pct']:.1f}%)")
    out_lines.append("")
    out_lines.append("Sex distribution (Kajiado North):")
    for it in sex_items_north[:10]:
        out_lines.append(f"  {it['key']}: {it['count']} ({it['pct']:.1f}%)")
    out_lines.append("")
    out_lines.append("Age stats (county):")
    out_lines.append(f"  count: {age_stats_county['count']}, mean: {age_stats_county['mean']:.1f} if age_stats_county['mean'] else 'N/A', median: {age_stats_county['median']}")
    out_lines.append("Age stats (Kajiado North):")
    out_lines.append(f"  count: {age_stats_north['count']}, mean: {age_stats_north['mean']:.1f} if age_stats_north['mean'] else 'N/A', median: {age_stats_north['median']}")

    # Top CAWs
    out_lines.append("")
    out_lines.append("Top 10 CAWs in Kajiado North:")
    for k,v in caw_count_north.most_common(10):
        out_lines.append(f"  {k}: {v}")

    # Age band summaries
    out_lines.append("")
    out_lines.append("Age bands (county):")
    for k,v in ageband_county.most_common():
        out_lines.append(f"  {k}: {v}")
    out_lines.append("")
    out_lines.append("Age bands (Kajiado North):")
    for k,v in ageband_north.most_common():
        out_lines.append(f"  {k}: {v}")

    # Missing
    out_lines.append("")
    out_lines.append("Missing counts by column:")
    for k,v in missing_counts.items():
        out_lines.append(f"  {k}: {v}")

    summary_path = os.path.join(OUTPUT_DIR, 'analysis_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))

    print(f"Wrote summary to {summary_path}")

    # Plots: sex share and age band comparison
    try:
        # Sex share bar chart
        fig, ax = plt.subplots(1,2, figsize=(12,5))
        keys_c, vals_c = zip(*sex_count_county.most_common()) if sex_count_county else ([],[])
        keys_n, vals_n = zip(*sex_count_north.most_common()) if sex_count_north else ([],[])
        ax[0].bar(keys_c, vals_c)
        ax[0].set_title('Sex distribution (county)')
        ax[1].bar(keys_n, vals_n)
        ax[1].set_title('Sex distribution (Kajiado North)')
        plt.tight_layout()
        p1 = os.path.join(OUTPUT_DIR, 'sex_distribution_comparison.png')
        fig.savefig(p1)
        plt.close(fig)

        # Age bands
        fig2, ax2 = plt.subplots(1,2, figsize=(12,5))
        abk_c, abv_c = zip(*sorted(ageband_county.items())) if ageband_county else ([],[])
        abk_n, abv_n = zip(*sorted(ageband_north.items())) if ageband_north else ([],[])
        ax2[0].bar(abk_c, abv_c)
        ax2[0].set_title('Age bands (county)')
        ax2[1].bar(abk_n, abv_n)
        ax2[1].set_title('Age bands (Kajiado North)')
        plt.tight_layout()
        p2 = os.path.join(OUTPUT_DIR, 'ageband_comparison.png')
        fig2.savefig(p2)
        plt.close(fig2)

        print(f"Saved plots to {OUTPUT_DIR}")
    except Exception as e:
        print("Plotting failed:", e)


if __name__ == '__main__':
    process()

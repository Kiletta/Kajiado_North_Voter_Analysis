# Kajiado North Voter Data Analysis Framework

## 1. Purpose
This framework is designed to help you analyze the voter dataset from Kajiado County while focusing specifically on the Kajiado North constituency.

## 2. Dataset scope
The CSV contains voter registration records for Kajiado County. Important fields include:
- `county`
- `constituency`
- `caw` (County Assembly Ward)
- `polling_center`
- `polling_station`
- `pstream`
- `date_of_birth`
- `fname`, `mname`, `sname`
- `sex`
- `id_passport_no`

## 3. Recommended analysis workflow
1. Load the dataset.
2. Clean and standardize fields.
3. Filter data to `constituency == 'KAJIADO NORTH'`.
4. Derive useful columns such as age, full name, and location hierarchy.
5. Run data quality checks.
6. Compute summary statistics and compare Kajiado North against the full county.
7. Visualize results for demographic and geographic patterns.

## 4. Preprocessing and cleaning
### 4.1 Load data
- Use a CSV reader that preserves text values.
- Ensure encoding is correct.

### 4.2 Normalize text fields
- Trim whitespace.
- Convert `county`, `constituency`, `caw`, `polling_center`, `polling_station`, and `sex` to a consistent case.
- Standardize missing values such as `NULL`, empty strings, or whitespace-only values.

### 4.3 Derive new columns
- `full_name` = `fname` + `mname` + `sname`
- `birth_date` = parsed `date_of_birth`
- `birth_year` = year extracted from `birth_date`
- `age` = reference year minus `birth_year` (or exact age if needed)
- `location_key` = combination of `caw`, `polling_center`, `polling_station`, `pstream`

### 4.4 Filter to Kajiado North
- Keep only rows where `constituency` equals `KAJIADO NORTH`.
- Optionally keep county data separately for comparison.

## 5. Data quality checks
### 5.1 Completeness
- Count missing values by column.
- Verify all records in Kajiado North have nonempty `id_passport_no`, `date_of_birth`, and `sex`.

### 5.2 Consistency
- Confirm `constituency` values appear as expected.
- Check for inconsistent ward or polling center names.

### 5.3 Duplicate detection
- Find duplicates using `id_passport_no`.
- Also check duplicates by `full_name + date_of_birth + sex`.

### 5.4 Date validation
- Verify `date_of_birth` can be parsed.
- Flag ages outside a realistic range (e.g. less than 15 or greater than 110).

## 6. Core analysis dimensions
### 6.1 Demographic analysis
- Total registered voters in Kajiado North.
- Sex distribution: Male, Female, other/missing.
- Age distribution and age bands, for example:
  - Under 18
  - 18-24
  - 25-34
  - 35-44
  - 45-54
  - 55-64
  - 65+
- Average and median age.

### 6.2 Geographic analysis
- Voters by CAW.
- Voters by polling center.
- Voters by polling station.
- Voters by `pstream`.
- Top and bottom units by size.
- Location-level sex and age distributions.

### 6.3 Comparative analysis
- Kajiado North vs the rest of Kajiado County.
- Compare district-level voter counts and demographic composition.
- Identify whether Kajiado North has different age or gender patterns.

## 7. Suggested analysis functions
### 7.1 Loading and cleaning
- `load_data(path)`
- `clean_text_fields(df)`
- `parse_birth_dates(df)`
- `derive_age_and_name(df, reference_year)`

### 7.2 Filtering and grouping
- `filter_constituency(df, constituency_name)`
- `group_and_summarize(df, group_keys, metrics)`

### 7.3 Data quality
- `count_missing_values(df)`
- `find_invalid_dates(df)`
- `find_duplicate_ids(df)`

### 7.4 Reporting
- `summary_by_sex(df)`
- `summary_by_age_band(df)`
- `summary_by_location(df, level)`
- `compare_constituency_vs_county(df, constituency_name)`

## 8. Example analysis functions in pseudocode
```python
import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df


def clean_text_fields(df):
    text_cols = ['county','constituency','caw','polling_center','polling_station','sex']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.upper()
    df = df.replace({'NULL': None, '': None})
    return df


def parse_birth_dates(df):
    df['birth_date'] = pd.to_datetime(df['date_of_birth'], dayfirst=True, errors='coerce')
    df['birth_year'] = df['birth_date'].dt.year
    return df


def derive_age(df, reference_year=2026):
    df['age'] = reference_year - df['birth_year']
    return df


def filter_constituency(df, constituency_name='KAJIADO NORTH'):
    return df[df['constituency'] == constituency_name].copy()


def summary_by_location(df, level):
    return df.groupby(level).agg(
        voters=('id_passport_no','count'),
        male=('sex', lambda x: (x=='MALE').sum()),
        female=('sex', lambda x: (x=='FEMALE').sum())
    ).reset_index()
```

## 9. Analysis questions to answer
- How many registered voters are in Kajiado North?
- What is the age profile of Kajiado North voters?
- How balanced is gender representation?
- Which CAWs or polling centers have the largest voter populations?
- Are there any polling stations with unusually low or high voter counts?
- Where are the data quality issues concentrated?

## 10. Visualization and output
- Bar charts for voter counts by CAW and polling center.
- Age pyramid / histogram for Kajiado North.
- Pie chart or bar chart for sex share.
- Tables of top polling stations and wards.
- Data quality dashboard for missing or invalid records.

## 11. Next steps
1. Build the data pipeline using the functions above.
2. Load and inspect the full dataset.
3. Filter to Kajiado North and validate the subset.
4. Generate summaries and visualizations.
5. Iterate on questions as new patterns emerge.

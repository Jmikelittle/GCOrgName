import os
import pandas as pd
from rapidfuzz import process

# Paths to the CSV files
script_folder = os.path.dirname(os.path.abspath(__file__))
rg_data_file = os.path.join(script_folder, 'rg_data.csv')
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
matched_file = os.path.join(script_folder, 'rg_matched.csv')
fixed_file = os.path.join(script_folder, 'rg_fixed.csv')

# Read the CSV files
rg_data_df = pd.read_csv(rg_data_file)
manual_org_df = pd.read_csv(manual_org_file)

# Try to read the fixed file, but create an empty DataFrame if it doesn't exist
try:
    fixed_df = pd.read_csv(fixed_file)
except FileNotFoundError:
    fixed_df = pd.DataFrame(columns=['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'Organization Legal Name English', 'gc_orgID'])

# Extract the relevant columns for matching
rg_names = rg_data_df['rg_dept_en']
manual_org_names = manual_org_df['Organization Legal Name English']

# Function to perform fuzzy matching and return best match and score
def fuzzy_match(name, choices, threshold=80):
    result = process.extractOne(name, choices)
    if result is not None:
        match, score = result[0], result[1]
        if score >= threshold:
            return match, score
    return None, 0

# Perform fuzzy matching for rg_data_df
matches = rg_names.apply(lambda x: fuzzy_match(x, manual_org_names))

# Create a DataFrame with the matching results
match_df = pd.DataFrame({
    'RGOriginalName': rg_names,
    'rgnumber': rg_data_df['rgnumber'],
    'MatchedName': matches.apply(lambda x: x[0]),
    'MatchScore': matches.apply(lambda x: x[1])
})

# Merge the matched names with the manual organization names to get GC OrgID
final_df = match_df.merge(manual_org_df[['Organization Legal Name English', 'gc_orgID']],
                          left_on='MatchedName', right_on='Organization Legal Name English', how='left')

# Ensure 'rgnumber' values do not have decimals
final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)

# Sort by 'MatchedName' and 'MatchScore' in descending order
final_df = final_df.sort_values(by=['MatchedName', 'MatchScore'], ascending=[True, False])

# Remove duplicates based on 'MatchedName', keeping the one with the highest 'MatchScore'
final_df = final_df.drop_duplicates(subset=['MatchedName'], keep='first')

# Reorder columns to ensure 'rgnumber' is the second field
final_df = final_df[['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'gc_orgID']]

# Save the result to a new CSV file (rg_matched.csv)
final_df.to_csv(matched_file, index=False, encoding='utf-8-sig')

print(f"The matched names have been saved to {matched_file}")

# Update rg_fixed.csv with new entries from rg_matched.csv
new_entries = final_df[~final_df['RGOriginalName'].isin(fixed_df['RGOriginalName'])]

# Create a copy to modify for rg_fixed.csv
fixed_entries = new_entries.copy()

# For each entry, get the Organization Legal Name English from manual_org_df based on MatchedName
fixed_entries = fixed_entries.merge(
    manual_org_df[['Organization Legal Name English', 'gc_orgID']],
    left_on='MatchedName',
    right_on='Organization Legal Name English',
    how='left',
    suffixes=('', '_from_match')
)

# Ensure Organization Legal Name English is properly set
# - First, try to use the exact match from 'Organization Legal Name English' as it came from the merge
# - If that's not available (None or empty), use the MatchedName as a fallback
fixed_entries['Organization Legal Name English'] = fixed_entries.apply(
    lambda row: row['Organization Legal Name English'] 
    if pd.notna(row.get('Organization Legal Name English')) and row.get('Organization Legal Name English') != '' 
    else row['MatchedName'],
    axis=1
)

# Clean up any duplicate columns that might have been created
if 'Organization Legal Name English_from_match' in fixed_entries.columns:
    fixed_entries = fixed_entries.drop(columns=['Organization Legal Name English_from_match'])

# Define the expected columns for rg_fixed.csv
fixed_columns = ['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'Organization Legal Name English', 'gc_orgID']

# Ensure all expected columns exist in both DataFrames
for col in fixed_columns:
    if col not in fixed_entries.columns:
        fixed_entries[col] = ""
    if col not in fixed_df.columns:
        fixed_df[col] = ""

# Append new entries to the fixed DataFrame
updated_fixed_df = pd.concat([fixed_df, fixed_entries], ignore_index=True)

# Ensure the columns are in the correct order
updated_fixed_df = updated_fixed_df[fixed_columns]

# Save the updated fixed DataFrame to the CSV file
updated_fixed_df.to_csv(fixed_file, index=False, encoding='utf-8-sig')

print(f"rg_fixed.csv has been updated with new entries from rg_matched.csv")

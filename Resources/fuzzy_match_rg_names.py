import os
import pandas as pd
from rapidfuzz import process

# Paths to the CSV files
script_folder = os.path.dirname(os.path.abspath(__file__))
receiver_general_file = os.path.join(script_folder, 'receiver_general.csv')
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
rg_duplicates_file = os.path.join(script_folder, 'RGDuplicates.csv')
matched_file = os.path.join(script_folder, 'matched_RG_names.csv')
fixed_file = os.path.join(script_folder, 'Fixed_RG_names.csv')

# Read the CSV files
receiver_general_df = pd.read_csv(receiver_general_file)
manual_org_df = pd.read_csv(manual_org_file)
rg_duplicates_df = pd.read_csv(rg_duplicates_file)
fixed_df = pd.read_csv(fixed_file)

# Extract the relevant columns for matching
rg_names = receiver_general_df['RGOriginalName']
manual_org_names = manual_org_df['Organization Legal Name English']
rg_duplicates_names = rg_duplicates_df['Department']

# Function to perform fuzzy matching and return best match and score
def fuzzy_match(name, choices, threshold=80):
    result = process.extractOne(name, choices)
    if result is not None:
        match, score = result[0], result[1]
        if score >= threshold:
            return match, score
    return None, 0

# Perform fuzzy matching for receiver_general_df
matches = rg_names.apply(lambda x: fuzzy_match(x, manual_org_names))

# Create a DataFrame with the matching results
match_df = pd.DataFrame({
    'RGOriginalName': rg_names,
    'rgnumber': receiver_general_df['Number'],
    'MatchedName': matches.apply(lambda x: x[0]),
    'MatchScore': matches.apply(lambda x: x[1])
})

# Perform fuzzy matching for rg_duplicates_df
rg_duplicates_matches = rg_duplicates_names.apply(lambda x: fuzzy_match(x, manual_org_names))

# Create a DataFrame with the matching results for rg_duplicates_df
rg_duplicates_match_df = pd.DataFrame({
    'RG DeptNo': rg_duplicates_df['RG DeptNo'],
    'RGOriginalName': rg_duplicates_names,  # Place 'Department' values into 'RGOriginalName'
    'MatchedName': rg_duplicates_matches.apply(lambda x: x[0]),
    'MatchScore': rg_duplicates_matches.apply(lambda x: x[1])
})

# Merge the matched names with the manual organization names to get GC OrgID
final_df = match_df.merge(manual_org_df[['Organization Legal Name English', 'gc_orgID']],
                          left_on='MatchedName', right_on='Organization Legal Name English', how='left')

# Merge the rg_duplicates_match_df with the manual organization names to get GC OrgID
rg_duplicates_final_df = rg_duplicates_match_df.merge(manual_org_df[['Organization Legal Name English', 'gc_orgID']], 
                                                      left_on='MatchedName', right_on='Organization Legal Name English', how='left')

# Ensure 'rgnumber' values do not have decimals
final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)
rg_duplicates_final_df['RG DeptNo'] = pd.to_numeric(rg_duplicates_final_df['RG DeptNo'], errors='coerce').fillna(0).astype(int)

# Concatenate the two DataFrames
final_df = pd.concat([final_df, rg_duplicates_final_df], ignore_index=True)

# Sort by 'MatchedName' and 'MatchScore' in descending order
final_df = final_df.sort_values(by=['MatchedName', 'MatchScore'], ascending=[True, False])

# Remove duplicates based on 'MatchedName', keeping the one with the highest 'MatchScore'
final_df = final_df.drop_duplicates(subset=['MatchedName'], keep='first')

# Ensure 'rgnumber' values do not have decimals and fill missing 'rgnumber' with 'RG DeptNo'
final_df['rgnumber'] = final_df['rgnumber'].fillna(final_df['RG DeptNo']).astype(int)

# Reorder columns to ensure 'rgnumber' is the second field
final_df = final_df[['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'gc_orgID']]

# Save the result to a new CSV file
final_df.to_csv(matched_file, index=False, encoding='utf-8-sig')

print(f"The matched names have been saved to {matched_file}")

# Update Fixed_RG_names.csv with new entries from matched_RG_names.csv
new_entries = final_df[~final_df['RGOriginalName'].isin(fixed_df['RGOriginalName'])]

# Append new entries to the fixed DataFrame
updated_fixed_df = pd.concat([fixed_df, new_entries], ignore_index=True)

# Save the updated fixed DataFrame to the CSV file
updated_fixed_df.to_csv(fixed_file, index=False, encoding='utf-8-sig')

print("Fixed_RG_names.csv has been updated with new entries from matched_RG_names.csv")

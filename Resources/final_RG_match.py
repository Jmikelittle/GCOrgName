import os
import pandas as pd

# Function to standardize hyphens and apostrophes
def standardize_text(text):
    if pd.isna(text):
        return text
    return text.replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'")

# Get the directory of the current script
script_folder = os.getcwd()

# Paths to the CSV files
matched_file = os.path.join(script_folder, 'Resources', 'matched_RG_names.csv')
fixed_file = os.path.join(script_folder, 'Resources', 'Fixed_RG_names.csv')

# Load the CSV files
matched_df = pd.read_csv(matched_file)
fixed_df = pd.read_csv(fixed_file)

# Standardize hyphens and apostrophes in relevant columns if they exist
for df, columns in [(matched_df, ['RGOriginalName', 'MatchedName']),
                    (fixed_df, ['RGOriginalName', 'Organization Legal Name English'])]:
    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(standardize_text)

# Replace values in 'MatchedName' and 'GC OrgID' when MatchScore is less than 95
for index, row in matched_df.iterrows():
    if row['MatchScore'] < 95:
        fixed_row = fixed_df[fixed_df['RGOriginalName'] == row['RGOriginalName']]
        if not fixed_row.empty:
            matched_df.at[index, 'MatchedName'] = fixed_row['Organization Legal Name English'].values[0]
            matched_df.at[index, 'GC OrgID'] = fixed_row['GC OrgID'].values[0]

# Identify new entries in 'Fixed_RG_names.csv' based on 'GC OrgID'
new_entries = fixed_df[~fixed_df['GC OrgID'].isin(matched_df['GC OrgID'])]

# Append new entries to the matched DataFrame
final_df = pd.concat([matched_df, new_entries], ignore_index=True)

# Set GC OrgID to whole numbers, handling non-finite values
final_df['GC OrgID'] = pd.to_numeric(final_df['GC OrgID'], errors='coerce').fillna(0).astype(int)

# Merge 'rgnumber' field from 'Fixed_RG_names.csv' to 'final_RG_match.csv'
if 'rgnumber' in fixed_df.columns:
    final_df = final_df.merge(fixed_df[['RGOriginalName', 'rgnumber']], on='RGOriginalName', how='left')

# Remove duplicate columns resulting from the merge
final_df = final_df.drop(columns=['rgnumber_y'], errors='ignore')
final_df = final_df.rename(columns={'rgnumber_x': 'rgnumber'}, errors='ignore')

# Reorder columns to ensure 'rgnumber' is the second field if it exists
if 'rgnumber' in final_df.columns:
    columns_order = ['RGOriginalName', 'rgnumber'] + [col for col in final_df.columns if col not in ['RGOriginalName', 'rgnumber']]
    final_df = final_df[columns_order]

# Set rgnumber to whole numbers, handling non-finite values
if 'rgnumber' in final_df.columns:
    final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)

# Round all numeric fields to whole numbers, handling non-finite values before conversion
for col in final_df.select_dtypes(include=['float64', 'int64']).columns:
    final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0).round(0).astype(int)

# Save the updated DataFrame to a new CSV file in the Resources folder
updated_output_file = os.path.join(script_folder, 'Resources', 'final_RG_match.csv')
final_df.to_csv(updated_output_file, index=False, encoding='utf-8-sig')

print(f"The updated matched names have been saved to {updated_output_file}")

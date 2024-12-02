import os
import pandas as pd

# Function to standardize hyphens and apostrophes
def standardize_text(text):
    if pd.isna(text):
        return text
    text = text.replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'")
    return text

# Get the directory of the current script
script_folder = os.getcwd()

# Paths to the CSV files
matched_file = os.path.join(script_folder, 'Resources', 'matched_RG_names.csv')
fixed_file = os.path.join(script_folder, 'Resources', 'Fixed_RG_names.csv')

# Load the matched_RG_names.csv file
matched_df = pd.read_csv(matched_file)

# Load the Fixed_RG_names.csv file
fixed_df = pd.read_csv(fixed_file)

# Standardize hyphens and apostrophes in the relevant columns if they exist
if 'RGOriginalName' in matched_df.columns:
    matched_df['RGOriginalName'] = matched_df['RGOriginalName'].apply(standardize_text)
if 'MatchedName' in matched_df.columns:
    matched_df['MatchedName'] = matched_df['MatchedName'].apply(standardize_text)
if 'RGOriginalName' in fixed_df.columns:
    fixed_df['RGOriginalName'] = fixed_df['RGOriginalName'].apply(standardize_text)
if 'Organization Legal Name English' in fixed_df.columns:
    fixed_df['Organization Legal Name English'] = fixed_df['Organization Legal Name English'].apply(standardize_text)

# Replace values in 'MatchedName' and 'GC OrgID' when MatchScore is less than 95
for index, row in matched_df.iterrows():
    if row['MatchScore'] < 95:
        fixed_row = fixed_df[fixed_df['RGOriginalName'] == row['RGOriginalName']]
        if not fixed_row.empty:
            matched_df.at[index, 'MatchedName'] = fixed_row['Organization Legal Name English'].values[0]
            matched_df.at[index, 'GC OrgID'] = fixed_row['GC OrgID'].values[0]

# Identify new entries in 'Fixed_RG_names.csv' based on 'GC OrgID'
new_entries = fixed_df[~fixed_df['GC OrgID'].isin(matched_df['GC OrgID'])]

# Append these new entries to the matched DataFrame
final_df = pd.concat([matched_df, new_entries], ignore_index=True)

# Set GC OrgID to whole numbers, handling non-finite values
final_df['GC OrgID'] = pd.to_numeric(final_df['GC OrgID'], errors='coerce').fillna(0).astype(int)

# Add the 'rgnumber' field from 'Fixed_RG_names.csv' to 'final_RG_match.csv'
if 'rgnumber' in fixed_df.columns:
    final_df = final_df.merge(fixed_df[['RGOriginalName', 'rgnumber']], on='RGOriginalName', how='left')

# Debugging: Print columns and data types before removing duplicates and rounding numbers
print("Columns before removing duplicates and rounding numbers:")
print(final_df.columns)
print("Data types before removing duplicates and rounding numbers:")
print(final_df.dtypes)

# Remove any duplicate columns resulting from the merge (e.g., rgnumber_x, rgnumber_y)
if 'rgnumber_y' in final_df.columns:
    final_df = final_df.drop(columns=['rgnumber_y'])

# Rename rgnumber_x to rgnumber if it exists
if 'rgnumber_x' in final_df.columns:
    final_df = final_df.rename(columns={'rgnumber_x': 'rgnumber'})

# Debugging: Print columns after removing duplicates and renaming
print("Columns after removing duplicates and renaming:")
print(final_df.columns)

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

# Debugging: Print columns and data types after rounding numbers
print("Columns after rounding numbers:")
print(final_df.columns)
print("Data types after rounding numbers:")
print(final_df.dtypes)

# Save the updated DataFrame to a new CSV file in the Resources folder
updated_output_file = os.path.join(script_folder, 'Resources', 'final_RG_match.csv')
final_df.to_csv(updated_output_file, index=False, encoding='utf-8-sig')

print(f"The updated matched names have been saved to {updated_output_file}")

import os
import pandas as pd

# Enable debugging
DEBUG = True

def debug_print(message):
    if DEBUG:
        print(f"DEBUG: {message}")

# Function to standardize hyphens and apostrophes
def standardize_text(text):
    if pd.isna(text):
        debug_print(f"standardize_text received NA value")
        return text
    debug_print(f"standardizing: '{text}'")
    standardized = text.replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'")
    if standardized != text:
        debug_print(f"text standardized to: '{standardized}'")
    return standardized

# Get the directory of the current script
script_folder = os.getcwd()
debug_print(f"Script folder: {script_folder}")

# Paths to the CSV files
matched_file = os.path.join(script_folder, 'Resources', 'rg_matched.csv')
fixed_file = os.path.join(script_folder, 'Resources', 'rg_fixed.csv')
debug_print(f"Matched file: {matched_file}")
debug_print(f"Fixed file: {fixed_file}")

# Load the CSV files
try:
    matched_df = pd.read_csv(matched_file)
    debug_print(f"Matched data loaded with {len(matched_df)} rows")
    debug_print(f"Matched data columns: {list(matched_df.columns)}")
    debug_print(f"Sample matched data: {matched_df.head(3).to_dict('records')}")
except Exception as e:
    debug_print(f"Error loading matched file: {str(e)}")
    raise

try:
    fixed_df = pd.read_csv(fixed_file)
    debug_print(f"Fixed data loaded with {len(fixed_df)} rows")
    debug_print(f"Fixed data columns: {list(fixed_df.columns)}")
    debug_print(f"Sample fixed data: {fixed_df.head(3).to_dict('records')}")
except Exception as e:
    debug_print(f"Error loading fixed file: {str(e)}")
    raise

# Standardize hyphens and apostrophes in relevant columns if they exist
debug_print("Standardizing text in dataframes...")
for df_name, df, columns in [
    ("matched_df", matched_df, ['RGOriginalName', 'MatchedName']),
    ("fixed_df", fixed_df, ['RGOriginalName', 'MatchedName', 'Organization Legal Name English'])
]:
    for column in columns:
        if column in df.columns:
            debug_print(f"Standardizing {df_name}.{column}")
            df[column] = df[column].apply(standardize_text)
        else:
            debug_print(f"Column {column} not found in {df_name}")

# Check if Organization Legal Name English exists in fixed_df
if 'Organization Legal Name English' in fixed_df.columns:
    debug_print("Organization Legal Name English column found in fixed_df")
    debug_print(f"Null values: {fixed_df['Organization Legal Name English'].isna().sum()}")
    debug_print(f"Empty strings: {(fixed_df['Organization Legal Name English'] == '').sum()}")
    if not fixed_df.empty:
        debug_print(f"Sample values: {fixed_df['Organization Legal Name English'].head().tolist()}")
else:
    debug_print("ERROR: Organization Legal Name English column NOT found in fixed_df")

# Replace values in 'MatchedName' and 'gc_orgID' when MatchScore is less than 95
debug_print("Replacing poor matches with fixed data...")
replacements_made = 0
for index, row in matched_df.iterrows():
    if row['MatchScore'] < 95:
        debug_print(f"Low score ({row['MatchScore']}) for '{row['RGOriginalName']}'")
        fixed_row = fixed_df[fixed_df['RGOriginalName'] == row['RGOriginalName']]
        if not fixed_row.empty:
            debug_print(f"Found in fixed_df: {fixed_row[['RGOriginalName', 'MatchedName', 'gc_orgID']].iloc[0].to_dict()}")
            matched_df.at[index, 'MatchedName'] = fixed_row['MatchedName'].values[0]
            matched_df.at[index, 'gc_orgID'] = fixed_row['gc_orgID'].values[0]
            replacements_made += 1
        else:
            debug_print(f"Not found in fixed_df")

debug_print(f"Made {replacements_made} replacements from fixed data")

# Identify new entries in rg_fixed.csv based on 'gc_orgID'
new_entries = fixed_df[~fixed_df['gc_orgID'].isin(matched_df['gc_orgID'])]
debug_print(f"Found {len(new_entries)} new entries in fixed_df not in matched_df")

# Append new entries to the matched DataFrame
final_df = pd.concat([matched_df, new_entries], ignore_index=True)
debug_print(f"Combined final_df has {len(final_df)} rows")

# Set gc_orgID to whole numbers, handling non-finite values
debug_print("Converting gc_orgID to integers...")
final_df['gc_orgID'] = pd.to_numeric(final_df['gc_orgID'], errors='coerce').fillna(0).astype(int)

# Merge 'rgnumber' field from rg_fixed.csv to final_RG_match.csv
if 'rgnumber' in fixed_df.columns:
    debug_print("Merging rgnumber from fixed_df...")
    before_merge = len(final_df)
    final_df = final_df.merge(fixed_df[['RGOriginalName', 'rgnumber']], on='RGOriginalName', how='left')
    after_merge = len(final_df)
    debug_print(f"Merge resulted in {after_merge} rows (was {before_merge})")
else:
    debug_print("rgnumber column not found in fixed_df")

# Check for duplicate columns after merge
duplicate_cols = [col for col in final_df.columns if col.endswith('_x') or col.endswith('_y')]
if duplicate_cols:
    debug_print(f"Found duplicate columns after merge: {duplicate_cols}")

# Remove duplicate columns resulting from the merge
if 'rgnumber_y' in final_df.columns:
    debug_print("Dropping rgnumber_y column")
    final_df = final_df.drop(columns=['rgnumber_y'])
if 'rgnumber_x' in final_df.columns:
    debug_print("Renaming rgnumber_x to rgnumber")
    final_df = final_df.rename(columns={'rgnumber_x': 'rgnumber'})

# Reorder columns to ensure 'rgnumber' is the second field if it exists
if 'rgnumber' in final_df.columns:
    debug_print("Reordering columns to put rgnumber second")
    columns_order = ['RGOriginalName', 'rgnumber'] + [col for col in final_df.columns if col not in ['RGOriginalName', 'rgnumber']]
    final_df = final_df[columns_order]
    debug_print(f"New column order: {list(final_df.columns)}")

# Set rgnumber to whole numbers, handling non-finite values
if 'rgnumber' in final_df.columns:
    debug_print("Converting rgnumber to integers...")
    final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)

# Round all numeric fields to whole numbers, handling non-finite values before conversion
debug_print("Rounding all numeric fields...")
for col in final_df.select_dtypes(include=['float64', 'int64']).columns:
    debug_print(f"Processing numeric column: {col}")
    final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0).round(0).astype(int)

# Final check on data
debug_print("Final check of data:")
debug_print(f"Final dataframe has {len(final_df)} rows and columns: {list(final_df.columns)}")
if 'Organization Legal Name English' in final_df.columns:
    debug_print(f"Organization Legal Name English column is present")
    debug_print(f"Null values: {final_df['Organization Legal Name English'].isna().sum()}")
    debug_print(f"Empty strings: {(final_df['Organization Legal Name English'] == '').sum() if '' in final_df['Organization Legal Name English'].values else 0}")
else:
    debug_print("Organization Legal Name English column is NOT present in final output")

# Save the updated DataFrame to a new CSV file in the Resources folder
updated_output_file = os.path.join(script_folder, 'Resources', 'rg_final.csv')
debug_print(f"Saving final result to {updated_output_file}")
final_df.to_csv(updated_output_file, index=False, encoding='utf-8-sig')

print(f"The updated matched names have been saved to {updated_output_file}")

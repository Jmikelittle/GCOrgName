import os
import pandas as pd
from rapidfuzz import process

# Enable debugging
DEBUG = True

def debug_print(message):
    if DEBUG:
        print(f"DEBUG: {message}")

# Paths to the CSV files
script_folder = os.path.dirname(os.path.abspath(__file__))
rg_data_file = os.path.join(script_folder, 'rg_data.csv')
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
matched_file = os.path.join(script_folder, 'rg_matched.csv')
fixed_file = os.path.join(script_folder, 'rg_fixed.csv')

debug_print(f"Script folder: {script_folder}")
debug_print(f"RG data file: {rg_data_file}")
debug_print(f"Manual org file: {manual_org_file}")

# Read the CSV files
rg_data_df = pd.read_csv(rg_data_file)
debug_print(f"RG data loaded with {len(rg_data_df)} rows")
debug_print(f"RG data columns: {list(rg_data_df.columns)}")

manual_org_df = pd.read_csv(manual_org_file)
debug_print(f"Manual org data loaded with {len(manual_org_df)} rows")
debug_print(f"Manual org columns: {list(manual_org_df.columns)}")
debug_print(f"First 5 organization names: {manual_org_df['Organization Legal Name English'].head().tolist()}")

# Try to read the fixed file, but create an empty DataFrame if it doesn't exist
try:
    fixed_df = pd.read_csv(fixed_file)
    debug_print(f"Fixed data loaded with {len(fixed_df)} rows")
    debug_print(f"Fixed data columns: {list(fixed_df.columns)}")
except FileNotFoundError:
    debug_print("Fixed file not found, creating empty DataFrame")
    fixed_df = pd.DataFrame(columns=['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'Organization Legal Name English', 'gc_orgID'])

# Extract the relevant columns for matching
rg_names = rg_data_df['rg_dept_en']
manual_org_names = manual_org_df['Organization Legal Name English']

# Function to perform fuzzy matching and return best match and score
def fuzzy_match(name, choices, threshold=80):
    if pd.isna(name) or name == "":
        debug_print(f"Empty name provided to fuzzy_match")
        return None, 0
    
    debug_print(f"Fuzzy matching: '{name}'")
    result = process.extractOne(name, choices)
    if result is not None:
        match, score = result[0], result[1]
        debug_print(f"Match found: '{match}' with score {score}")
        if score >= threshold:
            return match, score
        else:
            debug_print(f"Score below threshold ({threshold})")
    else:
        debug_print("No match found")
    return None, 0

# Perform fuzzy matching for rg_data_df
debug_print("Starting fuzzy matching process...")
matches = rg_names.apply(lambda x: fuzzy_match(x, manual_org_names))
debug_print(f"Completed fuzzy matching: {len(matches)} results")

# Create a DataFrame with the matching results
match_df = pd.DataFrame({
    'RGOriginalName': rg_names,
    'rgnumber': rg_data_df['rgnumber'],
    'MatchedName': matches.apply(lambda x: x[0]),
    'MatchScore': matches.apply(lambda x: x[1])
})
debug_print(f"Created match_df with {len(match_df)} rows")
debug_print(f"Match_df columns: {list(match_df.columns)}")
debug_print(f"Sample of matches: {match_df[['RGOriginalName', 'MatchedName', 'MatchScore']].head().to_dict('records')}")

# Function to look up Organization Legal Name English and gc_orgID from manual_org_df
def lookup_org_details(matched_name):
    if pd.isna(matched_name) or matched_name == "":
        debug_print(f"Empty matched_name provided to lookup_org_details")
        return None, None
    
    debug_print(f"Looking up details for: '{matched_name}'")
    
    # First try exact match
    match_row = manual_org_df[manual_org_df['Organization Legal Name English'] == matched_name]
    
    if not match_row.empty:
        org_name = match_row['Organization Legal Name English'].iloc[0]
        org_id = match_row['gc_orgID'].iloc[0]
        debug_print(f"Found exact match: name='{org_name}', id={org_id}")
        return org_name, org_id
    
    # If no exact match, try a fuzzy match with a high threshold
    debug_print(f"No exact match found, trying fuzzy match")
    best_match = process.extractOne(matched_name, manual_org_df['Organization Legal Name English'])
    if best_match and best_match[1] > 95:  # High confidence threshold
        match_name = best_match[0]
        match_row = manual_org_df[manual_org_df['Organization Legal Name English'] == match_name]
        if not match_row.empty:
            org_name = match_row['Organization Legal Name English'].iloc[0]
            org_id = match_row['gc_orgID'].iloc[0]
            debug_print(f"Found fuzzy match: name='{org_name}', id={org_id}, score={best_match[1]}")
            return org_name, org_id
    
    debug_print(f"No match found in manual_org_df for '{matched_name}'")
    return matched_name, None  # Return the matched_name as fallback for org_name

# Apply the lookup function to get Organization Legal Name English and gc_orgID
debug_print("Looking up organization details...")
org_details = match_df['MatchedName'].apply(lookup_org_details)
debug_print(f"Completed organization detail lookup: {len(org_details)} results")

match_df['Organization Legal Name English'] = org_details.apply(lambda x: x[0] if x is not None else None)
match_df['gc_orgID'] = org_details.apply(lambda x: x[1] if x is not None else None)

# Make a special check for matches with no gc_orgID
debug_print("Checking for matches with no gc_orgID...")
for i, row in match_df.iterrows():
    if pd.isna(row['gc_orgID']) or row['gc_orgID'] == "":
        debug_print(f"Row {i} has no gc_orgID: {row['RGOriginalName']} -> {row['MatchedName']}")
        # Look for the matched name directly in manual_org_df
        try:
            closest_match = process.extractOne(row['MatchedName'], manual_org_df['Organization Legal Name English'])
            if closest_match and closest_match[1] >= 95:
                match_name = closest_match[0]
                debug_print(f"Found close match: {match_name} with score {closest_match[1]}")
                match_row = manual_org_df[manual_org_df['Organization Legal Name English'] == match_name]
                if not match_row.empty:
                    debug_print(f"Setting Organization Legal Name English to {match_name}")
                    match_df.at[i, 'Organization Legal Name English'] = match_name
                    match_df.at[i, 'gc_orgID'] = match_row['gc_orgID'].iloc[0]
        except Exception as e:
            debug_print(f"Error during closest match lookup: {str(e)}")

# Count how many records have Organization Legal Name English populated after additional check
debug_print(f"Records with 'Organization Legal Name English' populated after additional check: {match_df['Organization Legal Name English'].notna().sum()}")
debug_print(f"Records with 'gc_orgID' populated after additional check: {match_df['gc_orgID'].notna().sum()}")

# Count how many records have Organization Legal Name English populated
debug_print(f"Records with 'Organization Legal Name English' populated: {match_df['Organization Legal Name English'].notna().sum()}")
debug_print(f"Records with 'gc_orgID' populated: {match_df['gc_orgID'].notna().sum()}")

# Identify records with missing Organization Legal Name English
missing_org_names = match_df[match_df['Organization Legal Name English'].isna()]
if not missing_org_names.empty:
    debug_print(f"Example of records with missing Organization Legal Name English:")
    debug_print(missing_org_names[['RGOriginalName', 'MatchedName', 'MatchScore']].head().to_dict('records'))

# Create final_df from match_df
final_df = match_df.copy()

# Ensure 'rgnumber' values do not have decimals
final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)

# Sort by 'MatchedName' and 'MatchScore' in descending order
final_df = final_df.sort_values(by=['MatchedName', 'MatchScore'], ascending=[True, False])

# Remove duplicates based on 'MatchedName', keeping the one with the highest 'MatchScore'
before_dedup = len(final_df)
final_df = final_df.drop_duplicates(subset=['MatchedName'], keep='first')
after_dedup = len(final_df)
debug_print(f"Removed {before_dedup - after_dedup} duplicate matches")

# Reorder columns for rg_matched.csv
matched_columns = ['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'gc_orgID']
final_df_matched = final_df[matched_columns]
debug_print(f"Prepared final_df_matched with {len(final_df_matched)} rows and columns: {list(final_df_matched.columns)}")

# Save the result to rg_matched.csv
final_df_matched.to_csv(matched_file, index=False, encoding='utf-8-sig')
debug_print(f"Saved matched data to {matched_file}")

# Update rg_fixed.csv with new entries from rg_matched.csv
new_entries = final_df[~final_df['RGOriginalName'].isin(fixed_df['RGOriginalName'])]
debug_print(f"Found {len(new_entries)} new entries to add to fixed file")

# Create a copy to modify for rg_fixed.csv
fixed_entries = new_entries.copy()
debug_print(f"Created fixed_entries with {len(fixed_entries)} rows")

# Check and report on 'Organization Legal Name English' field before processing
debug_print(f"Organization Legal Name English field before processing:")
debug_print(f"Null values: {fixed_entries['Organization Legal Name English'].isna().sum()}")
debug_print(f"Empty strings: {(fixed_entries['Organization Legal Name English'] == '').sum()}")
if not fixed_entries.empty:
    debug_print(f"Sample values: {fixed_entries['Organization Legal Name English'].head().tolist()}")

# Ensure Organization Legal Name English is set properly in fixed_entries
debug_print("Ensuring Organization Legal Name English is set properly...")

# First, let's make sure fixed_entries has the column
if 'Organization Legal Name English' not in fixed_entries.columns:
    debug_print("Adding missing 'Organization Legal Name English' column to fixed_entries")
    fixed_entries['Organization Legal Name English'] = None

# Process each row to ensure Organization Legal Name English is populated
for i, row in fixed_entries.iterrows():
    debug_print(f"Processing row {i}: '{row['RGOriginalName']}' -> '{row['MatchedName']}'")
    
    # Try to find organization name in manual_org_df using MatchedName
    if not pd.isna(row['MatchedName']) and row['MatchedName'] != "":
        matched_name = row['MatchedName']
        
        # First try direct lookup
        direct_match = manual_org_df[manual_org_df['Organization Legal Name English'] == matched_name]
        if not direct_match.empty:
            org_name = direct_match['Organization Legal Name English'].iloc[0]
            org_id = direct_match['gc_orgID'].iloc[0]
            debug_print(f"  Found direct match: '{org_name}', id={org_id}")
            fixed_entries.at[i, 'Organization Legal Name English'] = org_name
            fixed_entries.at[i, 'gc_orgID'] = org_id
            continue
            
        # If no direct match, try fuzzy match
        try:
            closest_match = process.extractOne(matched_name, manual_org_df['Organization Legal Name English'])
            if closest_match and closest_match[1] >= 90:  # Lower threshold to catch more
                org_name = closest_match[0]
                debug_print(f"  Found fuzzy match: '{org_name}' with score {closest_match[1]}")
                match_row = manual_org_df[manual_org_df['Organization Legal Name English'] == org_name]
                if not match_row.empty:
                    fixed_entries.at[i, 'Organization Legal Name English'] = org_name
                    fixed_entries.at[i, 'gc_orgID'] = match_row['gc_orgID'].iloc[0]
                    continue
        except Exception as e:
            debug_print(f"  Error during fuzzy match: {str(e)}")
    
    # If we still don't have Organization Legal Name English, use MatchedName as fallback
    if pd.isna(fixed_entries.at[i, 'Organization Legal Name English']) or fixed_entries.at[i, 'Organization Legal Name English'] == "":
        debug_print(f"  Using MatchedName as fallback")
        fixed_entries.at[i, 'Organization Legal Name English'] = row['MatchedName']

# Check and report on 'Organization Legal Name English' field after processing
debug_print(f"Organization Legal Name English field after processing:")
debug_print(f"Null values: {fixed_entries['Organization Legal Name English'].isna().sum()}")
debug_print(f"Empty strings: {(fixed_entries['Organization Legal Name English'] == '').sum() if '' in fixed_entries['Organization Legal Name English'].values else 0}")
if not fixed_entries.empty:
    debug_print(f"Sample values: {fixed_entries['Organization Legal Name English'].head().tolist()}")

# Make a final pass to ensure no null values remain
fixed_entries['Organization Legal Name English'] = fixed_entries.apply(
    lambda row: row['MatchedName'] if pd.isna(row['Organization Legal Name English']) or row['Organization Legal Name English'] == "" else row['Organization Legal Name English'],
    axis=1
)

# Define the expected columns for rg_fixed.csv
fixed_columns = ['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'Organization Legal Name English', 'gc_orgID']

# Ensure all expected columns exist in both DataFrames
for col in fixed_columns:
    if col not in fixed_entries.columns:
        debug_print(f"Adding missing column '{col}' to fixed_entries")
        fixed_entries[col] = ""
    if col not in fixed_df.columns:
        debug_print(f"Adding missing column '{col}' to fixed_df")
        fixed_df[col] = ""

# Append new entries to the fixed DataFrame
updated_fixed_df = pd.concat([fixed_df, fixed_entries], ignore_index=True)
debug_print(f"Updated fixed_df now has {len(updated_fixed_df)} rows")

# Ensure the columns are in the correct order
updated_fixed_df = updated_fixed_df[fixed_columns]
debug_print(f"Fixed columns final order: {list(updated_fixed_df.columns)}")

# Save the updated fixed DataFrame to the CSV file
updated_fixed_df.to_csv(fixed_file, index=False, encoding='utf-8-sig')
debug_print(f"Saved fixed data to {fixed_file}")

print(f"The matched names have been saved to {matched_file}")
print(f"rg_fixed.csv has been updated with new entries from rg_matched.csv")

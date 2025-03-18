import os
import pandas as pd
from rapidfuzz import process

# Paths to the CSV files
script_folder = os.path.dirname(os.path.abspath(__file__))
receiver_general_file = os.path.join(script_folder, 'receiver_general.csv')
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
# rg_duplicates_file = os.path.join(script_folder, 'RGDuplicates.csv')  # Commented out
matched_file = os.path.join(script_folder, 'matched_RG_names.csv')
fixed_file = os.path.join(script_folder, 'Fixed_RG_names.csv')

# Read the CSV files
receiver_general_df = pd.read_csv(receiver_general_file)
manual_org_df = pd.read_csv(manual_org_file)
# rg_duplicates_df = pd.read_csv(rg_duplicates_file)  # Commented out
fixed_df = pd.read_csv(fixed_file)

# Extract the relevant columns for matching
rg_names = receiver_general_df['RGOriginalName']
manual_org_names = manual_org_df['Organization Legal Name English']
# rg_duplicates_names = rg_duplicates_df['Department']  # Commented out

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

# Commenting out the RG duplicates matching section
"""
# Perform fuzzy matching for rg_duplicates_df
rg_duplicates_matches = rg_duplicates_names.apply(lambda x: fuzzy_match(x, manual_org_names))

# Create a DataFrame with the matching results for rg_duplicates_df
rg_duplicates_match_df = pd.DataFrame({
    'RG DeptNo': rg_duplicates_df['RG DeptNo'],
    'RGOriginalName': rg_duplicates_names,  # Place 'Department' values into 'RGOriginalName'
    'MatchedName': rg_duplicates_matches.apply(lambda x: x[0]),
    'MatchScore': rg_duplicates_matches.apply(lambda x: x[1])
})
"""

# Merge the matched names with the manual organization names to get GC OrgID
final_df = match_df.merge(manual_org_df[['Organization Legal Name English', 'gc_orgID']],
                          left_on='MatchedName', right_on='Organization Legal Name English', how='left')

# Commenting out the RG duplicates merging section
"""
# Merge the rg_duplicates_match_df with the manual organization names to get GC OrgID
rg_duplicates_final_df = rg_duplicates_match_df.merge(manual_org_df[['Organization Legal Name English', 'gc_orgID']], 
                                                      left_on='MatchedName', right_on='Organization Legal Name English', how='left')
"""

# Ensure 'rgnumber' values do not have decimals
final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)
# rg_duplicates_final_df['RG DeptNo'] = pd.to_numeric(rg_duplicates_final_df['RG DeptNo'], errors='coerce').fillna(0).astype(int)  # Commented out

# Commenting out the concatenation of the two DataFrames
# final_df = pd.concat([final_df, rg_duplicates_final_df], ignore_index=True)  # Commented out

# Sort by 'MatchedName' and 'MatchScore' in descending order
final_df = final_df.sort_values(by=['MatchedName', 'MatchScore'], ascending=[True, False])

# Remove duplicates based on 'MatchedName', keeping the one with the highest 'MatchScore'
final_df = final_df.drop_duplicates(subset=['MatchedName'], keep='first')

# Ensure rgnumber is an integer
final_df['rgnumber'] = pd.to_numeric(final_df['rgnumber'], errors='coerce').fillna(0).astype(int)

# Reorder columns to ensure 'rgnumber' is the second field
final_df = final_df[['RGOriginalName', 'rgnumber', 'MatchedName', 'MatchScore', 'gc_orgID']]

# Sort by rgnumber, placing 0s at the top, then sorting ascending
final_df['sort_key'] = (final_df['rgnumber'] != 0).astype(int)  # 0 for rgnumber=0, 1 for others
final_df = final_df.sort_values(by=['sort_key', 'rgnumber'], ascending=[True, True])
final_df = final_df.drop(columns=['sort_key'])  # Remove temporary sort column

# Save the result to a new CSV file
final_df.to_csv(matched_file, index=False, encoding='utf-8-sig')

print(f"The matched names have been saved to {matched_file}")

# Update Fixed_RG_names.csv with new entries from matched_RG_names.csv
new_entries = final_df[~final_df['RGOriginalName'].isin(fixed_df['RGOriginalName'])]

# Append new entries to the fixed DataFrame
updated_fixed_df = pd.concat([fixed_df, new_entries], ignore_index=True)

# Create a set of original RG names from receiver_general_df for quick lookup
original_rg_names = set(receiver_general_df['RGOriginalName'])

# Ensure rgnumber is properly updated for all records in fixed_df
if 'rgnumber' in updated_fixed_df.columns:
    # Create a mapping of RGOriginalName to rgnumber from final_df
    rgnumber_mapping = dict(zip(final_df['RGOriginalName'], final_df['rgnumber']))
    
    # Update rgnumber in updated_fixed_df based on the mapping
    for index, row in updated_fixed_df.iterrows():
        if row['RGOriginalName'] in rgnumber_mapping:
            updated_fixed_df.at[index, 'rgnumber'] = rgnumber_mapping[row['RGOriginalName']]
        
        # Reset rgnumber to 0 if the RGOriginalName is not in the original receiver_general.csv
        # This will BREAK duplicates if you want duplicates
        if row['RGOriginalName'] not in original_rg_names:
            updated_fixed_df.at[index, 'rgnumber'] = 0
    
    # Ensure rgnumber is an integer
    updated_fixed_df['rgnumber'] = pd.to_numeric(updated_fixed_df['rgnumber'], errors='coerce').fillna(0).astype(int)
    
    # Sort by rgnumber, placing 0s at the top, then sorting ascending
    updated_fixed_df['sort_key'] = (updated_fixed_df['rgnumber'] != 0).astype(int)
    updated_fixed_df = updated_fixed_df.sort_values(by=['sort_key', 'rgnumber'], ascending=[True, True])
    updated_fixed_df = updated_fixed_df.drop(columns=['sort_key'])  # Remove temporary sort column

# Save the updated fixed DataFrame to the CSV file
updated_fixed_df.to_csv(fixed_file, index=False, encoding='utf-8-sig')

print("Fixed_RG_names.csv has been updated with new entries from matched_RG_names.csv")
print("Entries not in the original receiver_general.csv have had their rgnumber set to 0")

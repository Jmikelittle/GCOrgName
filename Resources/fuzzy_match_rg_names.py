import os
import pandas as pd
from fuzzywuzzy import process

# Paths to the CSV files
script_folder = os.path.dirname(os.path.abspath(__file__))
receiver_general_file = os.path.join(script_folder, 'receiver_general.csv')
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
output_file = os.path.join(script_folder, 'matched_RG_names.csv')

# Read the CSV files
receiver_general_df = pd.read_csv(receiver_general_file)
manual_org_df = pd.read_csv(manual_org_file)

# Extract the relevant columns for matching
rg_names = receiver_general_df['RGOriginalName']
manual_org_names = manual_org_df['Organization Legal Name English']

# Function to perform fuzzy matching and return best match and score
def fuzzy_match(name, choices, threshold=80):
    result = process.extractOne(name, choices)
    if result is not None:
        match, score = result[0], result[1]
        if score >= threshold:
            return match, score
    return None, 0

# Perform fuzzy matching
matches = rg_names.apply(lambda x: fuzzy_match(x, manual_org_names))

# Create a DataFrame with the matching results
match_df = pd.DataFrame({
    'RGOriginalName': rg_names,
    'MatchedName': matches.apply(lambda x: x[0]),
    'MatchScore': matches.apply(lambda x: x[1])
})

# Merge the matched names with the manual organization names to get GC OrgID
final_df = match_df.merge(manual_org_df[['Organization Legal Name English', 'GC OrgID']], 
                          left_on='MatchedName', right_on='Organization Legal Name English', how='left')

# Save the result to a new CSV file
final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"The matched names have been saved to {output_file}")

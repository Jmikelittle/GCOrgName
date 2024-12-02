import os
import pandas as pd

# Function to standardize hyphens and apostrophes
def standardize_text(text):
    if pd.isna(text):
        return text
    text = text.replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'")
    return text

# Get the directory of the current script
script_folder = os.path.dirname(os.path.abspath(__file__))

# Paths to the CSV files
matched_file = os.path.join(script_folder, 'matched_RG_names.csv')
fixed_file = os.path.join(script_folder, 'Fixed_RG_names.csv')

# Load the matched_RG_names.csv file
matched_df = pd.read_csv(matched_file)

# Load the Fixed_RG_names.csv file
fixed_df = pd.read_csv(fixed_file)

# Standardize hyphens and apostrophes in the relevant columns
matched_df['RGOriginalName'] = matched_df['RGOriginalName'].apply(standardize_text)
matched_df['Organization Legal Name English'] = matched_df['Organization Legal Name English'].apply(standardize_text)
fixed_df['RGOriginalName'] = fixed_df['RGOriginalName'].apply(standardize_text)
fixed_df['Organization Legal Name English'] = fixed_df['Organization Legal Name English'].apply(standardize_text)

# Replace values in 'Organization Legal Name English' and 'GC OrgID' when MatchScore is less than 95
for index, row in matched_df.iterrows():
    if row['MatchScore'] < 95:
        fixed_row = fixed_df[fixed_df['RGOriginalName'] == row['RGOriginalName']]
        if not fixed_row.empty:
            matched_df.at[index, 'Organization Legal Name English'] = fixed_row['Organization Legal Name English'].values[0]
            matched_df.at[index, 'GC OrgID'] = fixed_row['GC OrgID'].values[0]

# Identify new entries in 'Fixed_RG_names.csv' based on 'GC OrgID'
new_entries = fixed_df[~fixed_df['GC OrgID'].isin(matched_df['GC OrgID'])]

# Append these new entries to the matched DataFrame
final_df = pd.concat([matched_df, new_entries], ignore_index=True)

# Set GC OrgID to whole numbers, handling non-finite values
final_df['GC OrgID'] = pd.to_numeric(final_df['GC OrgID'], errors='coerce').fillna(0).astype(int)

# Save the updated DataFrame to a new CSV file
updated_output_file = os.path.join(script_folder, 'final_RG_match.csv')
final_df.to_csv(updated_output_file, index=False, encoding='utf-8-sig')

print(f"The updated matched names have been saved to {updated_output_file}")

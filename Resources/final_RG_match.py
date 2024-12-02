import os
import pandas as pd

# Get the directory of the current script
script_folder = os.path.dirname(os.path.abspath(__file__))

# Paths to the CSV files
matched_file = os.path.join(script_folder, 'matched_RG_names.csv')
fixed_file = os.path.join(script_folder, 'Fixed_RG_names.csv')

# Load the matched_RG_names.csv file
matched_df = pd.read_csv(matched_file)

# Load the Fixed_RG_names.csv file
fixed_df = pd.read_csv(fixed_file)

# Replace values in 'Organization Legal Name English' and 'GC OrgID' when MatchScore is less than 95
for index, row in matched_df.iterrows():
    if row['MatchScore'] < 95:
        fixed_row = fixed_df[fixed_df['RGOriginalName'] == row['RGOriginalName']]
        if not fixed_row.empty:
            matched_df.at[index, 'Organization Legal Name English'] = fixed_row['Organization Legal Name English'].values[0]
            matched_df.at[index, 'GC OrgID'] = fixed_row['GC OrgID'].values[0]

# Save the updated DataFrame to a new CSV file
updated_output_file = os.path.join(script_folder, 'final_RG_match.csv')
matched_df.to_csv(updated_output_file, index=False, encoding='utf-8-sig')

print(f"The updated matched names have been saved to {updated_output_file}")

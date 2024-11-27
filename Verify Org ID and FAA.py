import os
import pandas as pd

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))

# Paths to the CSV files
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
combined_faa_file = os.path.join(script_folder, 'Scraping', 'combined_FAA_names.csv')
applied_en_file = os.path.join(script_folder, 'applied_en.csv')

# Read the CSV files
manual_org_df = pd.read_csv(manual_org_file)
combined_faa_df = pd.read_csv(combined_faa_file)
applied_en_df = pd.read_csv(applied_en_file)

# Remove the 'Unnamed: 0' field if it exists
if 'Unnamed: 0' in combined_faa_df.columns:
    combined_faa_df = combined_faa_df.drop(columns=['Unnamed: 0'])

# Function to replace typographic apostrophes and non-breaking hyphens with standard ones
def standardize_text(df):
    return df.apply(lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() if x.dtype == "object" else x)

# Apply the function to all dataframes
manual_org_df = standardize_text(manual_org_df)
combined_faa_df = standardize_text(combined_faa_df)
applied_en_df = standardize_text(applied_en_df)

# Preserve the original 'English Name' column
combined_faa_df['Original English Name'] = combined_faa_df['English Name']

# Rename the column in combined_faa_df to match the manual_org_df for joining
combined_faa_df = combined_faa_df.rename(columns={'English Name': 'Organization Legal Name English'})

# Perform an outer join on the 'Organization Legal Name English' column
joined_df = pd.merge(manual_org_df, combined_faa_df, on='Organization Legal Name English', how='outer')

# Add a binary column where 1 means names don't match, and 0 means names do match
joined_df['Names Match'] = joined_df.apply(
    lambda row: 0 if pd.notna(row['Organization Legal Name English']) else 1, axis=1
)

# Separate unmatched values into a different DataFrame
unmatched_values = joined_df[joined_df['Names Match'] == 1]

# Remove unmatched values from the joined DataFrame
joined_df = joined_df[joined_df['Names Match'] == 0]

# Join with applied_en_df on 'Legal title' and 'Organization Legal Name English'
final_joined_df = pd.merge(joined_df, applied_en_df, left_on='Organization Legal Name English', right_on='Legal title', how='outer')

# Sort the final joined DataFrame alphabetically based on the 'Organization Legal Name English' field
final_joined_df = final_joined_df.sort_values(by='Organization Legal Name English')

# Save the final joined DataFrame to a new CSV file with UTF-8 encoding
output_file = os.path.join(script_folder, 'verify org ID with FAA and applied_en.csv')
final_joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

# Save the unmatched values to a separate CSV file with UTF-8 encoding
unmatched_output_file = os.path.join(script_folder, 'unmatched_org_IDs.csv')
unmatched_values.to_csv(unmatched_output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")
print(f"The unmatched values have been saved to {unmatched_output_file}")

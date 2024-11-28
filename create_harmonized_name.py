import os
import pandas as pd

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))

# Paths to the CSV files
manual_org_file = os.path.join(script_folder, 'Manual org ID link.csv')
applied_en_file = os.path.join(script_folder, 'applied_en.csv')

# Read the CSV files
manual_org_df = pd.read_csv(manual_org_file)
applied_en_df = pd.read_csv(applied_en_file)

# Function to replace typographic apostrophes and non-breaking hyphens with standard ones
def standardize_text(df):
    return df.apply(lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() if x.dtype == "object" else x)

# Apply the function to all dataframes
manual_org_df = standardize_text(manual_org_df)
applied_en_df = standardize_text(applied_en_df)

# Perform a left join to include all entries from manual_org_df and only matching entries from applied_en_df
joined_df = pd.merge(manual_org_df, applied_en_df, left_on='Organization Legal Name English', right_on='Legal title', how='left')

# Create the 'preferred_name' field
joined_df['preferred_name'] = joined_df['Applied title']
joined_df.loc[joined_df['preferred_name'].isna(), 'preferred_name'] = joined_df['Organization Legal Name English']

# Create the 'nom_préféré' field
joined_df['nom_préféré'] = joined_df["Titre d'usage"]
joined_df.loc[joined_df['nom_préféré'].isna(), 'nom_préféré'] = joined_df['Organization Legal Name French']

# Set the field 'GC OrgID' so that there are no decimals
joined_df['GC OrgID'] = joined_df['GC OrgID'].astype(str).str.split('.').str[0]

# Sort the final joined DataFrame by GC OrgID from lowest to highest
joined_df = joined_df.sort_values(by='GC OrgID')

# Save the final joined DataFrame to a new CSV file with UTF-8 encoding
output_file = os.path.join(script_folder, 'create_harmonized_name.csv')
joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")

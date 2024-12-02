import os
import pandas as pd

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))
resources_folder = os.path.join(script_folder, 'Resources')
scraping_folder = os.path.join(script_folder, 'Scraping')

# Paths to the CSV files
manual_org_file = os.path.join(resources_folder, 'Manual org ID link.csv')
combined_faa_file = os.path.join(scraping_folder, 'combined_FAA_names.csv')
applied_en_file = os.path.join(resources_folder, 'applied_en.csv')
infobase_en_file = os.path.join(resources_folder, 'infobase_en.csv')
infobase_fr_file = os.path.join(resources_folder, 'infobase_fr.csv')
fixed_rg_file = os.path.join(resources_folder, 'Fixed_RG_names.csv')

# Read the CSV files
manual_org_df = pd.read_csv(manual_org_file)
combined_faa_df = pd.read_csv(combined_faa_file)
applied_en_df = pd.read_csv(applied_en_file)
infobase_en_df = pd.read_csv(infobase_en_file)
infobase_fr_df = pd.read_csv(infobase_fr_file)
fixed_rg_df = pd.read_csv(fixed_rg_file)

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
infobase_en_df = standardize_text(infobase_en_df)
infobase_fr_df = standardize_text(infobase_fr_df)
fixed_rg_df = standardize_text(fixed_rg_df)

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
final_joined_df = pd.merge(joined_df, applied_en_df[['Legal title', 'Applied title', "Titre d'usage"]], left_on='Organization Legal Name English', right_on='Legal title', how='left')

# Join with infobase_en_df on 'Legal Title' and 'Organization Legal Name English'
final_joined_df = pd.merge(final_joined_df, infobase_en_df[['Legal Title', 'OrgID', 'Website']], left_on='Organization Legal Name English', right_on='Legal Title', how='left')

# Join with infobase_fr_df on 'Appellation legale' and 'appellation_légale'
final_joined_df = pd.merge(final_joined_df, infobase_fr_df[['Appellation legale', 'Site Web']], left_on='Organization Legal Name French', right_on='Appellation legale', how='left')

# Create the 'harmonized_name' field
final_joined_df['harmonized_name'] = final_joined_df['Applied title']
final_joined_df.loc[final_joined_df['harmonized_name'].isna(), 'harmonized_name'] = final_joined_df['Organization Legal Name English']

# Create the 'nom_harmonisé' field
final_joined_df['nom_harmonisé'] = final_joined_df["Titre d'usage"]
final_joined_df.loc[final_joined_df['nom_harmonisé'].isna(), 'nom_harmonisé'] = final_joined_df['Organization Legal Name French']

# Set the field 'GC OrgID' so that there are no decimals
final_joined_df['GC OrgID'] = final_joined_df['GC OrgID'].astype(str).str.split('.').str[0]

# Rename 'GC OrgID' to 'gc_orgID'
final_joined_df = final_joined_df.rename(columns={'GC OrgID': 'gc_orgID'})

# Rename 'OrgID' to 'infobaseID' and set as whole number
final_joined_df = final_joined_df.rename(columns={'OrgID': 'infobaseID'})
final_joined_df['infobaseID'] = final_joined_df['infobaseID'].fillna(0).astype(int)

# Rename 'Website' to 'website'
final_joined_df = final_joined_df.rename(columns={'Website': 'website'})

# Rename 'Site Web' to 'site_web'
final_joined_df = final_joined_df.rename(columns={'Site Web': 'site_web'})

# Remove rows where 'gc_orgID' is NaN
final_joined_df = final_joined_df.dropna(subset=['gc_orgID'])

# Check if 'abbreviation' and 'abreviation' columns exist, if not, create them with empty values
if 'abbreviation' not in final_joined_df.columns:
    final_joined_df['abbreviation'] = ''
if 'abreviation' not in final_joined_df.columns:
    final_joined_df['abreviation'] = ''

# Convert gc_orgID to string type for merging
final_joined_df['gc_orgID'] = final_joined_df['gc_orgID'].astype(str)
fixed_rg_df['GC OrgID'] = fixed_rg_df['GC OrgID'].astype(str)

# Join with fixed_rg_df on 'GC OrgID' and 'gc_orgID'
final_joined_df = pd.merge(final_joined_df, fixed_rg_df[['GC OrgID', 'rgnumber']], left_on='gc_orgID', right_on='GC OrgID', how='left')

# Drop the redundant 'GC OrgID' column from the final DataFrame
final_joined_df = final_joined_df.drop(columns=['GC OrgID'])

# Rename the new field to 'rg'
final_joined_df = final_joined_df.rename(columns={'rgnumber': 'rg'})

# Reorder the fields to include 'rg'
ordered_fields = ['gc_orgID', 'rg', 'harmonized_name', 'nom_harmonisé', 'abbreviation', 'abreviation', 'infobaseID', 'website', 'site_web']
final_joined_df = final_joined_df[ordered_fields]

# Sort the final joined DataFrame by gc_orgID from lowest to highest
final_joined_df = final_joined_df.sort_values(by='gc_orgID')

# Save the final joined DataFrame to a new CSV file with UTF-8 encoding in the main folder
output_file = os.path.join(script_folder, 'gc_concordance.csv')
final_joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

# Save the unmatched values to a separate CSV file with UTF-8 encoding in the main folder
unmatched_output_file = os.path.join(script_folder, 'unmatched_org_IDs.csv')
unmatched_values.to_csv(unmatched_output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")
print(f"The unmatched values have been saved to {unmatched_output_file}")

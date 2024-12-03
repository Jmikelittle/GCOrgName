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
final_rg_match_file = os.path.join(resources_folder, 'final_RG_match.csv')
manual_pop_phoenix_file = os.path.join(resources_folder, 'manual pop phoenix.csv')

# Read the CSV files
dfs = {name: pd.read_csv(path) for name, path in [
    ('manual_org_df', manual_org_file),
    ('combined_faa_df', combined_faa_file),
    ('applied_en_df', applied_en_file),
    ('infobase_en_df', infobase_en_file),
    ('infobase_fr_df', infobase_fr_file),
    ('final_rg_match_df', final_rg_match_file),
    ('manual_pop_phoenix_df', manual_pop_phoenix_file)
]}

# Function to standardize text
def standardize_text(df):
    return df.apply(lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() if x.dtype == "object" else x)

# Apply the function to all dataframes
dfs = {name: standardize_text(df) for name, df in dfs.items()}

# Ensure GC OrgID is a string
for df in dfs.values():
    if 'GC OrgID' in df.columns:
        df['GC OrgID'] = df['GC OrgID'].astype(str)

# Ensure 'gc_orgID' is a string for manual_pop_phoenix_df
if 'gc_orgID' in dfs['manual_pop_phoenix_df'].columns:
    dfs['manual_pop_phoenix_df']['gc_orgID'] = dfs['manual_pop_phoenix_df']['gc_orgID'].astype(str)

# Preserve the original 'English Name' column
dfs['combined_faa_df']['Original English Name'] = dfs['combined_faa_df']['English Name']
dfs['combined_faa_df'] = dfs['combined_faa_df'].rename(columns={'English Name': 'Organization Legal Name English'})

# Perform the merges
final_joined_df = pd.merge(dfs['manual_org_df'], dfs['combined_faa_df'], on='Organization Legal Name English', how='outer')
final_joined_df['Names Match'] = final_joined_df.apply(lambda row: 0 if pd.notna(row['Organization Legal Name English']) else 1, axis=1)
unmatched_values = final_joined_df[final_joined_df['Names Match'] == 1]
final_joined_df = final_joined_df[final_joined_df['Names Match'] == 0]

final_joined_df = final_joined_df.merge(dfs['applied_en_df'][['Legal title', 'Applied title', "Titre d'usage", 'Abbreviation', 'Abreviation']], left_on='Organization Legal Name English', right_on='Legal title', how='left')
final_joined_df = final_joined_df.merge(dfs['infobase_en_df'][['Legal Title', 'OrgID', 'Website']], left_on='Organization Legal Name English', right_on='Legal Title', how='left')
final_joined_df = final_joined_df.merge(dfs['infobase_fr_df'][['Appellation legale', 'Site Web']], left_on='Organization Legal Name French', right_on='Appellation legale', how='left')

# Create harmonized fields
final_joined_df['harmonized_name'] = final_joined_df['Applied title'].fillna(final_joined_df['Organization Legal Name English'])
final_joined_df['nom_harmonisé'] = final_joined_df["Titre d'usage"].fillna(final_joined_df['Organization Legal Name French'])

# Standardize GC OrgID and other columns
final_joined_df['GC OrgID'] = final_joined_df['GC OrgID'].astype(str).str.split('.').str[0]
final_joined_df = final_joined_df.rename(columns={'GC OrgID': 'gc_orgID', 'OrgID': 'infobaseID', 'Website': 'website', 'Site Web': 'site_web'})
final_joined_df['infobaseID'] = final_joined_df['infobaseID'].fillna(0).astype(int)

# Ensure all numerical columns are whole numbers
numerical_columns = ['infobaseID']
for col in numerical_columns:
    final_joined_df[col] = final_joined_df[col].astype(int)

# Join with final_rg_match_df on 'gc_orgID'
final_joined_df = final_joined_df.merge(dfs['final_rg_match_df'][['GC OrgID', 'rgnumber']], left_on='gc_orgID', right_on='GC OrgID', how='left').drop(columns=['GC OrgID'])
final_joined_df = final_joined_df.rename(columns={'rgnumber': 'rg'})

# Ensure 'rg' is blank if zero
final_joined_df['rg'] = final_joined_df['rg'].apply(lambda x: '' if x == 0 else int(x) if pd.notna(x) else '')

# Join with manual_pop_phoenix_df on 'gc_orgID'
final_joined_df = final_joined_df.merge(dfs['manual_pop_phoenix_df'], on='gc_orgID', how='left')

# Drop duplicate 'gc_orgID' columns if any exist
final_joined_df = final_joined_df.loc[:,~final_joined_df.columns.duplicated()]

# Reorder the fields to include 'rg'
ordered_fields = ['gc_orgID', 'rg', 'harmonized_name', 'nom_harmonisé', 'Abbreviation', 'Abreviation', 'infobaseID', 'website', 'site_web']
manual_pop_phoenix_columns = dfs['manual_pop_phoenix_df'].columns.difference(ordered_fields, sort=False).tolist()
final_joined_df = final_joined_df[ordered_fields + manual_pop_phoenix_columns]

# Sort by gc_orgID and save the results
final_joined_df = final_joined_df.sort_values(by='gc_orgID')

output_file = os.path.join(script_folder, 'gc_concordance.csv')
final_joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

unmatched_output_file = os.path.join(script_folder, 'unmatched_org_IDs.csv')
unmatched_values.to_csv(unmatched_output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")
print(f"The unmatched values have been saved to {unmatched_output_file}")

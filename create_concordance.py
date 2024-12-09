import os
import pandas as pd

# Define paths
script_folder = os.path.dirname(os.path.abspath(__file__))
resources_folder = os.path.join(script_folder, 'Resources')
scraping_folder = os.path.join(script_folder, 'Scraping')

# Load CSV files
files = {
    'manual_org_df': os.path.join(resources_folder, 'Manual org ID link.csv'),
    'combined_faa_df': os.path.join(scraping_folder, 'combined_FAA_names.csv'),
    'applied_en_df': os.path.join(resources_folder, 'applied_en.csv'),
    'infobase_en_df': os.path.join(resources_folder, 'infobase_en.csv'),
    'infobase_fr_df': os.path.join(resources_folder, 'infobase_fr.csv'),
    'final_rg_match_df': os.path.join(resources_folder, 'final_RG_match.csv'),
    'manual_pop_phoenix_df': os.path.join(resources_folder, 'manual pop phoenix.csv')
}
dfs = {name: pd.read_csv(path) for name, path in files.items()}

# Standardize text
for name, df in dfs.items():
    dfs[name] = df.apply(lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() if x.dtype == "object" else x)

# Convert 'GC OrgID' and 'gc_orgID' to string
for name, df in dfs.items():
    if 'GC OrgID' in df.columns:
        df['GC OrgID'] = df['GC OrgID'].astype(str)
    if 'gc_orgID' in df.columns:
        df['gc_orgID'] = df['gc_orgID'].astype(str)

# Rename columns for joining
dfs['combined_faa_df']['Original English Name'] = dfs['combined_faa_df']['English Name']
dfs['combined_faa_df'] = dfs['combined_faa_df'].rename(columns={'English Name': 'Organization Legal Name English'})

# Merge dataframes
final_joined_df = dfs['manual_org_df'].merge(dfs['combined_faa_df'], on='Organization Legal Name English', how='outer')
final_joined_df['Names Match'] = final_joined_df.apply(lambda row: 0 if pd.notna(row['Organization Legal Name English']) else 1, axis=1)
unmatched_values = final_joined_df[final_joined_df['Names Match'] == 1]
final_joined_df = final_joined_df[final_joined_df['Names Match'] == 0]

merge_columns = [
    ('applied_en_df', 'Legal title', ['Legal title', 'Applied title', "Titre d'usage", 'Abbreviation', 'Abreviation']),
    ('infobase_en_df', 'Legal Title', ['Legal Title', 'OrgID', 'Website']),
    ('infobase_fr_df', 'Appellation legale', ['Appellation legale', 'Site Web'])
]
for df_name, on_col, columns in merge_columns:
    final_joined_df = final_joined_df.merge(dfs[df_name][columns], left_on='Organization Legal Name English', right_on=on_col, how='left')

# Create harmonized fields
final_joined_df['harmonized_name'] = final_joined_df['Applied title'].fillna(final_joined_df['Organization Legal Name English'])
final_joined_df['nom_harmonisé'] = final_joined_df["Titre d'usage"].fillna(final_joined_df['Organization Legal Name French'])

# Standardize columns
final_joined_df['GC OrgID'] = final_joined_df['GC OrgID'].astype(str).str.split('.').str[0]
final_joined_df = final_joined_df.rename(columns={'GC OrgID': 'gc_orgID', 'OrgID': 'infobaseID', 'Website': 'website', 'Site Web': 'site_web'})
final_joined_df['infobaseID'] = final_joined_df['infobaseID'].fillna(0).astype(int)
final_joined_df = final_joined_df.merge(dfs['final_rg_match_df'][['GC OrgID', 'rgnumber']], left_on='gc_orgID', right_on='GC OrgID', how='left').drop(columns=['GC OrgID'])
final_joined_df = final_joined_df.rename(columns={'rgnumber': 'rg'})
final_joined_df['rg'] = final_joined_df['rg'].apply(lambda x: '' if x == 0 else int(x) if pd.notna(x) else '')

# Merge with manual_pop_phoenix_df
final_joined_df = final_joined_df.merge(dfs['manual_pop_phoenix_df'], on='gc_orgID', how='left')

# Drop the 'gc_orgID' from manual_pop_phoenix_df after merge
if 'gc_orgID_y' in final_joined_df.columns:
    final_joined_df = final_joined_df.drop(columns=['gc_orgID_y'])
final_joined_df = final_joined_df.rename(columns={'gc_orgID_x': 'gc_orgID'})

# Remove duplicates based on gc_orgID
final_joined_df = final_joined_df.drop_duplicates(subset=['gc_orgID'])

# Rename fields
final_joined_df = final_joined_df.rename(columns={'Abbreviation': 'abbreviation', 'Abreviation': 'abreviation'})

# Manual changes
manual_changes = {
    "2281": {"abbreviation": "OIC", "abreviation": "CI"},
    "2282": {"abbreviation": "OPC", "abreviation": "CPVP"}
}

for gc_orgID, changes in manual_changes.items():
    for field, value in changes.items():
        final_joined_df.loc[final_joined_df['gc_orgID'] == gc_orgID, field] = value

# Reorder and sort
final_field_order = [
    'gc_orgID', 'harmonized_name', 'nom_harmonisé', 'abbreviation', 'abreviation', 'infobaseID', 'rg',
    'ati', 'open_gov_ouvert', 'pop', 'phoenix', 'website', 'site_web'
]
final_joined_df = final_joined_df[final_field_order].sort_values(by='gc_orgID')

# Save results
output_file = os.path.join(script_folder, 'gc_concordance.csv')
final_joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
unmatched_output_file = os.path.join(script_folder, 'unmatched_org_IDs.csv')
unmatched_values.to_csv(unmatched_output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")
print(f"The unmatched values have been saved to {unmatched_output_file}")

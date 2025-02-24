import os
import pandas as pd

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))
resources_folder = os.path.join(script_folder, 'Resources')

# Paths to the CSV files
manual_org_file = os.path.join(resources_folder, 'Manual org ID link.csv')
applied_en_file = os.path.join(resources_folder, 'applied_en.csv')
infobase_en_file = os.path.join(resources_folder, 'infobase_en.csv')
infobase_fr_file = os.path.join(resources_folder, 'infobase_fr.csv')

# Read the CSV files
manual_org_df = pd.read_csv(manual_org_file)
applied_en_df = pd.read_csv(applied_en_file)
infobase_en_df = pd.read_csv(infobase_en_file)
infobase_fr_df = pd.read_csv(infobase_fr_file)

# Standardize text
def standardize_text(df):
    return df.apply(lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() if x.dtype == "object" else x)

# Apply the function to all dataframes
manual_org_df = standardize_text(manual_org_df)
applied_en_df = standardize_text(applied_en_df)
infobase_en_df = standardize_text(infobase_en_df)
infobase_fr_df = standardize_text(infobase_fr_df)

# Perform a left join to include all entries from manual_org_df and only matching entries from applied_en_df
joined_df = pd.merge(manual_org_df, applied_en_df, left_on='Organization Legal Name English', right_on='Legal title', how='left')

# Merge with infobase_en_df and infobase_fr_df using the correct column names, excluding 'Applied title' and 'Appellation legale'
joined_df = pd.merge(joined_df, infobase_en_df[['Legal title']], left_on='Organization Legal Name English', right_on='Legal title', how='left')
joined_df = pd.merge(joined_df, infobase_fr_df[['Titre applique']], left_on='Organization Legal Name French', right_on='Titre applique', how='left')

# Debug: Print the columns of joined_df
print("Columns in joined_df:", joined_df.columns)

# Create the 'harmonized_name' field with the specified priority
joined_df['harmonized_name'] = joined_df['Applied title']
joined_df.loc[joined_df['harmonized_name'].isna(), 'harmonized_name'] = joined_df['Organization Legal Name English']

# Create the 'nom_harmonisé' field with the specified priority
joined_df['nom_harmonisé'] = joined_df["Titre d'usage"]
joined_df.loc[joined_df['nom_harmonisé'].isna(), 'nom_harmonisé'] = joined_df['Titre applique']
joined_df.loc[joined_df['nom_harmonisé'].isna(), 'nom_harmonisé'] = joined_df['Organization Legal Name French']

# Manual changes
manual_changes = {
    'gc_orgID': 2271,
    'harmonized_name': 'Elections Canada',
    'nom_harmonisé': 'Élections Canada'
}

# Apply manual changes explicitly
joined_df.loc[joined_df['gc_orgID'] == manual_changes['gc_orgID'], 'harmonized_name'] = manual_changes['harmonized_name']
joined_df.loc[joined_df['gc_orgID'] == manual_changes['gc_orgID'], 'nom_harmonisé'] = manual_changes['nom_harmonisé']

# Set the field 'gc_orgID' so that there are no decimals
joined_df['gc_orgID'] = joined_df['gc_orgID'].astype(str).str.split('.').str[0]

# Drop 'Legal title_x' and 'Legal title_y' columns if they exist
joined_df = joined_df.drop(columns=['Legal title_x', 'Legal title_y'], errors='ignore')

# Sort the final joined DataFrame by gc_orgID from lowest to highest
joined_df = joined_df.sort_values(by='gc_orgID')

# Save the final joined DataFrame to a new CSV file with UTF-8 encoding
output_file = os.path.join(script_folder, 'create_harmonized_name.csv')
joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")

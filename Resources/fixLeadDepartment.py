import pandas as pd
import os

# Paths to the CSV files
resources_folder = os.path.dirname(os.path.abspath(__file__))
harmonized_names_file = os.path.join(resources_folder, '..', 'create_harmonized_name.csv')
manual_lead_department_file = os.path.join(resources_folder, 'Manual_leadDepartmentPortfolio.csv')
manual_ministries_file = os.path.join(resources_folder, 'manualMinistries.csv')

# Read the CSV files
harmonized_names_df = pd.read_csv(harmonized_names_file)
manual_lead_department_df = pd.read_csv(manual_lead_department_file)
manual_ministries_df = pd.read_csv(manual_ministries_file)

# Ensure the 'Parent GC OrgID' and 'GC OrgID' columns are treated as strings without decimals
manual_lead_department_df['Parent GC OrgID'] = manual_lead_department_df['Parent GC OrgID'].astype(str).str.split('.').str[0]
harmonized_names_df['GC OrgID'] = harmonized_names_df['GC OrgID'].astype(str)

# Merge the dataframes on 'GC OrgID' from create_harmonized_name.csv and 'Parent GC OrgID' from Manual_leadDepartmentPortfolio.csv
merged_df = pd.merge(manual_lead_department_df, harmonized_names_df[['GC OrgID', 'harmonized_name', 'nom_harmonisé']], left_on='Parent GC OrgID', right_on='GC OrgID', how='left')

# Replace values in 'lead department' with 'harmonized_name' only if not already filled
merged_df['lead department'] = merged_df.apply(
    lambda row: row['harmonized_name'] if pd.isna(row['lead department']) else row['lead department'], axis=1
)

# Replace values in 'ministère responsable' with 'nom_harmonisé' only if not already filled
merged_df['ministère responsable'] = merged_df.apply(
    lambda row: row['nom_harmonisé'] if pd.isna(row['ministère responsable']) else row['ministère responsable'], axis=1
)

# Fill lead department and ministère responsable with values from manualMinistries.csv if Parent GC OrgID starts with 'm'
for index, row in merged_df.iterrows():
    if str(row['Parent GC OrgID']).startswith('m'):
        min_id = row['Parent GC OrgID']
        title_value = manual_ministries_df.loc[manual_ministries_df['minID'] == min_id, 'Title'].values
        titre_value = manual_ministries_df.loc[manual_ministries_df['minID'] == min_id, 'Titre'].values
        if len(title_value) > 0:
            merged_df.at[index, 'lead department'] = title_value[0]
        if len(titre_value) > 0:
            merged_df.at[index, 'ministère responsable'] = titre_value[0]

# Drop the 'harmonized_name', 'nom_harmonisé', and 'GC OrgID_y' columns as they are no longer needed
merged_df = merged_df.drop(columns=['harmonized_name', 'nom_harmonisé', 'GC OrgID_y'])

# Rename 'GC OrgID_x' back to 'GC OrgID'
merged_df = merged_df.rename(columns={'GC OrgID_x': 'GC OrgID'})

# Save the updated dataframe back to the CSV file
merged_df.to_csv(manual_lead_department_file, index=False, encoding='utf-8-sig')

print("The Manual_leadDepartmentPortfolio.csv file has been updated successfully.")

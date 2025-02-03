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

# Merge the dataframes on 'GC OrgID' from create_harmonized_name.csv and 'Parent GC OrgID' from Manual_leadDepartmentPortfolio.csv
merged_df = pd.merge(manual_lead_department_df, harmonized_names_df[['GC OrgID', 'harmonized_name', 'nom_harmonisé']], left_on='Parent GC OrgID', right_on='GC OrgID', how='left')

# Replace values in 'lead department' with 'harmonized_name'
merged_df['lead department'] = merged_df['harmonized_name']

# Replace values in 'ministère responsable' with 'nom_harmonisé'
merged_df['ministère responsable'] = merged_df['nom_harmonisé']

# Fill lead department with values from manualMinistries.csv if Parent GC OrgID starts with 'm'
for index, row in merged_df.iterrows():
    if str(row['Parent GC OrgID']).startswith('m'):
        min_id = row['Parent GC OrgID']
        title_value = manual_ministries_df.loc[manual_ministries_df['minID'] == min_id, 'Title'].values
        if len(title_value) > 0:
            merged_df.at[index, 'lead department'] = title_value[0]

# Drop the 'harmonized_name', 'nom_harmonisé', and 'GC OrgID_y' columns as they are no longer needed
merged_df = merged_df.drop(columns=['harmonized_name', 'nom_harmonisé', 'GC OrgID_y'])

# Rename 'GC OrgID_x' back to 'GC OrgID'
merged_df = merged_df.rename(columns={'GC OrgID_x': 'GC OrgID'})

# Save the updated dataframe back to the CSV file
merged_df.to_csv(manual_lead_department_file, index=False, encoding='utf-8-sig')

print("The Manual_leadDepartmentPortfolio.csv file has been updated successfully.")

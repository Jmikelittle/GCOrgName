import os
import pandas as pd

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))

# Paths to the CSV files
manual_org_file = os.path.join(script_folder, 'Resources', 'Manual org ID link.csv')
combined_faa_file = os.path.join(script_folder, 'Scraping', 'combined_FAA_names.csv')
applied_en_file = os.path.join(script_folder, 'Resources', 'applied_en.csv')
infobase_en_file = os.path.join(script_folder, 'Resources', 'infobase_en.csv')
harmonized_names_file = os.path.join(script_folder, 'create_harmonized_name.csv')
manual_lead_department_file = os.path.join(script_folder, 'Resources', 'manual_leadDepartmentPortfolio.csv')

# Read the CSV files
manual_org_df = pd.read_csv(manual_org_file)
combined_faa_df = pd.read_csv(combined_faa_file)
applied_en_df = pd.read_csv(applied_en_file)
infobase_en_df = pd.read_csv(infobase_en_file)
harmonized_names_df = pd.read_csv(harmonized_names_file)
manual_lead_department_df = pd.read_csv(manual_lead_department_file)

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
harmonized_names_df = standardize_text(harmonized_names_df)
manual_lead_department_df = standardize_text(manual_lead_department_df)

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
final_joined_df = pd.merge(
    joined_df, 
    applied_en_df[['Legal title', 'Applied title', "Titre d'usage", 'Abbreviation', 'Abreviation']], 
    left_on='Organization Legal Name English', 
    right_on='Legal title', 
    how='left'
)

# Join with infobase_en_df on 'Legal Title' and 'Organization Legal Name English'
final_joined_df = pd.merge(
    final_joined_df, 
    infobase_en_df[['Legal Title', 'Status', 'End date']], 
    left_on='Organization Legal Name English', 
    right_on='Legal Title', 
    how='left'
)

# Pull in new values for harmonized_name and nom_harmonisé from create_harmonized_name.csv
harmonized_names_df = harmonized_names_df[['GC OrgID', 'harmonized_name', 'nom_harmonisé']]
final_joined_df = final_joined_df.merge(harmonized_names_df, on='GC OrgID', how='left')

# Set the field 'GC OrgID' so that there are no decimals
final_joined_df['GC OrgID'] = final_joined_df['GC OrgID'].astype(str).str.split('.').str[0]

# Rename 'GC OrgID' to 'gc_orgID'
final_joined_df = final_joined_df.rename(columns={'GC OrgID': 'gc_orgID'})

# Rename 'Status' to 'status_statut' and set value to 'a' if empty
final_joined_df = final_joined_df.rename(columns={'Status': 'status_statut'})
final_joined_df['status_statut'] = final_joined_df['status_statut'].fillna('a')

# Check if 'End date' exists, then rename to 'end_date_fin' and set value to empty if it is '.'
if 'End date' in final_joined_df.columns:
    final_joined_df = final_joined_df.rename(columns={'End date': 'end_date_fin'})
    final_joined_df['end_date_fin'] = final_joined_df['end_date_fin'].replace('.', '')
else:
    final_joined_df['end_date_fin'] = ''

# Rename fields as specified
final_joined_df = final_joined_df.rename(columns={
    'Organization Legal Name English': 'legal_title',
    'Organization Legal Name French': 'appellation_légale',
    'FAA': 'FAA_LGFP',
    'Applied title': 'preferred_name',
    "Titre d'usage": 'nom_préféré',
    'Abbreviation': 'abbreviation',
    'Abreviation': 'abreviation'
})

# Add the new columns after 'nom_préféré'
final_joined_df.insert(final_joined_df.columns.get_loc('nom_préféré') + 1, 'lead_department', '')
final_joined_df.insert(final_joined_df.columns.get_loc('nom_préféré') + 2, 'ministère_responsable', '')

# Function to update lead_department and ministère_responsable
def update_lead_ministere(row):
    try:
        parent_gc_orgID = row['gc_orgID']
        print(f"Processing gc_orgID: {parent_gc_orgID}")
        lead_dept = manual_lead_department_df[manual_lead_department_df['Parent GC OrgID'] == parent_gc_orgID]['Part GC Org ID'].values[0]
        print(f"Found lead_dept: {lead_dept}")
        lead_department = harmonized_names_df[harmonized_names_df['GC OrgID'] == lead_dept]['harmonized_name'].values[0]
        ministere_responsable = harmonized_names_df[harmonized_names_df['GC OrgID'] == lead_dept]['nom_harmonisé'].values[0]
        row['lead_department'] = lead_department
        row['ministère_responsable'] = ministere_responsable
        print(f"Updated row for gc_orgID {parent_gc_orgID}: lead_department = {lead_department}, ministère_responsable = {ministere_responsable}")
    except (IndexError, KeyError) as e:
        print(f"Failed to update row for gc_orgID {parent_gc_orgID}: {e}")
        pass  # Ignore errors and continue
    return row

# Apply the function to each row
final_joined_df = final_joined_df.apply(update_lead_ministere, axis=1)

# Reorder the fields
ordered_fields = ['gc_orgID', 'harmonized_name', 'nom_harmonisé', 'legal_title', 'appellation_légale', 
                  'preferred_name', 'nom_préféré', 'lead_department', 'ministère_responsable',
                  'abbreviation', 'abreviation', 'FAA_LGFP', 'status_statut', 'end_date_fin']
final_joined_df = final_joined_df[ordered_fields]

# Sort the final joined DataFrame by gc_orgID from lowest to highest
final_joined_df = final_joined_df.sort_values(by='gc_orgID')

# Save the final joined DataFrame to a new CSV file with UTF-8 encoding
output_file = os.path.join(script_folder, 'GC Org Info.csv')
final_joined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

# Save the unmatched values to a separate CSV file with UTF-8 encoding
unmatched_output_file = os.path.join(script_folder, 'unmatched_org_IDs.csv')
unmatched_values.to_csv(unmatched_output_file, index=False, encoding='utf-8-sig')

print(f"The final joined DataFrame has been saved to {output_file}")
print(f"The unmatched values have been saved to {unmatched_output_file}")

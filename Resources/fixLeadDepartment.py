import pandas as pd
import os

# Paths to the CSV files
resources_folder = os.path.dirname(os.path.abspath(__file__))
manual_lead_department_file = os.path.join(resources_folder, 'Manual_leadDepartmentPortfolio.csv')
gc_org_info_file = os.path.join(resources_folder, '..', 'gc_org_info.csv')
manual_ministries_file = os.path.join(resources_folder, 'manualMinistries.csv')

# Read the CSV files
try:
    manual_lead_department_df = pd.read_csv(manual_lead_department_file)
    gc_org_info_df = pd.read_csv(gc_org_info_file)
    manual_ministries_df = pd.read_csv(manual_ministries_file)
    
    print("Successfully loaded all CSV files")
    print(f"Manual lead department file has {len(manual_lead_department_df)} rows")
    print(f"GC Org Info file has {len(gc_org_info_df)} rows")
    print(f"Manual ministries file has {len(manual_ministries_df)} rows")
except Exception as e:
    print(f"Error loading CSV files: {str(e)}")
    exit(1)

# Create a backup of the original file
backup_file = os.path.join(resources_folder, 'Manual_leadDepartmentPortfolio_backup.csv')
manual_lead_department_df.to_csv(backup_file, index=False)
print(f"Backup created at {backup_file}")

# Create a mapping of gc_orgID to harmonized_name from gc_org_info_df
gc_orgid_to_name = {}
for _, row in gc_org_info_df.iterrows():
    if pd.notna(row['gc_orgID']) and pd.notna(row['harmonized_name']):
        gc_orgid_to_name[str(int(row['gc_orgID']))] = row['harmonized_name']

# Create a mapping of ministry IDs to titles from manual_ministries_df
ministry_id_to_title = {}
for _, row in manual_ministries_df.iterrows():
    if pd.notna(row['minID']) and pd.notna(row['Title']):
        ministry_id_to_title[str(row['minID'])] = row['Title']

# Update the 'Harmonized GC Name' based on gc_orgID or Parent GC OrgID
updated_count = 0
ministry_updated_count = 0

for index, row in manual_lead_department_df.iterrows():
    # Check if Parent GC OrgID starts with 'm' (ministry ID)
    if pd.notna(row['Parent GC OrgID']) and str(row['Parent GC OrgID']).startswith('m'):
        # It's a ministry, use the Title from manualMinistries.csv
        ministry_id = str(row['Parent GC OrgID'])
        
        if ministry_id in ministry_id_to_title:
            old_name = manual_lead_department_df.at[index, 'Harmonized GC Name']
            new_name = ministry_id_to_title[ministry_id]
            
            # Update both the harmonized name and lead_department for ministries
            if old_name != new_name:
                manual_lead_department_df.at[index, 'Harmonized GC Name'] = new_name
                manual_lead_department_df.at[index, 'lead_department'] = new_name
                manual_lead_department_df.at[index, 'ministère_responsable'] = row.get('ministère_responsable', '')  # Preserve French if available
                ministry_updated_count += 1
                print(f"Updated Ministry ID {ministry_id}: '{old_name}' -> '{new_name}'")
    
    # For regular entries, update based on gc_orgID
    elif pd.notna(row['gc_orgID']):
        # Convert to string and remove decimal point if present
        gc_orgid = str(int(row['gc_orgID']))
        
        if gc_orgid in gc_orgid_to_name:
            # Update the harmonized name
            old_name = manual_lead_department_df.at[index, 'Harmonized GC Name']
            new_name = gc_orgid_to_name[gc_orgid]
            
            if old_name != new_name:
                manual_lead_department_df.at[index, 'Harmonized GC Name'] = new_name
                updated_count += 1
                print(f"Updated ID {gc_orgid}: '{old_name}' -> '{new_name}'")

print(f"Updated {updated_count} organization harmonized names")
print(f"Updated {ministry_updated_count} ministry harmonized names")

# Save the updated dataframe back to the CSV file
manual_lead_department_df.to_csv(manual_lead_department_file, index=False)
print(f"Updated file saved to {manual_lead_department_file}")

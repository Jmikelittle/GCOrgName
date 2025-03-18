import pandas as pd
import os
# Add these imports for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Paths to the CSV files
resources_folder = os.path.dirname(os.path.abspath(__file__))
manual_lead_department_file = os.path.join(resources_folder, 'lead_manual.csv')  # Changed
gc_org_info_file = os.path.join(resources_folder, '..', 'gc_org_info.csv')
manual_ministries_file = os.path.join(resources_folder, 'lead_code_ministers.csv')  # Changed

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
backup_file = os.path.join(resources_folder, 'lead_manual_backup.csv')  # Changed
manual_lead_department_df.to_csv(backup_file, index=False)
print(f"Backup created at {backup_file}")

# Create a mapping of gc_orgID to harmonized_name from gc_org_info_df
gc_orgid_to_name = {}
for _, row in gc_org_info_df.iterrows():
    if pd.notna(row['gc_orgID']) and pd.notna(row['harmonized_name']):
        gc_orgid_to_name[str(int(row['gc_orgID']))] = row['harmonized_name']

# Get a set of existing gc_orgIDs in manual_lead_department_df
existing_gc_orgids = set()
for _, row in manual_lead_department_df.iterrows():
    if pd.notna(row['gc_orgID']):
        existing_gc_orgids.add(str(int(row['gc_orgID'])))

# Identify missing gc_orgIDs and create new rows
new_rows = []
missing_count = 0

for gc_orgid, harmonized_name in gc_orgid_to_name.items():
    if gc_orgid not in existing_gc_orgids:
        # Create a new row with the gc_orgID and harmonized_name
        new_row = {col: '' for col in manual_lead_department_df.columns}  # Initialize with empty values
        new_row['gc_orgID'] = gc_orgid
        new_row['Harmonized GC Name'] = harmonized_name
        new_rows.append(new_row)
        missing_count += 1
        print(f"Adding missing org ID {gc_orgid}: '{harmonized_name}'")

# Add new rows to the dataframe
if new_rows:
    manual_lead_department_df = pd.concat([manual_lead_department_df, pd.DataFrame(new_rows)], ignore_index=True)

print(f"Added {missing_count} missing organizations")

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

# Identify organizations without a lead department
orgs_without_lead = manual_lead_department_df[
    (manual_lead_department_df['lead_department'].isna()) | 
    (manual_lead_department_df['lead_department'] == '')
]

if not orgs_without_lead.empty:
    print(f"Found {len(orgs_without_lead)} organizations without a lead department")
else:
    print("All organizations have lead departments assigned")

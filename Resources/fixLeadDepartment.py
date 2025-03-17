import pandas as pd
import os

# Paths to the CSV files
resources_folder = os.path.dirname(os.path.abspath(__file__))
harmonized_names_file = os.path.join(resources_folder, '..', 'create_harmonized_name.csv')
manual_lead_department_file = os.path.join(resources_folder, 'Manual_leadDepartmentPortfolio.csv')
manual_ministries_file = os.path.join(resources_folder, 'manualMinistries.csv')

# Read the CSV files
try:
    harmonized_names_df = pd.read_csv(harmonized_names_file)
    manual_lead_department_df = pd.read_csv(manual_lead_department_file)
    manual_ministries_df = pd.read_csv(manual_ministries_file)
    
    print("Successfully loaded all CSV files")
    print(f"Manual lead department file has {len(manual_lead_department_df)} rows")
except Exception as e:
    print(f"Error loading CSV files: {str(e)}")
    exit(1)

# Add this near the beginning of your script, after loading the CSV
original_df = manual_lead_department_df.copy()

# Then after making changes, create your updated_df
updated_df = manual_lead_department_df.copy()
# (make your modifications to updated_df)

# Create a new dataframe for the updated data to preserve manual edits
# Start with a copy of the original dataframe to maintain all original columns and data
original_df = manual_lead_department_df.copy()  # Save original for comparison
updated_df = manual_lead_department_df.copy()   # Create a copy for modifications

# Ensure the 'Parent GC OrgID' and 'GC OrgID' columns are treated as strings without decimals
# Only convert for processing, keep original values in updated_df
parent_gc_orgids = manual_lead_department_df['Parent GC OrgID'].astype(str).str.split('.').str[0]
harmonized_names_df['gc_orgID'] = harmonized_names_df['gc_orgID'].astype(str)

# Process each row and update only specific columns
updates = 0
for index, row in manual_lead_department_df.iterrows():
    parent_gc_orgid = parent_gc_orgids.iloc[index]
    
    # Case 1: Parent GC OrgID starts with 'm' (ministry ID)
    if str(parent_gc_orgid).startswith('m'):
        # Find the corresponding ministry in manualMinistries.csv
        ministry_match = manual_ministries_df[manual_ministries_df['minID'] == parent_gc_orgid]
        
        if not ministry_match.empty:
            # Update English department name
            if 'Title' in ministry_match.columns and not pd.isna(ministry_match['Title'].iloc[0]):
                ministry_title = ministry_match['Title'].iloc[0]
                updated_df.at[index, 'Harmonized GC Name'] = ministry_title
                updated_df.at[index, 'lead department'] = ministry_title
                if 'lead_department' in updated_df.columns:
                    updated_df.at[index, 'lead_department'] = ministry_title
                
            # Update French department name
            if 'Titre' in ministry_match.columns:
                # If French title is available in ministry data
                if not pd.isna(ministry_match['Titre'].iloc[0]) and ministry_match['Titre'].iloc[0] != '':
                    updated_df.at[index, 'ministère_responsable'] = ministry_match['Titre'].iloc[0]
                # If French title is missing but English title is available, use English as fallback
                elif 'Title' in ministry_match.columns and not pd.isna(ministry_match['Title'].iloc[0]):
                    updated_df.at[index, 'ministère_responsable'] = ministry_match['Title'].iloc[0]
                    print(f"Warning: No French title for ministry ID {parent_gc_orgid}, using English title as fallback")
                
            updates += 1
    
    # Case 2: Parent GC OrgID is a regular organization ID
    else:
        # Find the corresponding organization in harmonized_names_df
        org_match = harmonized_names_df[harmonized_names_df['gc_orgID'] == parent_gc_orgid]
        
        if not org_match.empty:
            # Update English department name
            if 'harmonized_name' in org_match.columns and not pd.isna(org_match['harmonized_name'].iloc[0]):
                harmonized_name = org_match['harmonized_name'].iloc[0]
                updated_df.at[index, 'Harmonized GC Name'] = harmonized_name
                updated_df.at[index, 'lead department'] = harmonized_name
                if 'lead_department' in updated_df.columns:
                    updated_df.at[index, 'lead_department'] = harmonized_name
                
            # Update French department name
            if 'nom_harmonisé' in org_match.columns and not pd.isna(org_match['nom_harmonisé'].iloc[0]):
                updated_df.at[index, 'ministère_responsable'] = org_match['nom_harmonisé'].iloc[0]
                
            updates += 1

# Ensure consistency between lead_department and lead department fields
if 'lead_department' in updated_df.columns and 'lead department' in updated_df.columns:
    updated_df['lead_department'] = updated_df['lead department']
    print("Synchronized 'lead_department' with 'lead department' for consistency")

print(f"Process complete. Updated {updates} departments")

# Compare with original to see changes - using the correct variable names now
changed_rows = (original_df != updated_df).any(axis=1)
if changed_rows.any():
    print(f"\nModified {changed_rows.sum()} of {len(updated_df)} rows")
    
    # Print details of what was changed for ministries with 'm' IDs
    m_id_rows = parent_gc_orgids.str.startswith('m')
    if m_id_rows.any():
        m_id_changes = changed_rows & m_id_rows
        if m_id_changes.any():
            print("\nDetails of changes for ministry IDs:")
            for idx in m_id_changes[m_id_changes].index:
                print(f"Row {idx}: {updated_df.loc[idx]['gc_orgID']} under {updated_df.loc[idx]['Parent GC OrgID']}")
                
                # Check what fields changed
                for col in ['lead department', 'lead_department', 'ministère_responsable', 'Harmonized GC Name']:
                    if col in updated_df.columns and col in original_df.columns:
                        if updated_df.loc[idx, col] != original_df.loc[idx, col]:
                            print(f"  - {col}: '{original_df.loc[idx, col]}' → '{updated_df.loc[idx, col]}'")

    # Preview changes before saving
    print("\nReady to write changes to CSV. Preview of changes:")
    preview_count = min(5, changed_rows.sum())
    if preview_count > 0:
        change_indices = changed_rows[changed_rows].index[:preview_count]
        for idx in change_indices:
            print(f"Row {idx}: {updated_df.loc[idx]['gc_orgID']} - Parent ID: {updated_df.loc[idx]['Parent GC OrgID']}")
    
    # Save the updated dataframe back to the CSV file
    updated_df.to_csv(manual_lead_department_file, index=False, encoding='utf-8-sig')
    print(f"\nChanges saved to {manual_lead_department_file}")
else:
    print("No changes were detected. File not modified.")

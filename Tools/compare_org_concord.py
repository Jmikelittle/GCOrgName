import os
import pandas as pd
import sys

# Define the paths to the CSV files in the parent folder
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
gc_org_info_path = os.path.join(parent_folder, 'gc_org_info.csv')
gc_concordance_path = os.path.join(parent_folder, 'gc_concordance.csv')

# Load the CSV files with error handling
try:
    gc_org_info_df = pd.read_csv(gc_org_info_path)
    print(f"Successfully loaded {gc_org_info_path}")
    print(f"Number of records in gc_org_info: {len(gc_org_info_df)}")
except Exception as e:
    print(f"Error loading {gc_org_info_path}: {str(e)}")
    sys.exit(1)

try:
    gc_concordance_df = pd.read_csv(gc_concordance_path)
    print(f"Successfully loaded {gc_concordance_path}")
    print(f"Number of records in gc_concordance: {len(gc_concordance_df)}")
except Exception as e:
    print(f"Error loading {gc_concordance_path}: {str(e)}")
    sys.exit(1)

# Check for duplicates in gc_orgID
dup_info = gc_org_info_df['gc_orgID'].duplicated().sum()
dup_concord = gc_concordance_df['gc_orgID'].duplicated().sum()
if dup_info > 0 or dup_concord > 0:
    print(f"\nWARNING: Found duplicates - gc_org_info: {dup_info}, gc_concordance: {dup_concord}")

# Ensure gc_orgID has the same type in both dataframes
gc_org_info_df['gc_orgID'] = gc_org_info_df['gc_orgID'].astype(str)
gc_concordance_df['gc_orgID'] = gc_concordance_df['gc_orgID'].astype(str)

# Check for records present in one file but not the other
print("\nAnalyzing records across datasets...")
info_only = gc_org_info_df[~gc_org_info_df['gc_orgID'].isin(gc_concordance_df['gc_orgID'])]
concord_only = gc_concordance_df[~gc_concordance_df['gc_orgID'].isin(gc_org_info_df['gc_orgID'])]

if len(info_only) > 0:
    print(f"Found {len(info_only)} records in gc_org_info but not in gc_concordance")
    # Save these records for reference
    info_only.to_csv(os.path.join(parent_folder, 'info_only_records.csv'), index=False)
    
if len(concord_only) > 0:
    print(f"Found {len(concord_only)} records in gc_concordance but not in gc_org_info")
    # Save these records for reference
    concord_only.to_csv(os.path.join(parent_folder, 'concord_only_records.csv'), index=False)

# Merge datasets for comparison on common records
print("\nComparing name values in common records...")
common_records = pd.merge(
    gc_org_info_df, 
    gc_concordance_df, 
    on='gc_orgID', 
    how='inner',
    suffixes=('_info', '_concordance')
)

# Find mismatches in harmonized names
mismatches = common_records[
    (common_records['harmonized_name_info'] != common_records['harmonized_name_concordance']) |
    (common_records['nom_harmonisé_info'] != common_records['nom_harmonisé_concordance'])
]

# Report results
print(f"\nSummary:")
print(f"- Common records: {len(common_records)}")
print(f"- Mismatches found: {len(mismatches)}")

if len(mismatches) > 0:
    print("\nMismatches detected. Saving to 'mismatches.csv'")
    
    # Create a clean view of mismatches focusing only on the differences
    mismatch_view = mismatches[['gc_orgID', 
                               'harmonized_name_info', 'harmonized_name_concordance',
                               'nom_harmonisé_info', 'nom_harmonisé_concordance']]
    
    # Save mismatches to a CSV file for further analysis
    mismatch_file = os.path.join(parent_folder, 'mismatches.csv')
    mismatch_view.to_csv(mismatch_file, index=False)
else:
    print("\nNo mismatches found in common records.")

# Overall assessment
if len(info_only) > 0 or len(concord_only) > 0 or len(mismatches) > 0:
    print("\nDiscrepancies found between the datasets. See output files for details.")
else:
    print("\nThe datasets are consistent.")

import os
import pandas as pd

# Define the paths to the CSV files in the parent folder
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
gc_org_info_path = os.path.join(parent_folder, 'GC Org Info.csv')
gc_concordance_path = os.path.join(parent_folder, 'gc_concordance.csv')

# Load the CSV files
gc_org_info_df = pd.read_csv(gc_org_info_path)
gc_concordance_df = pd.read_csv(gc_concordance_path)

# Merge the dataframes on 'gc_orgID' to compare the values
merged_df = gc_org_info_df.merge(gc_concordance_df, on='gc_orgID', suffixes=('_info', '_concordance'))

# Find mismatches in 'harmonized_name' and 'nom_harmonisé'
mismatches = merged_df[(merged_df['harmonized_name_info'] != merged_df['harmonized_name_concordance']) |
                       (merged_df['nom_harmonisé_info'] != merged_df['nom_harmonisé_concordance'])]

# Print the first five mismatches
print("First five mismatches:")
print(mismatches[['gc_orgID', 'harmonized_name_info', 'harmonized_name_concordance', 'nom_harmonisé_info', 'nom_harmonisé_concordance']].head(5))

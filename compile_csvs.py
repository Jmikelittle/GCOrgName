import os
import pandas as pd
import glob

# Define the fields you want to compile from the specific CSVs
fields_manual_org = ['GC OrgID', 'Organization Legal Name English', 'Organization Legal Name French']

# Path to the folder containing the CSV files
csv_folder = os.path.dirname(os.path.abspath(__file__))

# Read the specified fields from 'Manual org ID link.csv'
manual_org_file = os.path.join(csv_folder, 'Manual org ID link.csv')
manual_org_df = pd.read_csv(manual_org_file, usecols=fields_manual_org)

# List other CSV files in the folder (excluding 'Manual org ID link.csv')
csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))
csv_files = [file for file in csv_files if 'Manual org ID link.csv' not in file]
print("CSV files found:", csv_files)

# Define the fields you want to compile from other CSVs
#fields_other_csvs = ['Field1', 'Field2']  # Replace with your actual field names

# List to hold individual DataFrames from other CSV files
dfs = [manual_org_df]  # Start with the manual_org_df

# Read the specific fields from each CSV file and append to the list of DataFrames
for file in csv_files:
    try:
        df = pd.read_csv(file, usecols=fields_other_csvs)
        dfs.append(df)
        print(f"Successfully read {file}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Concatenate all DataFrames into one
combined_df = pd.concat(dfs, ignore_index=True)

# Save the combined DataFrame to a new CSV file
output_file = os.path.join(csv_folder, 'GC Org Info.csv')
combined_df.to_csv(output_file, index=False)

print(f"All CSV files have been compiled into {output_file}")

import os
import glob
import pandas as pd

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))

# Print the current working directory and the path to the script's folder
print("Current Working Directory:", os.getcwd())
print("Script Folder Path:", script_folder)

# List all files in the script's folder
print("Files in the Script Folder:", os.listdir(script_folder))

# List CSV files matching the pattern 'FAA*.csv' in the script's folder
csv_files = glob.glob(os.path.join(script_folder, 'FAA*.csv'))
print("CSV files found:", csv_files)

# List to hold individual DataFrames
dfs = []

# Read each CSV file and append to the list of DataFrames
for file in csv_files:
    try:
        df = pd.read_csv(file)
        # Ensure all values in the 'FAA' column are strings
        df['FAA'] = df['FAA'].astype(str)
        dfs.append(df)
        print(f"Successfully read {file}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Check if there are any DataFrames to concatenate
if dfs:
    # Concatenate all DataFrames into one
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Trim whitespace from English Name and French Name columns
    combined_df['English Name'] = combined_df['English Name'].str.strip()
    combined_df['French Name'] = combined_df['French Name'].str.strip()
    
    # Define the priority order for the 'FAA' column
    priority_order = {'1': 1, '4': 2, '3': 3, '2': 4, 'i1': 5}
    
    # Map the priority order to a new column
    combined_df['priority'] = combined_df['FAA'].map(priority_order)
    
    # Sort the DataFrame based on English Name, French Name, and priority
    combined_df = combined_df.sort_values(by=['English Name', 'French Name', 'priority'])
    
    # Drop duplicates based on English Name and French Name, keeping the highest priority
    combined_df = combined_df.drop_duplicates(subset=['English Name', 'French Name'], keep='first')
    
    # Drop the priority column as it's no longer needed
    combined_df = combined_df.drop(columns=['priority'])
    
    # Sort the DataFrame based on the 'FAA' field for readability
    combined_df = combined_df.sort_values(by='FAA')
    
    # Save the combined DataFrame to a new CSV file with UTF-8 encoding
    combined_df.to_csv(os.path.join(script_folder, 'combined_FAA_names.csv'), index=False, encoding='utf-8-sig')
    
    print("All CSV files have been combined into combined_FAA_names.csv")
else:
    print("No DataFrames to concatenate")

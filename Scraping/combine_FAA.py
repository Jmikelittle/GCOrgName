import os
import glob
import pandas as pd

# Path to the 'Scraping' folder
scraping_folder = os.path.join(os.getcwd(), 'Scraping')

# Print the current working directory and the path to the 'Scraping' folder
print("Current Working Directory:", os.getcwd())
print("Scraping Folder Path:", scraping_folder)

# List all files in the 'Scraping' folder
print("Files in the Scraping Folder:", os.listdir(scraping_folder))

# List CSV files matching the pattern 'FAA*.csv' in the 'Scraping' folder
csv_files = glob.glob(os.path.join(scraping_folder, 'FAA*.csv'))
print("CSV files found:", csv_files)

# List to hold individual DataFrames
dfs = []

# Read each CSV file and append to the list of DataFrames
for file in csv_files:
    try:
        df = pd.read_csv(file)
        dfs.append(df)
        print(f"Successfully read {file}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Check if there are any DataFrames to concatenate
if dfs:
    # Concatenate all DataFrames into one
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Save the combined DataFrame to a new CSV file with UTF-8 encoding
    combined_df.to_csv(os.path.join(scraping_folder, 'combined_FAA_names.csv'), index=False, encoding='utf-8-sig')
    
    print("All CSV files have been combined into combined_FAA_names.csv")
else:
    print("No DataFrames to concatenate")

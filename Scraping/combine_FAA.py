import pandas as pd
import glob

# List of CSV files to combine
csv_files = glob.glob('FAA*.csv')

# Check which files are found
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
    combined_df.to_csv('combined_FAA_names.csv', index=False, encoding='utf-8-sig')
    
    print("All CSV files have been combined into combined_FAA_names.csv")
else:
    print("No DataFrames to concatenate")
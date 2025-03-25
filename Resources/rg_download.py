import os
import requests
import pandas as pd

# URL of the CSV file
url = 'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/min-dept/min-dept.csv'

# Path to save the downloaded CSV file
script_folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_folder, 'rg_data.csv')

# Download the CSV file
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the content to a temporary CSV file
    temp_file = os.path.join(script_folder, 'downloaded_file.csv')
    with open(temp_file, 'wb') as file:
        file.write(response.content)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(temp_file)

    # Print the original column names for debugging
    print(f"Original column names in the CSV: {', '.join(df.columns)}")

    # Rename the columns to the desired output names
    column_mapping = {
        'Department_number-Ministère_numéro': 'rgnumber',
        'Department-name_English-Ministère_nom_anglais': 'rg_dept_en',
        'Department_name_French': 'rg_dept_fr'
    }

    # Apply the column mapping, only for columns that exist
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
        else:
            print(f"Warning: Column '{old_name}' not found in the DataFrame.")

    # Format the rgnumber to be zero-padded to three digits and convert to string
    if 'rgnumber' in df.columns:
        df['rgnumber'] = df['rgnumber'].apply(lambda x: f"{int(x):03d}" if pd.notna(x) else x).astype(str)
    else:
        print("Warning: 'rgnumber' column not found after renaming.")

    # Print file path info for debugging
    print(f"Script folder: {script_folder}")
    print(f"Output file path: {output_file}")
    
    # Save the DataFrame to a CSV file with UTF-8-SIG encoding and verify it was saved
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    if os.path.exists(output_file):
        print(f"File was successfully saved to: {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
    else:
        print(f"Warning: The file was not saved to {output_file}. Check permissions or disk space.")
    
    # Clean up temporary file
    if os.path.exists(temp_file):
        os.remove(temp_file)

    print(f"The file has been downloaded and saved as {output_file}")
    print(f"Final column names in the output CSV: {', '.join(df.columns)}")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")

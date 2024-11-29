import os
import requests
import pandas as pd

# URL of the text file
url = 'https://www.tpsgc-pwgsc.gc.ca/recgen/pceaf-gwcoa/2425/fichiers-files/rg-3-num-eng.txt'

# Path to save the downloaded CSV file
script_folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_folder, 'receiver_general.csv')

# Download the text file
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the content to a text file
    with open('downloaded_file.txt', 'wb') as file:
        file.write(response.content)

    # Read the text file into a DataFrame
    df = pd.read_csv('downloaded_file.txt', sep="\t")  # Assuming the file is tab-separated

    # Format the numbers in the 'Number' field to be zero-padded to three digits and convert to string
    if 'Number' in df.columns:
        df['Number'] = df['Number'].apply(lambda x: f"{int(x):03d}" if pd.notna(x) else x).astype(str)
    else:
        print("Error: 'Number' column not found in the DataFrame.")

    # Rename the 'Name' column to 'RGOriginalName'
    if 'Name' in df.columns:
        df = df.rename(columns={'Name': 'RGOriginalName'})
    else:
        print("Error: 'Name' column not found in the DataFrame.")

    # Save the DataFrame to a CSV file with UTF-8-SIG encoding
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"The file has been downloaded and saved as {output_file}")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")

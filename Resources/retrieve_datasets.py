import os
import requests

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))

def download_and_fix_csv(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        # Decode the content to a string
        content = response.text
        print("Original content snippet:", content[:100])  # Print the first 100 characters of the original content
        # Replace non-breaking hyphens (U+2011) with regular hyphens (U+002D)
        fixed_content = content.replace('\u2011', '-')
        # Replace typographic apostrophes (U+2018 and U+2019) with regular apostrophes (U+0027)
        fixed_content = fixed_content.replace('\u2018', "'").replace('\u2019', "'")
        print("Fixed content snippet:", fixed_content[:100])  # Print the first 100 characters of the fixed content
        # Save the fixed content to a file with UTF-8 encoding
        file_path = os.path.join(script_folder, filename)
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(fixed_content)
        print(f'{filename} downloaded and fixed successfully!')
    else:
        print(f'Failed to download {filename}. Status code: {response.status_code}')

# Infobase Datasets
download_and_fix_csv('https://open.canada.ca/data/en/datastore/dump/7c131a87-7784-4208-8e5c-043451240d95?bom=True', 'infobase_en.csv')
download_and_fix_csv('https://open.canada.ca/data/en/datastore/dump/45069fe9-abe3-437f-97dd-3f64958bfa85?bom=True', 'infobase_fr.csv')

# Applied titles
download_and_fix_csv('https://open.canada.ca/data/en/datastore/dump/f0ca63e0-c15e-45b5-9656-77abe1564b1c?bom=True', 'applied_en.csv')
download_and_fix_csv('https://ouvert.canada.ca/data/fr/datastore/dump/f0ca63e0-c15e-45b5-9656-77abe1564b1c?bom=True', 'applied_fr.csv')

# Open Portal List Download
download_and_fix_csv('https://open.canada.ca/data/en/datastore/dump/04cbec5c-5a3d-4d34-927d-e41c9e6e3736?bom=True', 'ogp.csv')

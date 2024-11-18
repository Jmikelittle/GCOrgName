import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET

# Function to remove namespaces
def remove_namespace(doc, namespace):
    ns = '{' + namespace + '}'
    nsl = len(ns)
    for elem in doc.iter():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]
        if elem.attrib:
            for key in list(elem.attrib):
                if key.startswith(ns):
                    new_key = key[nsl:]
                    elem.attrib[new_key] = elem.attrib.pop(key)

# URL of the XML file
url = 'https://laws-lois.justice.gc.ca/eng/XML/F-11.xml'

# Path to the folder where the script is located
script_folder = os.path.dirname(os.path.abspath(__file__))

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the content of the request with ElementTree
    root = ET.fromstring(response.content)
    
    # Remove namespaces
    remove_namespace(root, 'http://justice.gc.ca/lims')
    
    # Lists to hold the data
    divisions_en = []
    divisions_fr = []
    faa_values = []

    # Find the tbody element with lims:id="230503"
    tbody = root.find('.//tbody[@id="230503"]')
    
    if tbody is not None:
        # Iterate through each row in the tbody
        for row in tbody.findall('.//row'):
            # Extract English and French division names
            division_entry_en = row.find('.//BilingualGroup//BilingualItemEn')
            division_entry_fr = row.find('.//BilingualGroup//BilingualItemFr')
            division_en = division_entry_en.text if division_entry_en is not None else None
            division_fr = division_entry_fr.text if division_entry_fr is not None else None
            
            if division_en and division_fr:
                divisions_en.append(division_en)
                divisions_fr.append(division_fr)
                faa_values.append('i1')

    # Create a DataFrame
    data = {'English Name': divisions_en, 'French Name': divisions_fr, 'FAA': faa_values}
    df = pd.DataFrame(data)
    
    # Save the DataFrame to a CSV file with UTF-8 encoding in the script's folder
    output_file_path = os.path.join(script_folder, 'FAA i1 names.csv')
    df.to_csv(output_file_path, index=True, encoding='utf-8-sig')
    print(f"DataFrame saved to {output_file_path}")
else:
    print(f'Failed to retrieve the XML file. Status code: {response.status_code}')

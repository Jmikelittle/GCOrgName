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
    
    # Lists to hold English and French names
    english_names = []
    french_names = []
    faa_values = []
    
    # Find all Schedule elements
    schedules = root.findall('.//Schedule')

    # Iterate through Schedule elements and look for BilingualGroup with id="230473"
    for schedule in schedules:
        section = schedule.find('.//BilingualGroup[@id="230473"]')
        
        if section is not None:
            # Extract all BilingualItemEn and BilingualItemFr elements
            english_items = section.findall('.//BilingualItemEn')
            french_items = section.findall('.//BilingualItemFr')
            
            # Append the text content to the respective lists
            for item in english_items:
                english_names.append(item.text)
            
            for item in french_items:
                french_names.append(item.text)
                faa_values.append('1')
    
    # Create a DataFrame
    data = {'English Name': english_names, 'French Name': french_names, 'FAA': faa_values}
    df = pd.DataFrame(data)
    
    # Save the DataFrame to a CSV file with UTF-8 encoding in the scripts folder
    output_file_path = os.path.join(script_folder, 'FAA 1 names.csv')
    df.to_csv(output_file_path, index=True, encoding='utf-8-sig')
    print(f"DataFrame saved to {output_file_path}")
else:
    print(f'Failed to retrieve the XML file. Status code: {response.status_code}')

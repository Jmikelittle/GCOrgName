import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import re

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

    # Iterate through Schedule elements and look for BilingualGroup with id="230535" or id="230572"
    for schedule in schedules:
        section_230535 = schedule.find('.//BilingualGroup[@id="230535"]')
        section_230572 = schedule.find('.//BilingualGroup[@id="230572"]')
        
        if section_230535 is not None:
            # Extract all BilingualItemEn and BilingualItemFr elements for id="230535"
            english_items_230535 = section_230535.findall('.//BilingualItemEn')
            french_items_230535 = section_230535.findall('.//BilingualItemFr')
            
            # Append the text content to the respective lists
            for item in english_items_230535:
                english_names.append(item.text)
            
            for item in french_items_230535:
                french_names.append(item.text)
                faa_values.append('3')
    
        if section_230572 is not None:
            # Extract all BilingualItemEn and BilingualItemFr elements for id="230572"
            english_items_230572 = section_230572.findall('.//BilingualItemEn')
            french_items_230572 = section_230572.findall('.//BilingualItemFr')
            
            # Append the text content to the respective lists
            for item in english_items_230572:
                english_names.append(item.text)
            
            for item in french_items_230572:
                french_names.append(item.text)
                faa_values.append('3')
    
    # Create a DataFrame
    data = {'English Name': english_names, 'French Name': french_names, 'FAA': faa_values}
    df = pd.DataFrame(data)
    
    # Save the DataFrame to a CSV file with UTF-8 encoding in the scripts folder
    output_file_path = os.path.join(script_folder, 'FAA 3 names.csv')
    df.to_csv(output_file_path, index=True, encoding='utf-8-sig')
    print(f"DataFrame saved to {output_file_path}")
else:
    print(f'Failed to retrieve the XML file. Status code: {response.status_code}')
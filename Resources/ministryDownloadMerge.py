import requests
import pandas as pd
import os

# Define paths
url_en = "https://www.ourcommons.ca/members/en/ministries/csv"
url_fr = "https://www.ourcommons.ca/members/fr/ministries/csv"
csv_path_en = 'Resources/ministries.csv'
csv_path_fr = 'Resources/ministries_fr.csv'
json_path = 'Resources/ministries.json'
manual_csv_path = 'Resources/manualMinistries.csv'

# Download the English CSV file
response_en = requests.get(url_en)
with open(csv_path_en, 'wb') as file:
    file.write(b'\xef\xbb\xbf')  # Write BOM
    file.write(response_en.content)
print("The English CSV file has been downloaded and saved as 'Resources/ministries.csv' with utf-8-sig encoding.")

# Download the French CSV file
response_fr = requests.get(url_fr)
with open(csv_path_fr, 'wb') as file:
    file.write(b'\xef\xbb\xbf')  # Write BOM
    file.write(response_fr.content)
print("The French CSV file has been downloaded and saved as 'Resources/ministries_fr.csv' with utf-8-sig encoding.")

# Load the downloaded CSVs into DataFrames
new_data_en = pd.read_csv(csv_path_en, encoding='utf-8-sig')
new_data_fr = pd.read_csv(csv_path_fr, encoding='utf-8-sig')

# Merge the English and French DataFrames on 'Precedence'
new_data = pd.merge(new_data_en, new_data_fr[['Precedence', 'Titre']], on='Precedence', how='left')

# Load the manually edited CSV into a DataFrame
manual_data = pd.read_csv(manual_csv_path)

# Remove BOM character if present
manual_data.columns = manual_data.columns.str.replace('\ufeff', '')

# Add a marker for new titles in new_data
new_data['minID'] = 'New Title'

# Set an empty notes field for new entries
new_data['notes'] = None

# Merge the data based on 'Title'
merged_data = pd.merge(manual_data, new_data, on='Title', how='outer', suffixes=('_manual', '_new'))

# Ensure all columns are present
columns = ['Precedence', 'Honorific Title', 'First Name', 'Last Name', 'Title', 'Province / Territory', 'Start Date', 'End Date', 'minID', 'notes', 'Titre']
for column in columns:
    if column not in merged_data.columns:
        merged_data[column] = None

# Update fields and track changes
def update_fields(row):
    if pd.isna(row.get('Precedence_manual')) and not pd.isna(row.get('Precedence_new')):  # New entry
        row['Precedence'] = row.get('Precedence_new')
        row['Honorific Title'] = row.get('Honorific Title_new')
        row['First Name'] = row.get('First Name_new')
        row['Last Name'] = row.get('Last Name_new')
        row['Province / Territory'] = row.get('Province / Territory_new')
        row['Start Date'] = row.get('Start Date_new')
        row['End Date'] = row.get('End Date_new')
        row['minID'] = 'New Title'
    elif pd.isna(row.get('Precedence_new')) and not pd.isna(row.get('Precedence_manual')):  # Title removed or changed
        row['notes'] = 'Title changed/deleted'
    else:  # Title exists, update fields if necessary
        row['Precedence'] = row.get('Precedence_new')
        row['Honorific Title'] = row.get('Honorific Title_new')
        row['First Name'] = row.get('First Name_new')
        row['Last Name'] = row.get('Last Name_new')
        row['Province / Territory'] = row.get('Province / Territory_new')
        row['Start Date'] = row.get('Start Date_new')
        row['End Date'] = row.get('End Date_new')
        row['minID'] = row.get('minID_manual')
        row['notes'] = row.get('notes_manual')
        row['Titre'] = row.get('Titre')
    return row

# Apply the update function to each row
merged_data = merged_data.apply(update_fields, axis=1)

# Drop the '_manual' and '_new' columns used for merging
merged_data = merged_data.drop(columns=[col for col in merged_data.columns if '_manual' in col or '_new' in col])

# Remove duplicate columns
merged_data = merged_data.loc[:, ~merged_data.columns.duplicated()]

# Sort the data by 'Precedence'
merged_data = merged_data.sort_values(by='Precedence', ascending=True)

# Save the updated data to manualMinistries.csv
merged_data.to_csv(manual_csv_path, index=False, encoding='utf-8-sig')
print(f"The data has been merged and saved to '{manual_csv_path}'.")

# Save the updated data as a JSON file
merged_data.to_json(json_path, orient='records', indent=4, force_ascii=False)
print(f"The data has been merged, updated, and saved as '{json_path}'.")

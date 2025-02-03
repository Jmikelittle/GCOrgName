import requests
import pandas as pd
import os

# Define paths
url = "https://www.ourcommons.ca/members/en/ministries/csv"
csv_path = 'Resources/ministries.csv'
json_path = 'Resources/ministries.json'
manual_csv_path = 'Resources/manualMinistries.csv'

# Download the CSV file
response = requests.get(url)
with open(csv_path, 'wb') as file:
    file.write(b'\xef\xbb\xbf')  # Write BOM
    file.write(response.content)
print("The CSV file has been downloaded and saved as 'Resources/ministries.csv' with utf-8-sig encoding.")

# Load the downloaded CSV into a DataFrame
new_data = pd.read_csv(csv_path, encoding='utf-8-sig')
print("New data loaded:\n", new_data)

# Load the manually edited CSV into a DataFrame
manual_data = pd.read_csv(manual_csv_path)

# Remove BOM character if present
manual_data.columns = manual_data.columns.str.replace('\ufeff', '')
print("Manual data loaded:\n", manual_data)

# Add a marker for new titles in new_data
new_data['minID'] = 'New Title'

# Set an empty notes field for new entries
new_data['notes'] = None

# Merge the data based on 'Title'
merged_data = pd.merge(manual_data, new_data, on='Title', how='outer', suffixes=('_manual', '_new'))
print("Merged data:\n", merged_data)

# Ensure all columns are present
columns = ['Precedence', 'Honorific Title', 'First Name', 'Last Name', 'Title', 'Province / Territory', 'Start Date', 'End Date', 'minID', 'notes']
for column in columns:
    if column not in merged_data.columns:
        merged_data[column] = None

# Update fields and track changes
def update_fields(row):
    print("\nProcessing row before update:", row.to_dict())
    
    title_manual = row.get('Title')
    title_new = row.get('Title')
    print(f"Comparing Titles: Manual: '{title_manual}', New: '{title_new}'")
    
    if pd.isna(row.get('Precedence_manual')) and not pd.isna(row.get('Precedence_new')):  # New entry
        print("New entry detected.")
        row['Precedence'] = row.get('Precedence_new')
        row['Honorific Title'] = row.get('Honorific Title_new')
        row['First Name'] = row.get('First Name_new')
        row['Last Name'] = row.get('Last Name_new')
        row['Province / Territory'] = row.get('Province / Territory_new')
        row['Start Date'] = row.get('Start Date_new')
        row['End Date'] = row.get('End Date_new')
        row['minID'] = 'New Title'
    elif pd.isna(row.get('Precedence_new')) and not pd.isna(row.get('Precedence_manual')):  # Title removed or changed
        print("Title removed or changed.")
        row['notes'] = 'Title changed/deleted'
    else:  # Title exists, update fields if necessary
        print("Updating existing entry.")
        row['Precedence'] = row.get('Precedence_new')
        row['Honorific Title'] = row.get('Honorific Title_new')
        row['First Name'] = row.get('First Name_new')
        row['Last Name'] = row.get('Last Name_new')
        row['Province / Territory'] = row.get('Province / Territory_new')
        row['Start Date'] = row.get('Start Date_new')
        row['End Date'] = row.get('End Date_new')
        row['minID'] = row.get('minID_manual')
        row['notes'] = row.get('notes_manual')
    
    print("Processing row after update:", row.to_dict())
    return row

# Apply the update function to each row
merged_data = merged_data.apply(update_fields, axis=1)
print("Merged data after updates:\n", merged_data)

# Drop the '_manual' and '_new' columns used for merging
merged_data = merged_data.drop(columns=[col for col in merged_data.columns if '_manual' in col or '_new' in col])
print("Merged data after dropping suffixes:\n", merged_data)

# Remove duplicate columns
merged_data = merged_data.loc[:, ~merged_data.columns.duplicated()]
print("Merged data after removing duplicates:\n", merged_data)

# Sort the data by 'Precedence'
merged_data = merged_data.sort_values(by='Precedence', ascending=True)
print("Sorted merged data:\n", merged_data)

# Save the updated data to manualMinistries.csv
merged_data.to_csv(manual_csv_path, index=False, encoding='utf-8-sig')
print(f"The data has been merged and saved to '{manual_csv_path}'.")

# Save the updated data as a JSON file
merged_data.to_json(json_path, orient='records', indent=4, force_ascii=False)
print(f"The data has been merged, updated, and saved as '{json_path}'.")

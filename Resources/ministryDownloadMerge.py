import requests
import pandas as pd
import os

print("Starting Ministry Download and Merge process...")

# Define paths
url_en = "https://www.ourcommons.ca/members/en/ministries/csv"
url_fr = "https://www.ourcommons.ca/members/fr/ministries/csv"
csv_path_en = 'Resources/ministries.csv'
csv_path_fr = 'Resources/ministries_fr.csv'
json_path = 'Resources/ministries.json'
manual_csv_path = 'Resources/manualMinistries.csv'

print(f"Downloading English CSV from {url_en}")
# Download the English CSV file
response_en = requests.get(url_en)
with open(csv_path_en, 'wb') as file:
    file.write(b'\xef\xbb\xbf')  # Write BOM
    file.write(response_en.content)
print(f"The English CSV file has been downloaded and saved as '{csv_path_en}' with utf-8-sig encoding.")

print(f"Downloading French CSV from {url_fr}")
# Download the French CSV file
response_fr = requests.get(url_fr)
with open(csv_path_fr, 'wb') as file:
    file.write(b'\xef\xbb\xbf')  # Write BOM
    file.write(response_fr.content)
print(f"The French CSV file has been downloaded and saved as '{csv_path_fr}' with utf-8-sig encoding.")

# Load the downloaded CSVs into DataFrames
print("Loading downloaded CSV files into DataFrames...")
new_data_en = pd.read_csv(csv_path_en, encoding='utf-8-sig')
new_data_fr = pd.read_csv(csv_path_fr, encoding='utf-8-sig')

print(f"English CSV loaded with {len(new_data_en)} rows and columns: {', '.join(new_data_en.columns.tolist())}")
print(f"French CSV loaded with {len(new_data_fr)} rows and columns: {', '.join(new_data_fr.columns.tolist())}")

# Rename French columns to match expected format
print("Renaming French columns to match expected format...")
column_map = {
    'Titre': 'Titre',
    'Precedence': 'Precedence',
    'Titre honorifique': 'Honorific Title_fr',
    'Prénom': 'First Name_fr',
    'Nom de famille': 'Last Name_fr',
    'Province / Territoire': 'Province / Territory_fr',
    'Date de début': 'Start Date_fr',
    'Date de fin': 'End Date_fr'
}
new_data_fr = new_data_fr.rename(columns=column_map)

# Create a mapping dictionary from English to French titles using Precedence as the key
print("Creating mapping from English to French titles...")
fr_titles_dict = {}
for _, row in new_data_fr.iterrows():
    precedence = row['Precedence']
    fr_title = row['Titre']
    fr_titles_dict[precedence] = fr_title

print(f"Found {len(fr_titles_dict)} French titles mapped by precedence")

# Add French titles to English dataframe
print("Adding French titles to English dataframe...")
new_data_en['Titre'] = new_data_en['Precedence'].map(fr_titles_dict)

# Show which French titles were mapped
mapped_count = sum(~new_data_en['Titre'].isna())
print(f"Successfully mapped {mapped_count} French titles out of {len(new_data_en)} English titles ({mapped_count/len(new_data_en)*100:.1f}%)")

# For debugging: Show any missing mappings
if mapped_count < len(new_data_en):
    print("Entries missing French titles:")
    missing_titles = new_data_en[new_data_en['Titre'].isna()]
    for _, row in missing_titles.iterrows():
        print(f"  - Precedence: {row['Precedence']}, Title: {row['Title']}")

# Load the manually edited CSV into a DataFrame
print(f"\nLoading manually edited CSV from {manual_csv_path}...")
manual_data = pd.read_csv(manual_csv_path)
print(f"Loaded manual data with {len(manual_data)} rows and columns: {', '.join(manual_data.columns.tolist())}")

# Remove BOM character if present
manual_data.columns = manual_data.columns.str.replace('\ufeff', '')

# Add a marker for new titles in new_data
new_data_en['minID'] = 'New Title'

# Set an empty notes field for new entries
new_data_en['notes'] = None

# Merge the data based on 'Title'
print("\nMerging manual data with new data based on 'Title'...")
merged_data = pd.merge(manual_data, new_data_en, on='Title', how='outer', suffixes=('_manual', '_new'))
print(f"Merged data has {len(merged_data)} rows")

# Debug merging issues
print(f"Rows only in manual data: {sum(pd.isna(merged_data['Precedence_new']) & ~pd.isna(merged_data['Precedence_manual']))}")
print(f"Rows only in new data: {sum(~pd.isna(merged_data['Precedence_new']) & pd.isna(merged_data['Precedence_manual']))}")
print(f"Rows in both datasets: {sum(~pd.isna(merged_data['Precedence_new']) & ~pd.isna(merged_data['Precedence_manual']))}")

# Ensure all columns are present
columns = ['Precedence', 'Honorific Title', 'First Name', 'Last Name', 'Title', 'Province / Territory', 'Start Date', 'End Date', 'minID', 'notes', 'Titre']
for column in columns:
    if column not in merged_data.columns:
        merged_data[column] = None

# Update fields and track changes
def update_fields(row):
    # Initialize a dictionary to store the updated row
    updated_row = {}
    
    # First, copy all the existing columns to the updated row
    for col in columns:
        if col in row:
            updated_row[col] = row[col]
        else:
            updated_row[col] = None
    
    if pd.isna(row.get('Precedence_manual')) and not pd.isna(row.get('Precedence_new')):  # New entry
        updated_row['Precedence'] = row.get('Precedence_new')
        updated_row['Honorific Title'] = row.get('Honorific Title_new')
        updated_row['First Name'] = row.get('First Name_new')
        updated_row['Last Name'] = row.get('Last Name_new')
        updated_row['Title'] = row.get('Title')
        updated_row['Province / Territory'] = row.get('Province / Territory_new')
        updated_row['Start Date'] = row.get('Start Date_new')
        updated_row['End Date'] = row.get('End Date_new')
        updated_row['minID'] = 'New Title'
        updated_row['notes'] = None
        updated_row['Titre'] = row.get('Titre_new', None)  # Get French title from new data
    elif pd.isna(row.get('Precedence_new')) and not pd.isna(row.get('Precedence_manual')):  # Title removed or changed
        updated_row['notes'] = 'Title changed/deleted'
        # Keep other existing values from manual data
        updated_row['Precedence'] = row.get('Precedence_manual')
        updated_row['Honorific Title'] = row.get('Honorific Title_manual')
        updated_row['First Name'] = row.get('First Name_manual')
        updated_row['Last Name'] = row.get('Last Name_manual')
        updated_row['Title'] = row.get('Title')
        updated_row['Province / Territory'] = row.get('Province / Territory_manual')
        updated_row['Start Date'] = row.get('Start Date_manual')
        updated_row['End Date'] = row.get('End Date_manual')
        updated_row['minID'] = row.get('minID_manual')
        updated_row['Titre'] = row.get('Titre_manual', None)  # Keep existing French title
    else:  # Title exists, update fields if necessary
        updated_row['Precedence'] = row.get('Precedence_new')
        updated_row['Honorific Title'] = row.get('Honorific Title_new')
        updated_row['First Name'] = row.get('First Name_new')
        updated_row['Last Name'] = row.get('Last Name_new')
        updated_row['Title'] = row.get('Title')
        updated_row['Province / Territory'] = row.get('Province / Territory_new')
        updated_row['Start Date'] = row.get('Start Date_new')
        updated_row['End Date'] = row.get('End Date_new')
        updated_row['minID'] = row.get('minID_manual')
        updated_row['notes'] = row.get('notes_manual')
        
        # Prioritize new French title if available, otherwise keep existing
        if not pd.isna(row.get('Titre_new')):
            updated_row['Titre'] = row.get('Titre_new')
        else:
            updated_row['Titre'] = row.get('Titre_manual')
    
    return pd.Series(updated_row)

print("\nApplying update function to each row...")
# Apply the update function to each row
try:
    updated_data = merged_data.apply(update_fields, axis=1)
except ValueError as e:
    print(f"Error during update_fields application: {e}")
    print("Row causing the error:")
    print(merged_data.loc[merged_data.apply(lambda row: update_fields(row).isna().any(), axis=1)])

# Sort the data by 'Precedence'
updated_data = updated_data.sort_values(by='Precedence', ascending=True)

# Display statistics about the French titles
print("\nVerifying French titles in final dataset:")
french_titles_count = sum(~updated_data['Titre'].isna())
print(f"Final data has {french_titles_count} French titles for {len(updated_data)} rows ({french_titles_count/len(updated_data)*100:.1f}%)")

# Show sample of data with French titles
print("Sample of data with French titles (first 5 rows):")
sample_with_fr = updated_data[~updated_data['Titre'].isna()].head(5)
for _, row in sample_with_fr.iterrows():
    print(f"  - {row['Title']} / {row['Titre']}")

# Show rows missing French titles
missing_fr_titles = updated_data[pd.isna(updated_data['Titre'])]
if not missing_fr_titles.empty:
    print(f"\nEntries missing French titles ({len(missing_fr_titles)}):")
    for _, row in missing_fr_titles.head(5).iterrows():
        print(f"  - {row['minID'] if not pd.isna(row['minID']) else 'N/A'}: {row['Title']}")
    if len(missing_fr_titles) > 5:
        print(f"  ... and {len(missing_fr_titles) - 5} more")

# Save the updated data to manualMinistries.csv
print(f"\nSaving updated data to {manual_csv_path}...")
updated_data.to_csv(manual_csv_path, index=False, encoding='utf-8-sig')
print(f"The data has been merged and saved to '{manual_csv_path}'.")

# Save the updated data as a JSON file
updated_data.to_json(json_path, orient='records', indent=4, force_ascii=False)
print(f"The data has been merged, updated, and saved as '{json_path}'.")

# Fix for fixLeadDepartment.py script
print("\nChecking for missing French titles that might affect fixLeadDepartment.py:")
m_ids = updated_data[pd.notna(updated_data['minID']) & updated_data['minID'].str.startswith('m')]
print(f"Found {len(m_ids)} entries with m-prefixed IDs")
missing_fr = m_ids[pd.isna(m_ids['Titre'])]
if not missing_fr.empty:
    print(f"Warning: Found {len(missing_fr)} ministries with missing French titles:")
    for _, row in missing_fr.iterrows():
        print(f"  - {row['minID']}: {row['Title']}")
else:
    print("All ministries have French titles. fixLeadDepartment.py should work correctly.")

print("\nMinistry Download and Merge process completed.")

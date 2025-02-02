import requests
import pandas as pd

# URL of the CSV file
url = "https://www.ourcommons.ca/members/en/ministries/csv"

# Send a GET request to the URL
response = requests.get(url)

# Save the content as 'ministries.csv' with utf-8-sig encoding to the Resources directory
csv_path = 'Resources/ministries.csv'
with open(csv_path, 'wb') as file:
    file.write(b'\xef\xbb\xbf')  # Write BOM
    file.write(response.content)

print("The CSV file has been downloaded and saved as 'Resources/ministries.csv' with utf-8-sig encoding.")

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(csv_path, encoding='utf-8-sig')

# Convert the DataFrame to a JSON file
json_path = 'Resources/ministries.json'
df.to_json(json_path, orient='records', indent=4, force_ascii=False)

print(f"The CSV file has been converted to JSON and saved as '{json_path}'.")

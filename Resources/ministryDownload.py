import requests

# URL of the CSV file
url = "https://www.ourcommons.ca/members/en/ministries/csv"

# Send a GET request to the URL
response = requests.get(url)

# Save the content as 'ministries.csv' with utf-8-sig encoding to the Resources directory
with open('Resources/ministries.csv', 'w', encoding='utf-8-sig') as file:
    file.write(response.text)

print("The CSV file has been downloaded and saved as 'Resources/ministries.csv' with utf-8-sig encoding.")

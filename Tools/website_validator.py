import requests
import csv
import os

def check_websites_from_csv(file_path):
    invalid_websites = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            website = row[0]
            if not website.startswith("http"):
                website = "http://" + website
            try:
                response = requests.get(website)
                if response.status_code != 200:
                    invalid_websites.append(website)
            except requests.exceptions.RequestException as e:
                invalid_websites.append(website)
    return invalid_websites

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the websites.csv file
file_path = os.path.join(current_dir, 'websites.csv')

# Check the validity of websites listed in websites.csv
invalid_websites = check_websites_from_csv(file_path)

print("Invalid websites:")
for website in invalid_websites:
    print(website)
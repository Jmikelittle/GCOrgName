There are lot of important files and scripts in this folder. 

Manual org ID link.csv is how all organizations are assigned an orgID. When new organizations are created, it's important to give them a new number that's never been used before, and include their legal name in English and in French (but for the purposes of this scripting, English is the most necessary piece here)

Below is an auto-generated summary
This folder contains various resources and scripts used for managing and updating data related to governmental ministries. Below is a summary of each file and an explanation of how the scripts interact with one another.

Files and Folders
ministries.csv
Description: This file contains the latest data of governmental ministries downloaded from an external source.

Purpose: Provides the source data for updates and comparisons against manually edited data.

manualMinistries.csv
Description: This file contains manually edited data of governmental ministries.

Purpose: Maintains manual changes, IDs, and notes for each ministry.

ministries.json
Description: A JSON representation of the merged and updated data from ministries.csv and manualMinistries.csv.

Purpose: Provides a structured, JSON format of the updated data for easy access and usage in web applications or other JSON-consuming services.

ministryDownload.py
Description: A script to download the latest ministries data and save it to ministries.csv.

Purpose: Ensures the local ministries.csv is always up-to-date with the latest external data.

ministryDownloadMerge.py
Description: A script to merge the data from ministries.csv and manualMinistries.csv, update fields as needed, and save the merged data to ministries.json.

Purpose: Merges new and manual data, updates fields, and maintains manual changes, IDs, and notes.

How the Scripts Interact
Download Latest Data:

Run ministryDownload.py to download the latest ministries data and save it to ministries.csv.

Merge and Update Data:

Run ministryDownloadMerge.py to merge the data from ministries.csv and manualMinistries.csv.

The script checks for changes, updates fields, and maintains manual changes, IDs, and notes.

The merged and updated data is saved to ministries.json.

Manual Updates:

Make manual edits directly in manualMinistries.csv for specific titles, IDs, or notes.

This setup ensures that the latest data is always integrated with your manual changes, providing a comprehensive and up-to-date view of governmental ministries.
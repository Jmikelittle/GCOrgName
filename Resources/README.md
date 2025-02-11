# Resources Folder Overview

There are a lot of important files and scripts in this folder.

`Manual org ID link.csv` is how all organizations are assigned an orgID. When new organizations are created, it's important to give them a new number that's never been used before, and include their legal name in English and in French (but for the purposes of this scripting, English is the most necessary piece here).

Below is an auto-generated summary of the files and scripts in this folder, along with an explanation of how the scripts interact with one another.

## Files and Folders

### `ministries.csv`
- **Description**: This file contains the latest data of governmental ministries downloaded from an external source.
- **Purpose**: Provides the source data for updates and comparisons against manually edited data.

### `manualMinistries.csv`
- **Description**: This file contains manually edited data of governmental ministries.
- **Purpose**: Maintains manual changes, IDs, and notes for each ministry.

### `ministries.json`
- **Description**: A JSON representation of the merged and updated data from `ministries.csv` and `manualMinistries.csv`.
- **Purpose**: Provides a structured, JSON format of the updated data for easy access and usage in web applications or other JSON-consuming services.

### `receiver_general.csv`
- **Description**: Contains original names and numbers for receiver general entries.
- **Purpose**: Source data for fuzzy matching and assigning organization IDs.

### `Manual org ID link.csv`
- **Description**: Contains the legal names of organizations in English and their assigned org IDs.
- **Purpose**: Provides the reference for assigning and verifying organization IDs.

### `RGDuplicates.csv`
- **Description**: Contains department names and their corresponding RG department numbers.
- **Purpose**: Provides additional names for fuzzy matching and ensures all departments are correctly assigned an RG number.

### `matched_RG_names.csv`
- **Description**: Output file containing the matched names and their corresponding RG numbers and organization IDs.
- **Purpose**: Provides the final matched results after processing and fuzzy matching.

## Scripts

### `ministryDownload.py`
- **Description**: A script to download the latest ministries data and save it to `ministries.csv`.
- **Purpose**: Ensures the local `ministries.csv` is always up-to-date with the latest external data.
- **Output**: `ministries.csv`

### `ministryDownloadMerge.py`
- **Description**: A script to merge the data from `ministries.csv` and `manualMinistries.csv`, update fields as needed, and save the merged data to `ministries.json`.
- **Purpose**: Merges new and manual data, updates fields, and maintains manual changes, IDs, and notes.
- **Output**: `ministries.json`

### `RGTableTransform.py`
- **Description**: A script to read an HTML file containing RG department numbers, convert the table to a JSON string, and save it to a file.
- **Purpose**: Converts HTML table data to JSON format for further processing.
- **Output**: `RGDuplicates.json`

### `final_RG_match.py`
- **Description**: A script to standardize text, replace values based on match scores, identify new entries, and merge fields from `Fixed_RG_names.csv` to `final_RG_match.csv`.
- **Purpose**: Ensures all RG names are correctly matched and updated with the latest information.
- **Output**: `final_RG_match.csv`

### `fuzzy_match_rg_names.py`
- **Description**: A script to perform fuzzy matching of RG names from `receiver_general.csv` and `RGDuplicates.csv` against `Manual org ID link.csv`, and save the matched results.
- **Purpose**: Matches RG names to their corresponding organization IDs using fuzzy matching.
- **Output**: `matched_RG_names.csv`

## How the Scripts Interact

### Download Latest Data:
1. Run `ministryDownload.py` to download the latest ministries data and save it to `ministries.csv`.

### Merge and Update Data:
1. Run `ministryDownloadMerge.py` to merge the data from `ministries.csv` and `manualMinistries.csv`.
2. The script checks for changes, updates fields, and maintains manual changes, IDs, and notes.
3. The merged and updated data is saved to `ministries.json`.

### Fuzzy Matching and Updating RG Names:
1. Run `fuzzy_match_rg_names.py` to perform fuzzy matching of RG names from `receiver_general.csv` and `RGDuplicates.csv` against `Manual org ID link.csv`.
2. The matched results are saved to `matched_RG_names.csv`.

### Final Matching and Merging:
1. Run `final_RG_match.py` to standardize text, replace values based on match scores, identify new entries, and merge fields from `Fixed_RG_names.csv` to `final_RG_match.csv`.
2. The final matched results are saved to `final_RG_match.csv`.

### Manual Updates:
1. Make manual edits directly in `manualMinistries.csv` for specific titles, IDs, or notes.

This setup ensures that the latest data is always integrated with your manual changes, providing a comprehensive and up-to-date view of governmental ministries.
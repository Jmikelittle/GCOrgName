# Resources Folder Overview

There are a lot of important files and scripts in this folder.

`Manual org ID link.csv` is how all organizations are assigned an orgID. When new organizations are created, it's important to give them a new number that's never been used before, and include their legal name in English and in French (but for the purposes of this scripting, English is the most necessary piece here).
Please note that the correct legal name needs to be used, and is manually entered. It is not automatically sourced from the Financial Administration Action, however the FAA is available in the scraping folder. 

Below is an auto-generated summary of the files and scripts in this folder, along with an explanation of how the scripts interact with one another.

# Actions to Complete

**Update workflow, in order**
1. retrieve_datasets.py
(Probably not necessary, Receiver General only changes annually)
2a. receiver_general.py
2b. fuzzy_match_rg_names.py
2c. Fixed_RG_names.csv - manually update the GCOrgID for any new entries that arn't linked up automatically
2d. final_RG_match.py
3. ministryDownloadMerge.py
4. manualMinistries.csv - find new ministers or title changes, then manually update the minID
5. manual pop phoenix.csv - update any changes to the HR Codes or Phoneix Codes. 

## Files and Folders

### `ministries.csv`
- **Description**: This file contains the latest data of Ministers and their titles from the House of Commons.
- **Purpose**: Provides the source data for updates and comparisons against manually edited data.

### `ministries.json`
- **Description**: A JSON representation of the merged and updated data from `ministries.csv` and `manualMinistries.csv`.
- **Purpose**: Provides a structured, JSON format of the updated data for easy access and usage in web applications or other JSON-consuming services.

### `manualMinistries.csv`
- **Description**: This file contains manually edited data of ministries. Names of ministers come from ministries.csv and a separate identifier is added to help structure the data and link it to portfolios in create_gcOrgInfo.py.
- **Purpose**: Maintains manual changes, IDs, and notes for each minister.
- **Important Note**: When there is a change to the Ministry

### `receiver_general.csv`
- **Description**: Contains original names and numbers for receiver general entries. This is an annual release and needs to be updated yearly based on the new url.
- **Purpose**: Source data for fuzzy matching and assigning RG IDs.

### `Manual org ID link.csv`
- **Description**: The only way to match the legal names to GC orgIDs.
- **Purpose**: Provides the reference for assigning and verifying organization IDs.

### `RGDuplicates.csv`
- **Description**: A list of small organizations that share an RG number with a larger organization, but do not appear on the main receiver_general.csv list.
- **Purpose**: Provides additional names for fuzzy matching and ensures all departments are correctly assigned an RG number.

### `matched_RG_names.csv`
- **Description**: Output file containing the matched names and their corresponding RG numbers and GC orgIDs.
- **Purpose**: Provides the final matched results after processing and fuzzy matching.

## Scripts

### `ministryDownload.py`
- **Description**: A script to download the latest ministerial titles and save it to `ministries.csv`.
- **Purpose**: Ensures the local `ministries.csv` is always up-to-date with the latest external data.
- **Output**: `ministries.csv`

### `ministryDownloadMerge.py`
- **Description**: A script to merge the data from `ministries.csv` and `manualMinistries.csv`, update fields as needed, and save the merged data to `ministries.json`.
- **Purpose**: Merges new and manual data, updates fields, and maintains manual changes, IDs, and notes.
- **Output**: `ministries.json`

### `final_RG_match.py`
- **Description**: A script to standardize text, replace values based on match scores, identify new entries, and merge fields from `Fixed_RG_names.csv` to `final_RG_match.csv`.
- **Purpose**: Ensures all RG names are correctly matched and updated with the latest information.
- **Output**: `final_RG_match.csv`

### `fuzzy_match_rg_names.py`
- **Description**: A script to perform fuzzy matching of RG names from `receiver_general.csv` and `RGDuplicates.csv` against `Manual org ID link.csv`, and save the matched results.
- **Purpose**: Matches RG names to their corresponding organization IDs using fuzzy matching.
- **Output**: `matched_RG_names.csv`

## How the Scripts Interact - To be validated

### Download Latest Data:
1. Run `ministryDownload.py` to download the latest ministries data and save it to `ministries.csv`.

### Merge and Update Data:
1. Run `ministryDownloadMerge.py` to merge the data from `ministries.csv` and `manualMinistries.csv`.
2. The script checks for changes, updates fields, and maintains manual changes, IDs, and notes.
3. The merged and updated data is saved to `ministries.json` and `ministries.csv`.

### Fuzzy Matching and Updating RG Names:
1. Run `fuzzy_match_rg_names.py` to perform fuzzy matching of RG names from `receiver_general.csv` and `RGDuplicates.csv` against the legal titles in `Manual org ID link.csv`, in order to pull in GC orgIDs.
2. The matched results are saved to `matched_RG_names.csv`.
3. 

### Final Matching and Merging:
1. Run `final_RG_match.py` to standardize text, replace values based on match scores, identify new entries, and merge fields from `Fixed_RG_names.csv` to `final_RG_match.csv`.
2. The final matched results are saved to `final_RG_match.csv`.

### Manual Updates:
1. Make manual edits directly in `manualMinistries.csv` for specific titles, IDs, or notes.

This setup ensures that the latest data is always integrated with your manual changes, providing a comprehensive and up-to-date view of governmental ministries.
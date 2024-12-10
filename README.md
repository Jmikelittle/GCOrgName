# GCOrgName
Compile most used GC org names to get one harmonized name and ID number. 

This project combines information from several open datasets, with data from the Receiver General, Federal Identity Program, Infobase, the Financial Administration Act and the Open Government Portal. 
There are also manual components with both the assigning of Organizational ID numbers to each organization, as well as manually assigned HR and Pay related identifiers. As well, occasionally values will be overwritten when they are out of date in a source (like when a department name changes in one source but not another)


Sometimes there are names which need to be changed from source data. For example, several entries from the FAA have been changed to better explain what those organizations are. These changes have been made in the 'combine_csvs_to_script_folder.py'
In the FAA, the Offices of the Information and Privacy Commissioners are considered the same organization. However they are operated as separate organizations, and that real-world situation is reflected in the official list of GC organizations. This change is created in the 'combine_csvs_to_script_folder.py' script. 
Reflecting the Officies of the Information and Privacy Commissioners requires several manual changes. 

This main folder hosts the primary datasets, GC Org Info.csv and gc_concordance.csv, along with the scripts which create them. However, there are several other scripts which are important for updating source data located in this repo. 

Resources
This folder contains all datasets which can be downloaded from the web, along with some documents which must be manually kept up to date. 

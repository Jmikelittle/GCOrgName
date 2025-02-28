"""Module for combining FAA CSV files and handling specific data transformations."""
import os
import glob
import pandas as pd


def remove_specific_values(dataframe, filename):
    """
    Remove specific values from the DataFrame based on filename.

    Args:
        dataframe: DataFrame to process
        filename: Name of the file being processed

    Returns:
        DataFrame with specific values removed
    """
    if filename == 'FAA 4 names.csv':
        # Remove specific long entry
        long_entry = ("The portion of the federal public administration in the "
                     "Office of the Chief Electoral Officer in which the employees "
                     "referred to in section 509.3 of the")
        dataframe = dataframe[dataframe['English Name'].str.strip() != long_entry]
        dataframe = dataframe[
            dataframe['English Name'] != "Office of the Governor General's Secretary"]
        dataframe = dataframe[
            dataframe['English Name'] != "Staff of the Supreme Court"]
        dataframe = dataframe[
            dataframe['English Name'] != 
            "Offices of the Information and Privacy Commissioners of Canada"]
    elif filename == 'FAA 5 names.csv':
        dataframe = dataframe[
            dataframe['English Name'] != "Office of the Auditor General of Canada"]
    elif filename == 'FAA i1 names.csv':
        dataframe = dataframe[
            dataframe['English Name'] != 
            "Offices of the Information and Privacy Commissioners of Canada"]
    return dataframe


def main():
    """Main function to process and combine CSV files."""
    # Path to the folder where the script is located
    script_folder = os.path.dirname(os.path.abspath(__file__))

    # List CSV files matching the pattern 'FAA*.csv' in the script's folder
    csv_files = glob.glob(os.path.join(script_folder, 'FAA*.csv'))

    # List to hold individual DataFrames
    dfs = []

    # Read each CSV file, filter out specific values, and append to the list
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            
            # Ensure all values in the 'FAA' column are strings
            df['FAA'] = df['FAA'].astype(str)
            
            # Filter out specific values
            df = remove_specific_values(df, os.path.basename(file))
            
            dfs.append(df)
        except (pd.errors.EmptyDataError, pd.errors.ParserError,
                FileNotFoundError) as error:
            print(f"Error reading {file}: {error}")

    # Check if there are any DataFrames to concatenate
    if dfs:
        # Concatenate all DataFrames into one
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Overrides: Add the specified information manually
        new_data = {
            'English Name': [
                'Office of the Information Commissioner',
                'Office of the Privacy Commissioner of Canada'
            ],
            'French Name': [
                "Commissariat à l'information au Canada",
                'Commissariat à la protection de la vie privée du Canada'
            ],
            'FAA': ['4', '4']
        }
        new_df = pd.DataFrame(new_data)
        combined_df = pd.concat([combined_df, new_df], ignore_index=True)
        
        # Renaming: Update specific entries
        combined_df.loc[combined_df['English Name'] == "Registrar of the Supreme Court of Canada and that portion of the federal public administration appointed under subsection 12(2) of the Supreme Court Act", 'English Name'] = "Supreme Court of Canada"
        
        # Trim whitespace from English Name and French Name columns
        combined_df['English Name'] = combined_df['English Name'].str.replace('’', "'").str.strip()
        combined_df['French Name'] = combined_df['French Name'].str.replace('’', "'").str.strip()
        
        # Define the priority order for the 'FAA' column
        priority_order = {'1': 1, 'i1': 2, '4': 3, '2': 4, '3': 5, '5': 6}
        
        # Map the priority order to a new column
        combined_df['priority'] = combined_df['FAA'].map(priority_order)
        
        # Sort the DataFrame based on English Name, French Name, and priority
        combined_df = combined_df.sort_values(by=['English Name', 'French Name', 'priority'])
        
        # Drop duplicates based on English Name and French Name, keeping the highest priority
        combined_df = combined_df.drop_duplicates(subset=['English Name', 'French Name'], keep='first')
        
        # Drop the priority column as it's no longer needed
        combined_df = combined_df.drop(columns=['priority'])
        
        # Sort the DataFrame based on the 'FAA' field for readability
        combined_df = combined_df.sort_values(by='FAA')
        
        # Sort the DataFrame based on the 'English Name' field alphabetically
        combined_df = combined_df.sort_values(by='English Name')
        
        # Save the combined DataFrame to a new CSV file with UTF-8 encoding
        combined_df.to_csv(os.path.join(script_folder, 'combined_FAA_names.csv'), index=False, encoding='utf-8-sig')
        
        print("All CSV files have been combined into combined_FAA_names.csv")
    else:
        print("No DataFrames to concatenate")


if __name__ == "__main__":
    main()

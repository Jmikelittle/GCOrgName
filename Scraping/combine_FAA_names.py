"""Module for combining FAA CSV files and handling specific data transformations."""
import os
import glob
import pandas as pd


def remove_specific_values(dataframe, filename):
    """
    Remove specific values from the DataFrame based on filename.
    This function filters out entries that should not appear in the final output,
    either because they are duplicates or because they will be replaced with
    updated names in the overrides section.

    Args:
        dataframe: DataFrame to process - contains columns 'English Name', 'French Name', 'FAA'
        filename: Name of the file being processed - determines which filters to apply

    Returns:
        DataFrame with specific values removed based on the file type:
        - FAA 4: Removes long electoral entry, Governor General's Secretary, Supreme Court staff
        - FAA 5: Removes Auditor General entry (will be renamed later)
        - FAA i1: Removes Information and Privacy Commissioner entries (split into two later)
    """
    # For Schedule 4 of the FAA, remove specific entries
    if filename == 'FAA 4 names.csv':
        # Remove the truncated electoral office entry - it's incomplete
        long_entry = ("The portion of the federal public administration in the "
                     "Office of the Chief Electoral Officer in which the employees "
                     "referred to in section 509.3 of the")
        dataframe = dataframe[dataframe['English Name'].str.strip() != long_entry]
        
        # Remove entries that will be handled differently. The Priority is not removing these, so they're being removed here. 
        dataframe = dataframe[
            dataframe['English Name'] != "Office of the Governor General's Secretary"] #fun note that the French is translated different in schedules i1 and 4. 
        dataframe = dataframe[
            dataframe['English Name'] != "Staff of the Supreme Court"] #Only using one entry for the Supreme Court.
        dataframe = dataframe[
            dataframe['English Name'] != 
            "Offices of the Information and Privacy Commissioners of Canada"] #these organzations are split into two throughout this Data Reference Standard
    
    # For Schedule 5, remove entry that is not being removed in the priority section
    elif filename == 'FAA 5 names.csv':
        dataframe = dataframe[
            dataframe['English Name'] != "Office of the Auditor General of Canada"]
    
    # For Schedule i1, remove entry that will be split into two
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
        
        # Remove any 'Unnamed' columns
        unnamed_cols = [col for col in combined_df.columns if 'Unnamed' in col]
        if unnamed_cols:
            combined_df = combined_df.drop(columns=unnamed_cols)
        
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
        combined_df.loc[
            combined_df['English Name'] == (
                "Registrar of the Supreme Court of Canada and that portion of the "
                "federal public administration appointed under subsection 12(2) of "
                "the Supreme Court Act"
            ), 'English Name'
        ] = "Registrar of the Supreme Court of Canada"
        combined_df.loc[
            combined_df['French Name'] == (
                "Registraire de la Cour suprême du Canada et le secteur de l’administration publique fédérale nommé en vertu du paragraphe 12(2) de la Loi sur la Cour suprême"
            ), 'French Name'
        ] = "Registraire de la Cour suprême du Canada"

        # Trim whitespace from English Name and French Name columns
        combined_df['English Name'] = combined_df['English Name'].str.replace('’', "'").str.strip()
        combined_df['French Name'] = combined_df['French Name'].str.replace('’', "'").str.strip()
        
        # Define the priority order for the 'FAA' column
        priority_order = {'1': 1, 'i1': 2, '2': 3, '4': 4, '3': 5, '5': 6}
        
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
        output_file = os.path.join(script_folder, 'combined_FAA_names.csv')
        combined_df.to_csv(
            output_file,
            index=False,
            encoding='utf-8-sig'
        )
        
        print(f"Created {output_file}")
    else:
        print("No CSV files found to combine")


if __name__ == "__main__":
    main()

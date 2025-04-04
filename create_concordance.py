"""
This module creates a concordance of Government of Canada organizations
by merging data from multiple sources.
"""
import os
import logging
from typing import Dict, Tuple, List

import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_required_columns(df: pd.DataFrame, required_columns: List[str], df_name: str) -> None:
    """
    Ensure that a DataFrame has the required columns.
    
    Args:
        df: DataFrame to check
        required_columns: List of column names that must exist
        df_name: Name of the DataFrame for logging purposes
        
    Raises:
        ValueError: If any required column is missing
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        error_msg = f"Missing required columns in {df_name}: {missing_columns}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def setup_paths() -> Dict[str, str]:
    """
    Define and return important directory paths used in the script.
    
    Returns:
        Dict containing paths to script directory, resources, and scraping folders
    """
    script_folder = os.path.dirname(os.path.abspath(__file__))
    return {
        'script': script_folder,
        'resources': os.path.join(script_folder, 'Resources'),
        'scraping': os.path.join(script_folder, 'Scraping')
    }


def load_dataframes(paths: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """
    Load all required CSV files into dataframes.
    
    Args:
        paths: Dictionary containing file paths
        
    Returns:
        Dictionary of loaded dataframes
        
    Raises:
        Exception: If any file cannot be loaded
    """
    files = {
        'manual_org_df': os.path.join(paths['resources'], 'Manual org ID link.csv'),
        'combined_faa_df': os.path.join(paths['scraping'], 'combined_FAA_names.csv'),
        'applied_en_df': os.path.join(paths['resources'], 'applied_en.csv'),
        'infobase_en_df': os.path.join(paths['resources'], 'infobase_en.csv'),
        'infobase_fr_df': os.path.join(paths['resources'], 'infobase_fr.csv'),
        'final_rg_match_df': os.path.join(paths['resources'], 'rg_final.csv'),
        'manual_pop_phoenix_df': os.path.join(paths['resources'], 'manual pop phoenix.csv'),
        'harmonized_names_df': os.path.join(paths['script'], 'create_harmonized_name.csv')
    }
    
    dfs = {}
    for name, path in files.items():
        try:
            dfs[name] = pd.read_csv(path)
            logger.info("Successfully loaded %s from %s", name, path)
        except Exception as e:
            logger.error("Error loading %s from %s: %s", name, path, str(e))
            raise
    
    return dfs


def standardize_dataframes(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Clean and standardize all dataframes.
    
    Args:
        dfs: Dictionary of dataframes to standardize
        
    Returns:
        Dictionary of standardized dataframes
    """
    # Standardize text
    for name, df in dfs.items():
        dfs[name] = df.apply(
            lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() 
            if x.dtype == "object" else x
        )
    
    # Convert 'gc_orgID' to string
    for name, df in dfs.items():
        if 'gc_orgID' in df.columns:
            df['gc_orgID'] = df['gc_orgID'].astype(str)
    
    # Rename columns for joining
    dfs['combined_faa_df']['Original English Name'] = dfs['combined_faa_df']['English Name']
    dfs['combined_faa_df'] = dfs['combined_faa_df'].rename(
        columns={'English Name': 'Organization Legal Name English'}
    )
    
    # Convert 'OrgID' in infobase_fr_df to int for merging
    dfs['infobase_fr_df']['OrgID'] = dfs['infobase_fr_df']['OrgID'].astype(int)
    
    return dfs


def create_initial_merge(dfs: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create the initial merge and identify unmatched values.
    
    Args:
        dfs: Dictionary of dataframes
        
    Returns:
        Tuple containing (matched_dataframe, unmatched_dataframe)
    """
    final_joined_df = dfs['manual_org_df'].merge(
        dfs['combined_faa_df'], 
        on='Organization Legal Name English', 
        how='outer'
    )
    
    # Flag matched and unmatched rows
    final_joined_df['Names Match'] = final_joined_df.apply(
        lambda row: 0 if pd.notna(row['Organization Legal Name English']) else 1, 
        axis=1
    )
    
    # Separate unmatched values
    unmatched_values = final_joined_df[final_joined_df['Names Match'] == 1].copy()
    matched_values = final_joined_df[final_joined_df['Names Match'] == 0].copy()
    
    return matched_values, unmatched_values


def merge_additional_data(final_joined_df: pd.DataFrame, 
                          dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge additional data from various sources.
    
    Args:
        final_joined_df: Dataframe to merge data into
        dfs: Dictionary of source dataframes
        
    Returns:
        Dataframe with additional data merged
    """
    # Define merges to perform
    merge_columns = [
        ('applied_en_df', 'Legal title', 
         ['Legal title', 'Applied title', "Titre d'usage", 'Abbreviation', 'Abreviation']),
        ('infobase_en_df', 'Legal title', 
         ['Legal title', 'OrgID', 'Website'])
    ]
    
    # Perform merges
    for df_name, on_col, columns in merge_columns:
        final_joined_df = final_joined_df.merge(
            dfs[df_name][columns], 
            left_on='Organization Legal Name English', 
            right_on=on_col, 
            how='left'
        )
    
    # Pull in harmonized names
    harmonized_cols = ['gc_orgID', 'harmonized_name', 'nom_harmonisé']
    harmonized_names_df = dfs['harmonized_names_df'][harmonized_cols]
    final_joined_df = final_joined_df.merge(
        harmonized_names_df, 
        on='gc_orgID', 
        how='left'
    )
    
    # Standardize columns
    final_joined_df['gc_orgID'] = final_joined_df['gc_orgID'].astype(str).str.split('.').str[0]
    final_joined_df = final_joined_df.rename(
        columns={'OrgID': 'infobaseID', 'Website': 'website'}
    )
    final_joined_df['infobaseID'] = final_joined_df['infobaseID'].fillna(0).astype(int)
    
    # Merge RG numbers
    rg_cols = ['gc_orgID', 'rgnumber']
    final_joined_df = final_joined_df.merge(
        dfs['final_rg_match_df'][rg_cols], 
        on='gc_orgID', 
        how='left'
    )
    final_joined_df = final_joined_df.rename(columns={'rgnumber': 'rg'})
    
    def format_rg_value(value):
        """Format RG value appropriately"""
        if pd.isna(value):
            return ''
        return '' if value == 0 else int(value)
        
    final_joined_df['rg'] = final_joined_df['rg'].apply(format_rg_value)
    
    # Merge French info
    fr_cols = ['OrgID', 'Appellation legale', 'Site Web']
    final_joined_df = final_joined_df.merge(
        dfs['infobase_fr_df'][fr_cols], 
        left_on='infobaseID', 
        right_on='OrgID', 
        how='left'
    )
    final_joined_df = final_joined_df.rename(columns={'Site Web': 'site_web'})
    
    # Merge POP and Phoenix data
    final_joined_df = final_joined_df.merge(
        dfs['manual_pop_phoenix_df'], 
        on='gc_orgID', 
        how='left'
    )
    
    # Clean up column names after merge
    if 'gc_orgID_y' in final_joined_df.columns:
        final_joined_df = final_joined_df.drop(columns=['gc_orgID_y'])
    if 'gc_orgID_x' in final_joined_df.columns:
        final_joined_df = final_joined_df.rename(columns={'gc_orgID_x': 'gc_orgID'})
    
    # Remove duplicates
    final_joined_df = final_joined_df.drop_duplicates(subset=['gc_orgID'])
    
    # Rename fields for consistency
    final_joined_df = final_joined_df.rename(
        columns={
            'Abbreviation': 'abbreviation', 
            'Abreviation': 'abreviation'
        }
    )
    
    return final_joined_df


def apply_manual_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply manual changes to specific entries.
    
    Args:
        df: Dataframe to apply changes to
        
    Returns:
        Dataframe with manual changes applied
    """
    manual_changes = {
        # Office of the Information Commissioner
        "2281": {
            "abbreviation": "OIC", 
            "abreviation": "CI",
            "infobaseID": 256,
            "website": "https://www.oic-ci.gc.ca/en",
            "site_web": "https://www.oic-ci.gc.ca/fr"
        },  
        # Office of the Privacy Commissioner
        "2282": {
            "abbreviation": "OPC", 
            "abreviation": "CPVP",
            "infobaseID": 256,
            "website": "https://www.priv.gc.ca/en/",
            "site_web": "https://www.priv.gc.ca/fr/"
        },
    }
    
    for gc_orgid, changes in manual_changes.items():
        for field, value in changes.items():
            df.loc[df['gc_orgID'] == gc_orgid, field] = value
    
    return df


def finalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finalize the dataframe for output.
    
    Args:
        df: Dataframe to finalize
        
    Returns:
        Finalized dataframe ready for output
    """
    # Replace zero values in 'infobaseID' with blank strings
    df['infobaseID'] = df['infobaseID'].replace(0, '')
    
    # Ensure 'site_web' column exists
    if 'site_web' not in df.columns:
        df['site_web'] = None
    
    # Reorder and sort columns
    final_field_order = [
        'gc_orgID', 'harmonized_name', 'nom_harmonisé', 
        'abbreviation', 'abreviation', 'infobaseID', 'rg', 
        'ati', 'open_gov_ouvert', 'pop', 'phoenix', 
        'website', 'site_web'
    ]
    
    df = df[final_field_order].sort_values(by='gc_orgID')
    return df


def validate_unmatched_data(unmatched_df: pd.DataFrame) -> None:
    """
    Validate the unmatched data to ensure data quality.
    
    Args:
        unmatched_df: Dataframe containing unmatched records
        
    Logs information about the unmatched data for review
    """
    if unmatched_df.empty:
        logger.info("No unmatched records found - data appears to be clean!")
        return
        
    # Count records by column with missing values
    missing_counts = unmatched_df.isna().sum()
    logger.info("Unmatched records analysis:")
    logger.info("Total unmatched records: %d", len(unmatched_df))
    logger.info("Missing values by column: %s", missing_counts.to_string())
    
    # Report specific columns of interest
    if 'gc_orgID' in unmatched_df.columns:
        missing_ids = unmatched_df[unmatched_df['gc_orgID'].isna()].shape[0]
        logger.info("Records missing gc_orgID: %d", missing_ids)
    
    # Additional validation could be added here


def save_results(df: pd.DataFrame, unmatched_df: pd.DataFrame, script_folder: str) -> None:
    """
    Save the final dataframes to CSV files.
    
    Args:
        df: Final dataframe to save
        unmatched_df: Unmatched records dataframe to save
        script_folder: Folder path for output files
        
    Raises:
        Exception: If files cannot be saved
    """
    output_file = os.path.join(script_folder, 'gc_concordance.csv')
    unmatched_output_file = os.path.join(script_folder, 'unmatched_org_IDs.csv')
    
    try:
        # Validate unmatched data before saving
        validate_unmatched_data(unmatched_df)
        
        # Save files
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        unmatched_df.to_csv(unmatched_output_file, index=False, encoding='utf-8-sig')
        
        logger.info("The final joined DataFrame has been saved to %s", output_file)
        logger.info("The unmatched values have been saved to %s", unmatched_output_file)
    except Exception as e:
        logger.error("Error saving results: %s", str(e))
        raise


def main() -> None:
    """
    Main function to orchestrate the concordance creation process.
    """
    try:
        # Setup paths and load data
        paths = setup_paths()
        dfs = load_dataframes(paths)
        dfs = standardize_dataframes(dfs)
        
        # Create initial merge and identify unmatched values
        final_joined_df, unmatched_values = create_initial_merge(dfs)
        
        # Merge additional data
        final_joined_df = merge_additional_data(final_joined_df, dfs)
        
        # Apply manual changes
        final_joined_df = apply_manual_changes(final_joined_df)
        
        # Finalize dataframe
        final_joined_df = finalize_dataframe(final_joined_df)
        
        # Save results
        save_results(final_joined_df, unmatched_values, paths['script'])
        
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise


if __name__ == "__main__":
    main()

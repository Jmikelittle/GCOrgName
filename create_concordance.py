"""Module for creating GC organization concordance file."""
import os
import pandas as pd


def load_dataframes(script_dir, resources_dir, scraping_dir):
    """Load and standardize all required CSV files."""
    files = {
        'manual_org_df': os.path.join(resources_dir, 'Manual org ID link.csv'),
        'combined_faa_df': os.path.join(scraping_dir, 'combined_FAA_names.csv'),
        'applied_en_df': os.path.join(resources_dir, 'applied_en.csv'),
        'infobase_en_df': os.path.join(resources_dir, 'infobase_fr.csv'),
        'infobase_fr_df': os.path.join(resources_dir, 'infobase_fr.csv'),
        'final_rg_match_df': os.path.join(resources_dir, 'final_RG_match.csv'),
        'manual_pop_phoenix_df': os.path.join(resources_dir, 'manual pop phoenix.csv'),
        'harmonized_names_df': os.path.join(script_dir, 'create_harmonized_name.csv')
    }
    
    loaded_dfs = {}
    for name, path in files.items():
        print(f"Loading {name} from {path}")
        if not os.path.exists(path):
            print(f"Warning: File not found - {path}")
            continue
        loaded_dfs[name] = standardize_dataframe(pd.read_csv(path))
        print(f"Columns in {name}: {loaded_dfs[name].columns.tolist()}")
    
    return loaded_dfs


def standardize_dataframe(df):
    """Standardize text in DataFrame by replacing special characters."""
    return df.apply(
        lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip()
        if x.dtype == "object" else x
    )


def apply_manual_changes(df):
    """Apply manual overrides to specific organizations."""
    # Ensure gc_orgID is string type
    df['gc_orgID'] = df['gc_orgID'].astype(str)
    
    manual_changes = {
        "3592": {
            "abbreviation": "SCC",
            "abreviation": "CSC"
        }
        # Add more overrides as needed
    }

    # Add debugging to verify the changes
    print("Before changes - Row for gc_orgID 3592:")
    print(df[df['gc_orgID'] == "3592"])
    
    for gc_orgid, changes in manual_changes.items():
        for field, value in changes.items():
            mask = df['gc_orgID'] == gc_orgid
            if mask.any():
                df.loc[mask, field] = value
            else:
                print(f"Warning: gc_orgID {gc_orgid} not found in DataFrame")
    
    print(f"\nAfter changes - Row for gc_orgID 3592:")
    print(df[df['gc_orgID'] == "3592"])
    
    return df


def process_dataframes(dfs):
    """Process and merge all dataframes."""
    # Convert gc_orgID to string in all dataframes
    for name, df in dfs.items():
        if 'gc_orgID' in df.columns:
            df['gc_orgID'] = df['gc_orgID'].astype(str)
        print(f"Columns in {name}: {df.columns.tolist()}")

    # Prepare combined_faa_df
    dfs['combined_faa_df']['Original English Name'] = (
        dfs['combined_faa_df']['English Name'])
    dfs['combined_faa_df'] = dfs['combined_faa_df'].rename(
        columns={'English Name': 'Organization Legal Name English'})

    # Initial merge
    print("Merging manual_org_df and combined_faa_df on 'Organization Legal Name English'")
    final_df = dfs['manual_org_df'].merge(
        dfs['combined_faa_df'],
        on='Organization Legal Name English',
        how='outer'
    )
    print("Columns after initial merge:", final_df.columns.tolist())

    # Process matches
    final_df['Names Match'] = final_df.apply(
        lambda row: 0 if pd.notna(row['Organization Legal Name English']) else 1,
        axis=1
    )
    unmatched = final_df[final_df['Names Match'] == 1]
    final_df = final_df[final_df['Names Match'] == 0]

    return final_df, unmatched


def merge_additional_data(df, dfs):
    """Merge additional data from other dataframes."""
    print("\nBefore merges:")
    print("Current columns:", df.columns.tolist())
    
    # Add harmonized names merge
    if 'harmonized_names_df' in dfs:
        print("\nMerging harmonized names...")
        df = df.merge(
            dfs['harmonized_names_df'][['gc_orgID', 'harmonized_name', 'nom_harmonisé']],
            on='gc_orgID',
            how='left'
        )
    else:
        print("Warning: harmonized_names_df not found in dfs")
    
    # Add a merge for the manual pop phoenix data
    if 'manual_pop_phoenix_df' in dfs:
        print("\nMerging manual pop phoenix data...")
        df = df.merge(
            dfs['manual_pop_phoenix_df'][['gc_orgID', 'pop', 'phoenix', 'ati', 'open_gov_ouvert']],
            on='gc_orgID',
            how='left'
        )
    else:
        print("Warning: manual_pop_phoenix_df not found in dfs")
    
    # Add merge for RG data
    if 'final_rg_match_df' in dfs:
        print("\nMerging final RG match data...")
        print("Columns in final_rg_match_df before merge:", dfs['final_rg_match_df'].columns.tolist())
        df = df.merge(
            dfs['final_rg_match_df'][['gc_orgID', 'rgnumber']],
            on='gc_orgID',
            how='left'
        )
        print("RG data merged successfully.")
        print("Columns after RG merge:", df.columns.tolist())
    else:
        print("Warning: final_rg_match_df not found in dfs")
    
    # Ensure all required columns exist
    required_columns = ['harmonized_name', 'nom_harmonisé', 'rgnumber', 'ati', 'open_gov_ouvert', 'pop', 'phoenix']
    df = ensure_required_columns(df, required_columns)
    
    print("\nAfter all merges:")
    print("Final columns:", df.columns.tolist())
    
    return df


def ensure_required_columns(df, required_columns):
    """Ensure all required columns exist in the DataFrame."""
    current_columns = set(df.columns)
    missing_columns = [col for col in required_columns if col not in current_columns]
    
    # Print debug information
    print("Current columns:", current_columns)
    print("Missing columns:", missing_columns)
    
    # Initialize missing columns with empty strings
    for col in missing_columns:
        df[col] = ''
    
    return df


def main():
    """Create GC organization concordance file."""
    script_folder = os.path.dirname(os.path.abspath(__file__))
    resources_folder = os.path.join(script_folder, 'Resources')
    scraping_folder = os.path.join(script_folder, 'Scraping')

    # Load and process dataframes
    dfs = load_dataframes(script_folder, resources_folder, scraping_folder)
    final_df, unmatched_values = process_dataframes(dfs)
    
    # Merge additional data
    final_df = merge_additional_data(final_df, dfs)
    
    # Standardize and clean up
    final_df = standardize_fields(final_df)
    final_df = apply_manual_changes(final_df)
    
    # Save results
    save_results(final_df, unmatched_values, script_folder)


def standardize_fields(df):
    """Standardize fields in the final dataframe."""
    df['gc_orgID'] = df['gc_orgID'].astype(str).str.split('.').str[0]
    df = df.rename(columns={
        'OrgID': 'infobaseID',
        'Website': 'website',
        'Site Web': 'site_web',
        'Abbreviation': 'abbreviation',
        'Abreviation': 'abreviation'
    })
    
    df['infobaseID'] = df['infobaseID'].fillna(0).astype(int)
    df['infobaseID'] = df['infobaseID'].replace(0, '')
    
    if 'site_web' not in df.columns:
        df['site_web'] = None
    
    return df


def save_results(df, unmatched, output_dir):
    """Save results to CSV files."""
    # Ensure all required columns exist
    field_order = [
        'gc_orgID', 'harmonized_name', 'nom_harmonisé',
        'abbreviation', 'abreviation', 'infobaseID', 'rgnumber',
        'ati', 'open_gov_ouvert', 'pop', 'phoenix',
        'website', 'site_web'
    ]
    df = ensure_required_columns(df, field_order)
    
    # Now sort and save
    df = df.sort_values(by='gc_orgID')
    
    df.to_csv(
        os.path.join(output_dir, 'gc_concordance.csv'),
        index=False,
        encoding='utf-8-sig'
    )
    unmatched.to_csv(
        os.path.join(output_dir, 'unmatched_org_IDs.csv'),
        index=False,
        encoding='utf-8-sig'
    )


if __name__ == "__main__":
    main()

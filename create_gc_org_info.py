import os
import pandas as pd

def load_dataframes(script_folder):
    """Load all required CSV files into dataframes."""
    files = {
        'manual_org': 'Resources/Manual org ID link.csv',
        'combined_faa': 'Scraping/combined_FAA_names.csv',
        'applied_en': 'Resources/applied_en.csv',
        'infobase_en': 'Resources/infobase_en.csv',
        'harmonized_names': 'create_harmonized_name.csv',
        'manual_lead_department': 'Resources/lead_manual.csv'  # Changed from 'Resources/Manual_leadDepartmentPortfolio.csv'
    }
    
    dfs = {}
    for key, path in files.items():
        df = pd.read_csv(os.path.join(script_folder, path))
        dfs[key] = standardize_text(df)
    return dfs

def standardize_text(df):
    """Standardize text by replacing special characters."""
    return df.apply(lambda x: x.str.replace('’', "'").str.replace('\u2011', '-').str.strip() 
                   if x.dtype == "object" else x)

def apply_overrides(df):
    """Apply manual overrides to specific organizations."""
    # Override values for specific gc_orgIDs
    overrides = {
        '3592': {
            'abbreviation': 'SCC',
            'abreviation': 'CSC'
        }
        # Add more overrides as needed:
        # 'gc_orgID': {'field': 'value', ...}
    }
    
    for org_id, values in overrides.items():
        for field, value in values.items():
            df.loc[df['gc_orgID'] == org_id, field] = value
    
    return df

def main():
    """Main function to create GC organization information file."""
    script_folder = os.path.dirname(os.path.abspath(__file__))
    
    # Load all dataframes
    dfs = load_dataframes(script_folder)
    
    # Remove unnamed columns
    if 'Unnamed: 0' in dfs['combined_faa'].columns:
        dfs['combined_faa'] = dfs['combined_faa'].drop(columns=['Unnamed: 0'])
    
    # Prepare combined_faa dataframe
    dfs['combined_faa']['Original English Name'] = dfs['combined_faa']['English Name']
    dfs['combined_faa'] = dfs['combined_faa'].rename(
        columns={'English Name': 'Organization Legal Name English'})
    
    # Join dataframes
    joined_df = pd.merge(dfs['manual_org'], dfs['combined_faa'], 
                        on='Organization Legal Name English', how='outer')
    
    # Process matches
    joined_df['Names Match'] = joined_df.apply(
        lambda row: 0 if pd.notna(row['Organization Legal Name English']) else 1, axis=1)
    unmatched_values = joined_df[joined_df['Names Match'] == 1]
    joined_df = joined_df[joined_df['Names Match'] == 0]
    
    # Perform all merges
    final_df = (joined_df
        .merge(
            dfs['applied_en'][['Legal title', 'Applied title', "Titre d'usage", 
                             'Abbreviation', 'Abreviation']],
            left_on='Organization Legal Name English',
            right_on='Legal title',
            how='left'
        )
        .merge(
            dfs['infobase_en'][['Legal title', 'Status', 'End date']],
            left_on='Organization Legal Name English',
            right_on='Legal title',
            how='left'
        )
        .merge(
            dfs['harmonized_names'][['gc_orgID', 'harmonized_name', 'nom_harmonisé']],
            on='gc_orgID',
            how='left'
        )
    )
    
    # Clean up and standardize fields
    final_df['gc_orgID'] = final_df['gc_orgID'].astype(str).str.split('.').str[0]
    final_df = final_df.rename(columns={
        'Organization Legal Name English': 'legal_title',
        'Organization Legal Name French': 'appellation_légale',
        'FAA': 'FAA_LGFP',
        'Applied title': 'preferred_name',
        "Titre d'usage": 'nom_préféré',
        'Abbreviation': 'abbreviation',
        'Abreviation': 'abreviation',
        'Status': 'status_statut',
        'End date': 'end_date_fin'
    })
    
    # Apply overrides
    final_df = apply_overrides(final_df)
    
    # Set default values
    final_df['status_statut'] = final_df['status_statut'].fillna('a')
    final_df['end_date_fin'] = final_df['end_date_fin'].apply(
        lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip() != '' else '')
    
    # Convert gc_orgID to string in manual_lead_department DataFrame
    dfs['manual_lead_department']['gc_orgID'] = dfs['manual_lead_department']['gc_orgID'].astype(str)

    # Then perform the merge
    final_df = final_df.merge(
        dfs['manual_lead_department'][['gc_orgID', 'lead_department', 'ministère_responsable']],
        on='gc_orgID',
        how='left'
    )
    
    # Order fields
    ordered_fields = [
        'gc_orgID', 'harmonized_name', 'nom_harmonisé', 'legal_title', 
        'appellation_légale', 'preferred_name', 'nom_préféré', 'lead_department',
        'ministère_responsable', 'abbreviation', 'abreviation', 'FAA_LGFP',
        'status_statut', 'end_date_fin'
    ]
    final_df = final_df[ordered_fields].sort_values(by='gc_orgID')
    
    # Save files
    final_df.to_csv(
        os.path.join(script_folder, 'gc_org_info.csv'),
        index=False, encoding='utf-8-sig'
    )
    unmatched_values.to_csv(
        os.path.join(script_folder, 'unmatched_org_IDs.csv'),
        index=False, encoding='utf-8-sig'
    )

if __name__ == "__main__":
    main()

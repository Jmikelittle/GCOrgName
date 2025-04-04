import os
import pandas as pd

def main():
    """Main function to compare GC OrgIDs across multiple CSV files."""
    # Define the paths to the CSV files
    script_folder = os.path.dirname(os.path.abspath(__file__))
    resources_folder = os.path.join(script_folder, '..', 'Resources')

    final_rg_match_file = os.path.join(resources_folder, 'rg_final.csv')
    manual_org_id_link_file = os.path.join(resources_folder, 'Manual org ID link.csv')
    manual_pop_phoenix_file = os.path.join(resources_folder, 'manual pop phoenix.csv')
    manual_lead_department_portfolio_file = os.path.join(
        resources_folder, 'lead_manual.csv')
    rg_final_file = os.path.join(resources_folder, 'rg_final.csv')

    # Create a dictionary to store DataFrames and their IDs
    dfs = {}
    df_ids = {}
    
    # Read the CSV files with better error handling
    files_to_read = {
        'final_rg_match': final_rg_match_file,
        'manual_org_id_link': manual_org_id_link_file,
        'manual_pop_phoenix': manual_pop_phoenix_file,
        'manual_lead_department_portfolio': manual_lead_department_portfolio_file,
        'rg_final': rg_final_file
    }
    
    # Try to read each file individually
    for name, file_path in files_to_read.items():
        try:
            dfs[name] = pd.read_csv(file_path)
            print(f"Successfully read {os.path.basename(file_path)}")
        except FileNotFoundError:
            print(f"Warning: File not found - {file_path}")
            dfs[name] = None
        except pd.errors.EmptyDataError:
            print(f"Warning: File is empty - {file_path}")
            dfs[name] = None
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            dfs[name] = None

    # Extract the 'GC OrgID' columns
    try:
        for name, df in dfs.items():
            if df is not None and 'gc_orgID' in df.columns:
                df_ids[name] = set(df['gc_orgID'].dropna().astype(int))
            else:
                df_ids[name] = set()
        
        # Add diagnostic information about each file
        print(f"\nTotal number of records found in each file:")
        for name, df in dfs.items():
            if df is not None:
                print(f"  {name}: {len(df)} rows")
            else:
                print(f"  {name}: File not available")
        
        # Check for legal name columns in each dataframe
        legal_name_cols = {}
        for name, df in dfs.items():
            if df is None:
                continue
                
            # Find columns that might contain legal names
            potential_name_cols = [col for col in df.columns if 'name' in col.lower() or 'legal' in col.lower()]
            legal_name_cols[name] = potential_name_cols
            print(f"\nPotential legal name columns in {name}:")
            for col in potential_name_cols:
                non_null_count = df[col].notna().sum()
                print(f"  - {col}: {non_null_count} non-null values ({non_null_count/len(df)*100:.1f}%)")
        
        # For each file with a legal name column, check how many gc_orgIDs have legal names
        print("\nLegal name coverage by gc_orgID:")
        for name, df in dfs.items():
            if df is None or name not in legal_name_cols or not legal_name_cols[name]:
                if df is not None:
                    print(f"  {name}: No legal name columns found")
                continue
                
            # Check the first potential legal name column for each file
            name_col = legal_name_cols[name][0]
            if 'gc_orgID' not in df.columns:
                print(f"  {name}: No gc_orgID column found")
                continue
                
            has_id_and_name = df[df['gc_orgID'].notna() & df[name_col].notna()]
            if len(df[df['gc_orgID'].notna()]) > 0:
                percentage = len(has_id_and_name)/len(df[df['gc_orgID'].notna()])*100
                print(f"  {name} ({name_col}): {len(has_id_and_name)} out of {len(df[df['gc_orgID'].notna()])} gc_orgIDs have legal names ({percentage:.1f}%)")
            else:
                print(f"  {name} ({name_col}): 0 out of 0 gc_orgIDs have legal names (N/A)")
        
    except KeyError as e:
        print(f"Error analyzing data: {e}")
        exit(1)

    # Find missing IDs
    try:
        # Get a union of all available IDs
        all_ids = set()
        for name, id_set in df_ids.items():
            all_ids = all_ids.union(id_set)

        missing_ids = {}
        for name, id_set in df_ids.items():
            missing_ids[name] = all_ids - id_set
    except TypeError as e:
        print(f"Error finding missing IDs: {e}")
        exit(1)

    # Create the output text
    output_lines = []

    # Add count of IDs for each file
    for name, id_set in df_ids.items():
        output_lines.append(f"Count of GC OrgIDs in {name}: {len(id_set)}")
    output_lines.append("\n")

    # Add missing IDs for each file
    for name, missing_set in missing_ids.items():
        output_lines.append(f"Missing in {name}:")
        output_lines.extend(map(str, sorted(missing_set)))
        output_lines.append("\n")

    # Write the output to a text file
    output_file = os.path.join(script_folder, 'missing_gc_org_ids.txt')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))
        print(f"Output written to {output_file}")
    except IOError as e:
        print(f"Error writing output file: {e}")
        exit(1)

if __name__ == "__main__":
    main()
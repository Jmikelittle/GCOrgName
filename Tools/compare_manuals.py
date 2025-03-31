import os
import pandas as pd

def main():
    """Main function to compare GC OrgIDs across multiple CSV files."""
    # Define the paths to the CSV files
    script_folder = os.path.dirname(os.path.abspath(__file__))
    resources_folder = os.path.join(script_folder, '..', 'Resources')

    final_rg_match_file = os.path.join(resources_folder, 'final_RG_match.csv')
    manual_org_id_link_file = os.path.join(resources_folder, 'Manual org ID link.csv')
    manual_pop_phoenix_file = os.path.join(resources_folder, 'manual pop phoenix.csv')
    manual_lead_department_portfolio_file = os.path.join(
        resources_folder, 'lead_manual.csv')
    rg_final_file = os.path.join(resources_folder, 'rg_final.csv')

    # Read the CSV files
    try:
        final_rg_match_df = pd.read_csv(final_rg_match_file)
        manual_org_id_link_df = pd.read_csv(manual_org_id_link_file)
        manual_pop_phoenix_df = pd.read_csv(manual_pop_phoenix_file)
        manual_lead_department_portfolio_df = pd.read_csv(manual_lead_department_portfolio_file)
        rg_final_df = pd.read_csv(rg_final_file)
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"Error reading CSV files: {e}")
        exit(1)

    # Extract the 'GC OrgID' columns
    try:
        final_rg_match_ids = set(final_rg_match_df['gc_orgID'].dropna().astype(int))
        manual_org_id_link_ids = set(manual_org_id_link_df['gc_orgID'].dropna().astype(int))
        manual_pop_phoenix_ids = set(manual_pop_phoenix_df['gc_orgID'].dropna().astype(int))
        manual_lead_department_portfolio_ids = set(
            manual_lead_department_portfolio_df['gc_orgID'].dropna().astype(int))
        rg_final_ids = set(rg_final_df['gc_orgID'].dropna().astype(int))
        
        # Add diagnostic information about legal names
        print(f"Total number of records found in each file:")
        print(f"  final_RG_match.csv: {len(final_rg_match_df)} rows")
        print(f"  Manual org ID link.csv: {len(manual_org_id_link_df)} rows")
        print(f"  manual pop phoenix.csv: {len(manual_pop_phoenix_df)} rows")
        print(f"  lead_manual.csv: {len(manual_lead_department_portfolio_df)} rows")
        print(f"  rg_final.csv: {len(rg_final_df)} rows")
        
        # Check for legal name columns in each dataframe
        legal_name_cols = {}
        for df_name, df in [
            ('final_RG_match', final_rg_match_df),
            ('Manual org ID link', manual_org_id_link_df),
            ('manual pop phoenix', manual_pop_phoenix_df),
            ('lead_manual', manual_lead_department_portfolio_df),
            ('rg_final', rg_final_df)
        ]:
            # Find columns that might contain legal names
            potential_name_cols = [col for col in df.columns if 'name' in col.lower() or 'legal' in col.lower()]
            legal_name_cols[df_name] = potential_name_cols
            print(f"\nPotential legal name columns in {df_name}:")
            for col in potential_name_cols:
                non_null_count = df[col].notna().sum()
                print(f"  - {col}: {non_null_count} non-null values ({non_null_count/len(df)*100:.1f}%)")
        
        # For each file with a legal name column, check how many gc_orgIDs have legal names
        print("\nLegal name coverage by gc_orgID:")
        for df_name, df in [
            ('final_RG_match', final_rg_match_df),
            ('Manual org ID link', manual_org_id_link_df),
            ('manual pop phoenix', manual_pop_phoenix_df),
            ('lead_manual', manual_lead_department_portfolio_df),
            ('rg_final', rg_final_df)
        ]:
            if not legal_name_cols[df_name]:
                print(f"  {df_name}: No legal name columns found")
                continue
                
            # Check the first potential legal name column for each file
            name_col = legal_name_cols[df_name][0]
            has_id_and_name = df[df['gc_orgID'].notna() & df[name_col].notna()]
            print(f"  {df_name} ({name_col}): {len(has_id_and_name)} out of {len(df[df['gc_orgID'].notna()])} gc_orgIDs have legal names ({len(has_id_and_name)/len(df[df['gc_orgID'].notna()])*100:.1f}%)")
        
    except KeyError as e:
        print(f"Error analyzing data: {e}")
        exit(1)

    # Find missing IDs
    try:
        all_other_ids = manual_org_id_link_ids.union(
            manual_pop_phoenix_ids, manual_lead_department_portfolio_ids, rg_final_ids)
        missing_in_final_rg_match = all_other_ids - final_rg_match_ids
        
        all_other_ids = final_rg_match_ids.union(
            manual_pop_phoenix_ids, manual_lead_department_portfolio_ids, rg_final_ids)
        missing_in_manual_org_id_link = all_other_ids - manual_org_id_link_ids
        
        all_other_ids = final_rg_match_ids.union(
            manual_org_id_link_ids, manual_lead_department_portfolio_ids, rg_final_ids)
        missing_in_manual_pop_phoenix = all_other_ids - manual_pop_phoenix_ids
        
        all_other_ids = final_rg_match_ids.union(
            manual_org_id_link_ids, manual_pop_phoenix_ids, rg_final_ids)
        missing_in_manual_lead_department_portfolio = all_other_ids - manual_lead_department_portfolio_ids
        
        all_other_ids = final_rg_match_ids.union(
            manual_org_id_link_ids, manual_pop_phoenix_ids, manual_lead_department_portfolio_ids)
        missing_in_rg_final = all_other_ids - rg_final_ids
    except TypeError as e:
        print(f"Error finding missing IDs: {e}")
        exit(1)

    # Create the output text
    output_lines = []

    output_lines.append(f"Count of GC OrgIDs in final_RG_match.csv: {len(final_rg_match_ids)}")
    output_lines.append(f"Count of GC OrgIDs in Manual org ID link.csv: {len(manual_org_id_link_ids)}")
    output_lines.append(f"Count of GC OrgIDs in manual pop phoenix.csv: {len(manual_pop_phoenix_ids)}")
    output_lines.append(f"Count of GC OrgIDs in lead_manual.csv: {len(manual_lead_department_portfolio_ids)}")
    output_lines.append(f"Count of GC OrgIDs in rg_final.csv: {len(rg_final_ids)}")
    output_lines.append("\n")

    output_lines.append("Missing in final_RG_match.csv:")
    output_lines.extend(map(str, sorted(missing_in_final_rg_match)))
    output_lines.append("\n")

    output_lines.append("Missing in Manual org ID link.csv:")
    output_lines.extend(map(str, sorted(missing_in_manual_org_id_link)))
    output_lines.append("\n")

    output_lines.append("Missing in manual pop phoenix.csv:")
    output_lines.extend(map(str, sorted(missing_in_manual_pop_phoenix)))
    output_lines.append("\n")

    output_lines.append("Missing in lead_manual.csv:")
    output_lines.extend(map(str, sorted(missing_in_manual_lead_department_portfolio)))
    output_lines.append("\n")
    
    output_lines.append("Missing in rg_final.csv:")
    output_lines.extend(map(str, sorted(missing_in_rg_final)))
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
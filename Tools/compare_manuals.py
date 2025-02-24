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
        resources_folder, 'Manual_leadDepartmentPortfolio.csv')

    # Read the CSV files
    try:
        final_rg_match_df = pd.read_csv(final_rg_match_file)
        manual_org_id_link_df = pd.read_csv(manual_org_id_link_file)
        manual_pop_phoenix_df = pd.read_csv(manual_pop_phoenix_file)
        manual_lead_department_portfolio_df = pd.read_csv(manual_lead_department_portfolio_file)
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
    except KeyError as e:
        print(f"Error extracting 'GC OrgID' columns: {e}")
        exit(1)

    # Find missing IDs
    try:
        missing_in_final_rg_match = manual_org_id_link_ids.union(
            manual_pop_phoenix_ids, manual_lead_department_portfolio_ids) - final_rg_match_ids
        missing_in_manual_org_id_link = final_rg_match_ids.union(
            manual_pop_phoenix_ids, manual_lead_department_portfolio_ids) - manual_org_id_link_ids
        missing_in_manual_pop_phoenix = final_rg_match_ids.union(
            manual_org_id_link_ids, manual_lead_department_portfolio_ids) - manual_pop_phoenix_ids
        missing_in_manual_lead_department_portfolio = final_rg_match_ids.union(
            manual_org_id_link_ids, manual_pop_phoenix_ids) - manual_lead_department_portfolio_ids
    except TypeError as e:
        print(f"Error finding missing IDs: {e}")
        exit(1)

    # Create the output text
    output_lines = []

    output_lines.append(f"Count of GC OrgIDs in final_RG_match.csv: {len(final_rg_match_ids)}")
    output_lines.append(f"Count of GC OrgIDs in Manual org ID link.csv: {len(manual_org_id_link_ids)}")
    output_lines.append(f"Count of GC OrgIDs in manual pop phoenix.csv: {len(manual_pop_phoenix_ids)}")
    output_lines.append(f"Count of GC OrgIDs in Manual_leadDepartmentPortfolio.csv: {len(manual_lead_department_portfolio_ids)}")
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

    output_lines.append("Missing in Manual_leadDepartmentPortfolio.csv:")
    output_lines.extend(map(str, sorted(missing_in_manual_lead_department_portfolio)))
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
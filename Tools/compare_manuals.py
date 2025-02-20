import os
import pandas as pd

# Define the paths to the CSV files
script_folder = os.path.dirname(os.path.abspath(__file__))
resources_folder = os.path.join(script_folder, '..', 'Resources')

final_rg_match_file = os.path.join(resources_folder, 'final_RG_match.csv')
manual_org_id_link_file = os.path.join(resources_folder, 'Manual org ID link.csv')
manual_pop_phoenix_file = os.path.join(resources_folder, 'manual pop phoenix.csv')
manual_lead_department_portfolio_file = os.path.join(resources_folder, 'Manual_leadDepartmentPortfolio.csv')

# Debug: Print file paths
print(f"Script folder: {script_folder}")
print(f"Resources folder: {resources_folder}")
print(f"final_RG_match_file: {final_rg_match_file}")
print(f"manual_org_id_link_file: {manual_org_id_link_file}")
print(f"manual_pop_phoenix_file: {manual_pop_phoenix_file}")
print(f"manual_lead_department_portfolio_file: {manual_lead_department_portfolio_file}")

# Read the CSV files
try:
    final_rg_match_df = pd.read_csv(final_rg_match_file)
    manual_org_id_link_df = pd.read_csv(manual_org_id_link_file)
    manual_pop_phoenix_df = pd.read_csv(manual_pop_phoenix_file)
    manual_lead_department_portfolio_df = pd.read_csv(manual_lead_department_portfolio_file)
    print("CSV files read successfully.")
except Exception as e:
    print(f"Error reading CSV files: {e}")
    exit(1)

# Debug: Print the first few rows of each DataFrame
print("First few rows of final_rg_match_df:")
print(final_rg_match_df.head())
print("First few rows of manual_org_id_link_df:")
print(manual_org_id_link_df.head())
print("First few rows of manual_pop_phoenix_df:")
print(manual_pop_phoenix_df.head())
print("First few rows of manual_lead_department_portfolio_df:")
print(manual_lead_department_portfolio_df.head())

# Extract the 'GC OrgID' columns
try:
    final_rg_match_ids = set(final_rg_match_df['GC OrgID'].dropna().astype(int))
    manual_org_id_link_ids = set(manual_org_id_link_df['GC OrgID'].dropna().astype(int))
    manual_pop_phoenix_ids = set(manual_pop_phoenix_df['gc_orgID'].dropna().astype(int))
    manual_lead_department_portfolio_ids = set(manual_lead_department_portfolio_df['GC OrgID'].dropna().astype(int))
    print("GC OrgID columns extracted successfully.")
except Exception as e:
    print(f"Error extracting GC OrgID columns: {e}")
    exit(1)

# Print the number of GC Org IDs found per document
print(f"Number of unique GC OrgIDs in final_RG_match.csv: {len(final_rg_match_ids)}")
print(f"Number of unique GC OrgIDs in Manual org ID link.csv: {len(manual_org_id_link_ids)}")
print(f"Number of unique GC OrgIDs in manual pop phoenix.csv: {len(manual_pop_phoenix_ids)}")
print(f"Number of unique GC OrgIDs in Manual_leadDepartmentPortfolio.csv: {len(manual_lead_department_portfolio_ids)}")

# Debug: Print the extracted GC OrgID sets
print("GC OrgIDs in final_RG_match.csv:")
print(final_rg_match_ids)
print("GC OrgIDs in Manual org ID link.csv:")
print(manual_org_id_link_ids)
print("GC OrgIDs in manual pop phoenix.csv:")
print(manual_pop_phoenix_ids)
print("GC OrgIDs in Manual_leadDepartmentPortfolio.csv:")
print(manual_lead_department_portfolio_ids)

# Find missing IDs
try:
    missing_in_final_rg_match = manual_org_id_link_ids.union(manual_pop_phoenix_ids, manual_lead_department_portfolio_ids) - final_rg_match_ids
    missing_in_manual_org_id_link = final_rg_match_ids.union(manual_pop_phoenix_ids, manual_lead_department_portfolio_ids) - manual_org_id_link_ids
    missing_in_manual_pop_phoenix = final_rg_match_ids.union(manual_org_id_link_ids, manual_lead_department_portfolio_ids) - manual_pop_phoenix_ids
    missing_in_manual_lead_department_portfolio = final_rg_match_ids.union(manual_org_id_link_ids, manual_pop_phoenix_ids) - manual_lead_department_portfolio_ids
    print("Missing IDs calculated successfully.")
except Exception as e:
    print(f"Error calculating missing IDs: {e}")
    exit(1)

# Debug: Print the missing IDs
print("Missing in final_RG_match.csv:")
print(missing_in_final_rg_match)
print("Missing in Manual org ID link.csv:")
print(missing_in_manual_org_id_link)
print("Missing in manual pop phoenix.csv:")
print(missing_in_manual_pop_phoenix)
print("Missing in Manual_leadDepartmentPortfolio.csv:")
print(missing_in_manual_lead_department_portfolio)

# Create the output text
output_lines = []

output_lines.append(f"Total unique GC OrgIDs in final_RG_match.csv: {len(final_rg_match_ids)}")
output_lines.append(f"Total unique GC OrgIDs in Manual org ID link.csv: {len(manual_org_id_link_ids)}")
output_lines.append(f"Total unique GC OrgIDs in manual pop phoenix.csv: {len(manual_pop_phoenix_ids)}")
output_lines.append(f"Total unique GC OrgIDs in Manual_leadDepartmentPortfolio.csv: {len(manual_lead_department_portfolio_ids)}")
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
    with open(output_file, 'w') as f:
        f.write("\n".join(output_lines))
    print(f"Missing GC OrgIDs have been written to {output_file}")
except Exception as e:
    print(f"Error writing to output file: {e}")
    exit(1)
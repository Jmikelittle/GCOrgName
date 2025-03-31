# Tools

This folder contains a variety of tools which help improve data quality and automate tasks for the GCOrgName project.

## Available Tools

### Website Validator
**Status: Currently broken**
- `website_validator.py`: A script designed to validate website URLs and check their accessibility. This tool reads URLs from a CSV file, attempts to connect to each URL, and reports those that are inaccessible or return non-200 status codes.

### Data Comparison Tools
- `compare_org_concord.py`: Compares organization data between 'GC Org Info.csv' and 'gc_concordance.csv' to identify mismatches in harmonized names in both English and French.
- `compare_manuals.py`: Analyzes multiple CSV files in the Resources folder to identify missing GC organization IDs across different data sources and generates a report of discrepancies.

### PDF Generation
- `lead_dept_pdf.py`: Creates PDF reports showing lead departments and their associated organizations. Produces two PDF files:
  - A main report grouping organizations by lead department
  - A report of organizations without an assigned lead department

## Contributing

If you find bugs or want to improve any of these tools, please create an issue or submit a pull request.
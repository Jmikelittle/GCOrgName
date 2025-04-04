import os
import requests
import pandas as pd

# URL of the CSV file
url = 'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/min-dept/min-dept.csv'

# Path to save the downloaded CSV file
script_folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_folder, 'rg_data.csv')
temp_file = os.path.join(script_folder, 'downloaded_file.csv')

print(f"Downloading from: {url}")
print(f"Output file will be: {output_file}")

# Step 1: Download the file and save it locally
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for bad status codes
    
    with open(temp_file, 'wb') as file:
        file.write(response.content)
    print(f"✓ File downloaded successfully to {temp_file}")
    
    # Display the first 3 lines to see the file structure
    with open(temp_file, 'r', encoding='utf-8', errors='ignore') as file:
        header = file.readline().strip()
        print("\nFile header:")
        print(header)
        print("\nFirst two data rows:")
        print(file.readline().strip())
        print(file.readline().strip())
    
except Exception as e:
    print(f"Error downloading file: {e}")
    exit(1)

# Step 2: Read the CSV file
try:
    df = pd.read_csv(temp_file)
    print(f"\n✓ CSV loaded successfully with {len(df)} rows")
    print(f"Original columns: {df.columns.tolist()}")
except Exception as e:
    print(f"Error reading CSV with default options: {e}")
    print("Trying with different encoding...")
    try:
        df = pd.read_csv(temp_file, encoding='latin1')
        print(f"✓ CSV loaded successfully with latin1 encoding")
    except Exception as e2:
        print(f"Error with latin1 encoding: {e2}")
        print("CSV could not be loaded. Please check the file format manually.")
        exit(1)

# Step 3: Simple column renaming based on position
print("\nRenaming columns by position...")
original_columns = df.columns.tolist()

# Rename first three columns (if they exist)
if len(original_columns) >= 1:
    df = df.rename(columns={original_columns[0]: 'rgnumber'})
    print(f"Column 1: '{original_columns[0]}' → 'rgnumber'")

if len(original_columns) >= 2:
    df = df.rename(columns={original_columns[1]: 'rg_dept_en'})
    print(f"Column 2: '{original_columns[1]}' → 'rg_dept_en'")
    
if len(original_columns) >= 3:
    df = df.rename(columns={original_columns[2]: 'rg_dept_fr'})
    print(f"Column 3: '{original_columns[2]}' → 'rg_dept_fr'")

# Step 4: Format the department number
print("\nFormatting department numbers...")
try:
    # Convert any numeric values to zero-padded 3-digit strings
    if 'rgnumber' in df.columns:
        # First check the data type and show some examples
        print(f"rgnumber column dtype: {df['rgnumber'].dtype}")
        print(f"Sample values: {df['rgnumber'].head().tolist()}")
        
        # Convert to string and pad with zeros
        df['rgnumber'] = df['rgnumber'].astype(str)
        
        # Try to format numbers, handling non-numeric values
        def format_number(x):
            try:
                if pd.notna(x) and x.strip():
                    return f"{int(float(x)):03d}"
                return x
            except ValueError:
                return x
                
        df['rgnumber'] = df['rgnumber'].apply(format_number)
        print("✓ Department numbers formatted")
    else:
        print("Error: 'rgnumber' column not found after renaming")
except Exception as e:
    print(f"Error formatting department numbers: {e}")
    print("Continuing with unformatted numbers...")

# Step 5: Save the output file
print("\nSaving output file...")
try:
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    if os.path.exists(output_file):
        print(f"✓ File saved successfully to {output_file}")
        print(f"  File size: {os.path.getsize(output_file)} bytes")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {', '.join(df.columns)}")
    else:
        print("Error: File was not saved")
except Exception as e:
    print(f"Error saving output file: {e}")

# Clean up
try:
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"\n✓ Temporary file removed")
except Exception as e:
    print(f"Error removing temporary file: {e}")

print("\nProcess completed")

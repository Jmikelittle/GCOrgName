import os
import glob

# Print the current working directory
print("Current Working Directory:", os.getcwd())

# List all files in the current directory
print("Files in the Directory:", os.listdir(os.getcwd()))

# List CSV files matching the pattern 'FAA*.csv'
csv_files = glob.glob('FAA*.csv')
print("CSV files found:", csv_files)

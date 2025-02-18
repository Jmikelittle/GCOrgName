import subprocess
import sys
import os

# Get the directory where this script lives
script_dir = os.path.dirname(os.path.abspath(__file__))

print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {script_dir}")

# List the specific scripts to run (they are in the same directory as this file)
scripts = [
    "scrape_FAA1.py",
    "scrape_FAA1i.py",
    "scrape_FAA2.py",
    "scrape_FAA3.py",
    "scrape_FAA4.py",
    "scrape_FAA5.py"
]

for script in scripts:
    script_path = os.path.join(script_dir, script)
    print(f"Running {script_path}...")
    result = subprocess.run(["python", script_path])
    if result.returncode != 0:
        print(f"{script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
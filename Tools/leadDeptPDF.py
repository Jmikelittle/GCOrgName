import pandas as pd
from fpdf import FPDF

# Read the CSV data
data = pd.read_csv('/workspaces/GCOrgName/GC Org Info.csv')

# Fill NaN values with an empty string
data['harmonized_name'] = data['harmonized_name'].fillna('')
data['lead_department'] = data['lead_department'].fillna('')

# Filter out rows with empty lead_department
data = data[data['lead_department'] != '']

# Group data by lead_department
grouped = data.groupby('lead_department')

# Print the first 5 lead departments with associated harmonized names
for i, (lead_department, group) in enumerate(grouped):
    if i < 5:
        print(f"Lead Department: {lead_department}")
        print("Departments:")
        for department in group['harmonized_name'].tolist():
            print(f" - {department}")
        print("\n")

# Create a PDF class
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Government Departments and Their Lead Departments', 0, 1, 'C')

    def chapter_title(self, lead_department):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, lead_department, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, departments):
        self.set_font('Arial', '', 12)
        for department in departments:
            self.cell(0, 10, department, 0, 1)
        self.ln()

# Create a PDF object
pdf = PDF()

# Add a page for each lead department
for lead_department, group in grouped:
    pdf.add_page()
    pdf.chapter_title(lead_department)
    pdf.chapter_body(group['harmonized_name'].tolist())

# Save the PDF in the Tools folder
pdf.output('/workspaces/GCOrgName/Tools/lead_department.pdf')

print("PDF created successfully.")

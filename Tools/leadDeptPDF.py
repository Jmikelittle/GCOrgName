import pandas as pd
from fpdf import FPDF

# Read the CSV data
data = pd.read_csv('/workspaces/GCOrgName/GC Org Info.csv')

# Fill NaN values with an empty string
data['harmonized_name'] = data['harmonized_name'].fillna('')
data['lead_department'] = data['lead_department'].fillna('')
data['gc_orgID'] = data['gc_orgID'].fillna('')

# Filter out rows with empty lead_department
data = data[data['lead_department'] != '']

# Group data by lead_department
grouped = data.groupby('lead_department')

# List of lead departments for the special page
special_lead_departments = [
    'Minister of Crown-Indigenous Relations and Northern Affairs',
    'Minister of Democratic Institutions',
    'Minister of Indigenous Services',
    'Minister of Sport',
    'Minister of Tourism',
    'Minister responsible for the Atlantic Canada Opportunities Agency',
    'President of the King\'s Privy Council for Canada'
]

# Filter data for the special page
special_data = data[data['lead_department'].isin(special_lead_departments)]

# Create a PDF class
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Lead Departments and their Associated Organizations', 0, 1, 'C')

    def chapter_title(self, lead_department):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, lead_department, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, departments):
        self.set_font('Arial', '', 12)
        for index, row in departments.iterrows():
            self.cell(0, 10, f"{row['harmonized_name']} - GC Org ID: {row['gc_orgID']}", 0, 1)
        self.ln()

    def special_page(self, data):
        self.add_page()
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'Regional Development Agencies', 0, 1, 'C')
        self.ln(10)
        self.set_font('Arial', 'B', 7)  # Reduce font size by 40%
        self.cell(95, 10, 'Responsible Minister', 1)
        self.cell(95, 10, 'Agency', 1)
        self.ln()
        self.set_font('Arial', '', 7)  # Reduce font size by 40%
        for index, row in data.iterrows():
            self.cell(95, 10, row['lead_department'], 1)
            self.cell(95, 10, f"{row['harmonized_name']} - GC Org ID: {row['gc_orgID']}", 1)
            self.ln()

# Create a PDF object
pdf = PDF()

# Add a page for each lead department excluding the special ones
for lead_department, group in grouped:
    if lead_department not in special_lead_departments:
        pdf.add_page()
        pdf.chapter_title(lead_department)
        pdf.chapter_body(group)

# Add the special page at the end
pdf.special_page(special_data)

# Save the PDF in the Tools folder
pdf.output('/workspaces/GCOrgName/Tools/lead_department.pdf')

print("PDF created successfully.")

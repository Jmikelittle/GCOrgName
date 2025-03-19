import os
import pandas as pd
from fpdf import FPDF

# Get the directory of the current script
script_folder = os.path.dirname(os.path.abspath(__file__))

# Read the CSV data
data_file = os.path.join(script_folder, '..', 'gc_org_info.csv')
data = pd.read_csv(data_file)
resources_folder = os.path.join(script_folder, '..', 'Resources')
manual_lead_department_file = os.path.join(resources_folder, 'lead_manual.csv')

# Fill NaN values with an empty string
data['harmonized_name'] = data['harmonized_name'].fillna('')
data['lead_department'] = data['lead_department'].fillna('')
data['gc_orgID'] = data['gc_orgID'].fillna('')

# Filter out rows with empty lead_department
data = data[data['lead_department'] != '']

# Group data by lead_department
grouped = data.groupby('lead_department')

# List of gc_orgID for the special page
special_gc_orgIDs = [2240, 2244, 2249, 2257, 2258, 2298, 2299]

# Filter data for the special page
special_data = data[data['gc_orgID'].isin(special_gc_orgIDs)]

class PDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.disable_footer = False
        self.set_title('Lead Departments and their Associated Organizations')
        self.set_author('OCIO - TBS')

    def header(self):
        self.set_fill_color(0, 77, 113)  # Set fill color to #004D71
        self.rect(0, 0, 210, 30, 'F')     # Draw a filled rectangle
        self.set_y(10)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255) # Set text color to white
        self.cell(0, 10, 'Lead Departments and their Associated Organizations', 0, 1, 'C')

    def chapter_title(self, lead_department):
        self.set_y(33)  # Move the chapter title down to start at the 33rd pixel
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)       # Set text color to black
        self.cell(0, 10, lead_department, 1, 1, 'L')
        self.ln(6)
        self.title_y = self.get_y()       # Store the y-coordinate of the title

    def chapter_body(self, departments):
        self.set_font('Arial', '', 12)
        self.set_draw_color(89, 89, 89)    # Set draw color to grey (#595959)
        self.body_start_y = self.get_y()   # Store the starting y-coordinate of the body
        for index, row in departments.iterrows():
            self.set_x(30)  # Move the body text to the right by 30 pixels
            self.cell(0, 8, f"{row['harmonized_name']} - GC Org ID: {row['gc_orgID']}", 1, 1)  # Add a grey outline box around the text with reduced height
            self.ln(2)  # Add 2 pixels of space beneath each line
            self.set_draw_color(89, 89, 89)
            # Draw horizontal line centered vertically in the cell
            y_center = self.get_y() - 6
            self.line(10, y_center, 30, y_center)
        self.body_end_y = self.get_y()     # Store the ending y-coordinate of the body
        self.ln()

    def footer(self):
        # Only draw the footer if disable_footer is False
        if not self.disable_footer:
            self.set_draw_color(89, 89, 89)    # Set draw color to grey (#595959)
            self.line(10, self.title_y - 6, 10, self.body_end_y - 6)
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def special_page(self, data):
        self.add_page()
        # Disable footer for this special page
        self.disable_footer = True
        self.set_y(33)  # Move the title down to start at the 33rd pixel
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Regional Development Agencies', 0, 1, 'C')
        self.ln(10)
        self.set_font('Arial', 'B', 7)
        self.cell(95, 10, 'Department', 1)
        self.cell(95, 10, 'Lead Department', 1)
        self.ln()
        self.set_font('Arial', '', 7)
        for index, row in data.iterrows():
            self.cell(95, 10, f"{row['harmonized_name']} - GC Org ID: {row['gc_orgID']}", 1)
            self.cell(95, 10, row['lead_department'], 1)
            self.ln()

# Create a PDF object
pdf = PDF()

# Add a page for each lead department excluding the special ones
for lead_department, group in grouped:
    if lead_department not in special_data['lead_department'].unique():
        pdf.add_page()
        pdf.chapter_title(lead_department)
        pdf.chapter_body(group)

# Add the special page at the end (footer disabled on this page)
pdf.special_page(special_data)

# Save the PDF in the Tools folder
output_file = os.path.join(script_folder, 'lead_department.pdf')
pdf.output(output_file)

print("PDF created successfully.")

# Create a PDF for organizations without a lead department
class NoLeadDeptPDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.set_title('Organizations without a Lead Department')
        self.set_author('OCIO - TBS')

    def header(self):
        self.set_fill_color(0, 77, 113)  # Set fill color to #004D71
        self.rect(0, 0, 210, 30, 'F')     # Draw a filled rectangle
        self.set_y(10)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255)  # Set text color to white
        self.cell(0, 10, 'Organizations without a Lead Department', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def create_table(self, data):
        # TABLE_START_Y defines where the table begins on each page (40mm from top)
        # This allows space for the header on all pages
        TABLE_START_Y = 40  # Starting Y position in mm for table on all pages
        
        self.set_y(TABLE_START_Y)  # Position cursor at the defined starting position
        self.set_fill_color(200, 200, 200)  # Light grey for header row
        self.set_text_color(0)
        self.set_font('Arial', 'B', 10)
        
        # Calculate column widths
        page_width = self.w - 2 * 10  # Page width minus margins
        col_width = [page_width * 0.3, page_width * 0.7]  # 30% for ID, 70% for name
        
        # Header row
        self.cell(col_width[0], 10, 'GC Org ID', 1, 0, 'C', True)
        self.cell(col_width[1], 10, 'Organization Name', 1, 1, 'C', True)
        
        # Data rows
        self.set_font('Arial', '', 10)
        self.set_fill_color(255, 255, 255)  # White for data rows
        
        # Alternate row colors for better readability
        fill = False
        for row in data:
            if self.get_y() > self.h - 40:  # Check if we need a new page
                self.add_page()
                # Position the table at the same starting position on new pages
                self.set_y(TABLE_START_Y)
                
                # Repeat header
                self.set_fill_color(200, 200, 200)
                self.set_font('Arial', 'B', 10)
                self.cell(col_width[0], 10, 'GC Org ID', 1, 0, 'C', True)
                self.cell(col_width[1], 10, 'Organization Name', 1, 1, 'C', True)
                self.set_font('Arial', '', 10)
                self.set_fill_color(255, 255, 255)
            
            self.cell(col_width[0], 10, str(row[0]), 1, 0, 'C', fill)
            self.cell(col_width[1], 10, str(row[1]), 1, 1, 'L', fill)
            
            fill = not fill  # Toggle fill for next row

# Function to create the no lead department PDF
def create_no_lead_dept_pdf():
    try:
        # Get the data from lead_manual.csv
        manual_lead_department_df = pd.read_csv(manual_lead_department_file)
        
        # Identify organizations without a lead department
        orgs_without_lead = manual_lead_department_df[
            (manual_lead_department_df['lead_department'].isna()) | 
            (manual_lead_department_df['lead_department'] == '')
        ]
        
        if not orgs_without_lead.empty:
            print(f"Found {len(orgs_without_lead)} organizations without a lead department")
            
            # Create data for the table
            table_data = []
            for _, row in orgs_without_lead.iterrows():
                if pd.notna(row['gc_orgID']) and pd.notna(row['Harmonized GC Name']):
                    try:
                        gc_orgid = str(int(row['gc_orgID']))
                        table_data.append([gc_orgid, row['Harmonized GC Name']])
                    except:
                        # Handle non-numeric gc_orgID
                        table_data.append([str(row['gc_orgID']), row['Harmonized GC Name']])
            
            # Sort by gc_orgID numerically
            table_data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))
            
            # Create PDF
            no_lead_pdf = NoLeadDeptPDF()
            no_lead_pdf.add_page()
            no_lead_pdf.create_table(table_data)
            
            # Save the PDF
            output_file = os.path.join(script_folder, 'orgs_without_lead_department.pdf')
            no_lead_pdf.output(output_file)
            
            print(f"PDF of organizations without a lead department created at {output_file}")
        else:
            print("All organizations have lead departments assigned")
            
    except Exception as e:
        print(f"Error creating PDF for organizations without lead departments: {str(e)}")

# Call the function to generate the PDF
create_no_lead_dept_pdf()
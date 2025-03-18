import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
# Import font registration modules
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Noto Sans fonts
try:
    # Common locations for Noto Sans fonts
    font_paths = [
        '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
        '/usr/share/fonts/noto/NotoSans-Regular.ttf',
        '/usr/local/share/fonts/NotoSans-Regular.ttf',
    ]
    
    # Try each path until we find one that works
    for path in font_paths:
        if os.path.exists(path):
            # Register regular font
            pdfmetrics.registerFont(TTFont('NotoSans', path))
            
            # Try to register bold and italic variants if available
            bold_path = path.replace('Regular', 'Bold')
            italic_path = path.replace('Regular', 'Italic')
            bold_italic_path = path.replace('Regular', 'BoldItalic')
            
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont('NotoSans-Bold', bold_path))
            
            if os.path.exists(italic_path):
                pdfmetrics.registerFont(TTFont('NotoSans-Italic', italic_path))
                
            if os.path.exists(bold_italic_path):
                pdfmetrics.registerFont(TTFont('NotoSans-BoldItalic', bold_italic_path))
            
            print(f"Successfully registered Noto Sans fonts from {path}")
            break
    else:
        print("Could not find Noto Sans fonts. Falling back to default fonts.")
except Exception as e:
    print(f"Error registering Noto Sans fonts: {e}. Using default fonts.")

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
data_with_lead = data[data['lead_department'] != '']

# Group data by lead_department
grouped = data_with_lead.groupby('lead_department')

# List of gc_orgID for the special page
special_gc_orgIDs = [2240, 2244, 2249, 2257, 2258, 2298, 2299]

# Filter data for the special page
special_data = data[data['gc_orgID'].isin(special_gc_orgIDs)]

# Custom flowable for horizontal line
class HorizontalLine(Flowable):
    def __init__(self, width, height=1, color=colors.grey):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, self.height/2, self.width, self.height/2)

# Custom flowable for vertical line
class VerticalLine(Flowable):
    def __init__(self, height, width=1, color=colors.grey):
        Flowable.__init__(self)
        self.height = height
        self.width = width
        self.color = color
    
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, 0, 0, self.height)

# Create header style
styles = getSampleStyleSheet()
header_style = ParagraphStyle(
    'Header',
    parent=styles['Heading1'],
    fontName='NotoSans-Bold',  # Changed from Helvetica-Bold
    fontSize=12,
    textColor=colors.white,
    alignment=1,  # Center alignment
)

title_style = ParagraphStyle(
    'ChapterTitle',
    parent=styles['Heading2'],
    fontName='NotoSans-Bold',  # Changed from Helvetica-Bold
    fontSize=12,
    textColor=colors.black,
    borderWidth=1,
    borderColor=colors.black,
    borderPadding=6,
    leading=16,
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='NotoSans',  # Changed from Helvetica
    fontSize=10,
    borderWidth=1,
    borderColor=colors.grey,
    borderPadding=4,
)

# Custom header function for the document
def add_header_footer(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFillColor(colors.Color(0/255, 77/255, 113/255))  # #004D71
    canvas.rect(0, doc.height, doc.width + 50, 30*mm, fill=1)
    canvas.setFont('NotoSans-Bold', 12)  # Changed from Helvetica-Bold
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(doc.width/2, doc.height + 15*mm, 
                            'Lead Departments and their Associated Organizations')
    # Footer (page number)
    try:
        canvas.setFont('NotoSans', 8)  # Changed from Helvetica-Italic to NotoSans
    except:
        # Fallback if NotoSans isn't available
        canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(doc.width/2, 15*mm, f"Page {doc.page}")
    canvas.restoreState()

# Create PDF with lead departments
def create_lead_dept_pdf():
    pdf_file = os.path.join(script_folder, 'lead_department.pdf')
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    story = []
    
    # Create pages for each lead department
    for lead_department, group in grouped:
        if lead_department not in special_data['lead_department'].unique():
            # Add lead department title
            if story:  # Add page break except for first page
                story.append(PageBreak())
            
            story.append(Spacer(1, 33*mm))  # Space from top
            story.append(Paragraph(lead_department, title_style))
            story.append(Spacer(1, 6*mm))
            
            # Add organizations
            for index, row in group.iterrows():
                # Create table for organization with indentation
                org_text = f"{row['harmonized_name']} - GC Org ID: {row['gc_orgID']}"
                data_row = [['', org_text]]
                org_table = Table(data_row, colWidths=[20*mm, 170*mm])
                org_table.setStyle(TableStyle([
                    ('BOX', (1, 0), (1, 0), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),  # Changed from default
                ]))
                story.append(org_table)
                story.append(Spacer(1, 2*mm))
                
                # Add horizontal line
                line_table = Table([[HorizontalLine(20*mm), '']], colWidths=[20*mm, 170*mm])
                story.append(line_table)
                
            # Add vertical line (handled in onPage function)
    
    # Create special page for Regional Development Agencies
    story.append(PageBreak())
    story.append(Spacer(1, 33*mm))
    story.append(Paragraph('Regional Development Agencies', styles['Heading2']))
    story.append(Spacer(1, 10*mm))
    
    # Create table for special page
    special_data_rows = [['Department', 'Lead Department']]
    for index, row in special_data.iterrows():
        special_data_rows.append([
            f"{row['harmonized_name']} - GC Org ID: {row['gc_orgID']}",
            row['lead_department']
        ])
    
    special_table = Table(special_data_rows, colWidths=[95*mm, 95*mm])
    special_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSans-Bold'),  # Changed from Helvetica-Bold
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),  # For body text
    ]))
    story.append(special_table)
    
    # Build the PDF with custom header/footer
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print("Lead Departments PDF created successfully.")

# Create a separate PDF for organizations without a lead department
def create_no_lead_dept_pdf():
    # Get the data from lead_manual.csv since it's more comprehensive
    manual_lead_department_df = pd.read_csv(manual_lead_department_file)
    
    # Identify organizations without a lead department
    orgs_without_lead = manual_lead_department_df[
        (manual_lead_department_df['lead_department'].isna()) | 
        (manual_lead_department_df['lead_department'] == '')
    ]
    
    if not orgs_without_lead.empty:
        print(f"Found {len(orgs_without_lead)} organizations without a lead department")
        
        # Create a simplified DataFrame with just gc_orgID and harmonized name
        table_data = [['gc_orgID', 'Harmonized Organization Name']]  # Header row
        for _, row in orgs_without_lead.iterrows():
            if pd.notna(row['gc_orgID']) and pd.notna(row['Harmonized GC Name']):
                try:
                    gc_orgid = str(int(row['gc_orgID']))
                    table_data.append([gc_orgid, row['Harmonized GC Name']])
                except:
                    # Handle non-numeric gc_orgID
                    table_data.append([str(row['gc_orgID']), row['Harmonized GC Name']])
        
        # Create PDF with the table
        pdf_file = os.path.join(script_folder, 'orgs_without_lead_department.pdf')
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        
        # Add header
        header_style = styles['Heading1']
        header_style.fontName = 'NotoSans-Bold'  # Changed from default
        header = Paragraph("Organizations who operate without a Lead Department", header_style)
        elements.append(header)
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'NotoSans-Bold'),  # Changed from Helvetica-Bold
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),  # Changed from default
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        print(f"Generated PDF listing organizations without lead departments at {pdf_file}")
    else:
        print("All organizations have lead departments assigned")

# Generate both PDFs
create_lead_dept_pdf()
create_no_lead_dept_pdf()

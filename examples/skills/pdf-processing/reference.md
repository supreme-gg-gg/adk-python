# PDF Processing Advanced Reference

## Python Libraries

### pypdf (MIT License)
Primary library for PDF manipulation, merging, splitting, and form filling.

### pdfplumber (MIT License) 
Excellent for text extraction with layout preservation and table detection.

### reportlab (BSD License)
Comprehensive PDF creation library for generating documents from scratch.

## Advanced Text Extraction

### Extract Tables
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                print(df)
```

### Preserve Layout
```python
with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    
    # Extract with bounding box
    bbox = (0, 0, page.width/2, page.height)  # Left half
    left_text = page.within_bbox(bbox).extract_text()
```

## PDF Creation with reportlab

### Multi-page Documents
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf")
styles = getSampleStyleSheet()
story = []

# Add content
story.append(Paragraph("Page 1 Title", styles['Title']))
story.append(Paragraph("Page 1 content", styles['Normal']))
story.append(PageBreak())
story.append(Paragraph("Page 2 Title", styles['Title']))

doc.build(story)
```

### Custom Styling
```python
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

custom_style = ParagraphStyle(
    'CustomTitle',
    fontSize=18,
    textColor='blue',
    alignment=TA_CENTER,
    spaceAfter=20
)
```

## Command Line Tools

### pdftotext (poppler-utils)
```bash
# Basic text extraction
pdftotext document.pdf output.txt

# Preserve layout
pdftotext -layout document.pdf output.txt

# Specific page range
pdftotext -f 1 -l 5 document.pdf output.txt
```

### qpdf
```bash
# Decrypt password-protected PDF
qpdf --password=secret --decrypt encrypted.pdf decrypted.pdf

# Rotate pages
qpdf input.pdf --rotate=+90:1-3 output.pdf  # Rotate first 3 pages

# Extract pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
```

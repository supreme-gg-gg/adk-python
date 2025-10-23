---
name: pdf-processing
description: Process and manipulate PDF documents, including text extraction, form filling, and document creation. Use when working with PDF files.
license: Apache 2.0
---

# PDF Processing Skill

This skill provides comprehensive PDF processing capabilities including text extraction, form filling, document merging, and creation of new PDFs.

## Core Capabilities

### Text Extraction
Extract text content from PDF documents while preserving formatting and structure.

### Form Processing  
Fill out PDF forms programmatically. For fillable forms, use the `extract_form_fields.py` script to discover field information first.

### Document Manipulation
- Merge multiple PDFs into a single document
- Split PDFs into individual pages
- Rotate pages and modify document structure
- Add watermarks and annotations

### PDF Creation
Create new PDF documents from scratch with text, images, and formatting.

## Usage Guidelines

1. **For form filling**: First run `python scripts/extract_form_fields.py input.pdf` to discover available form fields
2. **For text extraction**: Use pdfplumber for better table and layout preservation
3. **For document creation**: Use reportlab for programmatic PDF generation

## Required Libraries

```python
pip install pypdf pdfplumber reportlab
```

## Quick Examples

### Extract Text
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

For detailed form processing instructions, see forms.md.
For advanced features and additional libraries, see reference.md.

# PDF Form Processing Guide

## Fillable Forms

If you need to fill out a PDF form, first check if it has fillable form fields by running:

```bash
python scripts/extract_form_fields.py input.pdf
```

This script will output information about all form fields in the PDF, including:
- Field names and types (text, checkbox, radio, dropdown)
- Field locations and bounding boxes
- Available options for choice fields

## Form Field Types

### Text Fields
Standard text input fields that can contain strings.

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

# Fill text field
writer.add_page(reader.pages[0])
writer.update_page_form_field_values(
    writer.pages[0],
    {"field_name": "Your text here"}
)
```

### Checkboxes
Boolean fields that can be checked or unchecked.

```python
# Check a checkbox (use the "checked_value" from field info)
writer.update_page_form_field_values(
    writer.pages[0],
    {"checkbox_field": "/Yes"}  # or whatever the checked_value is
)
```

### Radio Buttons
Multiple choice fields where only one option can be selected.

```python
# Select radio option (use value from radio_options)
writer.update_page_form_field_values(
    writer.pages[0],
    {"radio_group_field": "option_value"}
)
```

### Dropdown/Choice Fields
Fields with predefined options to choose from.

```python
# Select dropdown option
writer.update_page_form_field_values(
    writer.pages[0],
    {"dropdown_field": "selected_option"}
)
```

## Non-Fillable Forms

For PDFs without fillable form fields, you'll need to:
1. Extract text to identify field locations
2. Overlay new content at the appropriate positions
3. Use coordinate-based positioning to place text

This is more complex and requires manual positioning based on the PDF layout.

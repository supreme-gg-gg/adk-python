#!/usr/bin/env python3
"""
Extract form field information from a PDF file.

Usage: python extract_form_fields.py input.pdf [output.json]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf library not installed. Run: pip install pypdf")
    sys.exit(1)


def extract_form_fields(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract form field information from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of dictionaries containing form field information.
    """
    try:
        reader = PdfReader(pdf_path)
        fields = []

        if not reader.is_encrypted and hasattr(reader, "get_form_text_fields"):
            # Get form fields if available
            form_fields = reader.get_form_text_fields() or {}

            for page_num, page in enumerate(reader.pages, 1):
                if hasattr(page, "/Annots") and page["/Annots"]:
                    for annotation in page["/Annots"]:
                        annot_obj = annotation.get_object()
                        if annot_obj.get("/Subtype") == "/Widget":
                            field_info = {
                                "page": page_num,
                                "field_id": str(annot_obj.get("/T", "Unknown")),
                                "type": "unknown",
                            }

                            # Get field type
                            ft = annot_obj.get("/FT")
                            if ft == "/Tx":
                                field_info["type"] = "text"
                            elif ft == "/Btn":
                                field_info["type"] = "checkbox"
                            elif ft == "/Ch":
                                field_info["type"] = "choice"

                            # Get bounding rectangle
                            if "/Rect" in annot_obj:
                                field_info["rect"] = annot_obj["/Rect"]

                            fields.append(field_info)

        return fields

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_form_fields.py input.pdf [output.json]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(pdf_path).exists():
        print(f"Error: PDF file '{pdf_path}' not found")
        sys.exit(1)

    print(f"Extracting form fields from: {pdf_path}")
    fields = extract_form_fields(pdf_path)

    if not fields:
        print("No form fields found in the PDF")
        return

    print(f"Found {len(fields)} form fields:")

    for field in fields:
        print(f"  - {field['field_id']} ({field['type']}) on page {field['page']}")

    if output_path:
        with open(output_path, "w") as f:
            json.dump(fields, f, indent=2, default=str)
        print(f"Field information saved to: {output_path}")
    else:
        print("\nDetailed field information:")
        print(json.dumps(fields, indent=2, default=str))


if __name__ == "__main__":
    main()

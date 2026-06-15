"""
pdf_reader.py
=============
Utility to extract text from PDF files using PyMuPDF.
Used by the CV Parser agent to read uploaded CV files.
"""

import fitz  # PyMuPDF
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Full path to the PDF file
        
    Returns:
        Extracted text as a single string
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text = ""
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Loop through every page and extract text
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()
            text += "\n"  # separator between pages
        
        doc.close()
        
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")
    
    # Clean up extra whitespace
    text = "\n".join(
        line.strip() 
        for line in text.splitlines() 
        if line.strip()
    )
    
    return text


def get_pdf_info(pdf_path: str) -> dict:
    """
    Get basic info about a PDF file.
    
    Returns:
        Dict with page count and file size
    """
    doc = fitz.open(pdf_path)
    info = {
        "pages": len(doc),
        "file_size_kb": round(os.path.getsize(pdf_path) / 1024, 2),
        "file_name": os.path.basename(pdf_path)
    }
    doc.close()
    return info
#!/usr/bin/env python3
"""
Create a simple test PDF for the multilingual processor
"""

import fitz  # PyMuPDF

def create_test_pdf():
    """Create a simple test PDF with headings and a table"""
    
    # Create a new PDF document
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    
    # Add title
    title_point = fitz.Point(72, 100)
    page1.insert_text(title_point, "Test Document", fontsize=18)
    
    # Add H1 heading
    h1_point = fitz.Point(72, 150)
    page1.insert_text(h1_point, "Chapter 1: Introduction", fontsize=16)
    
    # Add some content
    content_point = fitz.Point(72, 180)
    page1.insert_text(content_point, "This is a test document for the PDF processor.", fontsize=12)
    
    # Add H2 heading
    h2_point = fitz.Point(72, 220)
    page1.insert_text(h2_point, "1.1 Overview", fontsize=14)
    
    # Add table-like content
    table_start = 280
    page1.insert_text(fitz.Point(72, table_start), "Algorithm", fontsize=12)
    page1.insert_text(fitz.Point(200, table_start), "Accuracy", fontsize=12)
    page1.insert_text(fitz.Point(300, table_start), "Speed", fontsize=12)
    
    page1.insert_text(fitz.Point(72, table_start + 20), "Method A", fontsize=12)
    page1.insert_text(fitz.Point(200, table_start + 20), "95%", fontsize=12)
    page1.insert_text(fitz.Point(300, table_start + 20), "Fast", fontsize=12)
    
    page1.insert_text(fitz.Point(72, table_start + 40), "Method B", fontsize=12)
    page1.insert_text(fitz.Point(200, table_start + 40), "87%", fontsize=12)
    page1.insert_text(fitz.Point(300, table_start + 40), "Medium", fontsize=12)
    
    # Page 2
    page2 = doc.new_page()
    
    # Add H1 heading
    h1_p2_point = fitz.Point(72, 100)
    page2.insert_text(h1_p2_point, "Chapter 2: Methods", fontsize=16)
    
    # Add H2 headings
    h2_p2_point1 = fitz.Point(72, 150)
    page2.insert_text(h2_p2_point1, "2.1 Data Collection", fontsize=14)
    
    h2_p2_point2 = fitz.Point(72, 200)
    page2.insert_text(h2_p2_point2, "2.2 Analysis", fontsize=14)
    
    # Save the PDF
    doc.save("test_input/sample_document.pdf")
    doc.close()
    
    print("Created test_input/sample_document.pdf")

if __name__ == "__main__":
    create_test_pdf()
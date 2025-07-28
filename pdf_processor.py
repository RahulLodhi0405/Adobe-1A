"""
Main PDF processor that coordinates outline and table extraction
"""

import json
import logging
import time
import unicodedata
from pathlib import Path
from typing import Dict, Any

import fitz  # PyMuPDF
import pdfplumber

from outline_extractor import OutlineExtractor
from table_extractor import TableExtractor
from utils import normalize_unicode_text, detect_document_language

class PDFProcessor:
    """Main processor for extracting outlines and tables from PDFs"""
    
    def __init__(self, max_pages=50):
        self.max_pages = max_pages
        self.outline_extractor = OutlineExtractor()
        self.table_extractor = TableExtractor()
        
    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file and extract outline and table data
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        start_time = time.time()
        
        # Validate file
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if pdf_path.stat().st_size == 0:
            raise ValueError(f"PDF file is empty: {pdf_path}")
        
        # Initialize result structure
        result = {
            "filename": pdf_path.name,
            "title": "",
            "language": "unknown",
            "outline": [],
            "tables": [],
            "page_count": 0,
            "processing_time": 0,
            "errors": []
        }
        
        try:
            # Open PDF with PyMuPDF for outline extraction
            with fitz.open(str(pdf_path)) as pdf_doc:
                page_count = min(len(pdf_doc), self.max_pages)
                result["page_count"] = page_count
                
                if page_count == 0:
                    raise ValueError("PDF contains no pages")
                
                logging.debug(f"Processing {page_count} pages")
                
                # Extract document metadata and title
                metadata = pdf_doc.metadata
                if metadata and metadata.get('title'):
                    result["title"] = normalize_unicode_text(metadata['title'])
                
                # Detect document language from first few pages
                sample_text = ""
                for page_num in range(min(3, page_count)):
                    page = pdf_doc[page_num]
                    page_text = page.get_text()
                    sample_text += normalize_unicode_text(page_text)[:1000]
                
                result["language"] = detect_document_language(sample_text)
                
                # Extract outline
                try:
                    outline_data = self.outline_extractor.extract_outline(pdf_doc, page_count)
                    result["outline"] = outline_data["outline"]
                    if not result["title"] and outline_data.get("title"):
                        result["title"] = outline_data["title"]
                except Exception as e:
                    logging.warning(f"Outline extraction failed: {str(e)}")
                    result["errors"].append(f"Outline extraction: {str(e)}")
            
            # Open PDF with pdfplumber for table extraction
            try:
                with pdfplumber.open(str(pdf_path)) as pdf:
                    tables_data = self.table_extractor.extract_tables(pdf, page_count)
                    result["tables"] = tables_data
            except Exception as e:
                logging.warning(f"Table extraction failed: {str(e)}")
                result["errors"].append(f"Table extraction: {str(e)}")
            
            # If no title found, try to extract from first heading
            if not result["title"] and result["outline"]:
                first_heading = next((item for item in result["outline"] if item["level"] == "H1"), None)
                if first_heading:
                    result["title"] = first_heading["text"]
            
            # Fallback title
            if not result["title"]:
                result["title"] = pdf_path.stem
            
            processing_time = time.time() - start_time
            result["processing_time"] = round(processing_time, 3)
            
            logging.debug(f"Extracted {len(result['outline'])} outline items and {len(result['tables'])} tables")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            result["processing_time"] = round(processing_time, 3)
            result["errors"].append(f"Processing error: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def save_result(self, result: Dict[str, Any], output_path: Path) -> None:
        """
        Save extraction result to JSON file with proper Unicode encoding
        
        Args:
            result: Dictionary containing extraction results
            output_path: Path where to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
            
            logging.debug(f"Results saved to {output_path}")
            
        except Exception as e:
            raise Exception(f"Failed to save results: {str(e)}")

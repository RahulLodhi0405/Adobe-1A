"""
Extract table data from PDF files with multilingual support
"""

import logging
import re
from typing import Dict, List, Any, Optional

import pdfplumber

from utils import normalize_unicode_text, detect_table_structure

class TableExtractor:
    """Extract table data with structure preservation"""
    
    def __init__(self):
        # Minimum table dimensions
        self.min_rows = 2
        self.min_cols = 2
        
        # Table detection settings
        self.table_settings = {
            "vertical_strategy": "lines_strict",
            "horizontal_strategy": "lines_strict",
            "intersection_strategy": "lines_strict",
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
            "min_words_vertical": 1,
            "min_words_horizontal": 1,
            "keep_blank_chars": False,
            "text_tolerance": 3,
            "text_x_tolerance": 3,
            "text_y_tolerance": 3
        }
    
    def extract_tables(self, pdf: pdfplumber.PDF, max_pages: int) -> List[Dict[str, Any]]:
        """
        Extract all tables from PDF with multilingual support
        
        Args:
            pdf: pdfplumber PDF object
            max_pages: Maximum number of pages to process
            
        Returns:
            List of table dictionaries
        """
        all_tables = []
        
        for page_num in range(min(len(pdf.pages), max_pages)):
            try:
                page = pdf.pages[page_num]
                page_tables = self._extract_page_tables(page, page_num + 1)
                all_tables.extend(page_tables)
                
            except Exception as e:
                logging.warning(f"Failed to extract tables from page {page_num + 1}: {str(e)}")
                continue
        
        logging.debug(f"Extracted {len(all_tables)} tables total")
        return all_tables
    
    def _extract_page_tables(self, page: pdfplumber.page.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables from a single page"""
        page_tables = []
        
        try:
            # Find tables using multiple strategies
            tables = page.find_tables(table_settings=self.table_settings)
            
            # If no tables found with strict settings, try relaxed settings
            if not tables:
                relaxed_settings = self.table_settings.copy()
                relaxed_settings.update({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "intersection_strategy": "lines"
                })
                tables = page.find_tables(table_settings=relaxed_settings)
            
            for table_idx, table in enumerate(tables):
                try:
                    table_data = self._process_table(table, page_num, table_idx)
                    if table_data:
                        page_tables.append(table_data)
                        
                except Exception as e:
                    logging.warning(f"Failed to process table {table_idx} on page {page_num}: {str(e)}")
                    continue
            
        except Exception as e:
            logging.warning(f"Failed to find tables on page {page_num}: {str(e)}")
        
        return page_tables
    
    def _process_table(self, table: pdfplumber.table.Table, page_num: int, table_idx: int) -> Optional[Dict[str, Any]]:
        """Process individual table and extract structured data"""
        try:
            # Extract table data
            raw_data = table.extract()
            if not raw_data:
                return None
            
            # Filter out empty rows
            filtered_data = []
            for row in raw_data:
                if row and any(cell and str(cell).strip() for cell in row):
                    filtered_data.append(row)
            
            if len(filtered_data) < self.min_rows:
                return None
            
            # Normalize text in all cells
            normalized_data = []
            for row in filtered_data:
                normalized_row = []
                for cell in row:
                    if cell is None:
                        normalized_row.append("")
                    else:
                        normalized_text = normalize_unicode_text(str(cell))
                        normalized_row.append(normalized_text)
                normalized_data.append(normalized_row)
            
            # Check minimum columns
            max_cols = max(len(row) for row in normalized_data)
            if max_cols < self.min_cols:
                return None
            
            # Standardize row lengths
            standardized_data = []
            for row in normalized_data:
                while len(row) < max_cols:
                    row.append("")
                standardized_data.append(row[:max_cols])
            
            # Detect table structure
            structure_info = detect_table_structure(standardized_data)
            
            # Extract headers if detected
            headers = []
            data_rows = standardized_data
            
            if structure_info.get("has_header", False):
                headers = standardized_data[0]
                data_rows = standardized_data[1:]
            
            # Build table dictionary
            table_dict = {
                "page": page_num,
                "table_index": table_idx,
                "headers": headers,
                "rows": data_rows,
                "row_count": len(data_rows),
                "column_count": max_cols,
                "bbox": table.bbox,
                "structure": structure_info
            }
            
            return table_dict
            
        except Exception as e:
            logging.warning(f"Error processing table: {str(e)}")
            return None
    
    def _clean_cell_text(self, text: str) -> str:
        """Clean and normalize cell text"""
        if not text:
            return ""
        
        # Normalize Unicode
        normalized = normalize_unicode_text(text)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', normalized).strip()
        
        return cleaned

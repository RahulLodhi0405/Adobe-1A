"""
Utility functions for PDF processing with multilingual support
"""

import re
import unicodedata
import logging
from typing import Dict, List, Any, Optional

def normalize_unicode_text(text: str) -> str:
    """
    Normalize Unicode text for consistent processing
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    try:
        # Normalize Unicode to NFC form
        normalized = unicodedata.normalize('NFC', text)
        
        # Remove control characters except newlines and tabs
        cleaned = ''.join(char for char in normalized 
                         if unicodedata.category(char)[0] != 'C' or char in '\n\t')
        
        # Normalize whitespace
        cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
        cleaned = re.sub(r' +', ' ', cleaned)
        
        return cleaned.strip()
        
    except Exception as e:
        logging.warning(f"Failed to normalize text: {str(e)}")
        return str(text).strip()

def detect_document_language(text: str) -> str:
    """
    Detect the primary language of document text
    
    Args:
        text: Sample text from document
        
    Returns:
        Language code or 'unknown'
    """
    if not text:
        return "unknown"
    
    # Simple heuristic-based language detection
    text_sample = text[:1000].lower()
    
    # Check for common language patterns
    if re.search(r'[\u0600-\u06FF]', text_sample):
        return "arabic"
    elif re.search(r'[\u4e00-\u9fff]', text_sample):
        return "chinese"
    elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text_sample):
        return "japanese"
    elif re.search(r'[\u0590-\u05FF]', text_sample):
        return "hebrew"
    elif re.search(r'[\u0400-\u04FF]', text_sample):
        return "russian"
    elif re.search(r'[a-z\s]{10,}', text_sample):
        return "english"
    else:
        return "unknown"

def get_text_direction(text: str) -> str:
    """
    Determine text direction (LTR, RTL, or mixed)
    
    Args:
        text: Text to analyze
        
    Returns:
        Direction: 'ltr', 'rtl', or 'mixed'
    """
    if not text:
        return "ltr"
    
    rtl_chars = 0
    ltr_chars = 0
    
    for char in text:
        direction = unicodedata.bidirectional(char)
        if direction in ('R', 'AL'):  # Right-to-left
            rtl_chars += 1
        elif direction in ('L',):  # Left-to-right
            ltr_chars += 1
    
    total_directional = rtl_chars + ltr_chars
    if total_directional == 0:
        return "ltr"
    
    rtl_ratio = rtl_chars / total_directional
    
    if rtl_ratio > 0.8:
        return "rtl"
    elif rtl_ratio < 0.2:
        return "ltr"
    else:
        return "mixed"

def is_likely_heading(text: str) -> bool:
    """
    Determine if text is likely a heading based on content analysis
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text appears to be a heading
    """
    if not text or len(text) < 2:
        return False
    
    # Skip very long text (likely paragraphs)
    if len(text) > 200:
        return False
    
    # Check for heading indicators
    heading_indicators = [
        # Numbers at start
        r'^\d+\.?\s',
        # Roman numerals
        r'^[IVX]+\.?\s',
        # Letters followed by period
        r'^[A-Za-z]\.?\s',
        # "Chapter", "Section", etc.
        r'^(chapter|section|part|appendix|introduction|conclusion)\s+',
        # Arabic section indicators
        r'^(الفصل|القسم|الجزء|المقدمة|الخاتمة)\s+',
        # Chinese section indicators
        r'^(第.*章|第.*节|附录)',
    ]
    
    text_lower = text.lower()
    for pattern in heading_indicators:
        if re.search(pattern, text_lower):
            return True
    
    # Check if text ends with colon (common in headings)
    if text.rstrip().endswith(':'):
        return True
    
    # Check capitalization patterns
    words = text.split()
    if len(words) <= 8:  # Short text
        # Title case
        if all(word[0].isupper() if word else False for word in words if len(word) > 2):
            return True
        
        # All caps (but not too short to avoid false positives)
        if text.isupper() and len(text) > 5:
            return True
    
    return False

def detect_table_structure(data: List[List[str]]) -> Dict[str, Any]:
    """
    Analyze table structure to detect headers and data patterns
    
    Args:
        data: 2D list representing table data
        
    Returns:
        Dictionary with structure information
    """
    if not data or len(data) < 2:
        return {"has_header": False, "numeric_columns": [], "text_columns": []}
    
    structure = {
        "has_header": False,
        "numeric_columns": [],
        "text_columns": [],
        "empty_columns": [],
        "row_types": []
    }
    
    if not data[0]:
        return structure
    
    num_cols = len(data[0])
    
    # Analyze first row for header characteristics
    first_row = data[0]
    second_row = data[1] if len(data) > 1 else []
    
    # Check if first row looks like headers
    header_score = 0
    
    for i, cell in enumerate(first_row):
        if not cell:
            continue
            
        # Headers often don't contain numbers
        if not re.search(r'\d', cell):
            header_score += 1
        
        # Headers are often shorter
        if len(cell) < 50:
            header_score += 0.5
        
        # Compare with second row if available
        if i < len(second_row) and second_row[i]:
            # If first row is text and second row has numbers
            if not re.search(r'\d', cell) and re.search(r'\d', second_row[i]):
                header_score += 1
    
    structure["has_header"] = header_score > num_cols * 0.6
    
    # Analyze column types
    start_row = 1 if structure["has_header"] else 0
    
    for col_idx in range(num_cols):
        column_values = [row[col_idx] if col_idx < len(row) else "" for row in data[start_row:]]
        column_values = [val for val in column_values if val.strip()]
        
        if not column_values:
            structure["empty_columns"].append(col_idx)
            continue
        
        # Check if column contains mostly numbers
        numeric_count = sum(1 for val in column_values if re.search(r'^\d+\.?\d*$', val.strip()))
        numeric_ratio = numeric_count / len(column_values)
        
        if numeric_ratio > 0.7:
            structure["numeric_columns"].append(col_idx)
        else:
            structure["text_columns"].append(col_idx)
    
    return structure

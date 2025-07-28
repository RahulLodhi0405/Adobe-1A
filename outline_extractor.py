"""
Extract structured document outline from PDF files with multilingual support
"""

import logging
import re
import unicodedata
from typing import Dict, List, Any, Tuple

import fitz  # PyMuPDF

from utils import normalize_unicode_text, is_likely_heading, get_text_direction

class OutlineExtractor:
    """Extract document outline with heading hierarchy detection"""
    
    def __init__(self):
        # Common heading patterns for multiple languages
        self.heading_patterns = {
            'english': [
                r'^(chapter|section|part)\s+\d+',
                r'^\d+\.?\s+[A-Z]',
                r'^[A-Z][A-Z\s]{2,}$',
                r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$'
            ],
            'arabic': [
                r'^(الفصل|القسم|الجزء)\s+\d+',
                r'^\d+\.?\s+[\u0600-\u06FF]',
                r'^[\u0600-\u06FF\s]{3,}$'
            ],
            'chinese': [
                r'^第[一二三四五六七八九十\d]+章',
                r'^第[一二三四五六七八九十\d]+节',
                r'^[\u4e00-\u9fff\s]{2,}$'
            ],
            'japanese': [
                r'^第[一二三四五六七八九十\d]+章',
                r'^[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\s]{2,}$'
            ]
        }
        
        # Minimum confidence threshold for heading detection
        self.min_heading_confidence = 0.6
    
    def extract_outline(self, pdf_doc: fitz.Document, max_pages: int) -> Dict[str, Any]:
        """
        Extract structured outline from PDF document
        
        Args:
            pdf_doc: PyMuPDF document object
            max_pages: Maximum number of pages to process
            
        Returns:
            Dictionary with title and outline data
        """
        outline_data = {
            "title": "",
            "outline": []
        }
        
        # Try to get built-in PDF outline first
        toc = pdf_doc.get_toc()
        if toc:
            outline_data["outline"] = self._process_built_in_outline(toc, max_pages)
            if outline_data["outline"]:
                logging.debug("Using built-in PDF outline")
                return outline_data
        
        # Fallback to text analysis
        logging.debug("No built-in outline found, analyzing text structure")
        
        # Collect text blocks with formatting information
        text_blocks = []
        for page_num in range(max_pages):
            try:
                page = pdf_doc[page_num]
                blocks = self._extract_text_blocks(page, page_num + 1)
                text_blocks.extend(blocks)
            except Exception as e:
                logging.warning(f"Failed to process page {page_num + 1}: {str(e)}")
                continue
        
        # Analyze and classify headings
        headings = self._analyze_headings(text_blocks)
        outline_data["outline"] = self._build_outline_hierarchy(headings)
        
        return outline_data
    
    def _process_built_in_outline(self, toc: List, max_pages: int) -> List[Dict[str, Any]]:
        """Process built-in PDF table of contents"""
        outline = []
        
        for item in toc:
            try:
                level, title, page_num = item
                
                # Skip items beyond max pages
                if page_num > max_pages:
                    continue
                
                # Normalize title text
                normalized_title = normalize_unicode_text(title.strip())
                if not normalized_title:
                    continue
                
                # Map outline level to heading level
                heading_level = f"H{min(level, 3)}"
                
                outline.append({
                    "level": heading_level,
                    "text": normalized_title,
                    "page": page_num
                })
                
            except Exception as e:
                logging.warning(f"Failed to process outline item: {str(e)}")
                continue
        
        return outline
    
    def _extract_text_blocks(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract text blocks with formatting information"""
        blocks = []
        
        try:
            # Get text with formatting details
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" not in block:  # Skip image blocks
                    continue
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span.get("text", "").strip()
                        if not text:
                            continue
                        
                        # Normalize text
                        normalized_text = normalize_unicode_text(text)
                        if not normalized_text:
                            continue
                        
                        # Extract formatting information
                        font_info = {
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0),  # Bold, italic, etc.
                            "bbox": span.get("bbox", [0, 0, 0, 0])
                        }
                        
                        blocks.append({
                            "text": normalized_text,
                            "page": page_num,
                            "font_info": font_info,
                            "line_bbox": line.get("bbox", [0, 0, 0, 0])
                        })
            
        except Exception as e:
            logging.warning(f"Failed to extract text blocks from page {page_num}: {str(e)}")
        
        return blocks
    
    def _analyze_headings(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze text blocks to identify potential headings"""
        headings = []
        
        if not text_blocks:
            return headings
        
        # Calculate font size statistics for relative size analysis
        font_sizes = [block["font_info"]["size"] for block in text_blocks if block["font_info"]["size"] > 0]
        if not font_sizes:
            return headings
        
        avg_font_size = sum(font_sizes) / len(font_sizes)
        max_font_size = max(font_sizes)
        
        for block in text_blocks:
            text = block["text"]
            font_info = block["font_info"]
            
            # Skip very short or very long text
            if len(text) < 2 or len(text) > 200:
                continue
            
            # Calculate heading confidence score
            confidence = self._calculate_heading_confidence(text, font_info, avg_font_size, max_font_size)
            
            if confidence >= self.min_heading_confidence:
                heading_level = self._determine_heading_level(font_info, avg_font_size, confidence)
                
                headings.append({
                    "text": text,
                    "page": block["page"],
                    "level": heading_level,
                    "confidence": confidence,
                    "font_size": font_info["size"]
                })
        
        # Sort by page and position
        headings.sort(key=lambda x: (x["page"], x.get("font_size", 0)), reverse=False)
        
        return headings
    
    def _calculate_heading_confidence(self, text: str, font_info: Dict, avg_font_size: float, max_font_size: float) -> float:
        """Calculate confidence score for text being a heading"""
        confidence = 0.0
        
        # Font size factor
        font_size = font_info.get("size", 0)
        if font_size > avg_font_size * 1.2:
            confidence += 0.3
        if font_size > avg_font_size * 1.5:
            confidence += 0.2
        
        # Bold text
        flags = font_info.get("flags", 0)
        if flags & 2**4:  # Bold flag
            confidence += 0.2
        
        # Text characteristics
        if is_likely_heading(text):
            confidence += 0.3
        
        # Pattern matching
        text_direction = get_text_direction(text)
        patterns = self.heading_patterns.get('english', [])  # Default to English patterns
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                confidence += 0.2
                break
        
        # Position-based factors (standalone lines are more likely to be headings)
        if len(text.split()) <= 10:  # Short lines
            confidence += 0.1
        
        # Capitalization patterns
        if text.isupper() and len(text) > 2:
            confidence += 0.1
        elif text.istitle():
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_heading_level(self, font_info: Dict, avg_font_size: float, confidence: float) -> str:
        """Determine heading level based on font characteristics"""
        font_size = font_info.get("size", 0)
        
        if font_size > avg_font_size * 1.8:
            return "H1"
        elif font_size > avg_font_size * 1.4:
            return "H2"
        else:
            return "H3"
    
    def _build_outline_hierarchy(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build final outline structure from detected headings"""
        outline = []
        
        for heading in headings:
            outline_item = {
                "level": heading["level"],
                "text": heading["text"],
                "page": heading["page"]
            }
            outline.append(outline_item)
        
        return outline

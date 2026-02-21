#!/usr/bin/env python3
"""
Multilingual PDF Outline and Table Extractor
Main entry point for the PDF processing application
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import time
from pdf_processor import PDFProcessor

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

def validate_directories(input_dir, output_dir):
    """Validate input and output directories"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    
    if not input_path.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    return input_path, output_path

def get_pdf_files(input_dir):
    """Get list of PDF files from input directory"""
    pdf_files = list(input_dir.glob("*.pdf"))
    pdf_files.extend(list(input_dir.glob("*.PDF")))
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {input_dir}")
    
    return pdf_files

def main():
    parser = argparse.ArgumentParser(
        description="Extract structured outlines and table data from PDF files with full Unicode support"
    )
    parser.add_argument(
        "--input", "-i",
        default="./input",
        help="Input directory containing PDF files (default: ./input)"
    )
    parser.add_argument(
        "--output", "-o", 
        default="./output",
        help="Output directory for JSON files (default: ./output)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to process per PDF (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logging.info("Starting multilingual PDF processing application")
    
    try:
        # Validate directories
        input_dir, output_dir = validate_directories(args.input, args.output)
        logging.info(f"Input directory: {input_dir}")
        logging.info(f"Output directory: {output_dir}")
        
        # Get PDF files
        
        pdf_files = get_pdf_files(input_dir)
        logging.info(f"Found {len(pdf_files)} PDF files to process")
        
        if not pdf_files:
            logging.info("No PDF files to process. Exiting.")
            return 0
        
        # Initialize processor
        processor = PDFProcessor(max_pages=args.max_pages)
        
        # Process each PDF file
        success_count = 0
        total_start_time = time.time()
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logging.info(f"Processing file {i}/{len(pdf_files)}: {pdf_file.name}")
            
            start_time = time.time()
            try:
                result = processor.process_pdf(pdf_file)
                
                # Generate output filename
                output_filename = pdf_file.stem + ".json"
                output_path = output_dir / output_filename
                
                # Save result
                processor.save_result(result, output_path)
                
                processing_time = time.time() - start_time
                logging.info(f"Successfully processed {pdf_file.name} in {processing_time:.2f} seconds")
                success_count += 1
                
            except Exception as e:
                processing_time = time.time() - start_time
                logging.error(f"Failed to process {pdf_file.name} after {processing_time:.2f} seconds: {str(e)}")
                continue
        
        total_time = time.time() - total_start_time
        logging.info(f"Processing complete: {success_count}/{len(pdf_files)} files successful")
        logging.info(f"Total processing time: {total_time:.2f} seconds")
        
        return 0 if success_count > 0 else 1
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash

# Multilingual PDF Processor Runner Script
# This script runs the PDF processor with proper error handling

set -e

# Default directories
INPUT_DIR="./input"
OUTPUT_DIR="./output"
VERBOSE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input|-i)
            INPUT_DIR="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --input, -i DIR     Input directory containing PDF files (default: ./input)"
            echo "  --output, -o DIR    Output directory for JSON files (default: ./output)"
            echo "  --verbose, -v       Enable verbose logging"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create directories if they don't exist
mkdir -p "$INPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "Starting multilingual PDF processor..."
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if required Python packages are available
python3 -c "import fitz, pdfplumber" 2>/dev/null || {
    echo "Error: Required Python packages are not installed"
    echo "Please install: PyMuPDF and pdfplumber"
    exit 1
}

# Run the processor
echo "Processing PDFs..."
python3 main.py --input "$INPUT_DIR" --output "$OUTPUT_DIR" $VERBOSE

echo "Processing complete!"

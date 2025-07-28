# Multilingual PDF Outline and Table Extractor

A robust Python application for extracting structured outlines and table data from PDF files with comprehensive Unicode support for all languages including RTL scripts (Arabic, Hebrew), CJK languages (Chinese, Japanese, Korean), and complex scripts.

## Features

- **Multilingual Support**: Full Unicode support for all writing systems
- **Outline Extraction**: Structured document outline with heading hierarchy (H1, H2, H3)
- **Table Extraction**: Complete table data with structure preservation
- **Language Detection**: Automatic detection of document language
- **Text Direction**: Proper handling of LTR, RTL, and mixed text directions
- **Robust Processing**: Multiple fallback strategies for outline and table detection
- **Fast Processing**: Optimized for processing under 10 seconds per PDF
- **Batch Processing**: Process multiple PDFs from input directory

## Requirements

- Python 3.7+
- PyMuPDF (fitz)
- pdfplumber

## Installation

### Option 1: Docker (Recommended)

1. Build the Docker image:
```bash
chmod +x build_docker.sh
./build_docker.sh
```

2. Create input and output directories:
```bash
mkdir -p input output
```

3. Place your PDF files in the `input` directory

4. Run the container:
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution:latest
```

### Option 2: Local Installation

1. Install required Python packages:
```bash
pip install PyMuPDF pdfplumber
```

2. Create directories and run:
```bash
mkdir -p input output
python3 main.py --input ./input --output ./output
```

## Docker Usage

The application is designed to run in a Docker container with no internet access. The container meets the requirements:

- **CPU-only processing** (amd64 architecture)
- **Model size ≤ 200MB** (uses only algorithmic approaches, no ML models)
- **Fast processing** (under 10 seconds per PDF)
- **No internet access** (uses `--network none`)

### Build and Run

```bash
# Build the image
./build_docker.sh

# Run with your PDFs
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution:latest
```

### Advanced Docker Options

```bash
# Custom page limit
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution:latest \
  python3 main.py --input /app/input --output /app/output --max-pages 30

# Verbose logging
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution:latest \
  python3 main.py --input /app/input --output /app/output --verbose
```

## Output Format

The application generates JSON files with the following structure:

```json
{
  "filename": "document.pdf",
  "title": "Document Title",
  "language": "english",
  "page_count": 20,
  "processing_time": 4.231,
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "What is AI?",
      "page": 2
    }
  ],
  "tables": [
    {
      "page": 10,
      "table_index": 0,
      "headers": ["Algorithm", "Accuracy", "Training Time"],
      "rows": [
        ["Decision Tree", "85.2%", "2.1 seconds"],
        ["Random Forest", "91.7%", "8.4 seconds"]
      ],
      "row_count": 2,
      "column_count": 3,
      "structure": {
        "has_header": true,
        "numeric_columns": [1, 2],
        "text_columns": [0]
      }
    }
  ],
  "errors": []
}
```

See `example_output.json` and `example_multilingual_output.json` for complete examples with English and multilingual content.

## Usage

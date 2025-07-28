---

# **Multilingual PDF Outline & Table Extractor**

A high-performance Python application for extracting structured outlines and table data from PDF files with full multilingual support. Designed to handle complex scripts and global writing systems, including RTL (Arabic, Hebrew), CJK (Chinese, Japanese, Korean), and mixed-direction texts.

---

## **Key Features**

* ✅ **Full Multilingual Support** – Comprehensive Unicode handling for all writing systems
* ✅ **Structured Outline Extraction** – Generate hierarchical document outlines (H1, H2, H3)
* ✅ **Accurate Table Extraction** – Preserve table structure and content integrity
* ✅ **Automatic Language Detection** – Identify primary document language seamlessly
* ✅ **Directional Text Handling** – Properly manage LTR, RTL, and mixed text
* ✅ **Optimized Performance** – Average processing time under 10 seconds per PDF
* ✅ **Batch Processing** – Process multiple PDFs simultaneously

---

## **System Requirements**

* **Python**: 3.7 or later
* **Libraries**:

  * [PyMuPDF (fitz)](https://pymupdf.readthedocs.io)
  * [pdfplumber](https://github.com/jsvine/pdfplumber)

---

## **Installation & Setup**

### **Option 1: Docker (Recommended)**

1. **Build the Docker image**

   ```bash
   chmod +x build_docker.sh
   ./build_docker.sh
   ```

2. **Prepare input/output directories**

   ```bash
   mkdir -p input output
   ```

3. **Add PDF files to `input` folder**

4. **Run the container**

   ```bash
   docker run --rm \
     -v $(pwd)/input:/app/input \
     -v $(pwd)/output:/app/output \
     --network none mysolution:latest
   ```

---

### **Option 2: Local Installation**

1. **Install dependencies**

   ```bash
   pip install PyMuPDF pdfplumber
   ```

2. **Create required directories & execute**

   ```bash
   mkdir -p input output
   python3 main.py --input ./input --output ./output
   ```

---

## **Docker Runtime Specifications**

* ✅ **Offline Mode** – No internet access (`--network none`)
* ✅ **Lightweight** – Model size ≤ 200MB (algorithmic approach only)
* ✅ **CPU-Optimized** – Runs on amd64 architecture
* ✅ **Fast Execution** – Under 10 seconds per PDF

---

### **Advanced Docker Usage**

**Custom page limit**

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none mysolution:latest \
  python3 main.py --input /app/input --output /app/output --max-pages 30
```

**Enable verbose logging**

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none mysolution:latest \
  python3 main.py --input /app/input --output /app/output --verbose
```

---

## **Output Structure**

The tool produces **JSON files** for each processed PDF, containing:

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

See examples in:

* `example_output.json`
* `example_multilingual_output.json`

---

## **Usage**

Run the script via CLI or inside Docker as shown above. Add `--help` for full options:

```bash
python3 main.py --help
```

---


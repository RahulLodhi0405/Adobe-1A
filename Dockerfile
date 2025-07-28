# Multilingual PDF Outline and Table Extractor Dockerfile
# CPU-only, optimized for amd64 architecture

FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Install Python dependencies directly (no requirements.txt needed)
# Using specific versions for reproducible builds and CPU-only processing
RUN pip install --no-cache-dir \
    PyMuPDF==1.26.3 \
    pdfplumber==0.11.7

# Copy application files
COPY main.py .
COPY pdf_processor.py .
COPY outline_extractor.py .
COPY table_extractor.py .
COPY utils.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash pdfuser && \
    chown -R pdfuser:pdfuser /app
USER pdfuser

# Set default command
CMD ["python3", "main.py", "--input", "/app/input", "--output", "/app/output", "--verbose"]

# Health check to ensure the application can start
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 main.py --help > /dev/null || exit 1

# Labels for container metadata
LABEL maintainer="PDF Processor" \
      description="Multilingual PDF outline and table extractor" \
      version="1.0"

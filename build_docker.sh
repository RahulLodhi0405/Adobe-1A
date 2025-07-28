#!/bin/bash

# Docker build script for Multilingual PDF Processor
# Builds the container and provides usage instructions

set -e

# Configuration
IMAGE_NAME="mysolution"
TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo "Building Multilingual PDF Processor Docker image..."
echo "Image name: ${FULL_IMAGE_NAME}"

# Build the Docker image
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 Usage Instructions:"
    echo ""
    echo "1. Create input and output directories:"
    echo "   mkdir -p input output"
    echo ""
    echo "2. Place your PDF files in the 'input' directory"
    echo ""
    echo "3. Run the container:"
    echo "   docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none ${FULL_IMAGE_NAME}"
    echo ""
    echo "4. Results will be saved as JSON files in the 'output' directory"
    echo ""
    echo "📋 Container Details:"
    docker images "${FULL_IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    echo "🔧 Advanced Usage:"
    echo "   # With custom max pages (default: 50)"
    echo "   docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none ${FULL_IMAGE_NAME} python3 main.py --input /app/input --output /app/output --max-pages 30"
    echo ""
    echo "   # Verbose logging"
    echo "   docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none ${FULL_IMAGE_NAME} python3 main.py --input /app/input --output /app/output --verbose"
else
    echo "❌ Docker build failed!"
    exit 1
fi

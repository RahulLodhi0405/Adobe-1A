#!/usr/bin/env python3
"""
Simple web interface for the Multilingual PDF Processor
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf_processor import PDFProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        # Process the PDF
        processor = PDFProcessor(max_pages=50)
        result = processor.process_pdf(filepath)
        
        # Clean up uploaded file
        filepath.unlink()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'message': 'Multilingual PDF Processor is ready',
        'features': [
            'PDF outline extraction (H1, H2, H3 headings)',
            'Table data extraction',
            'Multilingual support (Arabic, Chinese, Japanese, Hebrew, etc.)',
            'Fast processing (under 10 seconds)',
            'Unicode text normalization',
            'Language detection'
        ]
    })

@app.route('/templates/index.html')
def serve_template():
    return send_file('templates/index.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start the web server
    app.run(host='0.0.0.0', port=5000, debug=True)

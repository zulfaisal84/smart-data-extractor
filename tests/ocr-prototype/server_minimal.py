#!/usr/bin/env python3
"""
Minimal OCR Testing Backend - Flask Application
For testing basic functionality without OCR dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'tesseract': False,  # Not installed yet
            'google_vision': False,
            'aws_textract': False
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided', 'status': 'error'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected', 'status': 'error'}), 400
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        saved_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        
        file.save(file_path)
        
        logger.info(f"File uploaded: {file_id} -> {file_path}")
        
        return jsonify({
            'file_id': file_id,
            'filename': filename,
            'status': 'uploaded',
            'message': 'File uploaded successfully. Use /api/process/{file_id} to start OCR processing.'
        }), 200
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({
            'error': f'Upload failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/services', methods=['GET'])
def list_services():
    """List available OCR services"""
    services = {
        'tesseract': {
            'name': 'Tesseract (Local)',
            'available': False,  # Will be True when installed
            'description': 'Open-source OCR engine, works offline'
        },
        'google': {
            'name': 'Google Vision API',
            'available': False,
            'description': 'Google Cloud Vision API, requires API key'
        },
        'aws': {
            'name': 'AWS Textract',
            'available': False,
            'description': 'Amazon Textract service, requires AWS credentials'
        }
    }
    
    return jsonify({
        'services': services,
        'recommended': 'tesseract'
    }), 200

@app.route('/api/process/<file_id>', methods=['POST'])
def process_file(file_id):
    """Mock OCR processing endpoint"""
    try:
        data = request.get_json() if request.is_json else {}
        service = data.get('service', 'tesseract').lower()
        
        process_id = str(uuid.uuid4())
        
        # Mock processing result
        mock_result = {
            'process_id': process_id,
            'file_id': file_id,
            'service': service,
            'status': 'success',
            'processing_time': 1.5,
            'text': f'MOCK OCR RESULT\n\nFile ID: {file_id}\nService: {service}\n\nThis is a test extraction result.\nReal OCR will be available after installing Tesseract.',
            'confidence': 0.0,
            'pages_processed': 1,
            'words_found': 15
        }
        
        # Store mock result (in production, use database)
        app.config[f'result_{process_id}'] = mock_result
        
        return jsonify({
            'process_id': process_id,
            'file_id': file_id,
            'service': service,
            'status': 'started',
            'message': f'Mock OCR processing completed with {service}.'
        }), 200
        
    except Exception as e:
        logger.error(f"Process error: {str(e)}")
        return jsonify({
            'error': f'Processing failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/result/<process_id>', methods=['GET'])
def get_result(process_id):
    """Get processing result"""
    try:
        result = app.config.get(f'result_{process_id}')
        
        if not result:
            return jsonify({
                'error': f'Process not found: {process_id}',
                'status': 'error'
            }), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Result retrieval error: {str(e)}")
        return jsonify({
            'error': f'Failed to get result: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting OCR Testing Backend (Minimal Version)")
    print("📍 Server: http://127.0.0.1:5000")
    print("📋 Health: http://127.0.0.1:5000/api/health")
    print("📋 Services: http://127.0.0.1:5000/api/services")
    print()
    
    app.run(host='127.0.0.1', port=5000, debug=True)
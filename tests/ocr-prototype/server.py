#!/usr/bin/env python3
"""
OCR Testing Backend - Flask Application
Smart Data Extractor (SME) Project

Main Flask application for testing OCR services with file uploads.
Supports Tesseract (local), Google Vision API, and AWS Textract.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import time
import logging
import signal
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from file_handler import FileHandler
from ocr_services import OCRServices

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
ocr_services = OCRServices()

# In-memory storage for processing status (use Redis in production)
processing_status = {}

# Simple timeout tracking (signal-based timeout removed due to threading issues)
class ProcessingTimeoutError(Exception):
    pass

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large. Maximum size is 10MB.',
        'status': 'error'
    }), 413

@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request. Please check your input.',
        'status': 'error'
    }), 400

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error. Please try again later.',
        'status': 'error'
    }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'tesseract': ocr_services.check_tesseract_available(),
            'google_vision': ocr_services.check_google_vision_available(),
            'aws_textract': ocr_services.check_aws_textract_available()
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload file endpoint
    Accepts PDF, JPG, PNG files up to 10MB
    Returns file_id for processing
    """
    try:
        logger.info("=== FILE UPLOAD REQUEST STARTED ===")
        
        # Check if file is in request
        if 'file' not in request.files:
            logger.error("Upload failed: No file in request")
            return jsonify({'error': 'No file provided', 'status': 'error'}), 400
        
        file = request.files['file']
        logger.info(f"File received: filename='{file.filename}', content_type='{file.content_type}'")
        
        if file.filename == '':
            logger.error("Upload failed: Empty filename")
            return jsonify({'error': 'No file selected', 'status': 'error'}), 400
        
        # Get file size by seeking to end
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        logger.info(f"File size: {file_size} bytes ({file_size/(1024*1024):.2f} MB)")
        
        # Check file size
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            logger.error(f"Upload failed: File too large ({file_size} bytes > {app.config['MAX_CONTENT_LENGTH']} bytes)")
            return jsonify({
                'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"]/(1024*1024):.1f}MB, your file is {file_size/(1024*1024):.2f}MB',
                'status': 'error',
                'max_size_mb': app.config["MAX_CONTENT_LENGTH"]/(1024*1024),
                'file_size_mb': file_size/(1024*1024)
            }), 413
        
        # Validate file type
        if not file_handler.allowed_file(file.filename):
            logger.error(f"Upload failed: Invalid file type '{file.filename}'")
            return jsonify({
                'error': 'Invalid file type. Supported: PDF, JPG, JPEG, PNG',
                'status': 'error'
            }), 400
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        logger.info(f"Generated file_id: {file_id}")
        
        # Save file
        logger.info("Attempting to save file...")
        saved_path = file_handler.save_file(file, file_id)
        logger.info(f"File saved successfully: {file_id} -> {saved_path}")
        
        # Verify saved file
        if os.path.exists(saved_path):
            actual_size = os.path.getsize(saved_path)
            logger.info(f"File verification: exists=True, size={actual_size} bytes")
        else:
            logger.error(f"File verification failed: {saved_path} does not exist")
            raise Exception("File was not saved properly")
        
        logger.info("=== FILE UPLOAD COMPLETED SUCCESSFULLY ===")
        
        return jsonify({
            'file_id': file_id,
            'filename': secure_filename(file.filename),
            'file_size': file_size,
            'saved_path': saved_path,
            'status': 'uploaded',
            'message': 'File uploaded successfully. Use /api/process/{file_id} to start OCR processing.'
        }), 200
        
    except RequestEntityTooLarge:
        logger.error("Upload failed: RequestEntityTooLarge exception")
        return jsonify({
            'error': 'File too large. Maximum size is 10MB.',
            'status': 'error'
        }), 413
    except Exception as e:
        logger.error(f"=== UPLOAD ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        logger.error("=== END UPLOAD ERROR ===")
        return jsonify({
            'error': f'Upload failed: {str(e)}',
            'status': 'error',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/process/<file_id>', methods=['POST'])
def process_file(file_id):
    """
    Process file with OCR service
    Body: {"service": "tesseract|google|aws"}
    Returns process_id for status tracking
    """
    try:
        logger.info("=== OCR PROCESSING REQUEST STARTED ===")
        logger.info(f"File ID: {file_id}")
        
        # Validate request data
        if not request.is_json:
            logger.error("Processing failed: Request is not JSON")
            return jsonify({'error': 'Content-Type must be application/json', 'status': 'error'}), 400
        
        data = request.get_json()
        service = data.get('service', 'tesseract').lower()
        logger.info(f"Requested service: {service}")
        
        if service not in ['tesseract', 'google', 'aws']:
            logger.error(f"Processing failed: Invalid service '{service}'")
            return jsonify({
                'error': 'Invalid service. Choose: tesseract, google, or aws',
                'status': 'error'
            }), 400
        
        # Check if file exists
        logger.info("Checking if file exists...")
        if not file_handler.file_exists(file_id):
            logger.error(f"Processing failed: File not found '{file_id}'")
            return jsonify({
                'error': f'File not found: {file_id}',
                'status': 'error'
            }), 404
        
        file_path = file_handler.get_file_path(file_id)
        logger.info(f"File found: {file_path}")
        
        # Get file info
        file_info = file_handler.get_file_info(file_path)
        logger.info(f"File info: size={file_info['size']} bytes, type={file_info['extension']}, is_pdf={file_info['is_pdf']}")
        
        # Generate process ID
        process_id = str(uuid.uuid4())
        logger.info(f"Generated process_id: {process_id}")
        
        # Initialize processing status
        processing_status[process_id] = {
            'file_id': file_id,
            'service': service,
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat(),
            'processing_time': None,
            'text': None,
            'confidence': None,
            'error': None,
            'file_info': file_info
        }
        
        logger.info(f"Starting OCR processing: {process_id} with {service}")
        
        # Start OCR processing (synchronous for now, can be made async)
        start_time = time.time()
        
        try:
            # Get file path and process
            logger.info(f"Calling OCR service: {service}")
            
            if service == 'tesseract':
                logger.info("Processing with Tesseract...")
                result = ocr_services.process_with_tesseract(file_path)
            elif service == 'google':
                logger.info("Processing with Google Vision API...")
                result = ocr_services.process_with_google_vision(file_path)
            elif service == 'aws':
                logger.info("Processing with AWS Textract...")
                result = ocr_services.process_with_aws_textract(file_path)
            
            processing_time = time.time() - start_time
            logger.info(f"OCR service completed in {processing_time:.2f}s")
            logger.info(f"Result preview: text_length={len(result.get('text', ''))}, confidence={result.get('confidence', 0.0)}")
            
            # Update status with results
            processing_status[process_id].update({
                'status': 'success',
                'processing_time': round(processing_time, 2),
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0.0),
                'completed_at': datetime.utcnow().isoformat(),
                'words_found': result.get('words_found', 0),
                'pages_processed': result.get('pages_processed', 1)
            })
            
            logger.info(f"OCR processing completed successfully: {process_id}")
            logger.info("=== OCR PROCESSING COMPLETED SUCCESSFULLY ===")
            
        except Exception as ocr_error:
            processing_time = time.time() - start_time
            error_msg = str(ocr_error)
            
            logger.error("=== OCR PROCESSING ERROR ===")
            logger.error(f"Error type: {type(ocr_error).__name__}")
            logger.error(f"Error message: {error_msg}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            logger.error("=== END OCR PROCESSING ERROR ===")
            
            processing_status[process_id].update({
                'status': 'error',
                'processing_time': round(processing_time, 2),
                'error': error_msg,
                'error_type': type(ocr_error).__name__,
                'completed_at': datetime.utcnow().isoformat()
            })
            
            logger.error(f"OCR processing failed: {process_id} - {error_msg}")
        
        return jsonify({
            'process_id': process_id,
            'file_id': file_id,
            'service': service,
            'status': 'started',
            'message': f'OCR processing started with {service}. Use /api/status/{process_id} to check progress.'
        }), 200
        
    except Exception as e:
        logger.error(f"Process initiation error: {str(e)}")
        return jsonify({
            'error': f'Failed to start processing: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/status/<process_id>', methods=['GET'])
def get_status(process_id):
    """Get processing status"""
    try:
        if process_id not in processing_status:
            return jsonify({
                'error': f'Process not found: {process_id}',
                'status': 'error'
            }), 404
        
        status_info = processing_status[process_id].copy()
        return jsonify(status_info), 200
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'error': f'Failed to get status: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/result/<process_id>', methods=['GET'])
def get_result(process_id):
    """Get processing result"""
    try:
        if process_id not in processing_status:
            return jsonify({
                'error': f'Process not found: {process_id}',
                'status': 'error'
            }), 404
        
        result = processing_status[process_id]
        
        if result['status'] == 'processing':
            return jsonify({
                'process_id': process_id,
                'status': 'processing',
                'message': 'Processing still in progress. Please wait.'
            }), 202  # Accepted, still processing
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Result retrieval error: {str(e)}")
        return jsonify({
            'error': f'Failed to get result: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/services', methods=['GET'])
def list_services():
    """List available OCR services and their status"""
    try:
        services = {
            'tesseract': {
                'name': 'Tesseract (Local)',
                'available': ocr_services.check_tesseract_available(),
                'description': 'Open-source OCR engine, works offline'
            },
            'google': {
                'name': 'Google Vision API',
                'available': ocr_services.check_google_vision_available(),
                'description': 'Google Cloud Vision API, requires API key'
            },
            'aws': {
                'name': 'AWS Textract',
                'available': ocr_services.check_aws_textract_available(),
                'description': 'Amazon Textract service, requires AWS credentials'
            }
        }
        
        return jsonify({
            'services': services,
            'recommended': 'google' if services['google']['available'] else 'tesseract'
        }), 200
        
    except Exception as e:
        logger.error(f"Service listing error: {str(e)}")
        return jsonify({
            'error': f'Failed to list services: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old files and processing records"""
    try:
        # Get optional age parameter (hours)
        age_hours = request.get_json().get('age_hours', 24) if request.is_json else 24
        
        cleaned_files = file_handler.cleanup_old_files(age_hours)
        
        # Clean up old processing records
        current_time = datetime.utcnow()
        old_processes = []
        
        for process_id, status in list(processing_status.items()):
            created_at = datetime.fromisoformat(status['created_at'])
            age = (current_time - created_at).total_seconds() / 3600
            
            if age > age_hours:
                old_processes.append(process_id)
                del processing_status[process_id]
        
        logger.info(f"Cleanup completed: {cleaned_files} files, {len(old_processes)} process records")
        
        return jsonify({
            'status': 'success',
            'cleaned_files': cleaned_files,
            'cleaned_processes': len(old_processes),
            'age_hours': age_hours
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({
            'error': f'Cleanup failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/debug/test-ocr', methods=['GET'])
def test_ocr():
    """Debug endpoint to test basic OCR functionality"""
    try:
        logger.info("=== DEBUG OCR TEST STARTED ===")
        
        # Create a simple test image
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        # Create test image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        test_text = "TEST OCR FUNCTIONALITY\nThis is a debug test.\n123 ABC xyz"
        draw.text((20, 20), test_text, fill='black')
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name, 'PNG')
        temp_path = temp_file.name
        
        logger.info(f"Created test image: {temp_path}")
        
        # Test OCR services
        results = {}
        
        # Test Tesseract
        try:
            logger.info("Testing Tesseract...")
            if ocr_services.check_tesseract_available():
                result = ocr_services.process_with_tesseract(temp_path)
                results['tesseract'] = {
                    'available': True,
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0.0),
                    'processing_time': result.get('processing_time', 0.0),
                    'status': 'success'
                }
                logger.info(f"Tesseract test successful: {len(result.get('text', ''))} chars")
            else:
                results['tesseract'] = {
                    'available': False,
                    'status': 'not_available',
                    'error': 'Tesseract not installed or configured'
                }
        except Exception as e:
            logger.error(f"Tesseract test failed: {str(e)}")
            results['tesseract'] = {
                'available': True,
                'status': 'error',
                'error': str(e)
            }
        
        # Test Google Vision (will be mock if not configured)
        try:
            logger.info("Testing Google Vision...")
            result = ocr_services.process_with_google_vision(temp_path)
            results['google_vision'] = {
                'available': ocr_services.check_google_vision_available(),
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0.0),
                'processing_time': result.get('processing_time', 0.0),
                'status': 'success' if result.get('confidence', 0) > 0 else 'mock'
            }
        except Exception as e:
            logger.error(f"Google Vision test failed: {str(e)}")
            results['google_vision'] = {
                'available': False,
                'status': 'error',
                'error': str(e)
            }
        
        # Test AWS Textract (will be mock if not configured)
        try:
            logger.info("Testing AWS Textract...")
            result = ocr_services.process_with_aws_textract(temp_path)
            results['aws_textract'] = {
                'available': ocr_services.check_aws_textract_available(),
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0.0),
                'processing_time': result.get('processing_time', 0.0),
                'status': 'success' if result.get('confidence', 0) > 0 else 'mock'
            }
        except Exception as e:
            logger.error(f"AWS Textract test failed: {str(e)}")
            results['aws_textract'] = {
                'available': False,
                'status': 'error',
                'error': str(e)
            }
        
        # Clean up temp file
        import os
        try:
            os.unlink(temp_path)
        except:
            pass
        
        # System information
        system_info = {
            'tesseract_version': None,
            'python_version': __import__('sys').version,
            'platform': __import__('platform').platform(),
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'upload_folder_writable': os.access(app.config['UPLOAD_FOLDER'], os.W_OK),
            'max_file_size': app.config['MAX_CONTENT_LENGTH']
        }
        
        # Try to get Tesseract version
        try:
            import pytesseract
            system_info['tesseract_version'] = str(pytesseract.get_tesseract_version())
        except:
            system_info['tesseract_version'] = 'Not available'
        
        logger.info("=== DEBUG OCR TEST COMPLETED ===")
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'test_results': results,
            'system_info': system_info,
            'recommendations': [
                'Tesseract working' if results.get('tesseract', {}).get('status') == 'success' else 'Install Tesseract: brew install tesseract',
                'Upload folder accessible' if system_info['upload_folder_writable'] else 'Check upload folder permissions',
                'All OCR services tested' if len(results) == 3 else 'Some OCR services failed'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Debug test error: {str(e)}")
        import traceback
        logger.error(f"Debug test traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Frontend serving routes
@app.route('/')
def index():
    """Serve the frontend HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Print startup information
    print("🚀 Starting OCR Testing Backend")
    print(f"📍 API endpoints: http://{app.config['HOST']}:{app.config['PORT']}/api/")
    print(f"🌐 Frontend available at: http://{app.config['HOST']}:{app.config['PORT']}/")
    print(f"📋 Health check: http://{app.config['HOST']}:{app.config['PORT']}/api/health")
    print()
    
    # Run Flask app
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
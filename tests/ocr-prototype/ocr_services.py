"""
OCR Services Module
Smart Data Extractor (SME) - OCR Testing Backend

Implements OCR processing using multiple services:
- Tesseract (local)
- Google Vision API
- AWS Textract

Each service returns a standardized result format.
"""

import os
import logging
from typing import Dict, Any, List
import time
from PIL import Image

# OCR Service imports
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    vision = None

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

from file_handler import FileHandler

logger = logging.getLogger(__name__)

class OCRServices:
    """Manages multiple OCR service implementations"""
    
    def __init__(self):
        """Initialize OCR services"""
        self.file_handler = None  # Will be set by server
        self._setup_services()
    
    def _setup_services(self):
        """Setup and validate OCR services"""
        logger.info("Setting up OCR services...")
        
        # Test Tesseract
        if TESSERACT_AVAILABLE:
            try:
                # Try to get Tesseract version
                version = pytesseract.get_tesseract_version()
                logger.info(f"Tesseract available: {version}")
            except Exception as e:
                logger.warning(f"Tesseract setup issue: {str(e)}")
        
        # Test Google Vision
        if GOOGLE_VISION_AVAILABLE:
            try:
                # Check if credentials are available
                if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('GOOGLE_CLOUD_PROJECT'):
                    logger.info("Google Vision API credentials found")
                else:
                    logger.info("Google Vision API available but no credentials configured")
            except Exception as e:
                logger.warning(f"Google Vision setup issue: {str(e)}")
        
        # Test AWS
        if AWS_AVAILABLE:
            try:
                # Check if AWS credentials are available
                if os.getenv('AWS_ACCESS_KEY_ID') or os.path.exists(os.path.expanduser('~/.aws/credentials')):
                    logger.info("AWS credentials found")
                else:
                    logger.info("AWS Textract available but no credentials configured")
            except Exception as e:
                logger.warning(f"AWS setup issue: {str(e)}")
    
    def check_tesseract_available(self) -> bool:
        """Check if Tesseract is available and working"""
        if not TESSERACT_AVAILABLE:
            return False
        
        try:
            # Try to run a simple OCR test
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.error(f"Tesseract not available: {str(e)}")
            return False
    
    def check_google_vision_available(self) -> bool:
        """Check if Google Vision API is available"""
        if not GOOGLE_VISION_AVAILABLE:
            return False
        
        try:
            # Check for API key or credentials
            import os
            api_key = os.getenv('GOOGLE_VISION_API_KEY')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if api_key or credentials_path:
                # Try to create a client
                client = vision.ImageAnnotatorClient()
                return True
            else:
                logger.info("No Google Vision credentials found")
                return False
        except Exception as e:
            logger.error(f"Google Vision not available: {str(e)}")
            return False
    
    def check_aws_textract_available(self) -> bool:
        """Check if AWS Textract is available"""
        if not AWS_AVAILABLE:
            return False
        
        try:
            # Try to create a client
            client = boto3.client('textract')
            return True
        except Exception as e:
            logger.error(f"AWS Textract not available: {str(e)}")
            return False
    
    def process_with_tesseract(self, file_path: str) -> Dict[str, Any]:
        """
        Process file with Tesseract OCR
        
        Args:
            file_path: Path to file (PDF will be converted to images)
            
        Returns:
            Standardized OCR result
        """
        try:
            if not self.check_tesseract_available():
                raise RuntimeError("Tesseract is not available")
            
            logger.info(f"Processing with Tesseract: {file_path}")
            start_time = time.time()
            
            # Prepare file(s) for OCR
            if file_path.lower().endswith('.pdf'):
                # Use FileHandler to convert PDF to images
                temp_file_handler = FileHandler(os.path.dirname(file_path))
                image_paths = temp_file_handler.convert_pdf_to_images(file_path)
            else:
                image_paths = [file_path]
            
            # Process each image
            all_text = []
            total_confidence = 0
            
            for image_path in image_paths:
                try:
                    # Get text with confidence data
                    data = pytesseract.image_to_data(
                        image_path,
                        output_type=pytesseract.Output.DICT,
                        config='--psm 6'  # Uniform block of text
                    )
                    
                    # Extract text and calculate confidence
                    page_text = []
                    confidences = []
                    
                    for i, word in enumerate(data['text']):
                        if word.strip():  # Only non-empty words
                            page_text.append(word)
                            conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                            confidences.append(conf)
                    
                    page_text_str = ' '.join(page_text)
                    if page_text_str.strip():
                        all_text.append(page_text_str)
                        
                        # Calculate average confidence for this page
                        if confidences:
                            page_confidence = sum(confidences) / len(confidences)
                            total_confidence += page_confidence
                    
                    logger.info(f"Tesseract processed page: {len(page_text)} words")
                    
                except Exception as e:
                    logger.error(f"Error processing image {image_path}: {str(e)}")
                    # Continue with other images
                    continue
            
            # Clean up temporary images if PDF was converted
            if file_path.lower().endswith('.pdf'):
                for img_path in image_paths:
                    try:
                        os.remove(img_path)
                    except Exception:
                        pass
            
            # Combine results
            full_text = '\n\n'.join(all_text)
            avg_confidence = (total_confidence / len(image_paths)) / 100.0 if image_paths else 0.0
            
            processing_time = time.time() - start_time
            
            logger.info(f"Tesseract completed in {processing_time:.2f}s, confidence: {avg_confidence:.2f}")
            
            return {
                'text': full_text,
                'confidence': round(avg_confidence, 2),
                'service': 'tesseract',
                'processing_time': round(processing_time, 2),
                'pages_processed': len(image_paths),
                'words_found': len(full_text.split()) if full_text else 0
            }
            
        except Exception as e:
            logger.error(f"Tesseract processing error: {str(e)}")
            raise RuntimeError(f"Tesseract OCR failed: {str(e)}")
    
    def process_with_google_vision(self, file_path: str) -> Dict[str, Any]:
        """
        Process file with Google Vision API - Now with REAL implementation
        
        Args:
            file_path: Path to file (PDF, JPG, PNG)
            
        Returns:
            Standardized OCR result
        """
        try:
            if not self.check_google_vision_available():
                # Return mock response if API not available
                return self._mock_google_response(file_path)
            
            logger.info(f"Processing with Google Vision API (REAL): {file_path}")
            start_time = time.time()
            
            client = vision.ImageAnnotatorClient()
            
            # Handle PDFs natively with Google Vision - NO pdf2image conversion needed!
            if file_path.lower().endswith('.pdf'):
                logger.info("Using Google Vision native PDF processing")
                
                with open(file_path, 'rb') as file:
                    content = file.read()
                
                image = vision.Image(content=content)
                
                # Use document_text_detection for PDFs (better for documents)
                response = client.document_text_detection(image=image)
                
                if response.error.message:
                    raise Exception(f"Google Vision PDF error: {response.error.message}")
                
                # Extract full document text
                if response.full_text_annotation:
                    full_text = response.full_text_annotation.text
                    # Count pages from response
                    pages_count = len(response.full_text_annotation.pages) if response.full_text_annotation.pages else 1
                else:
                    full_text = ""
                    pages_count = 1
                
                logger.info(f"Google Vision processed PDF: {len(full_text)} chars, {pages_count} pages")
                
            else:
                # Handle images
                logger.info("Processing image with Google Vision")
                
                with open(file_path, 'rb') as file:
                    content = file.read()
                
                image = vision.Image(content=content)
                
                # Use text_detection for images
                response = client.text_detection(image=image)
                
                if response.error.message:
                    raise Exception(f"Google Vision image error: {response.error.message}")
                
                texts = response.text_annotations
                if texts:
                    full_text = texts[0].description
                else:
                    full_text = ""
                
                pages_count = 1
                logger.info(f"Google Vision processed image: {len(full_text)} chars")
            
            processing_time = time.time() - start_time
            
            # Calculate confidence - Google Vision is highly accurate
            confidence = 0.95 if full_text.strip() else 0.0
            words_found = len(full_text.split()) if full_text else 0
            
            logger.info(f"Google Vision completed in {processing_time:.2f}s, confidence: {confidence:.2f}")
            
            return {
                'text': full_text,
                'confidence': round(confidence, 2),
                'service': 'google_vision',
                'processing_time': round(processing_time, 2),
                'pages_processed': pages_count,
                'words_found': words_found
            }
            
        except Exception as e:
            logger.error(f"Google Vision processing error: {str(e)}")
            raise RuntimeError(f"Google Vision OCR failed: {str(e)}")
    
    def process_with_aws_textract(self, file_path: str) -> Dict[str, Any]:
        """
        Process file with AWS Textract
        
        Args:
            file_path: Path to file
            
        Returns:
            Standardized OCR result
        """
        try:
            if not self.check_aws_textract_available():
                # Return mock response if API not available
                return self._mock_aws_response(file_path)
            
            logger.info(f"Processing with AWS Textract: {file_path}")
            start_time = time.time()
            
            client = boto3.client('textract')
            
            # Prepare file(s) for OCR
            if file_path.lower().endswith('.pdf'):
                # For PDF, AWS Textract can handle it directly
                with open(file_path, 'rb') as document:
                    response = client.detect_document_text(
                        Document={'Bytes': document.read()}
                    )
            else:
                # For images
                with open(file_path, 'rb') as document:
                    response = client.detect_document_text(
                        Document={'Bytes': document.read()}
                    )
            
            # Extract text from response
            all_text = []
            total_confidence = 0
            word_count = 0
            
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    all_text.append(block['Text'])
                elif block['BlockType'] == 'WORD':
                    total_confidence += block['Confidence']
                    word_count += 1
            
            full_text = '\n'.join(all_text)
            avg_confidence = (total_confidence / word_count / 100.0) if word_count > 0 else 0.0
            
            processing_time = time.time() - start_time
            
            logger.info(f"AWS Textract completed in {processing_time:.2f}s, confidence: {avg_confidence:.2f}")
            
            return {
                'text': full_text,
                'confidence': round(avg_confidence, 2),
                'service': 'aws_textract',
                'processing_time': round(processing_time, 2),
                'pages_processed': 1,  # AWS handles multi-page PDFs as one request
                'words_found': word_count
            }
            
        except Exception as e:
            logger.error(f"AWS Textract processing error: {str(e)}")
            raise RuntimeError(f"AWS Textract OCR failed: {str(e)}")
    
    def _mock_google_response(self, file_path: str) -> Dict[str, Any]:
        """Generate mock response for Google Vision when API is not available"""
        logger.info("Generating mock Google Vision response (API not configured)")
        
        return {
            'text': 'MOCK RESPONSE - Google Vision API\n\nThis is a simulated OCR result for testing purposes.\n\nActual file: ' + os.path.basename(file_path) + '\n\nTo get real results, configure Google Vision API credentials.',
            'confidence': 0.0,
            'service': 'google_vision_mock',
            'processing_time': 0.5,
            'pages_processed': 1,
            'words_found': 20
        }
    
    def _mock_aws_response(self, file_path: str) -> Dict[str, Any]:
        """Generate mock response for AWS Textract when API is not available"""
        logger.info("Generating mock AWS Textract response (API not configured)")
        
        return {
            'text': 'MOCK RESPONSE - AWS Textract\n\nThis is a simulated OCR result for testing purposes.\n\nActual file: ' + os.path.basename(file_path) + '\n\nTo get real results, configure AWS credentials.',
            'confidence': 0.0,
            'service': 'aws_textract_mock',
            'processing_time': 0.7,
            'pages_processed': 1,
            'words_found': 18
        }
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all OCR services"""
        return {
            'tesseract': {
                'available': self.check_tesseract_available(),
                'type': 'local',
                'requires_api_key': False
            },
            'google_vision': {
                'available': self.check_google_vision_available(),
                'type': 'cloud',
                'requires_api_key': True
            },
            'aws_textract': {
                'available': self.check_aws_textract_available(),
                'type': 'cloud',
                'requires_api_key': True
            }
        }
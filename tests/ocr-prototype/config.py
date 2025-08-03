"""
Configuration Module
Smart Data Extractor (SME) - OCR Testing Backend

Handles application configuration including API keys and environment settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB (increased for larger PDFs)
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Processing timeouts
    OCR_TIMEOUT = int(os.getenv('OCR_TIMEOUT', '300'))  # 5 minutes for OCR processing
    UPLOAD_TIMEOUT = int(os.getenv('UPLOAD_TIMEOUT', '60'))  # 1 minute for file upload
    
    # OCR Service API Keys and Configuration
    
    # Google Vision API
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_VISION_API_KEY = os.getenv('GOOGLE_VISION_API_KEY', '')  # Alternative API key method
    
    # AWS Textract
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    # Tesseract configuration
    TESSERACT_CMD = os.getenv('TESSERACT_CMD')  # Path to tesseract executable if not in PATH
    
    # Processing configuration
    PDF_DPI = int(os.getenv('PDF_DPI', '200'))  # DPI for PDF to image conversion
    CLEANUP_AGE_HOURS = int(os.getenv('CLEANUP_AGE_HOURS', '24'))  # Auto-cleanup age
    
    @classmethod
    def get_api_key_status(cls) -> dict:
        """Check which API keys are configured"""
        return {
            'google_vision': {
                'project_id': bool(cls.GOOGLE_CLOUD_PROJECT),
                'credentials': bool(cls.GOOGLE_APPLICATION_CREDENTIALS and 
                                 os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS)) if cls.GOOGLE_APPLICATION_CREDENTIALS else False
            },
            'aws_textract': {
                'access_key': bool(cls.AWS_ACCESS_KEY_ID),
                'secret_key': bool(cls.AWS_SECRET_ACCESS_KEY),
                'credentials_file': os.path.exists(os.path.expanduser('~/.aws/credentials'))
            },
            'tesseract': {
                'custom_path': bool(cls.TESSERACT_CMD),
                'system_path': True  # Assume available, will be checked at runtime
            }
        }
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check upload folder
        if not os.path.exists(cls.UPLOAD_FOLDER):
            try:
                os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create upload folder: {e}")
        
        # Check Google Vision credentials
        if cls.GOOGLE_APPLICATION_CREDENTIALS:
            if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
                issues.append(f"Google credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
        
        # Check Tesseract path
        if cls.TESSERACT_CMD and not os.path.exists(cls.TESSERACT_CMD):
            issues.append(f"Tesseract executable not found: {cls.TESSERACT_CMD}")
        
        return issues
    
    @classmethod
    def get_environment_info(cls) -> dict:
        """Get information about the current environment"""
        return {
            'python_version': os.sys.version,
            'platform': os.name,
            'current_directory': os.getcwd(),
            'upload_folder': cls.UPLOAD_FOLDER,
            'debug_mode': cls.DEBUG,
            'max_file_size': f"{cls.MAX_CONTENT_LENGTH / (1024*1024):.1f}MB"
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    
    @classmethod
    def validate_config(cls) -> list:
        """Additional validation for production"""
        issues = super().validate_config()
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            issues.append("SECRET_KEY must be set for production")
        
        return issues

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = False
    UPLOAD_FOLDER = 'test_uploads'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
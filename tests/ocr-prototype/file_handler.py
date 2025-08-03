"""
File Handler Module
Smart Data Extractor (SME) - OCR Testing Backend

Handles file uploads, conversions, and temporary storage management.
Supports PDF to image conversion using pdf2image.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from pdf2image import convert_from_path
from PIL import Image
import tempfile

logger = logging.getLogger(__name__)

class FileHandler:
    """Manages file uploads, conversions, and cleanup"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, upload_folder: str):
        """Initialize file handler with upload directory"""
        self.upload_folder = upload_folder
        self.ensure_upload_folder()
    
    def ensure_upload_folder(self):
        """Create upload folder if it doesn't exist"""
        os.makedirs(self.upload_folder, exist_ok=True)
        logger.info(f"Upload folder ready: {self.upload_folder}")
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    def save_file(self, file: FileStorage, file_id: str) -> str:
        """
        Save uploaded file with unique ID
        Returns the saved file path
        """
        try:
            if not file or not file.filename:
                raise ValueError("No file provided")
            
            # Validate file
            if not self.allowed_file(file.filename):
                raise ValueError(f"File type not allowed: {file.filename}")
            
            # Create secure filename with file_id
            original_extension = self.get_file_extension(file.filename)
            secure_name = f"{file_id}.{original_extension}"
            file_path = os.path.join(self.upload_folder, secure_name)
            
            # Save file
            file.save(file_path)
            
            # Verify file size
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                os.remove(file_path)
                raise ValueError(f"File too large: {file_size} bytes > {self.MAX_FILE_SIZE} bytes")
            
            logger.info(f"File saved: {file_path} ({file_size} bytes)")
            return file_path
            
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            raise
    
    def file_exists(self, file_id: str) -> bool:
        """Check if file exists for given file_id"""
        # Check for any file with this file_id prefix
        for ext in self.ALLOWED_EXTENSIONS:
            file_path = os.path.join(self.upload_folder, f"{file_id}.{ext}")
            if os.path.exists(file_path):
                return True
        return False
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get file path for given file_id"""
        for ext in self.ALLOWED_EXTENSIONS:
            file_path = os.path.join(self.upload_folder, f"{file_id}.{ext}")
            if os.path.exists(file_path):
                return file_path
        return None
    
    def is_pdf(self, file_path: str) -> bool:
        """Check if file is a PDF"""
        return file_path.lower().endswith('.pdf')
    
    def convert_pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[str]:
        """
        Convert PDF to images and return list of image paths
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion (default 200)
            
        Returns:
            List of image file paths
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=dpi)
            
            if not images:
                raise ValueError("No pages found in PDF")
            
            # Save images temporarily
            image_paths = []
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for i, image in enumerate(images):
                image_filename = f"{base_name}_page_{i+1}.png"
                image_path = os.path.join(self.upload_folder, image_filename)
                
                # Save as PNG for better OCR quality
                image.save(image_path, 'PNG', optimize=True)
                image_paths.append(image_path)
                
                logger.info(f"Saved PDF page {i+1}: {image_path}")
            
            logger.info(f"PDF conversion completed: {len(images)} pages")
            return image_paths
            
        except Exception as e:
            logger.error(f"PDF conversion error: {str(e)}")
            raise
    
    def prepare_file_for_ocr(self, file_path: str) -> List[str]:
        """
        Prepare file for OCR processing
        
        For PDFs: Convert to images
        For images: Return as-is
        
        Returns:
            List of image file paths ready for OCR
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if self.is_pdf(file_path):
                # Convert PDF to images
                return self.convert_pdf_to_images(file_path)
            else:
                # Already an image, validate and return
                self.validate_image(file_path)
                return [file_path]
                
        except Exception as e:
            logger.error(f"File preparation error: {str(e)}")
            raise
    
    def validate_image(self, image_path: str):
        """Validate image file can be opened"""
        try:
            with Image.open(image_path) as img:
                img.verify()  # Verify image integrity
            logger.info(f"Image validated: {image_path}")
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = os.stat(file_path)
            
            info = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': self.get_file_extension(file_path),
                'is_pdf': self.is_pdf(file_path)
            }
            
            # Add image info if it's an image
            if not info['is_pdf']:
                try:
                    with Image.open(file_path) as img:
                        info['dimensions'] = img.size
                        info['mode'] = img.mode
                except Exception:
                    pass
            
            return info
            
        except Exception as e:
            logger.error(f"Get file info error: {str(e)}")
            raise
    
    def cleanup_old_files(self, age_hours: int = 24) -> int:
        """
        Clean up files older than specified hours
        
        Args:
            age_hours: Files older than this will be deleted
            
        Returns:
            Number of files deleted
        """
        try:
            if not os.path.exists(self.upload_folder):
                return 0
            
            cutoff_time = time.time() - (age_hours * 3600)
            deleted_count = 0
            
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                
                if os.path.isfile(file_path):
                    file_age = os.path.getmtime(file_path)
                    
                    if file_age < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"Deleted old file: {filename}")
                        except Exception as e:
                            logger.error(f"Failed to delete {filename}: {str(e)}")
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            return 0
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a specific file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Delete file error: {str(e)}")
            return False
    
    def delete_files_by_id(self, file_id: str) -> int:
        """Delete all files associated with a file_id"""
        deleted_count = 0
        for ext in self.ALLOWED_EXTENSIONS:
            file_path = os.path.join(self.upload_folder, f"{file_id}.{ext}")
            if self.delete_file(file_path):
                deleted_count += 1
        
        # Also delete any generated page images
        try:
            for filename in os.listdir(self.upload_folder):
                if filename.startswith(f"{file_id}_page_"):
                    file_path = os.path.join(self.upload_folder, filename)
                    if self.delete_file(file_path):
                        deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting page images: {str(e)}")
        
        return deleted_count
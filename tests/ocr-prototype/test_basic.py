#!/usr/bin/env python3
"""
Basic Test Script for OCR Testing Backend
Tests basic server functionality without OCR dependencies
"""

import sys
import os
import requests
import time
import tempfile
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """Create a simple test image with text"""
    # Create a simple image with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    text = "TEST DOCUMENT\nTNB UTILITY BILL\nAccount: 123456789\nAmount: RM 150.50"
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((20, 20), text, fill='black', font=font)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_server_health():
    """Test if server is responding"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    try:
        # Create test image
        test_image_path = create_test_image()
        print(f"📁 Created test image: {test_image_path}")
        
        # Upload file
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload: {response.status_code}")
            print(f"   File ID: {result['file_id']}")
            
            # Clean up
            os.unlink(test_image_path)
            return result['file_id']
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return None

def test_services_endpoint():
    """Test services listing"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/services', timeout=5)
        print(f"✅ Services endpoint: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print("   Available services:")
            for service_name, info in services['services'].items():
                status = "✅" if info['available'] else "❌"
                print(f"     {status} {service_name}: {info['name']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Services endpoint failed: {e}")
        return False

def test_ocr_processing(file_id):
    """Test OCR processing (will use mock if Tesseract not available)"""
    if not file_id:
        print("❌ No file ID for OCR test")
        return False
        
    try:
        # Start processing
        response = requests.post(
            f'http://127.0.0.1:5000/api/process/{file_id}',
            json={'service': 'tesseract'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            process_id = result['process_id']
            print(f"✅ OCR processing started: {process_id}")
            
            # Check result
            time.sleep(2)  # Give it time to process
            response = requests.get(f'http://127.0.0.1:5000/api/result/{process_id}', timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ OCR result received")
                print(f"   Status: {result['status']}")
                print(f"   Service: {result['service']}")
                print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
                print(f"   Text preview: {result.get('text', '')[:100]}...")
                return True
            else:
                print(f"❌ OCR result failed: {response.status_code}")
                return False
        else:
            print(f"❌ OCR processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OCR processing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 OCR Testing Backend - Basic Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_server_health():
        print("\n❌ Server not responding. Make sure to run:")
        print("   cd tests/ocr-prototype")
        print("   python server.py")
        return False
    
    print()
    
    # Test 2: Services endpoint
    test_services_endpoint()
    print()
    
    # Test 3: File upload
    file_id = test_file_upload()
    print()
    
    # Test 4: OCR processing
    if file_id:
        test_ocr_processing(file_id)
    
    print("\n" + "=" * 50)
    print("🎉 Basic tests completed!")
    print("\nNext steps:")
    print("1. Install Tesseract: brew install tesseract")
    print("2. Test with a real TNB utility bill PDF")
    print("3. Compare OCR results across services")

if __name__ == '__main__':
    main()
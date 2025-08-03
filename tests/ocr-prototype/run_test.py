#!/usr/bin/env python3
"""
Complete OCR Backend Test
Starts server and runs full functionality test
"""

import subprocess
import time
import requests
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_test_image():
    """Create a test image with utility bill-like content"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create content similar to a utility bill
    content = [
        "TNB UTILITY BILL",
        "",
        "Account Number: 123456789",
        "Billing Period: Jul 2025",
        "Amount Due: RM 150.50",
        "Due Date: 15 Aug 2025",
        "",
        "Previous Reading: 1,250 kWh",
        "Current Reading: 1,380 kWh",
        "Usage: 130 kWh",
        "",
        "Rate: RM 0.52/kWh",
        "Service Charge: RM 30.00",
        "Total Amount: RM 150.50"
    ]
    
    y_position = 20
    for line in content:
        if line:  # Skip empty lines for drawing
            draw.text((30, y_position), line, fill='black')
        y_position += 25
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_ocr_functionality():
    """Test the OCR functionality with our test image"""
    print("🧪 Testing OCR Backend Functionality")
    print("=" * 50)
    
    # Create test image
    test_image_path = create_test_image()
    print(f"📁 Created test image: {os.path.basename(test_image_path)}")
    
    try:
        # 1. Health check
        print("\n1. Testing health endpoint...")
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Tesseract: {data['services']['tesseract']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # 2. Upload file
        print("\n2. Testing file upload...")
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files, timeout=10)
        
        if response.status_code == 200:
            upload_result = response.json()
            file_id = upload_result['file_id']
            print(f"   ✅ File uploaded: {file_id}")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return False
        
        # 3. Process with Tesseract
        print("\n3. Testing OCR processing...")
        response = requests.post(
            f'http://127.0.0.1:5000/api/process/{file_id}',
            json={'service': 'tesseract'},
            timeout=15
        )
        
        if response.status_code == 200:
            process_result = response.json()
            process_id = process_result['process_id']
            print(f"   ✅ Processing started: {process_id}")
        else:
            print(f"   ❌ Processing failed: {response.status_code}")
            return False
        
        # 4. Get results
        print("\n4. Getting OCR results...")
        time.sleep(3)  # Wait for processing
        response = requests.get(f'http://127.0.0.1:5000/api/result/{process_id}', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result['status']}")
            print(f"   ✅ Service: {result['service']}")
            print(f"   ✅ Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"   ✅ Confidence: {result.get('confidence', 'N/A')}")
            print(f"   ✅ Words found: {result.get('words_found', 'N/A')}")
            
            # Show extracted text
            extracted_text = result.get('text', '')
            print(f"\n📄 Extracted Text Preview:")
            print("-" * 30)
            print(extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text)
            print("-" * 30)
            
            # Check if we extracted expected content
            expected_keywords = ['TNB', 'UTILITY', 'BILL', 'Account', '150.50']
            found_keywords = [kw for kw in expected_keywords if kw in extracted_text]
            
            print(f"\n🔍 Keyword Detection:")
            print(f"   Expected: {expected_keywords}")
            print(f"   Found: {found_keywords}")
            print(f"   Success rate: {len(found_keywords)}/{len(expected_keywords)} ({len(found_keywords)*100//len(expected_keywords)}%)")
            
            return len(found_keywords) > 0  # Success if we found any keywords
        else:
            print(f"   ❌ Result failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

def main():
    """Main test function"""
    print("🚀 Starting OCR Backend Complete Test")
    print("=" * 50)
    
    # Start server in background
    print("Starting Flask server...")
    server_process = subprocess.Popen([
        sys.executable, 'server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test functionality
        success = test_ocr_functionality()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 OCR Backend Test PASSED!")
            print("✅ File upload working")
            print("✅ OCR processing working")
            print("✅ Text extraction working")
            print("✅ Ready for TNB utility bill testing")
        else:
            print("\n" + "=" * 50)
            print("❌ OCR Backend Test FAILED!")
            print("Check the logs above for details")
            
    finally:
        # Stop server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    main()
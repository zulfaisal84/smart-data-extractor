#!/usr/bin/env python3
"""
Live Debug Test - Test OCR backend with real requests
Tests actual file upload and processing like CEO would use
"""

import subprocess
import time
import requests
import sys
import os
from PIL import Image, ImageDraw
import tempfile

def create_test_pdf():
    """Create a simple PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create PDF with text
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        c.drawString(100, 750, "TEST UTILITY BILL")
        c.drawString(100, 720, "Account Number: 123456789")
        c.drawString(100, 690, "Amount Due: RM 150.50")
        c.drawString(100, 660, "Due Date: 15 Aug 2025")
        c.drawString(100, 630, "Service Address: Kuala Lumpur")
        c.save()
        
        return temp_file.name
        
    except ImportError:
        print("reportlab not available, creating simple image instead")
        return create_test_image()

def create_test_image():
    """Create a test image that looks like a bill"""
    img = Image.new('RGB', (600, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add bill-like content
    content = [
        "TENAGA NASIONAL BERHAD",
        "UTILITY BILL",
        "",
        "Account Number: 123456789012",
        "Billing Period: July 2025",
        "Amount Due: RM 150.50",
        "Due Date: 15 August 2025",
        "",
        "Service Address:",
        "123 Jalan Test,",
        "50000 Kuala Lumpur",
        "",
        "Previous Reading: 1,250 kWh",
        "Current Reading: 1,380 kWh", 
        "Usage: 130 kWh",
        "",
        "Charges:",
        "Energy Charge: RM 120.50",
        "Service Charge: RM 30.00",
        "Total Amount: RM 150.50"
    ]
    
    y_position = 50
    for line in content:
        if line:  # Skip empty lines
            draw.text((50, y_position), line, fill='black')
        y_position += 35
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_full_workflow():
    """Test the complete upload and processing workflow"""
    print("🧪 Testing Complete OCR Workflow")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test 1: Debug endpoint
        print("\n1. Testing debug endpoint...")
        response = requests.get(f"{base_url}/api/debug/test-ocr", timeout=30)
        if response.status_code == 200:
            debug_data = response.json()
            tesseract_status = debug_data['test_results']['tesseract']['status']
            print(f"   ✅ Debug endpoint: {tesseract_status}")
            if tesseract_status != 'success':
                print(f"   ❌ Tesseract issue: {debug_data['test_results']['tesseract']}")
                return False
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
            return False
        
        # Test 2: Create and upload test file
        print("\n2. Creating test file...")
        test_file_path = create_test_image()  # Use image for reliable testing
        print(f"   📁 Created: {os.path.basename(test_file_path)}")
        print(f"   📏 Size: {os.path.getsize(test_file_path)} bytes")
        
        print("\n3. Uploading file...")
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            upload_data = response.json()
            file_id = upload_data['file_id']
            print(f"   ✅ Upload successful: {file_id}")
            print(f"   📊 File size: {upload_data.get('file_size', 'unknown')} bytes")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
            return False
        
        # Test 3: Process with Tesseract
        print("\n4. Processing with Tesseract...")
        response = requests.post(
            f"{base_url}/api/process/{file_id}",
            json={'service': 'tesseract'},
            timeout=30
        )
        
        if response.status_code == 200:
            process_data = response.json()
            process_id = process_data['process_id']
            print(f"   ✅ Processing started: {process_id}")
        else:
            print(f"   ❌ Processing failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
            return False
        
        # Test 4: Wait for results
        print("\n5. Waiting for results...")
        for attempt in range(12):  # Wait up to 60 seconds
            time.sleep(5)
            response = requests.get(f"{base_url}/api/result/{process_id}", timeout=10)
            
            if response.status_code == 200:
                result_data = response.json()
                status = result_data['status']
                print(f"   📊 Attempt {attempt + 1}: {status}")
                
                if status == 'success':
                    print(f"   ✅ Processing completed!")
                    print(f"   ⏱️  Time: {result_data.get('processing_time', 'unknown')}s")
                    print(f"   🎯 Confidence: {result_data.get('confidence', 'unknown')}")
                    print(f"   📄 Text length: {len(result_data.get('text', ''))} chars")
                    
                    # Show extracted text preview
                    text = result_data.get('text', '')
                    if text:
                        print(f"\n📋 Extracted Text Preview:")
                        print("-" * 40)
                        print(text[:200] + "..." if len(text) > 200 else text)
                        print("-" * 40)
                        
                        # Check for key terms
                        keywords = ['TENAGA', 'BILL', '150.50', 'Account', 'kWh']
                        found = [kw for kw in keywords if kw in text.upper()]
                        print(f"🔍 Keywords found: {found}")
                        
                        return True
                    else:
                        print("   ⚠️  No text extracted")
                        return False
                        
                elif status == 'error':
                    print(f"   ❌ Processing error: {result_data.get('error', 'unknown')}")
                    return False
                    
            else:
                print(f"   ❌ Result check failed: {response.status_code}")
                return False
        
        print("   ⏰ Timeout waiting for results")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            if 'test_file_path' in locals():
                os.unlink(test_file_path)
        except:
            pass

def main():
    """Run the complete test"""
    print("🚀 Starting OCR Backend Live Debug Test")
    print("=" * 50)
    
    # Start server
    print("Starting server...")
    server_process = subprocess.Popen([
        sys.executable, 'server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("Waiting for server startup...")
    time.sleep(3)
    
    try:
        success = test_full_workflow()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 OCR BACKEND TEST PASSED!")
            print("✅ Upload working")
            print("✅ Processing working")
            print("✅ Text extraction working")
            print("✅ Ready for CEO testing")
            print("\n📋 Server logs will show detailed debugging info")
        else:
            print("\n" + "=" * 50)
            print("❌ OCR BACKEND TEST FAILED!")
            print("📋 Check server logs for detailed error information")
            print("📋 Try the debug endpoint: http://127.0.0.1:5000/api/debug/test-ocr")
            
    finally:
        # Stop server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    main()
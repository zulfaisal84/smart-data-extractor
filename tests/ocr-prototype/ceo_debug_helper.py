#!/usr/bin/env python3
"""
CEO Debug Helper
A comprehensive diagnostic script to help identify OCR processing issues
"""

import subprocess
import time
import requests
import sys
import os
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")

def start_server():
    """Start the Flask server"""
    print("🚀 Starting OCR Backend Server...")
    server_process = subprocess.Popen([
        sys.executable, 'server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    return server_process

def test_server_health():
    """Test basic server health"""
    print_step(1, "Testing Server Health")
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server is running")
            print(f"   📊 Tesseract available: {data['services']['tesseract']}")
            print(f"   📊 Google Vision available: {data['services']['google_vision']}")
            print(f"   📊 AWS Textract available: {data['services']['aws_textract']}")
            return True
        else:
            print(f"   ❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False

def test_debug_endpoint():
    """Test the debug endpoint"""
    print_step(2, "Testing Debug Endpoint")
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/debug/test-ocr', timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Debug endpoint working")
            
            # System info
            system = data['system_info']
            print(f"   📊 Tesseract version: {system['tesseract_version']}")
            print(f"   📊 Max file size: {system['max_file_size']/(1024*1024):.1f}MB")
            print(f"   📊 Upload folder: {system['upload_folder']} (exists: {system['upload_folder_exists']}, writable: {system['upload_folder_writable']})")
            
            # Test results
            tesseract = data['test_results']['tesseract']
            print(f"   📊 Tesseract test: {tesseract['status']}")
            if tesseract['status'] == 'success':
                print(f"   📊 Tesseract extracted: {len(tesseract['text'])} chars, confidence: {tesseract['confidence']}")
            else:
                print(f"   ❌ Tesseract error: {tesseract.get('error', 'unknown')}")
            
            return tesseract['status'] == 'success'
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Debug endpoint error: {e}")
        return False

def test_file_upload(file_path):
    """Test file upload"""
    print_step(3, f"Testing File Upload: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"   ❌ File not found: {file_path}")
        return None
    
    file_size = os.path.getsize(file_path)
    print(f"   📁 File size: {file_size} bytes ({file_size/(1024*1024):.2f}MB)")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            file_id = data['file_id']
            print(f"   ✅ Upload successful: {file_id}")
            print(f"   📊 Server reported size: {data.get('file_size', 'unknown')} bytes")
            return file_id
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📋 Error: {error_data.get('error', 'unknown')}")
                if 'max_size_mb' in error_data:
                    print(f"   📋 Max size: {error_data['max_size_mb']}MB, Your file: {error_data['file_size_mb']}MB")
            except:
                print(f"   📋 Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return None

def test_ocr_processing(file_id, service='tesseract'):
    """Test OCR processing"""
    print_step(4, f"Testing OCR Processing with {service}")
    
    if not file_id:
        print("   ❌ No file_id provided")
        return None
    
    try:
        # Start processing
        response = requests.post(
            f'http://127.0.0.1:5000/api/process/{file_id}',
            json={'service': service},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            process_id = data['process_id']
            print(f"   ✅ Processing started: {process_id}")
            
            # Wait for results
            print("   ⏳ Waiting for processing to complete...")
            for attempt in range(20):  # Wait up to 100 seconds
                time.sleep(5)
                response = requests.get(f'http://127.0.0.1:5000/api/result/{process_id}', timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    status = result['status']
                    print(f"   📊 Attempt {attempt + 1}: {status}")
                    
                    if status == 'success':
                        print(f"   ✅ Processing completed!")
                        print(f"   ⏱️  Processing time: {result.get('processing_time', 'unknown')}s")
                        print(f"   🎯 Confidence: {result.get('confidence', 'unknown')}")
                        print(f"   📄 Text length: {len(result.get('text', ''))} chars")
                        print(f"   📊 Words found: {result.get('words_found', 'unknown')}")
                        print(f"   📊 Pages processed: {result.get('pages_processed', 'unknown')}")
                        
                        # Show text preview
                        text = result.get('text', '')
                        if text:
                            print(f"\n   📋 Text Preview (first 200 chars):")
                            print(f"   {'-' * 50}")
                            print(f"   {text[:200]}{'...' if len(text) > 200 else ''}")
                            print(f"   {'-' * 50}")
                        
                        return result
                        
                    elif status == 'error':
                        print(f"   ❌ Processing failed: {result.get('error', 'unknown')}")
                        print(f"   📊 Error type: {result.get('error_type', 'unknown')}")
                        return None
                        
                else:
                    print(f"   ❌ Status check failed: {response.status_code}")
                    return None
            
            print("   ⏰ Processing timed out")
            return None
            
        else:
            print(f"   ❌ Failed to start processing: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📋 Error: {error_data.get('error', 'unknown')}")
            except:
                print(f"   📋 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Processing error: {e}")
        return None

def main():
    """Main diagnostic function"""
    print_header("OCR Backend Diagnostic Tool")
    print("This tool will help identify issues with file upload and OCR processing.")
    
    # Check if file path provided
    if len(sys.argv) > 1:
        test_file_path = sys.argv[1]
        print(f"📁 Testing with file: {test_file_path}")
    else:
        print("📁 No test file provided. Usage: python ceo_debug_helper.py <file_path>")
        print("📁 Creating a test image for basic functionality check...")
        
        # Create a simple test image
        from PIL import Image, ImageDraw
        import tempfile
        
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "TEST DOCUMENT\nAccount: 123456789\nAmount: RM 150.50", fill='black')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name, 'PNG')
        test_file_path = temp_file.name
        print(f"📁 Created test file: {test_file_path}")
    
    # Start server
    server_process = start_server()
    
    try:
        # Run tests
        health_ok = test_server_health()
        if not health_ok:
            print("\n❌ Server health check failed. Cannot proceed.")
            return
        
        debug_ok = test_debug_endpoint()
        if not debug_ok:
            print("\n❌ Debug test failed. OCR system has issues.")
            return
        
        file_id = test_file_upload(test_file_path)
        if not file_id:
            print("\n❌ File upload failed. Check file size and format.")
            return
        
        result = test_ocr_processing(file_id)
        if not result:
            print("\n❌ OCR processing failed. Check server logs for details.")
            return
        
        print_header("DIAGNOSTIC COMPLETE - SUCCESS!")
        print("✅ All tests passed!")
        print("✅ OCR backend is working correctly")
        print("✅ Your file was processed successfully")
        
        if len(sys.argv) <= 1:
            print("\n💡 To test with your actual TNB bill:")
            print("   python ceo_debug_helper.py /path/to/your/tnb_bill.pdf")
        
    except KeyboardInterrupt:
        print("\n⏹️  Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
    finally:
        # Stop server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
        
        # Cleanup test file if created
        if len(sys.argv) <= 1 and 'test_file_path' in locals():
            try:
                os.unlink(test_file_path)
            except:
                pass

if __name__ == '__main__':
    main()
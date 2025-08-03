#!/usr/bin/env python3
"""
CEO Final Test Script
Tests the complete OCR system with Google Vision API for TNB bill processing
"""

import subprocess
import time
import requests
import sys
import os
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def test_api_key_setup():
    """Test API key configuration"""
    print("\n1. Testing API Key Setup...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_VISION_API_KEY')
        if api_key:
            print(f"   ✅ API Key loaded: {api_key[:10]}...{api_key[-5:]}")
            print(f"   📊 Key length: {len(api_key)} characters")
            return True
        else:
            print("   ❌ No API key found in .env file")
            return False
            
    except Exception as e:
        print(f"   ❌ Error loading API key: {e}")
        return False

def test_server_with_google_vision():
    """Test the server with Google Vision"""
    print("\n2. Testing Server with Google Vision...")
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            google_available = data['services']['google_vision']
            print(f"   ✅ Server running")
            print(f"   📊 Google Vision available: {google_available}")
            
            if google_available:
                print("   🎉 Google Vision API is ACTIVE!")
                return True
            else:
                print("   ⚠️  Google Vision running in mock mode")
                return False
        else:
            print(f"   ❌ Server health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Server connection error: {e}")
        return False

def test_debug_endpoint():
    """Test the debug endpoint"""
    print("\n3. Testing Debug Endpoint...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/debug/test-ocr", timeout=30)
        if response.status_code == 200:
            data = response.json()
            google_result = data['test_results']['google_vision']
            
            print(f"   ✅ Debug endpoint working")
            print(f"   📊 Google Vision status: {google_result['status']}")
            print(f"   📊 Processing time: {google_result.get('processing_time', 'N/A')}s")
            
            if google_result['status'] == 'success':
                print("   🎉 Google Vision API working with REAL processing!")
                return True
            elif google_result['status'] == 'mock':
                print("   ⚠️  Google Vision in mock mode (still functional)")
                return True
            else:
                print(f"   ❌ Google Vision error: {google_result.get('error', 'unknown')}")
                return False
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Debug test error: {e}")
        return False

def show_usage_instructions():
    """Show usage instructions for the CEO"""
    print_header("CEO Usage Instructions")
    
    print("🚀 Server is ready! Here's how to test with your TNB bill:")
    print()
    print("📋 Step-by-Step Instructions:")
    print("1. Open your web browser")
    print("2. Go to: http://127.0.0.1:5000/")
    print("3. You'll see the OCR Testing Interface")
    print("4. Click 'Choose File' and select your TNB bill PDF")
    print("5. Make sure 'Google Vision' is selected in the dropdown")
    print("6. Click 'Process Document'")
    print("7. Wait for processing (should be < 5 seconds)")
    print("8. View the extracted text results")
    print()
    print("🔍 What to Look For:")
    print("- Should extract text from your TNB bill")
    print("- Look for account numbers, amounts, dates")
    print("- Processing should be fast (< 5 seconds)")
    print("- High confidence score (>0.9)")
    print()
    print("❗ If Issues Occur:")
    print("- Check server logs in terminal")
    print("- Try with a different PDF/image")
    print("- Verify API key is valid")
    print()
    print("📱 Server Management:")
    print("- Server is running at: http://127.0.0.1:5000/")
    print("- Press Ctrl+C in terminal to stop server")
    print("- Restart with: python server.py")

def main():
    """Main test function"""
    print_header("CEO Final System Test")
    print("Testing the complete OCR system with Google Vision API")
    
    # Test 1: API Key
    api_key_ok = test_api_key_setup()
    if not api_key_ok:
        print("\n❌ CRITICAL: API key not configured properly")
        print("📋 Please check the .env file contains:")
        print("   GOOGLE_VISION_API_KEY=your-actual-api-key")
        return False
    
    # Start server
    print("\n🚀 Starting OCR Server...")
    server_process = subprocess.Popen([
        sys.executable, 'server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("⏳ Waiting for server startup...")
    time.sleep(4)
    
    try:
        # Test 2: Server with Google Vision
        server_ok = test_server_with_google_vision()
        
        # Test 3: Debug endpoint
        debug_ok = test_debug_endpoint()
        
        if server_ok and debug_ok:
            print_header("✅ ALL TESTS PASSED!")
            print("🎉 The OCR system is ready for production use!")
            print("✅ Google Vision API integration complete")
            print("✅ Server running successfully") 
            print("✅ Debug tests passed")
            
            show_usage_instructions()
            
            print(f"\n🔄 Server Status: RUNNING")
            print(f"📍 URL: http://127.0.0.1:5000/")
            print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
            print("\n💡 The server will keep running until you press Ctrl+C")
            print("   You can now test with your TNB bill in the browser!")
            
            # Keep server running
            try:
                print("\n⌨️  Press Ctrl+C to stop the server...")
                server_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                
        else:
            print_header("❌ TESTS FAILED")
            print("❌ Some components are not working properly")
            print("📋 Check the error messages above for details")
            
    finally:
        # Always stop server
        server_process.terminate()
        server_process.wait()
        print("🛑 Server stopped")

if __name__ == '__main__':
    main()
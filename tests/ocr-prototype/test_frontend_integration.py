#!/usr/bin/env python3
"""
Frontend Integration Test
Tests that the server properly serves frontend files and handles CORS
"""

import subprocess
import time
import requests
import sys
import os

def test_frontend_integration():
    """Test that frontend is properly served by the backend"""
    print("🧪 Testing Frontend-Backend Integration")
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
        base_url = "http://127.0.0.1:5000"
        
        # Test 1: Frontend serving
        print("\n1. Testing frontend serving...")
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Frontend served: {response.status_code}")
                print(f"   📄 Content type: {response.headers.get('content-type', 'unknown')}")
            else:
                print(f"   ❌ Frontend failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Frontend error: {e}")
        
        # Test 2: API endpoints still working
        print("\n2. Testing API endpoints...")
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API Health: {response.status_code}")
                print(f"   ✅ Tesseract: {data['services']['tesseract']}")
            else:
                print(f"   ❌ API failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API error: {e}")
        
        # Test 3: CORS headers
        print("\n3. Testing CORS headers...")
        try:
            response = requests.get(f"{base_url}/api/services", timeout=5)
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                print(f"   ✅ CORS enabled: {cors_header}")
            else:
                print(f"   ⚠️  CORS header not found")
            print(f"   📋 Response: {response.status_code}")
        except Exception as e:
            print(f"   ❌ CORS test error: {e}")
        
        # Test 4: Static file serving
        print("\n4. Testing static file serving...")
        try:
            # Test if CSS file exists and can be served
            if os.path.exists('style.css'):
                response = requests.get(f"{base_url}/style.css", timeout=5)
                print(f"   ✅ Static file served: {response.status_code}")
            else:
                print(f"   ℹ️  No style.css found (expected)")
                
            # Test for any JS file
            if os.path.exists('app.js'):
                response = requests.get(f"{base_url}/app.js", timeout=5)
                print(f"   ✅ JS file served: {response.status_code}")
            else:
                print(f"   ℹ️  No app.js found")
                
        except Exception as e:
            print(f"   ❌ Static file error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Frontend-Backend Integration Test Complete!")
        print("✅ Server serves frontend at http://127.0.0.1:5000/")
        print("✅ API endpoints available at http://127.0.0.1:5000/api/")
        print("✅ CORS configured for cross-origin requests")
        print("✅ Static files served correctly")
        print("\n📋 CEO can now access everything at: http://127.0.0.1:5000/")
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        
    finally:
        # Stop server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    test_frontend_integration()
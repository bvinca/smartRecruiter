"""
Quick test script to verify backend is accessible
Run this to test if the backend server is responding
"""
import requests
import sys

def test_backend():
    base_url = "http://localhost:8000"
    
    print("Testing backend connection...")
    print(f"Base URL: {base_url}")
    print()
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Health endpoint: Connection refused - Backend is not running!")
        return False
    except Exception as e:
        print(f"❌ Health endpoint: Error - {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint: Error - {e}")
        return False
    
    # Test CORS (simulate browser request)
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
        }
        response = requests.options(f"{base_url}/health", headers=headers, timeout=5)
        print(f"✅ CORS preflight: {response.status_code}")
        if 'access-control-allow-origin' in response.headers:
            print(f"   CORS headers: {response.headers.get('access-control-allow-origin')}")
        else:
            print("   ⚠️  No CORS headers found")
    except Exception as e:
        print(f"❌ CORS test: Error - {e}")
    
    print()
    print("Backend connection test complete!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)


"""
Test script to verify login endpoint is working
"""
import requests
import sys

def test_login():
    base_url = "http://localhost:8000"
    
    print("Testing login endpoint...")
    print(f"Base URL: {base_url}")
    print()
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"[OK] Server is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is NOT running! Start it with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"[ERROR] Server check failed: {e}")
        return False
    
    # Test login endpoint (with invalid credentials to see if endpoint exists)
    try:
        form_data = {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = requests.post(
            f"{base_url}/auth/login",
            data=form_data,
            timeout=5
        )
        
        if response.status_code == 401:
            print("[OK] Login endpoint exists and responds (401 = invalid credentials, which is expected)")
            print(f"     Response: {response.json()}")
        elif response.status_code == 200:
            print("[OK] Login endpoint exists and working!")
        else:
            print(f"[WARNING] Login endpoint returned unexpected status: {response.status_code}")
            print(f"     Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to login endpoint - server might not be running")
        return False
    except Exception as e:
        print(f"[ERROR] Login test failed: {e}")
        return False
    
    # Test CORS
    try:
        headers = {
            'Origin': 'http://localhost:3000',
        }
        response = requests.options(f"{base_url}/auth/login", headers=headers, timeout=5)
        print(f"[OK] CORS preflight: {response.status_code}")
    except Exception as e:
        print(f"[WARNING] CORS test failed: {e}")
    
    print()
    print("Login endpoint test complete!")
    return True

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)


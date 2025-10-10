#!/usr/bin/env python
"""
Test OAuth Endpoints
"""
import requests

def test_oauth_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    print("=== TESTING OAUTH ENDPOINTS ===")
    
    # Test 1: Google OAuth login endpoint
    print("\n1. Testing Google OAuth Login Endpoint:")
    try:
        response = requests.get(f"{base_url}/accounts/google/login/", allow_redirects=False)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 302:
            print(f"   ✅ SUCCESS: Redirects to Google OAuth (Location: {response.headers.get('Location', 'N/A')})")
        else:
            print(f"   ❌ FAILED: Expected 302 redirect, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: OAuth status endpoint
    print("\n2. Testing OAuth Status Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/oauth/status/")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ SUCCESS: {response.json()}")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Home page (should have Google OAuth button)
    print("\n3. Testing Home Page for OAuth Button:")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 302:
            print(f"   ✅ SUCCESS: Page loads correctly")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_oauth_endpoints()
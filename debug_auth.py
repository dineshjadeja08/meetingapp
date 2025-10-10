#!/usr/bin/env python
import requests
import json

print("=== Authentication Debug Test ===")

# Test 1: Check if login endpoint exists
print("\n1. Testing login endpoint availability...")
try:
    response = requests.get("http://127.0.0.1:8000/api/accounts/login/")
    print(f"Login endpoint GET status: {response.status_code}")
except Exception as e:
    print(f"Error accessing login endpoint: {e}")

# Test 2: Try to login with test user
print("\n2. Testing login with credentials...")
login_data = {"username": "testuser123", "password": "testpass123"}
try:
    response = requests.post("http://127.0.0.1:8000/api/accounts/login/", json=login_data)
    print(f"Login POST Status: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access')
        print(f"Access token received: {access_token[:20]}..." if access_token else "No access token")
        
        # Test 3: Use token to access protected endpoint
        print("\n3. Testing protected endpoint with token...")
        headers = {"Authorization": f"Bearer {access_token}"}
        rooms_response = requests.get("http://127.0.0.1:8000/video/api/rooms/", headers=headers)
        print(f"Rooms API Status: {rooms_response.status_code}")
        print(f"Rooms API Response: {rooms_response.text[:200]}...")
        
    else:
        print("Login failed, cannot test protected endpoints")
        
except Exception as e:
    print(f"Error during login test: {e}")

# Test 4: Check if user exists
print("\n4. Testing registration (to verify user creation works)...")
reg_data = {
    "username": "newtestuser", 
    "email": "newtest@example.com", 
    "password": "testpass123",
    "password2": "testpass123"
}
try:
    response = requests.post("http://127.0.0.1:8000/api/accounts/register/", json=reg_data)
    print(f"Registration Status: {response.status_code}")
    print(f"Registration Response: {response.text}")
except Exception as e:
    print(f"Error during registration test: {e}")

print("\n=== Debug Test Complete ===")
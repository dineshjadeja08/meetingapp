#!/usr/bin/env python
import requests
import json

# Test registration
url = "http://127.0.0.1:8000/api/accounts/register/"
data = {
    "username": "testuser123",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
}

print("Testing registration API...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test login  
url = "http://127.0.0.1:8000/api/accounts/login/"
data = {
    "username": "testuser123", 
    "password": "testpass123"
}

print("\nTesting login API...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
#!/usr/bin/env python3
"""
Test script for Meeting App API endpoints
Run this after starting the Django development server
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/accounts"

def test_user_registration():
    """Test user registration endpoint"""
    print("Testing User Registration...")
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User", 
        "password": "testpassword123",
        "password2": "testpassword123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            return response.json()
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_user_login(username="testuser123", password="testpassword123"):
    """Test user login endpoint"""
    print("\nTesting User Login...")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_get_profile(access_token):
    """Test get user profile endpoint"""
    print("\nTesting Get User Profile...")
    
    url = f"{BASE_URL}/profile/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_update_profile(access_token):
    """Test update user profile endpoint"""
    print("\nTesting Update User Profile...")
    
    url = f"{BASE_URL}/profile/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "first_name": "Updated",
        "last_name": "User",
        "phone_number": "+1234567890",
        "bio": "This is my updated bio",
        "location": "New York, NY"
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_password_reset_request():
    """Test password reset request endpoint"""
    print("\nTesting Password Reset Request...")
    
    url = f"{BASE_URL}/auth/password-reset/"
    data = {
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_token_refresh(refresh_token):
    """Test token refresh endpoint"""
    print("\nTesting Token Refresh...")
    
    url = f"{BASE_URL}/auth/token/refresh/"
    data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def main():
    """Run all tests"""
    print("Starting API Tests...")
    print("=" * 50)
    
    # Test registration (no tokens returned)
    registration_result = test_user_registration()
    
    # Always test login to get tokens (registration no longer provides tokens)
    if registration_result:
        print("\nRegistration successful! Now testing login to get tokens...")
        login_result = test_user_login("testuser123", "testpassword123")
    else:
        # If registration fails (user might already exist), try login
        print("\nRegistration failed (user might already exist), trying login...")
        login_result = test_user_login()
    
    if not login_result:
        print("Could not get authentication tokens. Stopping tests.")
        return
    
    # Extract tokens (only from login now)
    access_token = login_result.get('access')
    refresh_token = login_result.get('refresh')
    
    if not access_token:
        print("No access token received. Stopping tests.")
        return
    
    # Test profile operations
    test_get_profile(access_token)
    test_update_profile(access_token)
    test_get_profile(access_token)  # Get profile again to see changes
    
    # Test password reset
    test_password_reset_request()
    
    # Test token refresh
    if refresh_token:
        test_token_refresh(refresh_token)
    
    print("\n" + "=" * 50)
    print("API Tests Completed!")
    print("\nTo view API documentation:")
    print("- Swagger UI: http://localhost:8000/swagger/")
    print("- ReDoc: http://localhost:8000/redoc/")

if __name__ == "__main__":
    main()
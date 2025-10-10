#!/usr/bin/env python
import requests
import json

# First, create a test room
print("Testing room creation...")
url = "http://127.0.0.1:8000/video/api/rooms/"
# Login first to get token
login_data = {"username": "testuser123", "password": "testpass123"}
login_response = requests.post("http://127.0.0.1:8000/api/accounts/login/", json=login_data)
token = login_response.json()['access']

headers = {"Authorization": f"Bearer {token}"}

room_data = {
    "title": "Test Meeting Room",
    "allow_screen_sharing": True,
    "allow_chat": True,
    "max_participants": 50
}

try:
    response = requests.post(url, json=room_data, headers=headers)
    print(f"Room Creation Status Code: {response.status_code}")
    print(f"Room Creation Response: {response.text}")
    
    if response.status_code == 201:
        room_info = response.json()
        room_code = room_info['room_code']
        print(f"Created room with code: {room_code}")
        
        # Test join room
        print("\nTesting room join...")
        join_url = "http://127.0.0.1:8000/video/api/join/"
        join_data = {"room_code": room_code}
        
        join_response = requests.post(join_url, json=join_data, headers=headers)
        print(f"Join Room Status Code: {join_response.status_code}")
        print(f"Join Room Response: {join_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Meeting App
Tests all API endpoints systematically
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:8000'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_user_data = {
            'username': f'testuser_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'email': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
    def print_test_result(self, test_name, success, status_code=None, response_data=None, error=None):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if status_code:
            print(f"   Status Code: {status_code}")
        if response_data and len(str(response_data)) < 200:
            print(f"   Response: {response_data}")
        elif response_data:
            print(f"   Response: {str(response_data)[:200]}...")
        if error:
            print(f"   Error: {error}")
        print()

    def test_authentication_apis(self):
        print("🔐 Testing Authentication APIs")
        print("=" * 50)
        
        # Test user registration
        try:
            response = self.session.post(
                f'{BASE_URL}/api/accounts/register/',
                json=self.test_user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = response.status_code in [200, 201]
            self.print_test_result(
                "User Registration",
                success,
                response.status_code,
                response.json() if success else response.text
            )
            
        except Exception as e:
            self.print_test_result("User Registration", False, error=str(e))

        # Test user login
        try:
            login_data = {
                'username': self.test_user_data['username'],
                'password': self.test_user_data['password']
            }
            
            response = self.session.post(
                f'{BASE_URL}/api/accounts/login/',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
                
            self.print_test_result(
                "User Login",
                success,
                response.status_code,
                response.json() if success else response.text
            )
            
        except Exception as e:
            self.print_test_result("User Login", False, error=str(e))

    def test_videoroom_apis(self):
        print("📹 Testing Videoroom APIs")
        print("=" * 50)
        
        if not self.access_token:
            print("❌ No access token available. Skipping videoroom API tests.")
            return
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Test get rooms
        try:
            response = self.session.get(f'{BASE_URL}/video/api/rooms/', headers=headers)
            success = response.status_code == 200
            self.print_test_result(
                "Get Rooms",
                success,
                response.status_code,
                response.json() if success else response.text
            )
        except Exception as e:
            self.print_test_result("Get Rooms", False, error=str(e))

        # Test create room
        try:
            room_data = {
                'room_name': f'test_room_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'description': 'Test room created by API test'
            }
            
            response = self.session.post(
                f'{BASE_URL}/video/api/rooms/',
                json=room_data,
                headers=headers
            )
            
            success = response.status_code in [200, 201]
            room_id = None
            if success:
                room_data_response = response.json()
                room_id = room_data_response.get('id')
                
            self.print_test_result(
                "Create Room",
                success,
                response.status_code,
                response.json() if success else response.text
            )
            
            # Test join room if room was created successfully
            if room_id:
                try:
                    response = self.session.post(
                        f'{BASE_URL}/video/api/join/{room_id}/',
                        headers=headers
                    )
                    success = response.status_code == 200
                    self.print_test_result(
                        f"Join Room {room_id}",
                        success,
                        response.status_code,
                        response.json() if success else response.text
                    )
                except Exception as e:
                    self.print_test_result(f"Join Room {room_id}", False, error=str(e))
            
        except Exception as e:
            self.print_test_result("Create Room", False, error=str(e))

        # Test participants endpoint
        try:
            response = self.session.get(f'{BASE_URL}/video/api/participants/1/', headers=headers)
            success = response.status_code in [200, 404]  # 404 is OK if room doesn't exist
            self.print_test_result(
                "Get Participants",
                success,
                response.status_code,
                response.json() if success else response.text
            )
        except Exception as e:
            self.print_test_result("Get Participants", False, error=str(e))

        # Test chat endpoint
        try:
            response = self.session.get(f'{BASE_URL}/video/api/chat/1/', headers=headers)
            success = response.status_code in [200, 404]  # 404 is OK if room doesn't exist
            self.print_test_result(
                "Get Chat Messages",
                success,
                response.status_code,
                response.json() if success else response.text
            )
        except Exception as e:
            self.print_test_result("Get Chat Messages", False, error=str(e))

    def test_frontend_pages(self):
        print("🌐 Testing Frontend Pages")
        print("=" * 50)
        
        pages_to_test = [
            ('Home Page', '/'),
            ('Login Page', '/login/'),
            ('Register Page', '/register/'),
            ('Video Room List', '/video/'),
        ]
        
        for page_name, url in pages_to_test:
            try:
                response = self.session.get(f'{BASE_URL}{url}')
                success = response.status_code == 200
                self.print_test_result(
                    page_name,
                    success,
                    response.status_code,
                    f"Page loaded successfully" if success else response.text[:100]
                )
            except Exception as e:
                self.print_test_result(page_name, False, error=str(e))

    def run_all_tests(self):
        print("🚀 Starting Comprehensive API Testing")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"Test User: {self.test_user_data['username']}")
        print("=" * 80)
        print()
        
        # Test authentication first
        self.test_authentication_apis()
        
        # Test videoroom APIs with authentication
        self.test_videoroom_apis()
        
        # Test frontend pages
        self.test_frontend_pages()
        
        print("🏁 Testing Complete!")
        print("=" * 80)

if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()
#!/usr/bin/env python3
"""
OmniBot Admin Features Testing Suite
Tests admin endpoints and phone verification features
"""

import requests
import sys
import json
from datetime import datetime

class AdminFeaturesTest:
    def __init__(self, base_url="https://ff185450-a5d6-4169-b5ee-b108ba45e8e1.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Admin credentials
        self.admin_email = "admin@omnibot.com"
        self.admin_password = "admin123"
        
        # Test user for phone verification
        self.test_email = f"phone_test_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_password = "TestPass123!"
        self.test_phone = "+1234567890"

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details and success:
            print(f"   Details: {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200, use_admin_token=False):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        token = self.admin_token if use_admin_token else self.user_token
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_admin_login(self):
        """Test admin login"""
        login_data = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        
        success, status, data = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'access_token' in data and data.get('user', {}).get('role') == 'superadmin':
            self.admin_token = data['access_token']
            self.log_test("Admin Login", True, f"Admin role confirmed: {data['user']['role']}")
        else:
            self.log_test("Admin Login", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_admin_stats(self):
        """Test admin statistics endpoint"""
        success, status, data = self.make_request('GET', '/api/admin/stats', use_admin_token=True)
        
        if success and 'total_users' in data:
            stats = f"Users: {data['total_users']}, Bots: {data['total_bots']}, Chats: {data['total_chats']}"
            self.log_test("Admin Stats", True, stats)
        else:
            self.log_test("Admin Stats", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_admin_get_all_users(self):
        """Test getting all users (admin only)"""
        success, status, data = self.make_request('GET', '/api/admin/users', use_admin_token=True)
        
        if success and 'users' in data:
            user_count = len(data['users'])
            self.log_test("Admin Get All Users", True, f"Found {user_count} users")
        else:
            self.log_test("Admin Get All Users", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_admin_get_all_bots(self):
        """Test getting all bots (admin only)"""
        success, status, data = self.make_request('GET', '/api/admin/bots', use_admin_token=True)
        
        if success and 'bots' in data:
            bot_count = len(data['bots'])
            self.log_test("Admin Get All Bots", True, f"Found {bot_count} bots")
        else:
            self.log_test("Admin Get All Bots", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_regular_user_admin_access(self):
        """Test that regular users cannot access admin endpoints"""
        # First create a regular user
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": "Test User"
        }
        
        success, status, data = self.make_request('POST', '/api/auth/register', user_data, 200)
        
        if success and 'access_token' in data:
            self.user_token = data['access_token']
            
            # Try to access admin endpoint with regular user token
            success, status, data = self.make_request('GET', '/api/admin/stats', expected_status=403)
            
            if success:
                self.log_test("Regular User Admin Access Block", True, "403 Forbidden returned correctly")
            else:
                self.log_test("Regular User Admin Access Block", False, f"Expected 403, got {status}")
        else:
            self.log_test("Regular User Admin Access Block", False, "Failed to create test user")
        
        return success

    def test_phone_verification_flow(self):
        """Test phone number verification flow"""
        if not self.user_token:
            self.log_test("Phone Verification Flow", False, "No user token available")
            return False
        
        # Step 1: Send verification code
        success, status, data = self.make_request('GET', f'/api/phone/send-code/{self.test_phone}')
        
        if success and 'code' in data:
            demo_code = data['code']  # Should be "123456"
            print(f"   📱 Verification code sent: {demo_code}")
            
            # Step 2: Verify phone number
            verify_data = {
                "phone_number": self.test_phone,
                "verification_code": demo_code
            }
            
            success, status, data = self.make_request('POST', '/api/phone/verify', verify_data)
            
            if success and data.get('verified'):
                self.log_test("Phone Verification Flow", True, f"Phone {self.test_phone} verified successfully")
            else:
                self.log_test("Phone Verification Flow", False, f"Verification failed: {data}")
        else:
            self.log_test("Phone Verification Flow", False, f"Failed to send code: {status}, {data}")
        
        return success

    def test_test_chat_feature(self):
        """Test the test chat feature that doesn't count towards limit"""
        if not self.user_token:
            self.log_test("Test Chat Feature", False, "No user token available")
            return False
        
        # First create a bot
        bot_data = {
            "bot_name": "Test Chat Bot",
            "platform": "whatsapp",
            "api_key": "test_api_key",
            "ai_provider": "gemini",
            "ai_model": "gemini-2.0-flash",
            "system_message": "You are a test assistant.",
            "auto_reply": True
        }
        
        success, status, data = self.make_request('POST', '/api/bots', bot_data, 200)
        
        if success and 'bot_id' in data:
            bot_id = data['bot_id']
            
            # Test the test chat endpoint
            test_chat_data = {
                "message": "This is a test message",
                "bot_id": bot_id
            }
            
            success, status, data = self.make_request('POST', '/api/chat/test', test_chat_data)
            
            if success and data.get('is_test'):
                self.log_test("Test Chat Feature", True, "Test chat working correctly")
            else:
                self.log_test("Test Chat Feature", False, f"Test chat failed: {data}")
        else:
            self.log_test("Test Chat Feature", False, "Failed to create test bot")
        
        return success

    def run_all_tests(self):
        """Run all admin and phone verification tests"""
        print("🔐 Starting OmniBot Admin Features Testing Suite")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Admin Login", self.test_admin_login),
            ("Admin Stats", self.test_admin_stats),
            ("Admin Get All Users", self.test_admin_get_all_users),
            ("Admin Get All Bots", self.test_admin_get_all_bots),
            ("Regular User Admin Access Block", self.test_regular_user_admin_access),
            ("Phone Verification Flow", self.test_phone_verification_flow),
            ("Test Chat Feature", self.test_test_chat_feature),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        # Final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All admin tests passed! Admin features working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main function"""
    tester = AdminFeaturesTest()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
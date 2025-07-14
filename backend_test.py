#!/usr/bin/env python3
"""
OmniBot Backend API Testing Suite
Tests all API endpoints for the omni-channel chatbot platform
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class OmniBotAPITester:
    def __init__(self, base_url="https://ff185450-a5d6-4169-b5ee-b108ba45e8e1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.bot_id = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test user data
        self.test_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_password = "TestPass123!"
        self.test_full_name = "Test User"

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

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_root_endpoint(self):
        """Test root endpoint"""
        success, status, data = self.make_request('GET', '/')
        self.log_test("Root Endpoint", success, f"Status: {status}, Message: {data.get('message', '')}")
        return success

    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": self.test_full_name
        }
        
        success, status, data = self.make_request('POST', '/api/auth/register', user_data, 200)
        
        if success and 'access_token' in data:
            self.token = data['access_token']
            self.user_data = data['user']
            self.log_test("User Registration", True, f"User ID: {self.user_data.get('user_id')}")
        else:
            self.log_test("User Registration", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_user_login(self):
        """Test user login with existing credentials"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, status, data = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'access_token' in data:
            self.token = data['access_token']  # Update token
            self.log_test("User Login", True, f"Token received")
        else:
            self.log_test("User Login", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_get_user_profile(self):
        """Test getting user profile"""
        success, status, data = self.make_request('GET', '/api/auth/me')
        
        if success:
            self.log_test("Get User Profile", True, f"Email: {data.get('email')}, Plan: {data.get('plan')}")
        else:
            self.log_test("Get User Profile", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_create_bot(self):
        """Test bot creation"""
        bot_data = {
            "bot_name": "Test WhatsApp Bot",
            "platform": "whatsapp",
            "api_key": "test_api_key_123",
            "ai_provider": "gemini",
            "ai_model": "gemini-2.0-flash",
            "system_message": "You are a helpful WhatsApp assistant.",
            "auto_reply": True
        }
        
        success, status, data = self.make_request('POST', '/api/bots', bot_data, 200)
        
        if success and 'bot_id' in data:
            self.bot_id = data['bot_id']
            self.log_test("Create Bot", True, f"Bot ID: {self.bot_id}")
        else:
            self.log_test("Create Bot", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_get_bots(self):
        """Test getting user's bots"""
        success, status, data = self.make_request('GET', '/api/bots')
        
        if success and 'bots' in data:
            bot_count = len(data['bots'])
            self.log_test("Get Bots", True, f"Found {bot_count} bots")
        else:
            self.log_test("Get Bots", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_get_single_bot(self):
        """Test getting a single bot"""
        if not self.bot_id:
            self.log_test("Get Single Bot", False, "No bot ID available")
            return False
        
        success, status, data = self.make_request('GET', f'/api/bots/{self.bot_id}')
        
        if success:
            self.log_test("Get Single Bot", True, f"Bot name: {data.get('bot_name')}")
        else:
            self.log_test("Get Single Bot", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_update_bot(self):
        """Test updating a bot"""
        if not self.bot_id:
            self.log_test("Update Bot", False, "No bot ID available")
            return False
        
        update_data = {
            "bot_name": "Updated Test Bot",
            "platform": "whatsapp",
            "api_key": "updated_api_key_456",
            "ai_provider": "openai",
            "ai_model": "gpt-4o",
            "system_message": "You are an updated helpful assistant.",
            "auto_reply": True
        }
        
        success, status, data = self.make_request('PUT', f'/api/bots/{self.bot_id}', update_data)
        
        if success:
            self.log_test("Update Bot", True, "Bot updated successfully")
        else:
            self.log_test("Update Bot", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_send_chat_message(self):
        """Test sending a chat message"""
        if not self.bot_id:
            self.log_test("Send Chat Message", False, "No bot ID available")
            return False
        
        chat_data = {
            "message": "Hello, this is a test message!",
            "bot_id": self.bot_id,
            "platform": "whatsapp",
            "sender_id": "test_sender_123"
        }
        
        success, status, data = self.make_request('POST', '/api/chat/send', chat_data)
        
        if success and 'response' in data:
            self.log_test("Send Chat Message", True, f"AI Response received: {data['response'][:50]}...")
        else:
            self.log_test("Send Chat Message", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_get_chat_history(self):
        """Test getting chat history"""
        if not self.bot_id:
            self.log_test("Get Chat History", False, "No bot ID available")
            return False
        
        success, status, data = self.make_request('GET', f'/api/chat/history/{self.bot_id}')
        
        if success and 'history' in data:
            history_count = len(data['history'])
            self.log_test("Get Chat History", True, f"Found {history_count} chat messages")
        else:
            self.log_test("Get Chat History", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_get_ai_models(self):
        """Test getting available AI models"""
        success, status, data = self.make_request('GET', '/api/ai/models')
        
        if success and 'models' in data:
            providers = list(data['models'].keys())
            self.log_test("Get AI Models", True, f"Available providers: {', '.join(providers)}")
        else:
            self.log_test("Get AI Models", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_webhook_endpoints(self):
        """Test webhook endpoints"""
        if not self.bot_id:
            self.log_test("Webhook Endpoints", False, "No bot ID available")
            return False
        
        platforms = ['whatsapp', 'telegram', 'line', 'instagram']
        webhook_success = True
        
        for platform in platforms:
            test_payload = {"test": "webhook_data", "platform": platform}
            success, status, data = self.make_request('POST', f'/api/webhooks/{platform}/{self.bot_id}', test_payload)
            
            if success:
                print(f"   ✅ {platform.capitalize()} webhook working")
            else:
                print(f"   ❌ {platform.capitalize()} webhook failed: {status}")
                webhook_success = False
        
        self.log_test("Webhook Endpoints", webhook_success, "All platform webhooks tested")
        return webhook_success

    def test_delete_bot(self):
        """Test deleting a bot"""
        if not self.bot_id:
            self.log_test("Delete Bot", False, "No bot ID available")
            return False
        
        success, status, data = self.make_request('DELETE', f'/api/bots/{self.bot_id}')
        
        if success:
            self.log_test("Delete Bot", True, "Bot deleted successfully")
        else:
            self.log_test("Delete Bot", False, f"Status: {status}, Data: {data}")
        
        return success

    def test_unauthorized_access(self):
        """Test unauthorized access"""
        original_token = self.token
        self.token = None  # Remove token
        
        success, status, data = self.make_request('GET', '/api/auth/me', expected_status=401)
        
        self.token = original_token  # Restore token
        self.log_test("Unauthorized Access", success, f"Correctly returned 401 status")
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting OmniBot API Testing Suite")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get User Profile", self.test_get_user_profile),
            ("Create Bot", self.test_create_bot),
            ("Get Bots", self.test_get_bots),
            ("Get Single Bot", self.test_get_single_bot),
            ("Update Bot", self.test_update_bot),
            ("Send Chat Message", self.test_send_chat_message),
            ("Get Chat History", self.test_get_chat_history),
            ("Get AI Models", self.test_get_ai_models),
            ("Webhook Endpoints", self.test_webhook_endpoints),
            ("Unauthorized Access", self.test_unauthorized_access),
            ("Delete Bot", self.test_delete_bot),
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
            print("🎉 All tests passed! Backend API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main function"""
    tester = OmniBotAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
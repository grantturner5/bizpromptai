import requests
import sys
import json
from datetime import datetime

class BizPromptAITester:
    def __init__(self, base_url="https://bizpromptai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.content else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@bizpromptai.com", "password": "admin123"}
        )
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            return True
        return False

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_user_{datetime.now().strftime('%H%M%S')}@test.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True, test_email
        return False, None

    def test_user_login(self, email, password):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_current_user(self):
        """Test get current user info"""
        success, _ = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_lead_magnet_signup(self):
        """Test lead magnet signup"""
        test_email = f"lead_{datetime.now().strftime('%H%M%S')}@test.com"
        success, response = self.run_test(
            "Lead Magnet Signup",
            "POST",
            "lead-magnet/signup",
            200,
            data={
                "email": test_email,
                "first_name": "Lead",
                "lead_magnet_type": "ai_prompts_guide",
                "source": "website"
            }
        )
        return success

    def test_get_prompts(self):
        """Test get prompts"""
        success, _ = self.run_test(
            "Get Prompts",
            "GET",
            "prompts",
            200
        )
        return success

    def test_get_prompt_categories(self):
        """Test get prompt categories"""
        success, _ = self.run_test(
            "Get Prompt Categories",
            "GET",
            "prompts/categories",
            200
        )
        return success

    def test_get_premium_prompts(self):
        """Test get premium prompts (requires auth)"""
        success, _ = self.run_test(
            "Get Premium Prompts",
            "GET",
            "prompts/premium",
            403  # Should fail for free user
        )
        return success

    def test_get_surveys(self):
        """Test get active surveys"""
        success, response = self.run_test(
            "Get Active Surveys",
            "GET",
            "surveys",
            200
        )
        return success, response

    def test_submit_survey_response(self, survey_id):
        """Test submit survey response"""
        success, _ = self.run_test(
            "Submit Survey Response",
            "POST",
            f"surveys/{survey_id}/responses?user_email=test@example.com",
            200,
            data={
                "q1": "Email writing",
                "q2": "10",
                "q3": "Yes immediately",
                "q4": "No concerns"
            }
        )
        return success

    def test_create_payment_checkout(self):
        """Test create payment checkout"""
        success, response = self.run_test(
            "Create Payment Checkout",
            "POST",
            "payments/create-checkout",
            200
        )
        return success, response

    def test_admin_dashboard(self):
        """Test admin dashboard (requires admin auth)"""
        # Save current token
        user_token = self.token
        self.token = self.admin_token
        
        success, _ = self.run_test(
            "Admin Dashboard",
            "GET",
            "admin/dashboard",
            200
        )
        
        # Restore user token
        self.token = user_token
        return success

    def test_admin_get_users(self):
        """Test admin get all users"""
        # Save current token
        user_token = self.token
        self.token = self.admin_token
        
        success, _ = self.run_test(
            "Admin Get Users",
            "GET",
            "admin/users",
            200
        )
        
        # Restore user token
        self.token = user_token
        return success

    def test_admin_survey_responses(self):
        """Test admin get survey responses"""
        # Save current token
        user_token = self.token
        self.token = self.admin_token
        
        success, _ = self.run_test(
            "Admin Survey Responses",
            "GET",
            "admin/survey-responses",
            200
        )
        
        # Restore user token
        self.token = user_token
        return success

    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting BizPromptAI API Tests...")
        print(f"Testing against: {self.base_url}")
        print("=" * 50)

        # Test admin login first
        if not self.test_admin_login():
            print("❌ Admin login failed, stopping admin tests")
            return False

        # Test user registration and login
        reg_success, test_email = self.test_user_registration()
        if not reg_success:
            print("❌ User registration failed, stopping user tests")
            return False

        # Test user authentication flow
        self.test_get_current_user()

        # Test lead magnet
        self.test_lead_magnet_signup()

        # Test prompt library
        self.test_get_prompts()
        self.test_get_prompt_categories()
        self.test_get_premium_prompts()

        # Test surveys
        survey_success, surveys = self.test_get_surveys()
        if survey_success and surveys and len(surveys) > 0:
            survey_id = surveys[0].get('id')
            if survey_id:
                self.test_submit_survey_response(survey_id)

        # Test payment system
        payment_success, payment_response = self.test_create_payment_checkout()

        # Test admin endpoints
        self.test_admin_dashboard()
        self.test_admin_get_users()
        self.test_admin_survey_responses()

        # Print results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = BizPromptAITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/test_reports/backend_api_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "success_rate": (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            "test_results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
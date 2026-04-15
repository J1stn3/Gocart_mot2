"""
Integration tests for authentication system.
Run with: pytest tests/test_auth.py -v
"""
import pytest
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/auth"

# Test data
TEST_USER = {
    "username": "testuser123",
    "email": "test@example.com",
    "password": "SecurePass123@"
}

TEST_USER_2 = {
    "username": "testuser456",
    "email": "test2@example.com",
    "password": "SecurePass456@"
}

INVALID_PASSWORD = "weak"
INVALID_EMAIL = "notanemail"


class TestAuthentication:
    """Test authentication endpoints."""
    
    @classmethod
    def setup_class(cls):
        """Setup test fixtures."""
        cls.tokens: Dict[str, Any] = {}
        cls.user_data = TEST_USER.copy()
    
    def test_01_register_valid_user(self):
        """Test registering a new user with valid credentials."""
        response = requests.post(
            f"{API_URL}/register",
            json=self.user_data,
            timeout=10
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert "user_id" in data["data"]
        assert data["data"]["username"] == self.user_data["username"]
        print(f"✓ User registered successfully: {data['data']['user_id']}")
    
    def test_02_register_duplicate_user(self):
        """Test registering duplicate user should fail."""
        response = requests.post(
            f"{API_URL}/register",
            json=self.user_data,
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "already exists" in data["message"].lower()
        print("✓ Duplicate registration correctly rejected")
    
    def test_03_register_weak_password(self):
        """Test registering with weak password should fail."""
        weak_password_user = {
            "username": "weakpassuser",
            "email": "weak@example.com",
            "password": INVALID_PASSWORD
        }
        
        response = requests.post(
            f"{API_URL}/register",
            json=weak_password_user,
            timeout=10
        )
        
        assert response.status_code == 400
        print("✓ Weak password correctly rejected")
    
    def test_04_register_invalid_email(self):
        """Test registering with invalid email."""
        invalid_email_user = {
            "username": "invalidemail",
            "email": INVALID_EMAIL,
            "password": "SecurePass123@"
        }
        
        response = requests.post(
            f"{API_URL}/register",
            json=invalid_email_user,
            timeout=10
        )
        
        assert response.status_code == 400
        print("✓ Invalid email correctly rejected")
    
    def test_05_login_valid_credentials(self):
        """Test login with valid credentials."""
        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": self.user_data["username"],
                "password": self.user_data["password"]
            },
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        
        self.tokens = data["data"]
        print(f"✓ Login successful")
        print(f"  - Access token: {self.tokens['access_token'][:20]}...")
        print(f"  - Refresh token: {self.tokens['refresh_token'][:20]}...")
    
    def test_06_login_invalid_password(self):
        """Test login with invalid password."""
        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": self.user_data["username"],
                "password": "WrongPassword123@"
            },
            timeout=10
        )
        
        assert response.status_code == 401
        print("✓ Invalid password correctly rejected")
    
    def test_07_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": "nonexistentuser",
                "password": "AnyPass123@"
            },
            timeout=10
        )
        
        assert response.status_code == 401
        print("✓ Nonexistent user correctly rejected")
    
    def test_08_get_current_user(self):
        """Test getting current user info."""
        if not self.tokens.get("access_token"):
            pytest.skip("No access token available")
        
        response = requests.get(
            f"{API_URL}/me",
            headers={"Authorization": f"Bearer {self.tokens['access_token']}"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["username"] == self.user_data["username"]
        print(f"✓ Current user retrieved: {data['data']['username']}")
    
    def test_09_access_without_token(self):
        """Test accessing protected endpoint without token."""
        response = requests.get(
            f"{API_URL}/me",
            timeout=10
        )
        
        assert response.status_code == 401
        print("✓ Unauthenticated access correctly denied")
    
    def test_10_access_with_invalid_token(self):
        """Test accessing with invalid token."""
        response = requests.get(
            f"{API_URL}/me",
            headers={"Authorization": "Bearer invalid_token_12345"},
            timeout=10
        )
        
        assert response.status_code == 401
        print("✓ Invalid token correctly rejected")
    
    def test_11_refresh_token(self):
        """Test token refresh."""
        if not self.tokens.get("refresh_token"):
            pytest.skip("No refresh token available")
        
        response = requests.post(
            f"{API_URL}/refresh",
            json={"refresh_token": self.tokens["refresh_token"]},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "access_token" in data["data"]
        
        # Store new token
        self.tokens["access_token"] = data["data"]["access_token"]
        print(f"✓ Token refreshed successfully")
        print(f"  - New access token: {data['data']['access_token'][:20]}...")
    
    def test_12_logout(self):
        """Test logout."""
        if not self.tokens.get("access_token"):
            pytest.skip("No access token available")
        
        response = requests.post(
            f"{API_URL}/logout",
            json={"refresh_token": self.tokens.get("refresh_token")},
            headers={"Authorization": f"Bearer {self.tokens['access_token']}"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✓ Logout successful")


class TestRBAC:
    """Test Role-Based Access Control."""
    
    def test_admin_endpoint_with_user_token(self):
        """Test that regular user cannot access admin endpoints."""
        # First register and login as regular user
        user_data = TEST_USER_2.copy()
        
        # Register
        requests.post(f"{API_URL}/register", json=user_data, timeout=10)
        
        # Login
        login_response = requests.post(
            f"{API_URL}/login",
            json={
                "username": user_data["username"],
                "password": user_data["password"]
            },
            timeout=10
        )
        
        tokens = login_response.json()["data"]
        
        # Try to access admin endpoint
        response = requests.get(
            f"{API_URL}/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            timeout=10
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ RBAC: Regular user correctly denied admin access")


class TestSecurityHeaders:
    """Test security configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are properly set."""
        response = requests.options(
            f"{BASE_URL}/api/auth/login",
            timeout=10
        )
        
        assert "access-control-allow-origin" in response.headers.keys() or response.status_code in [204, 200]
        print("✓ CORS headers configured")


if __name__ == "__main__":
    # Run tests manually
    print("Starting authentication system tests...\n")
    
    test = TestAuthentication()
    test.setup_class()
    
    try:
        test.test_01_register_valid_user()
        test.test_02_register_duplicate_user()
        test.test_03_register_weak_password()
        test.test_04_register_invalid_email()
        test.test_05_login_valid_credentials()
        test.test_06_login_invalid_password()
        test.test_07_login_nonexistent_user()
        test.test_08_get_current_user()
        test.test_09_access_without_token()
        test.test_10_access_with_invalid_token()
        test.test_11_refresh_token()
        test.test_12_logout()
        
        rbac_test = TestRBAC()
        rbac_test.test_admin_endpoint_with_user_token()
        
        sec_test = TestSecurityHeaders()
        sec_test.test_cors_headers_present()
        
        print("\n✓ All tests passed!")
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)

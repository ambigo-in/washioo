"""
Testing guide for the authentication system.
Contains examples and best practices for testing all endpoints.
"""

# ============================================================

# API TESTING WITH CURL

# ============================================================

# 1. SEND OTP

# ---------

# For a new user (will return user_exist: false)

curl -X POST http://localhost:8000/auth/send-otp \
 -H "Content-Type: application/json" \
 -d '{"phone": "+919876543210"}'

# Response:

# {

# "message": "OTP sent successfully",

# "user_exist": false

# }

# 2. SIGNUP (New User)

# -------------------

# After receiving OTP from send-otp endpoint

curl -X POST http://localhost:8000/auth/signup \
 -H "Content-Type: application/json" \
 -d '{
"full_name": "John Doe",
"phone": "+919876543210",
"email": "john@example.com",
"otp": "123456",
"role": "customer"
}'

# Response:

# {

# "message": "User created successfully",

# "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

# "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

# "token_type": "bearer"

# }

# 3. SIGNIN (Existing User)

# -------------------------

# For existing user, use send-otp first (returns user_exist: true)

curl -X POST http://localhost:8000/auth/send-otp \
 -H "Content-Type: application/json" \
 -d '{"phone": "+919876543210"}'

# Then use the OTP with signin endpoint

curl -X POST http://localhost:8000/auth/signin \
 -H "Content-Type: application/json" \
 -d '{
"phone": "+919876543210",
"otp": "123456"
}'

# Response:

# {

# "message": "Login successful",

# "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

# "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

# "token_type": "bearer"

# }

# 4. REFRESH TOKEN

# ---------------

curl -X POST http://localhost:8000/auth/refresh-token \
 -H "Content-Type: application/json" \
 -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'

# Response:

# {

# "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

# "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

# "token_type": "bearer"

# }

# 5. LOGOUT

# --------

curl -X POST http://localhost:8000/auth/logout \
 -H "Content-Type: application/json" \
 -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'

# Response:

# {

# "message": "Logged out successfully"

# }

# ============================================================

# TESTING WITH PYTHON REQUESTS

# ============================================================

import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Send OTP

def test_send_otp():
response = requests.post(
f"{BASE_URL}/auth/send-otp",
json={"phone": "+919876543210"}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
return response.json()

# 2. Signup

def test_signup():
response = requests.post(
f"{BASE_URL}/auth/signup",
json={
"full_name": "John Doe",
"phone": "+919876543210",
"email": "john@example.com",
"otp": "123456",
"role": "customer"
}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
return response.json()

# 3. Signin

def test_signin():
response = requests.post(
f"{BASE_URL}/auth/signin",
json={
"phone": "+919876543210",
"otp": "123456"
}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
return response.json()

# 4. Refresh Token

def test_refresh_token(refresh_token):
response = requests.post(
f"{BASE_URL}/auth/refresh-token",
json={"refresh_token": refresh_token}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
return response.json()

# 5. Logout

def test_logout(refresh_token):
response = requests.post(
f"{BASE_URL}/auth/logout",
json={"refresh_token": refresh_token}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
return response.json()

# Run tests

if **name** == "**main**":
print("Testing Send OTP...")
otp_response = test_send_otp()

    print("\nTesting Signup...")
    signup_response = test_signup()
    refresh_token = signup_response.get("refresh_token")

    print("\nTesting Refresh Token...")
    refresh_response = test_refresh_token(refresh_token)

    print("\nTesting Logout...")
    test_logout(refresh_response.get("refresh_token"))

# ============================================================

# TESTING WITH PYTEST

# ============================================================

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthentication:
"""Test cases for authentication endpoints."""

    def test_send_otp_new_user(self):
        """Test sending OTP to a new user."""
        response = client.post(
            "/auth/send-otp",
            json={"phone": "+919876543210"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        assert data["user_exist"] == False

    def test_send_otp_invalid_phone(self):
        """Test sending OTP with invalid phone format."""
        response = client.post(
            "/auth/send-otp",
            json={"phone": "invalid"}
        )
        assert response.status_code == 422

    def test_signup_success(self):
        """Test successful user signup."""
        # First send OTP
        client.post(
            "/auth/send-otp",
            json={"phone": "+919876543211"}
        )

        # Then signup
        response = client.post(
            "/auth/signup",
            json={
                "full_name": "Jane Doe",
                "phone": "+919876543211",
                "email": "jane@example.com",
                "otp": "123456",
                "role": "customer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_user_exists(self):
        """Test signup when user already exists."""
        response = client.post(
            "/auth/signup",
            json={
                "full_name": "John Doe",
                "phone": "+919876543210",  # From previous test
                "email": "john@example.com",
                "otp": "123456",
                "role": "customer"
            }
        )
        assert response.status_code == 400

    def test_signin_success(self):
        """Test successful user signin."""
        # Send OTP
        client.post(
            "/auth/send-otp",
            json={"phone": "+919876543210"}
        )

        # Signin
        response = client.post(
            "/auth/signin",
            json={
                "phone": "+919876543210",
                "otp": "123456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_signin_invalid_otp(self):
        """Test signin with invalid OTP."""
        client.post(
            "/auth/send-otp",
            json={"phone": "+919876543210"}
        )

        response = client.post(
            "/auth/signin",
            json={
                "phone": "+919876543210",
                "otp": "000000"  # Wrong OTP
            }
        )
        assert response.status_code == 400

    def test_refresh_token_success(self):
        """Test token refresh."""
        # Get initial tokens
        client.post(
            "/auth/send-otp",
            json={"phone": "+919876543212"}
        )

        signup = client.post(
            "/auth/signup",
            json={
                "full_name": "Bob Smith",
                "phone": "+919876543212",
                "email": "bob@example.com",
                "otp": "123456",
                "role": "cleaner"
            }
        ).json()

        refresh_token = signup["refresh_token"]

        # Refresh
        response = client.post(
            "/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["refresh_token"] != refresh_token  # Token should rotate

    def test_refresh_token_invalid(self):
        """Test token refresh with invalid token."""
        response = client.post(
            "/auth/refresh-token",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401

    def test_logout_success(self):
        """Test logout."""
        # Get token
        client.post(
            "/auth/send-otp",
            json={"phone": "+919876543213"}
        )

        signup = client.post(
            "/auth/signup",
            json={
                "full_name": "Alice Admin",
                "phone": "+919876543213",
                "email": "alice@example.com",
                "otp": "123456",
                "role": "admin"
            }
        ).json()

        # Logout
        response = client.post(
            "/auth/logout",
            json={"refresh_token": signup["refresh_token"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    def test_rate_limiting_send_otp(self):
        """Test rate limiting on send OTP."""
        phone = "+919999999999"

        # Send 3 requests (should all pass)
        for i in range(3):
            response = client.post(
                "/auth/send-otp",
                json={"phone": phone}
            )
            assert response.status_code == 200

        # 4th request should be rate limited
        response = client.post(
            "/auth/send-otp",
            json={"phone": phone}
        )
        assert response.status_code == 429

# Run tests with: pytest test_auth.py -v

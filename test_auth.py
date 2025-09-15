import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_auth_system():
    """Test the complete authorization system"""
    print("Testing PyCasbin authorization system...")

    # Step 1: Create a corporation
    print("\n1. Creating a corporation...")
    timestamp = str(int(time.time()))
    corp_data = {
        "name": f"Test Corporation {timestamp}",
        "code": f"TEST{timestamp}",
        "description": "Test corporation for auth"
    }
    corp_response = requests.post(f"{BASE_URL}/api/v1/corporations/", json=corp_data)
    print(f"Corporation created: {corp_response.status_code}")
    if corp_response.status_code != 200:
        print(f"Corporation creation failed: {corp_response.text}")
        return
    corporation = corp_response.json()
    corporation_id = corporation["id"]
    print(f"Corporation ID: {corporation_id}")

    # Step 2: Create a user in this corporation
    print("\n2. Creating a user...")
    user_data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "full_name": "Test User",
        "password": "testpassword",
        "corporation_id": corporation_id
    }
    user_response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    print(f"User created: {user_response.status_code}")
    if user_response.status_code != 200:
        print(f"User creation failed: {user_response.text}")
        return
    user = user_response.json()
    user_id = user["id"]
    print(f"User ID: {user_id}")

    # Step 3: Login and get token
    print("\n3. Logging in to get token...")
    login_data = {
        "username": f"testuser{timestamp}",
        "password": "testpassword"
    }
    # Using form data for OAuth2PasswordRequestForm
    token_response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Login response: {token_response.status_code}")

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data["access_token"]
        print(f"Access token obtained: {access_token[:20]}...")

        # Step 4: Try to access corporation details with valid token
        print("\n4. Accessing corporation details with valid token...")
        headers = {"Authorization": f"Bearer {access_token}"}

        corp_detail_response = requests.get(
            f"{BASE_URL}/api/v1/corporations/{corporation_id}",
            headers=headers
        )
        print(f"Corporation detail access: {corp_detail_response.status_code}")

        if corp_detail_response.status_code == 200:
            print("✅ Authorization successful - User can access their own corporation")
            print(f"Corporation data: {corp_detail_response.json()['name']}")
        else:
            print("❌ Authorization failed")
            print(f"Error: {corp_detail_response.text}")

        # Step 5: Try to access another corporation (should fail)
        print("\n5. Creating another corporation and trying to access it...")
        other_corp_data = {
            "name": f"Other Corporation {timestamp}",
            "code": f"OTHER{timestamp}",
            "description": "Other corporation"
        }
        other_corp_response = requests.post(f"{BASE_URL}/api/v1/corporations/", json=other_corp_data)
        other_corporation = other_corp_response.json()
        other_corporation_id = other_corporation["id"]

        other_corp_detail_response = requests.get(
            f"{BASE_URL}/api/v1/corporations/{other_corporation_id}",
            headers=headers
        )
        print(f"Other corporation access: {other_corp_detail_response.status_code}")

        if other_corp_detail_response.status_code == 403:
            print("✅ Authorization working correctly - User cannot access other corporation")
        else:
            print("❌ Authorization security issue - User can access other corporation")
            print(f"Response: {other_corp_detail_response.text}")

    else:
        print(f"❌ Login failed: {token_response.text}")

if __name__ == "__main__":
    test_auth_system()
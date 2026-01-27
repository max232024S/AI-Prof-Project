"""
Test script for AI-Prof Flask API.
Run this after starting the Flask server with: python app.py
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"
TOKEN = None
USER_ID = None


def print_response(response, title):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health():
    """Test health check endpoint."""
    print("\n1. Testing Health Check Endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response, "Health Check")
    return response.status_code == 200


def test_register():
    """Test user registration."""
    global TOKEN, USER_ID
    print("\n2. Testing User Registration...")

    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test_{hash(str(id(object())))}@example.com",  # Unique email
        "password": "test123"
    }

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=data
    )
    print_response(response, "User Registration")

    if response.status_code == 201:
        result = response.json()
        TOKEN = result.get('token')
        USER_ID = result.get('user_id')
        print(f"\nSaved Token: {TOKEN}")
        print(f"Saved User ID: {USER_ID}")
        return True
    return False


def test_login():
    """Test user login (optional - we already have token from registration)."""
    print("\n3. Testing User Login...")
    print("Skipping - using token from registration")
    return True


def test_documents():
    """Test listing documents."""
    global TOKEN
    print("\n4. Testing List Documents...")

    if not TOKEN:
        print("Error: No token available. Registration failed.")
        return False

    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/documents", headers=headers)
    print_response(response, "List Documents")
    return response.status_code == 200


def test_conversations():
    """Test listing conversations."""
    global TOKEN
    print("\n5. Testing List Conversations...")

    if not TOKEN:
        print("Error: No token available. Registration failed.")
        return False

    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/conversations", headers=headers)
    print_response(response, "List Conversations")
    return response.status_code == 200


def test_unauthorized():
    """Test endpoint with invalid token."""
    print("\n6. Testing Unauthorized Access...")

    headers = {"Authorization": "Bearer invalid_token_12345"}
    response = requests.get(f"{BASE_URL}/api/conversations", headers=headers)
    print_response(response, "Unauthorized Access (Expected 401)")
    return response.status_code == 401


def test_chat():
    """Test chat endpoint (without uploaded documents)."""
    global TOKEN
    print("\n7. Testing Chat Endpoint...")

    if not TOKEN:
        print("Error: No token available. Registration failed.")
        return False

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "message": "Hello, can you help me understand this concept?"
    }

    response = requests.post(f"{BASE_URL}/api/chat", json=data, headers=headers)
    print_response(response, "Chat")
    return response.status_code == 200


def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*60)
    print("AI-PROF API TEST SUITE")
    print("="*60)
    print("\nMake sure the Flask server is running: python app.py")
    print("Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)

    tests = [
        ("Health Check", test_health),
        ("User Registration", test_register),
        ("User Login", test_login),
        ("List Documents", test_documents),
        ("List Conversations", test_conversations),
        ("Unauthorized Access", test_unauthorized),
        ("Chat", test_chat),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Error: Cannot connect to {BASE_URL}")
            print("Make sure the Flask server is running: python app.py")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error during {name}: {str(e)}")
            results.append((name, False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed_count = 0
    failed_count = 0

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
        if passed:
            passed_count += 1
        else:
            failed_count += 1

    print(f"\nTotal: {passed_count} passed, {failed_count} failed")

    if TOKEN:
        print(f"\n[INFO] Your API Token: {TOKEN}")
        print(f"[INFO] Your User ID: {USER_ID}")
        print("\nYou can use this token to test other endpoints manually:")
        print(f'curl -H "Authorization: Bearer {TOKEN}" {BASE_URL}/api/documents')

    return failed_count == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

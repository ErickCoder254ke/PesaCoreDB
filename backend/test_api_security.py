#!/usr/bin/env python3
"""
API Security Test Script
Tests API key authentication for PesacodeDB

Usage:
    python test_api_security.py
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
API_KEY = os.getenv('API_KEY', 'pesacodedb_dev_key_change_in_production_2024')
REQUIRE_API_KEY = os.getenv('REQUIRE_API_KEY', 'false').lower() == 'true'

API_BASE = f"{BACKEND_URL}/api"

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_test(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"        {message}")

def test_health_without_key():
    """Test 1: Health endpoint without API key"""
    print_header("Test 1: Health Check WITHOUT API Key")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        
        if REQUIRE_API_KEY:
            # Should fail if API key is required
            if response.status_code == 403:
                print_test("Health endpoint requires authentication", True, "Returns 403 as expected")
                return True
            else:
                print_test("Health endpoint requires authentication", False, 
                          f"Expected 403, got {response.status_code}")
                return False
        else:
            # Should work if API key is not required
            if response.status_code == 200:
                print_test("Health endpoint works without auth", True, "Returns 200 as expected")
                return True
            else:
                print_test("Health endpoint works without auth", False,
                          f"Expected 200, got {response.status_code}")
                return False
    except requests.RequestException as e:
        print_test("Health endpoint connection", False, f"Error: {str(e)}")
        return False

def test_health_with_valid_key():
    """Test 2: Health endpoint with valid API key"""
    print_header("Test 2: Health Check WITH Valid API Key")
    
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{API_BASE}/health", headers=headers, timeout=5)
        
        if response.status_code == 200:
            print_test("Health endpoint with valid key", True, "Authentication successful")
            print(f"        Response: {response.json()}")
            return True
        else:
            print_test("Health endpoint with valid key", False,
                      f"Expected 200, got {response.status_code}")
            return False
    except requests.RequestException as e:
        print_test("Health endpoint with valid key", False, f"Error: {str(e)}")
        return False

def test_health_with_invalid_key():
    """Test 3: Health endpoint with invalid API key"""
    print_header("Test 3: Health Check WITH Invalid API Key")
    
    if not REQUIRE_API_KEY:
        print_test("Invalid key test", True, "Skipped (authentication not required)")
        return True
    
    try:
        headers = {'X-API-Key': 'invalid_key_12345'}
        response = requests.get(f"{API_BASE}/health", headers=headers, timeout=5)
        
        if response.status_code == 403:
            print_test("Rejects invalid API key", True, "Returns 403 as expected")
            return True
        else:
            print_test("Rejects invalid API key", False,
                      f"Expected 403, got {response.status_code}")
            return False
    except requests.RequestException as e:
        print_test("Invalid key rejection", False, f"Error: {str(e)}")
        return False

def test_query_without_key():
    """Test 4: Query endpoint without API key"""
    print_header("Test 4: Query Endpoint WITHOUT API Key")
    
    try:
        data = {"sql": "SELECT * FROM users", "db": "default"}
        response = requests.post(f"{API_BASE}/query", json=data, timeout=5)
        
        if REQUIRE_API_KEY:
            if response.status_code == 403:
                print_test("Query requires authentication", True, "Returns 403 as expected")
                return True
            else:
                print_test("Query requires authentication", False,
                          f"Expected 403, got {response.status_code}")
                return False
        else:
            # May return error about table not existing, but shouldn't be 403
            if response.status_code != 403:
                print_test("Query works without auth", True, 
                          f"Returns {response.status_code} (not blocked)")
                return True
            else:
                print_test("Query works without auth", False, "Unexpectedly blocked")
                return False
    except requests.RequestException as e:
        print_test("Query endpoint connection", False, f"Error: {str(e)}")
        return False

def test_query_with_valid_key():
    """Test 5: Query endpoint with valid API key"""
    print_header("Test 5: Query Endpoint WITH Valid API Key")
    
    try:
        headers = {'X-API-Key': API_KEY}
        data = {"sql": "SELECT * FROM users", "db": "default"}
        response = requests.post(f"{API_BASE}/query", json=data, headers=headers, timeout=5)
        
        # Should not be 403 (may be other errors if table doesn't exist)
        if response.status_code != 403:
            result = response.json()
            if result.get('success') or 'error' in result:
                print_test("Query with valid key", True, "Authentication successful")
                return True
            else:
                print_test("Query with valid key", False, "Unexpected response format")
                return False
        else:
            print_test("Query with valid key", False, "Authentication failed")
            return False
    except requests.RequestException as e:
        print_test("Query with valid key", False, f"Error: {str(e)}")
        return False

def test_docs_access():
    """Test 6: Docs endpoint (should be public)"""
    print_header("Test 6: API Documentation Access (Should Be Public)")
    
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        
        if response.status_code == 200:
            print_test("Docs endpoint is public", True, "Accessible without authentication")
            return True
        else:
            print_test("Docs endpoint is public", False,
                      f"Expected 200, got {response.status_code}")
            return False
    except requests.RequestException as e:
        print_test("Docs endpoint access", False, f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and print summary"""
    print("\n" + "="*60)
    print("  🔒 PesacodeDB API Security Test Suite")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Backend URL: {BACKEND_URL}")
    print(f"  API Key: {'*' * (len(API_KEY) - 8) + API_KEY[-8:]}")
    print(f"  Authentication Required: {REQUIRE_API_KEY}")
    
    tests = [
        test_health_without_key,
        test_health_with_valid_key,
        test_health_with_invalid_key,
        test_query_without_key,
        test_query_with_valid_key,
        test_docs_access,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    # Summary
    print_header("Test Summary")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n✅ All tests passed! API security is working correctly.")
        if not REQUIRE_API_KEY:
            print("\n⚠️  WARNING: API key authentication is currently DISABLED")
            print("   Set REQUIRE_API_KEY=true in .env for production")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        print("   Common issues:")
        print("   - Backend server not running")
        print("   - Wrong API key in .env file")
        print("   - Incorrect REQUIRE_API_KEY setting")
    
    print("\n" + "="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        exit(1)

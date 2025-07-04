#!/usr/bin/env python3
"""
Test script to verify webhook validation improvements.
Tests various malformed payloads and edge cases.
"""

import json
import requests
import time

# Test webhook endpoint
WEBHOOK_URL = "http://localhost:5000/webhook"

def test_malformed_payloads():
    """Test various malformed payloads that should return 400."""
    
    print("Testing malformed payloads...")
    
    # Test 1: Invalid event type
    print("\n1. Testing invalid event type...")
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "invalid_event",
        "User-Agent": "GitHub-Hookshot/test"
    }
    payload = {"test": "data"}
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Push event missing required fields
    print("\n2. Testing push event missing 'after' field...")
    headers["X-GitHub-Event"] = "push"
    payload = {
        "ref": "refs/heads/main",
        "pusher": {"name": "testuser"}
        # Missing 'after' field
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Push event with invalid pusher
    print("\n3. Testing push event with invalid pusher...")
    payload = {
        "after": "abc123",
        "ref": "refs/heads/main",
        "pusher": {}  # Missing 'name' field
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Pull request event missing required fields
    print("\n4. Testing pull request event missing 'pull_request' field...")
    headers["X-GitHub-Event"] = "pull_request"
    payload = {
        "action": "opened"
        # Missing 'pull_request' field
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Pull request event with incomplete pull_request object
    print("\n5. Testing pull request event with incomplete pull_request object...")
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 123,
            "user": {"login": "testuser"}
            # Missing 'head' and 'base' fields
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")

def test_valid_payloads():
    """Test valid payloads to ensure they still work."""
    
    print("\n\nTesting valid payloads...")
    
    # Test 1: Valid push event
    print("\n1. Testing valid push event...")
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",
        "User-Agent": "GitHub-Hookshot/test"
    }
    payload = {
        "after": "abc123def456",
        "ref": "refs/heads/main",
        "pusher": {"name": "testuser"}
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Valid pull request opened event
    print("\n2. Testing valid pull request opened event...")
    headers["X-GitHub-Event"] = "pull_request"
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 12345,
            "number": 42,
            "user": {"login": "testuser"},
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"}
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Valid pull request merged event
    print("\n3. Testing valid pull request merged event...")
    payload = {
        "action": "closed",
        "pull_request": {
            "id": 12346,
            "number": 43,
            "user": {"login": "testuser"},
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
            "merged": True
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Webhook Validation Testing Script")
    print("=" * 50)
    print("Make sure to start the Flask app first: python app.py")
    print("=" * 50)
    
    test_malformed_payloads()
    test_valid_payloads()
    
    print("\nValidation testing complete!")

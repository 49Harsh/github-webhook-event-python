#!/usr/bin/env python3
"""
Test script to verify webhook functionality and error handling.
This script can be used to test the webhook endpoint without needing MongoDB.
"""

import json
import requests
import time

# Test webhook endpoint
WEBHOOK_URL = "http://localhost:5000/webhook"
EVENTS_URL = "http://localhost:5000/events"

def test_push_webhook():
    """Test push webhook payload."""
    payload = {
        "after": "abc123def456",
        "ref": "refs/heads/main",
        "pusher": {
            "name": "testuser"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",
        "User-Agent": "GitHub-Hookshot/test"
    }
    
    print("Testing push webhook...")
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to webhook endpoint. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_pull_request_webhook():
    """Test pull request webhook payload."""
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 12345,
            "number": 42,
            "user": {
                "login": "testuser"
            },
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request",
        "User-Agent": "GitHub-Hookshot/test"
    }
    
    print("\nTesting pull request webhook...")
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to webhook endpoint. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_webhook():
    """Test invalid webhook payload."""
    headers = {
        "Content-Type": "text/plain",
        "X-GitHub-Event": "push"
    }
    
    print("\nTesting invalid webhook (non-JSON)...")
    try:
        response = requests.post(WEBHOOK_URL, data="invalid data", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to webhook endpoint. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_events_endpoint():
    """Test events retrieval endpoint."""
    print("\nTesting events endpoint...")
    try:
        response = requests.get(EVENTS_URL)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            events = response.json()
            print(f"Number of events: {len(events)}")
            if events:
                print(f"Latest event: {events[0]}")
        else:
            print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to events endpoint. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Webhook Testing Script")
    print("=" * 50)
    print("Make sure to start the Flask app first: python app.py")
    print("=" * 50)
    
    test_push_webhook()
    test_pull_request_webhook()
    test_invalid_webhook()
    test_events_endpoint()
    
    print("\nTesting complete!")

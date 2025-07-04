#!/usr/bin/env python3
"""
Script to simulate GitHub webhook events for local testing.
This sends sample webhook payloads to the local webhook endpoint.
"""

import requests
import json
import sys
import time

# Base URL for the webhook endpoint
BASE_URL = "http://localhost:5000/webhook"

# Sample push event payload
PUSH_EVENT = {
    "ref": "refs/heads/main",
    "after": "abc123def456",
    "pusher": {
        "name": "test_user",
        "email": "test@example.com"
    }
}

# Sample pull request opened event payload
PR_OPEN_EVENT = {
    "action": "opened",
    "pull_request": {
        "id": 123456,
        "user": {
            "login": "test_user"
        },
        "head": {
            "ref": "feature-branch"
        },
        "base": {
            "ref": "main"
        }
    }
}

# Sample pull request merged event payload
PR_MERGED_EVENT = {
    "action": "closed",
    "pull_request": {
        "id": 123457,
        "merged": True,
        "user": {
            "login": "test_user"
        },
        "head": {
            "ref": "bugfix-branch"
        },
        "base": {
            "ref": "main"
        }
    }
}

def send_event(event_type, payload):
    """Send a simulated webhook event to the local endpoint"""
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": event_type,
        "User-Agent": "GitHub-Hookshot/Simulated"
    }
    
    print(f"Sending {event_type} event...")
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        print(f"Response: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending event: {e}")
        return False

def main():
    """Main function to simulate events"""
    print("GitHub Webhook Event Simulator")
    print("=" * 50)
    
    # Send push event
    if send_event("push", PUSH_EVENT):
        print("✓ Push event sent successfully")
    else:
        print("✗ Failed to send push event")
    
    time.sleep(1)
    
    # Send PR opened event
    if send_event("pull_request", PR_OPEN_EVENT):
        print("✓ Pull request opened event sent successfully")
    else:
        print("✗ Failed to send pull request opened event")
    
    time.sleep(1)
    
    # Send PR merged event
    if send_event("pull_request", PR_MERGED_EVENT):
        print("✓ Pull request merged event sent successfully")
    else:
        print("✗ Failed to send pull request merged event")

if __name__ == "__main__":
    main() 
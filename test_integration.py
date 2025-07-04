#!/usr/bin/env python3
"""
Integration test to verify the complete webhook + events workflow with timestamp formatting.
"""

import json
import requests
import time
import subprocess
import threading
from datetime import datetime

def test_webhook_events_integration():
    """Test the complete workflow: webhook -> storage -> events retrieval with timestamps."""
    print("Integration Test: Webhook + Events with Timestamp Formatting")
    print("=" * 60)
    
    # Test URLs
    webhook_url = "http://localhost:5000/webhook"
    events_url = "http://localhost:5000/events"
    
    # Test webhook payload
    webhook_payload = {
        "after": "integration_test_123",
        "ref": "refs/heads/main",
        "pusher": {
            "name": "integration_tester"
        }
    }
    
    webhook_headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",
        "User-Agent": "GitHub-Hookshot/test"
    }
    
    try:
        # Step 1: Send webhook
        print("Step 1: Sending webhook...")
        webhook_response = requests.post(webhook_url, json=webhook_payload, headers=webhook_headers)
        print(f"Webhook Status: {webhook_response.status_code}")
        print(f"Webhook Response: {webhook_response.json()}")
        
        if webhook_response.status_code != 200:
            print("ERROR: Webhook failed!")
            return False
        
        # Step 2: Wait a moment for processing
        time.sleep(1)
        
        # Step 3: Retrieve events
        print("\nStep 2: Retrieving events...")
        events_response = requests.get(events_url)
        print(f"Events Status: {events_response.status_code}")
        
        if events_response.status_code != 200:
            print("ERROR: Events retrieval failed!")
            return False
        
        events = events_response.json()
        print(f"Number of events: {len(events)}")
        
        # Step 4: Find our test event
        test_event = None
        for event in events:
            if event.get('request_id') == 'integration_test_123':
                test_event = event
                break
        
        if not test_event:
            print("ERROR: Test event not found!")
            return False
        
        # Step 5: Verify timestamp formats
        print("\nStep 3: Verifying timestamp formats...")
        print(f"Event Details:")
        print(f"  Action: {test_event.get('action')}")
        print(f"  Author: {test_event.get('author')}")
        print(f"  Original timestamp: {test_event.get('timestamp')}")
        print(f"  ISO timestamp: {test_event.get('timestamp_iso')}")
        print(f"  Human timestamp: {test_event.get('timestamp_human')}")
        
        # Verify required fields
        required_fields = ['timestamp_iso', 'timestamp_human']
        missing_fields = [field for field in required_fields if field not in test_event]
        
        if missing_fields:
            print(f"ERROR: Missing timestamp fields: {missing_fields}")
            return False
        
        # Verify ISO format matches original
        if test_event.get('timestamp_iso') != test_event.get('timestamp'):
            print(f"ERROR: ISO timestamp doesn't match original!")
            return False
        
        # Verify human format is different from ISO
        if test_event.get('timestamp_human') == test_event.get('timestamp_iso'):
            print(f"ERROR: Human timestamp is same as ISO timestamp!")
            return False
        
        print("SUCCESS: All timestamp formats are correct!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Make sure the Flask app is running first: python app.py")
    print("Press Enter to continue with the integration test...")
    input()
    
    success = test_webhook_events_integration()
    
    if success:
        print("\n✅ Integration test PASSED!")
    else:
        print("\n❌ Integration test FAILED!")

#!/usr/bin/env python3
"""
Test script to verify timestamp formatting utilities work correctly.
"""

import json
import requests
from datetime import datetime
from utils import format_timestamp

def test_format_timestamp():
    """Test the format_timestamp function with various inputs."""
    print("Testing format_timestamp function:")
    print("=" * 50)
    
    test_cases = [
        "2021-04-01T21:30:00",
        "2023-12-25T14:15:30Z",
        "2024-01-01T00:00:00.123456",
        "2024-07-04T12:34:56+00:00",
        "2024-11-22T09:45:30.987654Z"
    ]
    
    for iso_timestamp in test_cases:
        formatted = format_timestamp(iso_timestamp)
        print(f"Input:  {iso_timestamp}")
        print(f"Output: {formatted}")
        print("-" * 30)

def test_events_endpoint_with_timestamps():
    """Test the /events endpoint to verify it returns both timestamp formats."""
    print("\nTesting /events endpoint timestamp formatting:")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/events")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"Number of events: {len(events)}")
            
            if events:
                # Show the first event with both timestamp formats
                event = events[0]
                print(f"\nFirst event details:")
                print(f"Action: {event.get('action', 'N/A')}")
                print(f"Author: {event.get('author', 'N/A')}")
                print(f"Original timestamp: {event.get('timestamp', 'N/A')}")
                print(f"ISO timestamp: {event.get('timestamp_iso', 'N/A')}")
                print(f"Human timestamp: {event.get('timestamp_human', 'N/A')}")
                
                # Verify both timestamp fields are present
                required_fields = ['timestamp_iso', 'timestamp_human']
                missing_fields = [field for field in required_fields if field not in event]
                
                if missing_fields:
                    print(f"WARNING: Missing timestamp fields: {missing_fields}")
                else:
                    print("SUCCESS: Both timestamp formats are present!")
            else:
                print("No events found. You may need to send some webhook events first.")
        else:
            print(f"Error response: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to events endpoint. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_current_timestamp():
    """Test formatting the current timestamp."""
    print(f"\nTesting current timestamp formatting:")
    print("=" * 50)
    
    current_iso = datetime.utcnow().isoformat()
    current_formatted = format_timestamp(current_iso)
    
    print(f"Current UTC (ISO): {current_iso}")
    print(f"Current formatted: {current_formatted}")

if __name__ == "__main__":
    print("Timestamp Utilities Testing Script")
    print("=" * 50)
    
    test_format_timestamp()
    test_current_timestamp()
    test_events_endpoint_with_timestamps()
    
    print("\nTesting complete!")

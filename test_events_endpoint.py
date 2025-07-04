#!/usr/bin/env python3
"""
Pytest file for testing the /events endpoint.
Tests JSON schema validation and formatted timestamp presence.
"""

import pytest
import json
from datetime import datetime
from dateutil import parser
from app import app, init_mongodb, events as events_collection
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_events():
    """Sample events data for testing."""
    return [
        {
            "request_id": "test123",
            "author": "test_user",
            "action": "PUSH",
            "from_branch": "main",
            "to_branch": "main",
            "timestamp": "2024-01-15T10:30:00.000Z"
        },
        {
            "request_id": "test456",
            "author": "test_user2",
            "action": "PULL_REQUEST",
            "from_branch": "feature-branch",
            "to_branch": "main",
            "timestamp": "2024-01-15T11:45:00.000Z"
        },
        {
            "request_id": "test789",
            "author": "test_user3",
            "action": "MERGE",
            "from_branch": "bugfix-branch",
            "to_branch": "main",
            "timestamp": "2024-01-15T12:15:00.000Z"
        }
    ]

@pytest.fixture
def setup_test_db(sample_events):
    """Set up test database with sample events."""
    # Skip if MongoDB is not available
    try:
        client = MongoClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=1000,
            connectTimeoutMS=1000
        )
        client.admin.command('ping')
        db = client["github_webhooks_test"]
        events = db["events"]
        
        # Clear any existing test data
        events.delete_many({})
        
        # Insert sample events
        events.insert_many(sample_events)
        
        # Temporarily point the app to use test database
        original_events = events_collection
        app.config['events_collection'] = events
        
        yield events
        
        # Cleanup
        events.delete_many({})
        client.close()
        
    except (ServerSelectionTimeoutError, ConnectionFailure):
        pytest.skip("MongoDB not available for testing")

def validate_event_schema(event):
    """Validate that an event has the expected JSON schema."""
    required_fields = [
        'request_id', 'author', 'action', 'from_branch', 'to_branch', 'timestamp'
    ]
    
    # Check all required fields are present
    for field in required_fields:
        assert field in event, f"Missing required field: {field}"
    
    # Check field types
    assert isinstance(event['request_id'], str), "request_id should be a string"
    assert isinstance(event['author'], str), "author should be a string"
    assert isinstance(event['action'], str), "action should be a string"
    assert isinstance(event['from_branch'], str), "from_branch should be a string"
    assert isinstance(event['to_branch'], str), "to_branch should be a string"
    assert isinstance(event['timestamp'], str), "timestamp should be a string"
    
    # Check that action is one of the expected values
    valid_actions = ['PUSH', 'PULL_REQUEST', 'MERGE']
    assert event['action'] in valid_actions, f"action should be one of {valid_actions}"
    
    # Check that _id field is present and converted to string
    assert '_id' in event, "Missing _id field"
    assert isinstance(event['_id'], str), "_id should be converted to string"

def validate_timestamp_format(timestamp_str):
    """Validate that timestamp is in ISO format and parseable."""
    try:
        # Parse the timestamp
        dt = parser.parse(timestamp_str)
        # Check that it's a valid datetime
        assert isinstance(dt, datetime), "Timestamp should parse to a datetime object"
        # Check that it can be converted back to ISO format
        iso_str = dt.isoformat()
        assert iso_str is not None, "Timestamp should be convertible to ISO format"
        return True
    except Exception as e:
        pytest.fail(f"Invalid timestamp format: {timestamp_str}, error: {e}")

def validate_formatted_timestamp_presence(event):
    """Validate that formatted timestamp fields are present."""
    # Check for both timestamp formats
    assert 'timestamp_iso' in event, "Missing timestamp_iso field"
    assert 'timestamp_human' in event, "Missing timestamp_human field"
    
    # Validate that timestamp_iso is the original timestamp
    assert event['timestamp_iso'] == event['timestamp'], "timestamp_iso should match original timestamp"
    
    # Validate that timestamp_human is a formatted string
    assert isinstance(event['timestamp_human'], str), "timestamp_human should be a string"
    assert len(event['timestamp_human']) > 0, "timestamp_human should not be empty"
    
    # Check that timestamp_human has expected format (day + month + year + time + UTC)
    human_ts = event['timestamp_human']
    assert 'UTC' in human_ts, "timestamp_human should contain 'UTC'"
    assert any(month in human_ts for month in ['January', 'February', 'March', 'April', 'May', 'June', 
                                               'July', 'August', 'September', 'October', 'November', 'December']), \
        "timestamp_human should contain month name"

class TestEventsEndpoint:
    """Test class for /events endpoint."""
    
    def test_events_endpoint_without_mongodb(self, client):
        """Test /events endpoint when MongoDB is not available."""
        # This test assumes MongoDB is not available
        # If MongoDB is available, the test might need to be adjusted
        response = client.get('/events')
        # Should return either 503 (service unavailable) or 200 with empty list
        assert response.status_code in [200, 503]
    
    def test_events_endpoint_with_sample_data(self, client, sample_events):
        """Test /events endpoint with sample data."""
        # Skip if MongoDB is not available
        try:
            client_db = MongoClient(
                "mongodb://localhost:27017/",
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000
            )
            client_db.admin.command('ping')
            db = client_db["github_webhooks"]
            events = db["events"]
            
            # Clear existing data and insert sample data
            events.delete_many({})
            events.insert_many(sample_events)
            
            # Test the endpoint
            response = client.get('/events')
            assert response.status_code == 200
            
            # Parse JSON response
            data = json.loads(response.data)
            assert isinstance(data, list), "Response should be a list"
            assert len(data) == len(sample_events), f"Should return {len(sample_events)} events"
            
            # Validate each event
            for event in data:
                validate_event_schema(event)
                validate_timestamp_format(event['timestamp'])
                validate_formatted_timestamp_presence(event)
            
            # Cleanup
            events.delete_many({})
            client_db.close()
            
        except (ServerSelectionTimeoutError, ConnectionFailure):
            pytest.skip("MongoDB not available for testing")
    
    def test_events_endpoint_empty_database(self, client):
        """Test /events endpoint with empty database."""
        try:
            client_db = MongoClient(
                "mongodb://localhost:27017/",
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000
            )
            client_db.admin.command('ping')
            db = client_db["github_webhooks"]
            events = db["events"]
            
            # Clear all data
            events.delete_many({})
            
            # Test the endpoint
            response = client.get('/events')
            assert response.status_code == 200
            
            # Parse JSON response
            data = json.loads(response.data)
            assert isinstance(data, list), "Response should be a list"
            assert len(data) == 0, "Should return empty list when no events"
            
            client_db.close()
            
        except (ServerSelectionTimeoutError, ConnectionFailure):
            pytest.skip("MongoDB not available for testing")
    
    def test_events_endpoint_json_content_type(self, client):
        """Test that /events endpoint returns JSON content type."""
        response = client.get('/events')
        assert 'application/json' in response.content_type, "Response should have JSON content type"
    
    def test_events_schema_validation(self, sample_events):
        """Test individual event schema validation."""
        # Test valid event
        for event in sample_events:
            # Add _id field as it would be added by MongoDB
            event['_id'] = "test_id"
            validate_event_schema(event)
    
    def test_timestamp_format_validation(self, sample_events):
        """Test timestamp format validation."""
        for event in sample_events:
            validate_timestamp_format(event['timestamp'])
    
    def test_formatted_timestamp_validation(self, sample_events):
        """Test formatted timestamp validation."""
        for event in sample_events:
            # Simulate what the endpoint does
            event['_id'] = "test_id"
            event['timestamp_iso'] = event['timestamp']
            event['timestamp_human'] = "15th January 2024 - 10:30 AM UTC"  # Example format
            validate_formatted_timestamp_presence(event)

# Integration test that can be run independently
def test_events_endpoint_integration():
    """Integration test for /events endpoint."""
    import requests
    
    try:
        # Test against running Flask app
        response = requests.get('http://localhost:5000/events', timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # If there are events, validate them
        if data:
            for event in data:
                validate_event_schema(event)
                validate_timestamp_format(event['timestamp'])
                validate_formatted_timestamp_presence(event)
        
        print(f"Integration test passed - found {len(data)} events")
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Flask app not running on localhost:5000")
    except Exception as e:
        pytest.fail(f"Integration test failed: {e}")

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

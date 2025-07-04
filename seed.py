#!/usr/bin/env python3
"""
Standalone script to seed the database with sample events.
This script can be used independently of the Flask CLI command.
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def init_mongodb():
    """Initialize MongoDB connection with error handling."""
    try:
        client = MongoClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
        )
        # Test the connection
        client.admin.command('ping')
        db = client["github_webhooks"]
        events = db["events"]
        logger.info("MongoDB connection established successfully")
        return client, events
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        return None, None

def seed_database():
    """Seed the database with sample events."""
    client, events = init_mongodb()
    
    if events is None:
        print("Error: MongoDB is not available. Cannot seed database.")
        return False
    
    # Sample events data
    sample_events = [
        {
            "request_id": "abc123def456",
            "author": "john_doe",
            "action": "PUSH",
            "from_branch": "main",
            "to_branch": "main",
            "timestamp": "2024-01-15T10:30:00.000Z"
        },
        {
            "request_id": "def456ghi789",
            "author": "jane_smith",
            "action": "PULL_REQUEST",
            "from_branch": "feature-auth",
            "to_branch": "main",
            "timestamp": "2024-01-15T11:45:00.000Z"
        },
        {
            "request_id": "ghi789jkl012",
            "author": "bob_wilson",
            "action": "MERGE",
            "from_branch": "bugfix-validation",
            "to_branch": "main",
            "timestamp": "2024-01-15T12:15:00.000Z"
        },
        {
            "request_id": "jkl012mno345",
            "author": "alice_johnson",
            "action": "PUSH",
            "from_branch": "develop",
            "to_branch": "develop",
            "timestamp": "2024-01-15T13:20:00.000Z"
        },
        {
            "request_id": "mno345pqr678",
            "author": "charlie_brown",
            "action": "PULL_REQUEST",
            "from_branch": "feature-api",
            "to_branch": "develop",
            "timestamp": "2024-01-15T14:30:00.000Z"
        },
        {
            "request_id": "pqr678stu901",
            "author": "diana_prince",
            "action": "MERGE",
            "from_branch": "hotfix-security",
            "to_branch": "main",
            "timestamp": "2024-01-15T15:10:00.000Z"
        },
        {
            "request_id": "stu901vwx234",
            "author": "steve_rogers",
            "action": "PUSH",
            "from_branch": "feature-testing",
            "to_branch": "feature-testing",
            "timestamp": "2024-01-15T16:25:00.000Z"
        }
    ]
    
    try:
        # Clear existing events (optional - remove if you want to keep existing data)
        events.delete_many({})
        print("Cleared existing events.")
        
        # Insert sample events
        result = events.insert_many(sample_events)
        print(f"Successfully inserted {len(result.inserted_ids)} sample events.")
        
        # Display inserted events
        print("\nInserted events:")
        for i, event in enumerate(sample_events, 1):
            print(f"{i}. {event['action']} by {event['author']} from {event['from_branch']} to {event['to_branch']}")
            
        return True
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        logger.error(f"Failed to seed database: {e}")
        return False
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    print("Database Seeding Script")
    print("=" * 50)
    print("This script will insert sample events into the MongoDB database.")
    print("Make sure MongoDB is running on localhost:27017")
    print("=" * 50)
    
    success = seed_database()
    
    if success:
        print("\nSeeding completed successfully!")
        print("You can now test the /events endpoint to see the sample data.")
    else:
        print("\nSeeding failed. Please check the error messages above.")
        sys.exit(1)

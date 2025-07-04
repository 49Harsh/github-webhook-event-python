from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, DuplicateKeyError, BulkWriteError
from datetime import datetime
import logging
import os
import sys
from functools import wraps
from utils import format_timestamp

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if app.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('webhook.log')
    ]
)
logger = logging.getLogger(__name__)

# MongoDB setup with error handling
client = None
db = None
events = None

def init_mongodb():
    """Initialize MongoDB connection with error handling."""
    global client, db, events
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
        return True
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Application will continue without database functionality")
        return False
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        return False

# Initialize MongoDB on startup
mongo_available = init_mongodb()

# Validation functions
def validate_event_type(event_type):
    """Validate event type is supported."""
    supported_events = ['push', 'pull_request']
    if not event_type or event_type not in supported_events:
        return False
    return True

def validate_push_payload(data):
    """Validate push event payload has required fields."""
    required_fields = ['after', 'ref', 'pusher']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field for push event: {field}")
    
    # Validate pusher has name
    if not isinstance(data['pusher'], dict) or 'name' not in data['pusher']:
        raise ValueError("pusher.name is required for push events")
    
    return True

def validate_pull_request_payload(data):
    """Validate pull request event payload has required fields."""
    required_fields = ['action', 'pull_request']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field for pull_request event: {field}")
    
    pr = data['pull_request']
    required_pr_fields = ['id', 'user', 'head', 'base']
    for field in required_pr_fields:
        if field not in pr:
            raise ValueError(f"Missing required field in pull_request: {field}")
    
    # Validate nested fields
    if not isinstance(pr['user'], dict) or 'login' not in pr['user']:
        raise ValueError("pull_request.user.login is required")
    
    if not isinstance(pr['head'], dict) or 'ref' not in pr['head']:
        raise ValueError("pull_request.head.ref is required")
    
    if not isinstance(pr['base'], dict) or 'ref' not in pr['base']:
        raise ValueError("pull_request.base.ref is required")
    
    return True

# Payload creation helper functions
def create_push_payload(data):
    """Create payload for push events."""
    validate_push_payload(data)
    
    return {
        "request_id": data.get("after"),
        "author": data.get("pusher", {}).get("name", "unknown"),
        "action": "PUSH",
        "from_branch": data.get("ref", "").split("/")[-1],
        "to_branch": data.get("ref", "").split("/")[-1],
        "timestamp": datetime.utcnow().isoformat()
    }

def create_pull_request_opened_payload(data):
    """Create payload for pull request opened events."""
    validate_pull_request_payload(data)
    
    return {
        "request_id": str(data["pull_request"]["id"]),
        "author": data["pull_request"]["user"]["login"],
        "action": "PULL_REQUEST",
        "from_branch": data["pull_request"]["head"]["ref"],
        "to_branch": data["pull_request"]["base"]["ref"],
        "timestamp": datetime.utcnow().isoformat()
    }

def create_pull_request_merged_payload(data):
    """Create payload for pull request merged events."""
    validate_pull_request_payload(data)
    
    return {
        "request_id": str(data["pull_request"]["id"]),
        "author": data["pull_request"]["user"]["login"],
        "action": "MERGE",
        "from_branch": data["pull_request"]["head"]["ref"],
        "to_branch": data["pull_request"]["base"]["ref"],
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handling decorator
def handle_errors(f):
    """Decorator to handle exceptions and return proper JSON responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            logger.error(f"Missing required field in request: {e}")
            return jsonify({"error": f"Missing required field: {str(e)}"}), 400
        except ValueError as e:
            logger.error(f"Invalid data in request: {e}")
            return jsonify({"error": f"Invalid data: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function

# Helper function to check MongoDB availability
def check_mongodb():
    """Check if MongoDB is available and reconnect if needed."""
    global mongo_available
    if not mongo_available:
        logger.info("Attempting to reconnect to MongoDB...")
        mongo_available = init_mongodb()
    return mongo_available

@app.route('/webhook', methods=['POST'])
@handle_errors
def webhook():
    # Log incoming webhook with headers and minimal payload info
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    user_agent = request.headers.get('User-Agent', 'unknown')
    content_type = request.headers.get('Content-Type', 'unknown')
    
    logger.info(f"Incoming webhook - Event: {event_type}, User-Agent: {user_agent}, Content-Type: {content_type}")
    
    # Validate request has JSON data
    if not request.is_json:
        logger.warning("Webhook received non-JSON payload")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.json
    if not data:
        logger.warning("Webhook received empty payload")
        return jsonify({"error": "Empty payload"}), 400
    
    # Validate event type
    if not validate_event_type(event_type):
        logger.warning(f"Unsupported event type: {event_type}")
        return jsonify({"error": f"Unsupported event type: {event_type}"}), 400
    
    # Log minimal payload info for traceability
    if event_type == "push":
        logger.info(f"Push event - Ref: {data.get('ref', 'unknown')}, Pusher: {data.get('pusher', {}).get('name', 'unknown')}")
    elif event_type == "pull_request":
        pr_action = data.get('action', 'unknown')
        pr_number = data.get('pull_request', {}).get('number', 'unknown')
        logger.info(f"Pull request event - Action: {pr_action}, PR: #{pr_number}")
    
    payload = None

    try:
        if event_type == "push":
            payload = create_push_payload(data)
        elif event_type == "pull_request":
            action = data.get("action", "").upper()
            if action == "OPENED":
                payload = create_pull_request_opened_payload(data)
            elif action == "CLOSED" and data.get("pull_request", {}).get("merged"):
                payload = create_pull_request_merged_payload(data)
    except ValueError as e:
        logger.error(f"Payload validation failed: {e}")
        return jsonify({"error": str(e)}), 400
    
    if payload:
        # Check MongoDB availability before attempting to insert
        if not check_mongodb():
            logger.error("MongoDB unavailable - webhook data not stored")
            return jsonify({"error": "Database unavailable"}), 503
        
        try:
            events.insert_one(payload)
            logger.info(f"Successfully stored {payload['action']} event for {payload['author']}")
            return jsonify({"status": "ok"}), 200
        except (DuplicateKeyError, BulkWriteError) as e:
            logger.error(f"MongoDB write error: {e}")
            return jsonify({"error": "Failed to store webhook data - duplicate or bulk write error"}), 500
        except Exception as e:
            logger.error(f"Failed to insert event into database: {e}")
            return jsonify({"error": "Failed to store webhook data"}), 500
    
    logger.info(f"Webhook ignored - unsupported event type or action: {event_type}")
    return jsonify({"status": "ignored"}), 200

@app.route('/events')
@handle_errors
def get_events():
    # Check MongoDB availability
    if not check_mongodb():
        logger.error("MongoDB unavailable - cannot retrieve events")
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        result = []
        for event in events.find().sort("timestamp", -1):
            event["_id"] = str(event["_id"])
            
            # Add both timestamp formats for UI flexibility
            if "timestamp" in event:
                event["timestamp_iso"] = event["timestamp"]
                event["timestamp_human"] = format_timestamp(event["timestamp"])
            
            result.append(event)
        logger.info(f"Retrieved {len(result)} events")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        return jsonify({"error": "Failed to retrieve events"}), 500

@app.route('/')
@handle_errors
def index():
    return render_template('index.html')

# Flask CLI commands
@app.cli.command()
def seed_db():
    """Seed the database with sample events."""
    if not check_mongodb():
        print("Error: MongoDB is not available. Cannot seed database.")
        return
    
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
            
    except Exception as e:
        print(f"Error seeding database: {e}")
        logger.error(f"Failed to seed database: {e}")

if __name__ == '__main__':
    # Set debug mode based on environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Update logging level based on debug mode
    if debug_mode:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Running in DEBUG mode")
    else:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Running in PRODUCTION mode")
    
    # Log startup information
    logger.info(f"MongoDB connection status: {'Available' if mongo_available else 'Unavailable'}")
    logger.info(f"Starting Flask application on port 5000")
    
    app.run(port=5000, debug=debug_mode)

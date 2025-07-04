# GitHub Webhook Assignment: End-to-End Setup

## 🔥 **NEW: Hardened & Production-Ready Features**

### ✅ **Completed Hardening (Step 2)**
- **🔒 MongoDB Connection**: Wrapped in try/except with graceful fallback
- **📝 Comprehensive Logging**: INFO by default, DEBUG in dev mode
- **🛡️ Error Handling**: JSON responses with proper HTTP status codes
- **🔍 Request Tracing**: Logs headers and minimal payload for debugging

### 🚀 **Enhanced Features**
- Application continues running even if MongoDB is down
- Automatic reconnection attempts
- Detailed logging to both console and `webhook.log`
- Consistent error responses: `{"error": "message"}`
- Request validation and payload verification

## 1. Prerequisites

- Python 3.x
- MongoDB (local instance running on default port 27017) - **OPTIONAL NOW**
- GitHub account

## 2. Setup `webhook-repo`

### Initial Installation
```bash
cd webhook-repo
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

### MongoDB Setup (Optional)
- Start MongoDB if available: `mongod`
- App will work without MongoDB (with logging warnings)
- Database operations will return 503 errors gracefully

### Database Seeding
After MongoDB is running, seed the database with sample data:
```bash
# Using Flask CLI command
flask seed-db

# Or using the standalone script
python seed.py
```

### Running Tests
Run the comprehensive test suite to verify everything works:
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test files
pytest test_webhook.py
pytest test_events_endpoint.py
pytest test_validation.py
pytest test_timestamp_utils.py

# Run integration tests
pytest test_integration.py
```

## 3. Run the Flask App

### Development Mode (DEBUG logging)
```bash
python app.py
```

### Production Mode (INFO logging)
```bash
export FLASK_DEBUG=false  # Linux/Mac
set FLASK_DEBUG=false     # Windows
python app.py
```

The app will be available at http://localhost:5000

## 4. Setup `action-repo`

- Create a new repository on GitHub (e.g., `action-repo`).
- Make some commits, open pull requests, and merge PRs to generate webhook events.

## 5. Configure GitHub Webhook

### For Local Development with ngrok
1. **Install ngrok** (if not already installed):
   ```bash
   # Download from https://ngrok.com/download
   # Or install via package manager:
   
   # Windows (using chocolatey)
   choco install ngrok
   
   # macOS (using homebrew)
   brew install ngrok
   
   # Linux (using snap)
   snap install ngrok
   ```

2. **Start your Flask app** (in one terminal):
   ```bash
   python app.py
   ```

3. **Create public tunnel** (in another terminal):
   ```bash
   ngrok http 5000
   ```
   
   This will output something like:
   ```
   Forwarding    https://abc123.ngrok.io -> http://localhost:5000
   ```

4. **Configure GitHub webhook** with the ngrok URL:
   - Go to your `action-repo` on GitHub
   - Settings > Webhooks > Add webhook
     - **Payload URL:** `https://abc123.ngrok.io/webhook` (use your actual ngrok URL)
     - **Content type:** `application/json`
     - **Events:** Select "Just the push event" and "Pull requests"
     - Save

### For Production/Server Deployment
- Use your server's public IP or domain:
  - **Payload URL:** `http://<your-server-ip>:5000/webhook`
  - **Content type:** `application/json`
  - **Events:** Select "Just the push event" and "Pull requests"
  - Save

## 6. View Events

- Open http://localhost:5000 in your browser.
- The UI will update every 15 seconds with new events from MongoDB.
- If MongoDB is unavailable, endpoints will return appropriate error messages.

## 7. 📊 **Monitoring & Logging**

### View Live Logs
```bash
tail -f webhook.log        # Linux/Mac
Get-Content webhook.log -Wait  # Windows PowerShell
```

### Log Levels
- **DEBUG**: Development mode - detailed request/response info
- **INFO**: Production mode - important events only
- **ERROR**: Database issues, validation failures
- **WARNING**: Non-critical issues (missing MongoDB, ignored events)

### What Gets Logged
- 🔍 Incoming webhook requests (headers + minimal payload)
- 💾 Database operations (success/failure)
- 🔌 MongoDB connection status
- ⚠️ Error conditions and exceptions
- 🚀 Application startup/shutdown

---

## MongoDB Schema

```
{
  _id: ObjectId,
  request_id: string, // Git commit hash or PR ID
  author: string,     // GitHub user name
  action: string,     // Enum: "PUSH", "PULL_REQUEST", "MERGE"
  from_branch: string,
  to_branch: string,
  timestamp: string   // UTC ISO format
}
```

---

## 🔧 **API Endpoints & Error Handling**

### `POST /webhook`
- **200 OK**: Event processed successfully
- **200 OK**: Event ignored (unsupported type)
- **400 Bad Request**: Invalid JSON or missing fields
- **500 Internal Server Error**: Processing error
- **503 Service Unavailable**: Database unavailable

### `GET /events`
- **200 OK**: Events retrieved successfully
- **500 Internal Server Error**: Database query error
- **503 Service Unavailable**: Database unavailable

## 🛑️ **Enhanced Error Handling Behavior**

### 🔄 **Automatic Recovery Features**
- **MongoDB Auto-Reconnect**: Automatically attempts to reconnect to MongoDB when connection is lost
- **Graceful Degradation**: Application continues running even when MongoDB is unavailable
- **Request Retry Logic**: Built-in validation and error recovery for webhook processing

### 📝 **Comprehensive Error Logging**
- **Structured Logging**: All errors logged with timestamps, severity levels, and context
- **Request Tracing**: Each webhook request gets detailed logging including headers and payload info
- **Error Categorization**: Different log levels (DEBUG, INFO, WARNING, ERROR) for different scenarios
- **Persistent Logs**: All errors saved to `webhook.log` for post-mortem analysis

### 🔍 **Validation & Error Detection**
- **Payload Validation**: Comprehensive validation of GitHub webhook payloads
- **Content-Type Checking**: Ensures requests contain valid JSON data
- **Required Field Validation**: Checks for all required fields in push and pull request events
- **Data Type Validation**: Ensures nested objects and arrays are properly structured

### 🚑 **Response & Status Codes**
- **Consistent JSON Responses**: All errors return standardized `{"error": "message"}` format
- **Proper HTTP Status Codes**: 
  - `200 OK`: Successful processing or ignored events
  - `400 Bad Request`: Invalid JSON, missing fields, or malformed data
  - `500 Internal Server Error**: Unexpected application errors
  - `503 Service Unavailable**: Database connectivity issues
- **Detailed Error Messages**: Specific error descriptions to help with debugging

### 🔧 **Error Recovery Strategies**
- **Database Fallback**: App functions without MongoDB, logging warnings instead of failing
- **Exception Wrapping**: All routes protected with `@handle_errors` decorator
- **Timeout Handling**: Connection timeouts handled gracefully with appropriate error messages
- **Duplicate Handling**: Prevents duplicate webhook processing with proper error responses

### 🧪 **Testing Error Handling**
Verify error handling behavior with these test scenarios:

```bash
# Test all error handling scenarios
pytest test_validation.py -v

# Test endpoints with database issues
pytest test_events_endpoint.py -v

# Test webhook processing errors
pytest test_webhook.py -v

# Test integration scenarios
pytest test_integration.py -v
```

**Manual Error Testing:**
1. **Database Unavailable**: Stop MongoDB and test endpoints
2. **Invalid JSON**: Send malformed JSON to `/webhook`
3. **Missing Fields**: Send incomplete webhook payloads
4. **Wrong Content-Type**: Send non-JSON requests

## Notes

- For public webhook delivery, use [ngrok](https://ngrok.com/) to tunnel your local Flask server.
- The UI is plain HTML/JS for simplicity.
- You can extend the schema or UI as needed.
- **New**: Application logs detailed information to `webhook.log`
- **New**: MongoDB connection is optional - app works without it
- **New**: Comprehensive error handling with proper HTTP status codes

# GitHub Webhook Receiver

This project implements a GitHub webhook receiver that listens for repository events (Push, Pull Request, Merge) and stores them in MongoDB. The UI displays these events in real-time by polling the database every 15 seconds.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure MongoDB is running on localhost:27017
4. Run the application:
   ```
   python app.py
   ```

## GitHub Webhook Setup

To set up a GitHub webhook to send events to this application:

1. Create a new repository on GitHub (the "action-repo")
2. Go to the repository Settings > Webhooks > Add webhook
3. Set the Payload URL to your webhook endpoint (e.g., `http://your-server:5000/webhook`)
4. Set Content type to `application/json`
5. Select individual events: Push, Pull requests
6. Click "Add webhook"

For local testing, you can use a tool like [ngrok](https://ngrok.com/) to expose your local server:
```
ngrok http 5000
```

Then use the ngrok URL as your webhook endpoint.

## Testing

To test the application without actual GitHub events:

1. Seed the database with sample events:
   ```
   python seed.py
   ```
2. Visit `http://localhost:5000/` to view the events

## Troubleshooting

If you're not seeing events from GitHub:

1. Check MongoDB connection - make sure MongoDB is running
2. Check webhook logs in GitHub repository settings
3. Check `webhook.log` for any errors in event processing
4. Ensure case sensitivity is handled properly for event types and actions
   - GitHub sends lowercase event types: `push`, `pull_request`
   - GitHub sends lowercase actions: `opened`, `closed`

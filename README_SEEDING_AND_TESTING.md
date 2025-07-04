# Database Seeding and Testing

This document explains how to use the database seeding functionality and automated testing for the webhook application.

## Database Seeding

There are two ways to seed the database with sample events:

### Method 1: Flask CLI Command

Use the Flask CLI command to seed the database:

```bash
# Make sure MongoDB is running and the Flask app environment is set up
export FLASK_APP=app.py

# Run the seeding command
flask seed-db
```

This will:
- Clear existing events in the database
- Insert 5 sample events with different actions (PUSH, PULL_REQUEST, MERGE)
- Display a summary of inserted events

### Method 2: Standalone Script

Run the standalone seeding script:

```bash
python seed.py
```

This script:
- Works independently of the Flask app
- Inserts 7 sample events (more variety than the CLI command)
- Provides detailed logging and error handling
- Can be easily customized for different data sets

## Sample Data

The seeding process inserts events with the following structure:

```json
{
    "request_id": "abc123def456",
    "author": "john_doe",
    "action": "PUSH",
    "from_branch": "main",
    "to_branch": "main",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

Actions included in sample data:
- **PUSH**: Direct pushes to branches
- **PULL_REQUEST**: Pull request creation events
- **MERGE**: Pull request merge events

## Testing

### Automated Tests with Pytest

Run the comprehensive test suite:

```bash
# Install test dependencies first
pip install pytest pytest-flask

# Run all tests
pytest test_events_endpoint.py -v

# Run specific test classes
pytest test_events_endpoint.py::TestEventsEndpoint -v

# Run integration test only
pytest test_events_endpoint.py::test_events_endpoint_integration -v
```

### Test Coverage

The test suite covers:

1. **JSON Schema Validation**:
   - Validates all required fields are present
   - Checks correct data types for each field
   - Verifies action values are valid
   - Ensures _id field is converted to string

2. **Timestamp Format Validation**:
   - Validates ISO 8601 timestamp format
   - Ensures timestamps are parseable
   - Checks timestamp conversion capabilities

3. **Formatted Timestamp Presence**:
   - Validates presence of `timestamp_iso` and `timestamp_human` fields
   - Checks that `timestamp_human` contains expected format elements
   - Ensures human-readable timestamps include month names and "UTC"

4. **Endpoint Behavior**:
   - Tests response with sample data
   - Tests response with empty database
   - Tests response when MongoDB is unavailable
   - Validates JSON content type
   - Integration testing against running Flask app

### Test Database

Tests use a separate test database (`github_webhooks_test`) to avoid interfering with development data. The tests automatically:
- Create temporary test data
- Clean up after completion
- Skip tests if MongoDB is not available

## Usage Examples

### Complete Workflow

1. **Start MongoDB**:
   ```bash
   # Start MongoDB service (varies by OS)
   sudo systemctl start mongod  # Linux
   brew services start mongodb  # macOS
   ```

2. **Seed the Database**:
   ```bash
   python seed.py
   ```

3. **Start the Flask Application**:
   ```bash
   python app.py
   ```

4. **Test the /events Endpoint**:
   ```bash
   curl http://localhost:5000/events
   ```

5. **Run Automated Tests**:
   ```bash
   pytest test_events_endpoint.py -v
   ```

### Expected Output

After seeding, the `/events` endpoint should return JSON like:

```json
[
    {
        "_id": "65a5f...",
        "request_id": "abc123def456",
        "author": "john_doe",
        "action": "PUSH",
        "from_branch": "main",
        "to_branch": "main",
        "timestamp": "2024-01-15T10:30:00.000Z",
        "timestamp_iso": "2024-01-15T10:30:00.000Z",
        "timestamp_human": "15th January 2024 - 10:30 AM UTC"
    },
    ...
]
```

## Error Handling

### MongoDB Not Available
- Seeding scripts will display clear error messages
- Tests will be skipped with appropriate messages
- Flask app will continue running with degraded functionality

### Invalid Data
- Tests validate schema compliance
- Seeding uses pre-validated sample data
- Application includes robust error handling

## Customization

### Adding More Sample Data

Edit `seed.py` to add more events to the `sample_events` list:

```python
sample_events.append({
    "request_id": "your_id",
    "author": "your_author",
    "action": "PUSH",  # or "PULL_REQUEST", "MERGE"
    "from_branch": "source_branch",
    "to_branch": "target_branch",
    "timestamp": "2024-01-15T10:30:00.000Z"
})
```

### Modifying Test Validation

Update the validation functions in `test_events_endpoint.py`:
- `validate_event_schema()`: Modify required fields or validation rules
- `validate_timestamp_format()`: Change timestamp format requirements
- `validate_formatted_timestamp_presence()`: Adjust human-readable format checks

## Troubleshooting

### Common Issues

1. **MongoDB Connection Errors**:
   - Ensure MongoDB is running: `sudo systemctl status mongod`
   - Check MongoDB logs: `sudo journalctl -u mongod`

2. **Test Failures**:
   - Verify MongoDB is accessible
   - Check that Flask app is not running during tests (port conflicts)
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

3. **Permission Errors**:
   - Make scripts executable: `chmod +x seed.py`
   - Check MongoDB permissions and data directory access

### Getting Help

- Check application logs: `tail -f webhook.log`
- Run tests with verbose output: `pytest test_events_endpoint.py -v -s`
- Verify MongoDB connection: `mongo --eval "db.adminCommand('ismaster')"`

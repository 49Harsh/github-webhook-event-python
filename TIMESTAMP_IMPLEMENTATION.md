# Timestamp Storage and Conversion Implementation

## Overview
This implementation standardizes timestamp storage and conversion utilities to provide both ISO 8601 and human-readable timestamp formats for better UI flexibility.

## Changes Made

### 1. Timestamp Storage (Already Implemented)
- **Continued storing `datetime.utcnow()` in ISO 8601 format** in MongoDB
- Located in `app.py` lines 111, 124, 137 in the payload creation functions
- Format: `datetime.utcnow().isoformat()` produces strings like `"2021-04-01T21:30:00"`

### 2. New Utility Module: `utils.py`
Created a new utility module with timestamp formatting functions:

#### `format_timestamp(dt_iso)`
- **Purpose**: Converts ISO 8601 timestamps to human-readable format
- **Input**: ISO 8601 timestamp string (e.g., `"2021-04-01T21:30:00"`)
- **Output**: Human-readable format (e.g., `"1st April 2021 - 9:30 PM UTC"`)
- **Features**:
  - Uses `dateutil.parser` for robust ISO string parsing
  - Handles timezone-aware and timezone-naive timestamps
  - Adds ordinal suffixes (1st, 2nd, 3rd, 4th, etc.) to day numbers
  - Always displays time in UTC
  - Graceful error handling - returns original timestamp if formatting fails

#### `get_ordinal_suffix(day)`
- **Purpose**: Helper function to get ordinal suffixes for day numbers
- **Input**: Day number (1-31)
- **Output**: Appropriate suffix ('st', 'nd', 'rd', 'th')

### 3. Enhanced `/events` API Endpoint
Updated the `/events` endpoint in `app.py` to return both timestamp formats:

#### Response Format
Each event now includes:
- `timestamp`: Original ISO 8601 timestamp (for backward compatibility)
- `timestamp_iso`: Same as `timestamp` (explicit ISO format)
- `timestamp_human`: Human-readable formatted timestamp

#### Example Response
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "request_id": "abc123def456",
  "author": "testuser",
  "action": "PUSH",
  "from_branch": "main",
  "to_branch": "main",
  "timestamp": "2021-04-01T21:30:00",
  "timestamp_iso": "2021-04-01T21:30:00",
  "timestamp_human": "1st April 2021 - 9:30 PM UTC"
}
```

## Dependencies Added
- `python-dateutil`: For robust ISO timestamp parsing
- `pytz`: For timezone handling and UTC conversion

## Testing
Created comprehensive tests to verify the implementation:

### `test_timestamp_utils.py`
- Tests the `format_timestamp` function with various input formats
- Tests current timestamp formatting
- Tests the `/events` endpoint for proper timestamp formatting

### `test_integration.py`
- Full integration test that sends a webhook and verifies the complete workflow
- Verifies both timestamp formats are present in the API response
- Validates timestamp format correctness

## Usage Examples

### For UI Developers
The `/events` API now provides flexibility for displaying timestamps:

```javascript
// Use ISO format for programmatic operations
const eventTime = event.timestamp_iso;
const dateObj = new Date(eventTime);

// Use human-readable format for user display
const displayTime = event.timestamp_human;
document.getElementById('event-time').textContent = displayTime;
```

### For Backend Developers
```python
from utils import format_timestamp

# Convert any ISO timestamp to human-readable format
iso_timestamp = "2024-07-04T12:34:56Z"
human_readable = format_timestamp(iso_timestamp)
# Result: "4th July 2024 - 12:34 PM UTC"
```

## Benefits
1. **UI Flexibility**: Frontend can choose between ISO and human-readable formats
2. **Backward Compatibility**: Original `timestamp` field preserved
3. **Consistent Formatting**: All human timestamps follow the same pattern
4. **Robust Parsing**: Handles various ISO 8601 formats
5. **UTC Standardization**: All times displayed in UTC for consistency
6. **Error Resilience**: Graceful fallback to original timestamp on formatting errors

## Future Enhancements
- Add support for different timezone displays based on user preferences
- Add localization support for different languages
- Add relative time formats (e.g., "2 hours ago")
- Add customizable date/time format templates

from datetime import datetime
from dateutil import parser
import pytz
import logging

logger = logging.getLogger(__name__)

def format_timestamp(dt_iso):
    """
    Convert ISO 8601 timestamp to human-readable format.
    
    Args:
        dt_iso (str): ISO 8601 timestamp string
        
    Returns:
        str: Human-readable timestamp in format "1st April 2021 - 9:30 PM UTC"
        
    Example:
        >>> format_timestamp("2021-04-01T21:30:00")
        "1st April 2021 - 9:30 PM UTC"
    """
    try:
        # Parse the ISO string using dateutil
        dt = parser.parse(dt_iso)
        
        # Ensure we're working with UTC
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = dt.replace(tzinfo=pytz.UTC)
        
        # Convert to UTC if it's not already
        dt_utc = dt.astimezone(pytz.UTC) if dt.tzinfo else dt.replace(tzinfo=pytz.UTC)
        
        # Format the date with ordinal suffix
        day = dt_utc.day
        suffix = get_ordinal_suffix(day)
        
        # Format the full timestamp
        month_year = dt_utc.strftime("%B %Y")
        formatted_time = dt_utc.strftime("%I:%M %p")
        
        return f"{day}{suffix} {month_year} - {formatted_time} UTC"
        
    except Exception as e:
        logger.error(f"Failed to format timestamp '{dt_iso}': {e}")
        return dt_iso  # Return original if formatting fails


def get_ordinal_suffix(day):
    """
    Get the ordinal suffix for a given day number.
    
    Args:
        day (int): Day of the month (1-31)
        
    Returns:
        str: Ordinal suffix ('st', 'nd', 'rd', 'th')
    """
    if 10 <= day % 100 <= 20:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

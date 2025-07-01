import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import dateutil.parser as date_parser

def extract_datetime_info(text: str) -> Dict[str, any]:
    """
    Extract date and time information from natural language text.
    
    Args:
        text: Input text containing date/time references
        
    Returns:
        Dictionary containing extracted datetime information
    """
    result = {
        'date': None,
        'time': None,
        'duration': None,
        'date_str': None,
        'time_str': None,
        'parsed_datetime': None
    }
    
    text_lower = text.lower()
    
    # Date patterns
    date_patterns = [
        # Relative dates
        (r'\btoday\b', lambda: datetime.now().date()),
        (r'\btomorrow\b', lambda: (datetime.now() + timedelta(days=1)).date()),
        (r'\byesterday\b', lambda: (datetime.now() - timedelta(days=1)).date()),
        (r'\bnext\s+week\b', lambda: (datetime.now() + timedelta(weeks=1)).date()),
        (r'\bnext\s+(\w+day)\b', _parse_next_weekday),
        (r'\bthis\s+(\w+day)\b', _parse_this_weekday),
        
        # Specific date formats
        (r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})\b', _parse_date_slash),
        (r'\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b', _parse_date_iso),
        (r'\b(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?\b', _parse_month_day),
        (r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\b', _parse_day_month),
    ]
    
    # Time patterns
    time_patterns = [
        r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b',
        r'\b(\d{1,2})\s*(am|pm)\b',
        r'\b(\d{1,2})\.(\d{2})\b',
        r'\bnoon\b',
        r'\bmidnight\b',
        r'\bmorning\b',
        r'\bafternoon\b',
        r'\bevening\b'
    ]
    
    # Duration patterns
    duration_patterns = [
        (r'(\d+)\s*hours?', lambda m: int(m.group(1)) * 60),
        (r'(\d+)\s*mins?|minutes?', lambda m: int(m.group(1))),
        (r'(\d+)\s*hrs?', lambda m: int(m.group(1)) * 60),
        (r'half\s*hour', lambda m: 30),
        (r'quarter\s*hour', lambda m: 15),
    ]
    
    # Extract date
    for pattern, parser in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if callable(parser):
                    result['date'] = parser() if not match.groups() else parser(match)
                else:
                    result['date'] = parser
                result['date_str'] = result['date'].strftime('%Y-%m-%d')
                break
            except:
                continue
    
    # Extract time
    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                time_str = match.group(0)
                if time_str in ['noon']:
                    result['time'] = '12:00'
                elif time_str in ['midnight']:
                    result['time'] = '00:00'
                elif time_str in ['morning']:
                    result['time'] = '09:00'
                elif time_str in ['afternoon']:
                    result['time'] = '14:00'
                elif time_str in ['evening']:
                    result['time'] = '18:00'
                else:
                    # Parse specific time
                    result['time'] = _parse_time_match(match)
                
                result['time_str'] = result['time']
                break
            except:
                continue
    
    # Extract duration
    for pattern, parser in duration_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                result['duration'] = parser(match)
                break
            except:
                continue
    
    # Create parsed datetime if we have both date and time
    if result['date'] and result['time']:
        try:
            time_parts = result['time'].split(':')
            hour, minute = int(time_parts[0]), int(time_parts[1])
            result['parsed_datetime'] = datetime.combine(result['date'], datetime.min.time().replace(hour=hour, minute=minute))
        except:
            pass
    
    return result

def _parse_next_weekday(match):
    """Parse 'next Monday', 'next Friday', etc."""
    weekday_name = match.group(1)
    weekday_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    target_weekday = weekday_map.get(weekday_name.lower())
    if target_weekday is None:
        return None
    
    today = datetime.now().date()
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    return today + timedelta(days=days_ahead)

def _parse_this_weekday(match):
    """Parse 'this Monday', 'this Friday', etc."""
    weekday_name = match.group(1)
    weekday_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    target_weekday = weekday_map.get(weekday_name.lower())
    if target_weekday is None:
        return None
    
    today = datetime.now().date()
    days_ahead = target_weekday - today.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    
    return today + timedelta(days=days_ahead)

def _parse_date_slash(match):
    """Parse MM/DD/YYYY or DD/MM/YYYY format"""
    try:
        month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        
        # Handle 2-digit years
        if year < 100:
            year += 2000 if year < 50 else 1900
        
        # Assume MM/DD/YYYY format (US standard)
        return datetime(year, month, day).date()
    except:
        return None

def _parse_date_iso(match):
    """Parse YYYY/MM/DD or YYYY-MM-DD format"""
    try:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return datetime(year, month, day).date()
    except:
        return None

def _parse_month_day(match):
    """Parse 'January 15th', 'March 3rd', etc."""
    try:
        month_name, day = match.group(1), int(match.group(2))
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month = month_map.get(month_name.lower())
        if month is None:
            return None
        
        year = datetime.now().year
        # If the date has passed this year, assume next year
        date_this_year = datetime(year, month, day).date()
        if date_this_year < datetime.now().date():
            year += 1
        
        return datetime(year, month, day).date()
    except:
        return None

def _parse_day_month(match):
    """Parse '15th January', '3rd March', etc."""
    try:
        day, month_name = int(match.group(1)), match.group(2)
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month = month_map.get(month_name.lower())
        if month is None:
            return None
        
        year = datetime.now().year
        # If the date has passed this year, assume next year
        date_this_year = datetime(year, month, day).date()
        if date_this_year < datetime.now().date():
            year += 1
        
        return datetime(year, month, day).date()
    except:
        return None

def _parse_time_match(match):
    """Parse time from regex match"""
    try:
        if match.group(0) in ['noon', 'midnight', 'morning', 'afternoon', 'evening']:
            return match.group(0)  # Handle in main function
        
        groups = match.groups()
        hour = int(groups[0])
        minute = int(groups[1]) if len(groups) > 1 and groups[1] else 0
        am_pm = groups[-1] if len(groups) > 2 else None
        
        # Handle AM/PM
        if am_pm:
            am_pm = am_pm.lower()
            if am_pm == 'pm' and hour != 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    except:
        return None

def format_response(response: str) -> str:
    """
    Format the agent response for better readability.
    
    Args:
        response: Raw response from the agent
        
    Returns:
        Formatted response string
    """
    # Add emojis for better visual appeal
    emoji_replacements = {
        'successfully booked': '✅ Successfully booked',
        'successfully cancelled': '✅ Successfully cancelled',
        'available': '📅 Available',
        'no availability': '❌ No availability',
        'upcoming appointments': '📅 Upcoming appointments',
        'error': '❌ Error',
        'failed': '❌ Failed',
        'conflict': '⚠️ Conflict'
    }
    
    formatted = response
    for pattern, replacement in emoji_replacements.items():
        formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
    
    return formatted

def validate_datetime_input(date_str: str, time_str: str) -> Tuple[bool, str]:
    """
    Validate date and time input strings.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        time_str: Time string in HH:MM format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Validate date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        if date_obj < datetime.now().date():
            return False, "Cannot book appointments in the past"
        
        # Validate time
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Check for reasonable business hours (optional validation)
        if time_obj.hour < 6 or time_obj.hour > 22:
            return False, "Please choose a time between 6:00 AM and 10:00 PM"
        
        return True, ""
        
    except ValueError as e:
        return False, f"Invalid date/time format: {str(e)}"

def get_time_slot_suggestions(existing_events: List[Dict], preferred_date: str, 
                            duration_minutes: int = 60) -> List[str]:
    """
    Generate time slot suggestions based on existing events.
    
    Args:
        existing_events: List of existing calendar events
        preferred_date: Date in YYYY-MM-DD format
        duration_minutes: Duration of appointment in minutes
        
    Returns:
        List of suggested time slots
    """
    suggestions = []
    business_start = 9  # 9 AM
    business_end = 17   # 5 PM
    
    try:
        date_obj = datetime.strptime(preferred_date, '%Y-%m-%d')
        
        # Generate hourly slots
        for hour in range(business_start, business_end):
            slot_start = date_obj.replace(hour=hour, minute=0, second=0)
            slot_end = slot_start + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with existing events
            has_conflict = False
            for event in existing_events:
                event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                
                # Remove timezone for comparison
                event_start = event_start.replace(tzinfo=None)
                event_end = event_end.replace(tzinfo=None)
                
                if (slot_start < event_end and slot_end > event_start):
                    has_conflict = True
                    break
            
            if not has_conflict:
                suggestions.append(f"{hour:02d}:00")
        
        return suggestions[:5]  # Return top 5 suggestions
        
    except Exception as e:
        return ["09:00", "10:00", "14:00", "15:00", "16:00"]  # Default suggestions

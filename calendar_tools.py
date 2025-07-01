import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.tools import tool
import pytz

class CalendarManager:
    """Manages Google Calendar operations"""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = credentials_path
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"⚠️ Google Calendar credentials file not found: {self.credentials_path}")
                print("📋 Calendar integration is disabled. See setup instructions in the app.")
                self.service = None
                return
            
            # Check if credentials file is a placeholder
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
                if creds_data.get('type') == 'service_account_placeholder':
                    print("⚠️ Google Calendar credentials are placeholder. Calendar integration disabled.")
                    self.service = None
                    return
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            print("✅ Google Calendar service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Calendar service: {str(e)}")
            print("📋 Calendar integration is disabled. Please check your credentials.")
            self.service = None
    
    def get_events(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get events from calendar within time range"""
        if not self.service:
            return []
        
        try:
            # Convert to UTC for API
            start_utc = start_time.astimezone(pytz.UTC).isoformat()
            end_utc = end_time.astimezone(pytz.UTC).isoformat()
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_utc,
                timeMax=end_utc,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            
            return formatted_events
            
        except HttpError as e:
            print(f"Calendar API error: {e}")
            return []
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def create_event(self, summary: str, start_time: datetime, end_time: datetime, 
                    description: str = "", location: str = "") -> Optional[Dict]:
        """Create a new calendar event"""
        if not self.service:
            return None
        
        try:
            # Convert to UTC for API
            start_utc = start_time.astimezone(pytz.UTC).isoformat()
            end_utc = end_time.astimezone(pytz.UTC).isoformat()
            
            event = {
                'summary': summary,
                'start': {'dateTime': start_utc, 'timeZone': 'UTC'},
                'end': {'dateTime': end_utc, 'timeZone': 'UTC'},
                'description': description,
                'location': location
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event
            ).execute()
            
            return {
                'id': created_event['id'],
                'summary': created_event['summary'],
                'start': created_event['start']['dateTime'],
                'end': created_event['end']['dateTime'],
                'htmlLink': created_event.get('htmlLink', '')
            }
            
        except HttpError as e:
            print(f"Calendar API error: {e}")
            return None
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        if not self.service:
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
            
        except HttpError as e:
            print(f"Calendar API error: {e}")
            return False
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False

# Initialize global calendar manager
calendar_manager = CalendarManager()

@tool
def check_availability(date_str: str, start_hour: int = 9, end_hour: int = 17) -> str:
    """
    Check calendar availability for a specific date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        start_hour: Start hour for availability check (default 9 AM)
        end_hour: End hour for availability check (default 5 PM)
    
    Returns:
        String describing availability with time slots
    """
    if not calendar_manager.service:
        return "❌ Google Calendar is not connected. Please set up your service account credentials to check real availability."
    
    try:
        # Parse the date
        date = datetime.strptime(date_str, "%Y-%m-%d")
        start_time = date.replace(hour=start_hour, minute=0, second=0)
        end_time = date.replace(hour=end_hour, minute=0, second=0)
        
        # Get existing events
        events = calendar_manager.get_events(start_time, end_time)
        
        if not events:
            return f"✅ {date_str} is completely free from {start_hour}:00 to {end_hour}:00"
        
        # Find available slots
        available_slots = []
        current_time = start_time
        
        for event in events:
            event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            event_start = event_start.replace(tzinfo=None)  # Remove timezone for comparison
            
            if current_time < event_start:
                available_slots.append(f"{current_time.strftime('%H:%M')}-{event_start.strftime('%H:%M')}")
            
            event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
            event_end = event_end.replace(tzinfo=None)
            current_time = max(current_time, event_end)
        
        # Check for time after last event
        if current_time < end_time:
            available_slots.append(f"{current_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}")
        
        if available_slots:
            return f"📅 Available slots on {date_str}: {', '.join(available_slots)}"
        else:
            return f"❌ No availability on {date_str} between {start_hour}:00-{end_hour}:00"
            
    except Exception as e:
        return f"Error checking availability: {str(e)}"

@tool
def book_appointment(summary: str, date_str: str, start_time_str: str, duration_minutes: int = 60, 
                    description: str = "", location: str = "") -> str:
    """
    Book a new appointment in the calendar.
    
    Args:
        summary: Title/summary of the appointment
        date_str: Date in YYYY-MM-DD format
        start_time_str: Start time in HH:MM format (24-hour)
        duration_minutes: Duration in minutes (default 60)
        description: Optional description
        location: Optional location
    
    Returns:
        String confirmation of booking or error message
    """
    if not calendar_manager.service:
        return "❌ Google Calendar is not connected. Please set up your service account credentials to book real appointments."
    
    try:
        # Parse date and time
        date_time_str = f"{date_str} {start_time_str}"
        start_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Check for conflicts
        existing_events = calendar_manager.get_events(start_datetime, end_datetime)
        if existing_events:
            conflicts = [f"'{event['summary']}' ({event['start']} - {event['end']})" for event in existing_events]
            return f"❌ Booking conflict detected with: {', '.join(conflicts)}"
        
        # Create the event
        created_event = calendar_manager.create_event(
            summary=summary,
            start_time=start_datetime,
            end_time=end_datetime,
            description=description,
            location=location
        )
        
        if created_event:
            return f"✅ Successfully booked '{summary}' on {date_str} from {start_time_str} to {end_datetime.strftime('%H:%M')}"
        else:
            return "❌ Failed to create appointment. Please check your calendar permissions."
            
    except ValueError as e:
        return f"❌ Invalid date/time format: {str(e)}"
    except Exception as e:
        return f"❌ Error booking appointment: {str(e)}"

@tool
def list_upcoming_appointments(days_ahead: int = 7) -> str:
    """
    List upcoming appointments for the next specified days.
    
    Args:
        days_ahead: Number of days to look ahead (default 7)
    
    Returns:
        String listing upcoming appointments
    """
    if not calendar_manager.service:
        return "❌ Google Calendar is not connected. Please set up your service account credentials to view real appointments."
    
    try:
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days_ahead)
        
        events = calendar_manager.get_events(start_time, end_time)
        
        if not events:
            return f"📅 No appointments scheduled for the next {days_ahead} days"
        
        appointments = []
        for event in events:
            start_dt = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            start_formatted = start_dt.strftime("%Y-%m-%d %H:%M")
            appointments.append(f"• {event['summary']} - {start_formatted}")
        
        return f"📅 Upcoming appointments ({len(events)} total):\n" + "\n".join(appointments)
        
    except Exception as e:
        return f"Error listing appointments: {str(e)}"

@tool
def cancel_appointment(appointment_summary: str, date_str: str) -> str:
    """
    Cancel an appointment by summary and date.
    
    Args:
        appointment_summary: Title/summary of the appointment to cancel
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        String confirmation of cancellation or error message
    """
    if not calendar_manager.service:
        return "❌ Google Calendar is not connected. Please set up your service account credentials to cancel real appointments."
    
    try:
        # Get events for the specified date
        date = datetime.strptime(date_str, "%Y-%m-%d")
        start_time = date.replace(hour=0, minute=0, second=0)
        end_time = date.replace(hour=23, minute=59, second=59)
        
        events = calendar_manager.get_events(start_time, end_time)
        
        # Find matching event
        matching_events = [
            event for event in events 
            if appointment_summary.lower() in event['summary'].lower()
        ]
        
        if not matching_events:
            return f"❌ No appointment found with summary '{appointment_summary}' on {date_str}"
        
        if len(matching_events) > 1:
            summaries = [event['summary'] for event in matching_events]
            return f"❌ Multiple appointments found: {', '.join(summaries)}. Please be more specific."
        
        # Cancel the event
        event_to_cancel = matching_events[0]
        success = calendar_manager.delete_event(event_to_cancel['id'])
        
        if success:
            return f"✅ Successfully cancelled '{event_to_cancel['summary']}' on {date_str}"
        else:
            return f"❌ Failed to cancel appointment. Please try again."
            
    except ValueError as e:
        return f"❌ Invalid date format: {str(e)}"
    except Exception as e:
        return f"❌ Error cancelling appointment: {str(e)}"

# Export all tools for agent use
calendar_tools = [
    check_availability,
    book_appointment,
    list_upcoming_appointments,
    cancel_appointment
]

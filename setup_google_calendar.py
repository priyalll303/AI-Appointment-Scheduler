#!/usr/bin/env python3
"""
Google Calendar Setup Helper for TailorTalk
This script helps you set up Google Calendar integration step by step.
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def check_credentials_file():
    """Check if credentials.json exists and is valid"""
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found")
        return False
    
    try:
        with open("credentials.json", 'r') as f:
            creds_data = json.load(f)
            
        if creds_data.get('type') == 'service_account_placeholder':
            print("⚠️ credentials.json contains placeholder data")
            return False
            
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Missing required fields in credentials.json: {missing_fields}")
            return False
            
        print("✅ credentials.json found and appears valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def test_calendar_connection():
    """Test the Google Calendar API connection"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json",
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Test by getting calendar list
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        print(f"✅ Successfully connected to Google Calendar API")
        print(f"📅 Found {len(calendars)} calendar(s):")
        
        for calendar in calendars:
            print(f"  • {calendar['summary']} ({calendar['id']})")
            
        return True, service, calendars
        
    except FileNotFoundError:
        print("❌ credentials.json file not found")
        return False, None, []
    except Exception as e:
        print(f"❌ Failed to connect to Google Calendar: {e}")
        return False, None, []

def test_calendar_permissions(service, calendar_id="primary"):
    """Test if we can read and write to the calendar"""
    try:
        # Test reading events
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"✅ Successfully read calendar events: {len(events)} events found")
        
        # Test creating a test event
        test_event = {
            'summary': 'TailorTalk Test Event (Safe to Delete)',
            'start': {
                'dateTime': (now + timedelta(hours=1)).isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (now + timedelta(hours=2)).isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'description': 'This is a test event created by TailorTalk setup. You can safely delete it.',
        }
        
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=test_event
        ).execute()
        
        print(f"✅ Successfully created test event: {created_event['summary']}")
        
        # Clean up - delete the test event
        service.events().delete(
            calendarId=calendar_id,
            eventId=created_event['id']
        ).execute()
        
        print("✅ Successfully deleted test event - calendar permissions working correctly")
        return True
        
    except HttpError as e:
        if e.resp.status == 403:
            print("❌ Permission denied - make sure you've shared your calendar with the service account")
            print(f"📧 Service account email from credentials: {get_service_account_email()}")
        else:
            print(f"❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing calendar permissions: {e}")
        return False

def get_service_account_email():
    """Get the service account email from credentials"""
    try:
        with open("credentials.json", 'r') as f:
            creds_data = json.load(f)
        return creds_data.get('client_email', 'Email not found')
    except:
        return 'Unable to read email from credentials'

def main():
    """Main setup function"""
    print("🚀 TailorTalk Google Calendar Setup")
    print("=" * 40)
    
    # Step 1: Check credentials file
    print("\n1. Checking credentials file...")
    if not check_credentials_file():
        print("\n📋 Next steps:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create or select a project")
        print("3. Enable Google Calendar API")
        print("4. Create service account credentials")
        print("5. Download JSON file and replace credentials.json")
        print("6. Run this script again")
        return
    
    # Step 2: Test API connection
    print("\n2. Testing Google Calendar API connection...")
    success, service, calendars = test_calendar_connection()
    
    if not success:
        print("\n📋 Troubleshooting:")
        print("• Check that Google Calendar API is enabled in your project")
        print("• Verify credentials.json contains valid service account data")
        print("• Make sure you downloaded the JSON file correctly")
        return
    
    # Step 3: Test permissions
    print("\n3. Testing calendar permissions...")
    service_email = get_service_account_email()
    print(f"📧 Service account email: {service_email}")
    
    if not test_calendar_permissions(service):
        print("\n📋 To fix permissions:")
        print("1. Open Google Calendar in your browser")
        print("2. Go to your calendar settings")
        print("3. Share calendar with your service account:")
        print(f"   Email: {service_email}")
        print("   Permission: 'Make changes to events'")
        print("4. Run this script again to test")
        return
    
    # Success!
    print("\n🎉 Setup Complete!")
    print("✅ Google Calendar integration is ready")
    print("✅ TailorTalk can now manage your real calendar")
    print("\n📱 You can now:")
    print("• Book real appointments")
    print("• Check actual availability")
    print("• Cancel existing events")
    print("• Get accurate scheduling suggestions")

if __name__ == "__main__":
    main()
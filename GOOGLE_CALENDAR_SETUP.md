# Google Calendar Integration Setup Guide

This guide will help you connect TailorTalk to your Google Calendar so you can book real appointments.

## Prerequisites

- Google account
- Access to Google Cloud Console
- Your Google Calendar that you want to integrate

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or select an existing project
3. Give your project a name (e.g., "TailorTalk Calendar")
4. Click "Create"

### 2. Enable Google Calendar API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 3. Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the details:
   - Service account name: `tailortalk-calendar`
   - Description: `Service account for TailorTalk calendar integration`
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Skip user access (click "Done")

### 4. Generate Service Account Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" format
6. Click "Create"
7. A JSON file will download - this is your credentials file

### 5. Update TailorTalk

1. Open the downloaded JSON file
2. Copy all its contents
3. Replace the contents of `credentials.json` in your TailorTalk project with the copied content

### 6. Share Calendar with Service Account

1. Open Google Calendar in your browser
2. Find the calendar you want to integrate (usually "My Calendar")
3. Click the three dots next to the calendar name
4. Select "Settings and sharing"
5. Scroll to "Share with specific people"
6. Click "Add people"
7. Enter the service account email (found in your credentials.json file, looks like: `your-service-account@your-project.iam.gserviceaccount.com`)
8. Set permission to "Make changes to events"
9. Click "Send"

### 7. Test the Integration

1. Restart your TailorTalk application
2. You should see "✅ Google Calendar Connected" in the sidebar
3. Try asking: "What appointments do I have this week?"
4. Try booking: "Schedule a test meeting tomorrow at 2 PM"

## Troubleshooting

### "Calendar Not Connected" Error

- Check that `credentials.json` contains valid JSON (not placeholder text)
- Verify the service account email is correctly shared with your calendar
- Ensure Google Calendar API is enabled in your project

### "Permission Denied" Error

- Make sure you shared your calendar with the service account email
- Check that the service account has "Make changes to events" permission

### "API Key Invalid" Error

- Regenerate the service account key
- Make sure you copied the entire JSON content correctly

## Environment Variables (Optional)

You can also set these environment variables:

- `GOOGLE_CALENDAR_ID`: Your specific calendar ID (defaults to "primary")

To find your calendar ID:
1. Go to Google Calendar settings
2. Select your calendar
3. Scroll to "Calendar ID" section
4. Copy the calendar ID

## Security Notes

- Keep your `credentials.json` file secure and never share it publicly
- The service account only has access to calendars you explicitly share with it
- You can revoke access anytime by removing the service account from your calendar sharing settings

## Need Help?

If you encounter issues:
1. Check the console logs for specific error messages
2. Verify each step was completed correctly
3. Try creating a new service account if problems persist

Once setup is complete, TailorTalk will be able to:
- View your real calendar availability
- Book actual appointments
- Cancel and reschedule existing events
- Provide accurate scheduling suggestions
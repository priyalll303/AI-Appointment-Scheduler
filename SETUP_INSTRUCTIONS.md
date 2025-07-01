# Google Calendar Setup for TailorTalk

Follow these steps to connect your Google Calendar to TailorTalk for real appointment scheduling.

## Step 1: Create Google Cloud Project

1. **Open Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown at the top
   - Click "NEW PROJECT"
   - Project name: `TailorTalk Calendar` (or any name you prefer)
   - Click "CREATE"
   - Wait for the project to be created, then select it

## Step 2: Enable Google Calendar API

1. **Navigate to API Library**
   - In the left menu, go to: **APIs & Services > Library**

2. **Find Calendar API**
   - Search for "Google Calendar API"
   - Click on "Google Calendar API" in the results

3. **Enable the API**
   - Click the blue "ENABLE" button
   - Wait for it to be enabled

## Step 3: Create Service Account

1. **Go to Credentials**
   - In the left menu: **APIs & Services > Credentials**

2. **Create Service Account**
   - Click "+ CREATE CREDENTIALS"
   - Select "Service account"

3. **Configure Service Account**
   - Service account name: `tailortalk-calendar`
   - Service account ID: (auto-filled, keep as is)
   - Description: `Service account for TailorTalk appointment scheduling`
   - Click "CREATE AND CONTINUE"

4. **Skip Role Assignment**
   - Click "CONTINUE" (no roles needed)
   - Click "DONE"

## Step 4: Generate Credentials File

1. **Find Your Service Account**
   - You should see your service account listed
   - Click on the service account email

2. **Create JSON Key**
   - Go to the "Keys" tab
   - Click "ADD KEY" > "Create new key"
   - Select "JSON" format
   - Click "CREATE"

3. **Download and Save**
   - A JSON file will download automatically
   - **IMPORTANT**: Copy ALL the contents of this file
   - Replace the contents of `credentials.json` in your TailorTalk project with this data

## Step 5: Share Your Calendar

This is the MOST IMPORTANT step - without this, TailorTalk cannot access your calendar.

1. **Get Service Account Email**
   - From the downloaded JSON file, find the `client_email` field
   - It looks like: `tailortalk-calendar@your-project.iam.gserviceaccount.com`
   - Copy this email address

2. **Open Google Calendar**
   - Go to: https://calendar.google.com/
   - Make sure you're signed in with the same Google account

3. **Share Your Calendar**
   - Find your main calendar (usually called "Your Name" or "Primary")
   - Click the three dots next to your calendar name
   - Select "Settings and sharing"

4. **Add Service Account**
   - Scroll to "Share with specific people"
   - Click "Add people"
   - Paste the service account email
   - Change permission to "Make changes to events"
   - Click "Send"

## Step 6: Test the Connection

1. **Run the Test Script**
   ```bash
   python setup_google_calendar.py
   ```

2. **Expected Output**
   - ✅ credentials.json found and appears valid
   - ✅ Successfully connected to Google Calendar API
   - ✅ Found X calendar(s)
   - ✅ Successfully read calendar events
   - ✅ Successfully created test event
   - ✅ Successfully deleted test event
   - 🎉 Setup Complete!

## Troubleshooting

### "Permission Denied" Error
- Make sure you shared your calendar with the service account email
- Check that permission is set to "Make changes to events"
- Wait a few minutes for permissions to propagate

### "API Not Enabled" Error
- Go back to APIs & Services > Library
- Search for "Google Calendar API" and make sure it's enabled

### "Invalid Credentials" Error
- Check that you copied the entire JSON content correctly
- Make sure there are no extra characters or formatting issues

### "Calendar Not Found" Error
- Make sure you're using the same Google account for both Cloud Console and Calendar
- Verify the service account email is correctly shared with your calendar

## Security Notes

- Keep your `credentials.json` file secure and never share it publicly
- The service account only has access to calendars you explicitly share with it
- You can revoke access anytime by removing the service account from your calendar sharing settings

## What Happens Next

Once setup is complete, TailorTalk will be able to:
- View your real calendar availability
- Book actual appointments in your Google Calendar
- Cancel and reschedule existing events
- Provide accurate scheduling suggestions based on your real schedule

Your appointments will appear in your Google Calendar app and sync across all your devices!
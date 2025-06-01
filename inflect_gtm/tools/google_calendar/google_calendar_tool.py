import os
import datetime
from typing import Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from inflect_gtm.components.tool.tool import Tool

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_upcoming_events(context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        creds = None
        token_path = os.path.join(os.path.dirname(__file__), 'token.json')
        cred_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)

        max_results = int(context.get("n", 5))
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            formatted_events.append({
                "summary": event.get('summary', '(No title)'),
                "start": start,
                "end": end
            })

        return {"events": formatted_events}

    except Exception as e:
        return {"error": str(e)}


class GoogleCalendarTool(Tool):
    def __init__(self):
        super().__init__(name="GoogleCalendar", function=self.get_upcoming_events)

    def get_upcoming_events(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return get_upcoming_events(context)
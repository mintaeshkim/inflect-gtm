import os
import datetime
from typing import Dict, Any
from googleapiclient.discovery import build
from inflect_gtm.components.tool.tool import Tool
from inflect_gtm.tools.utils.google_auth import authenticate


class GoogleCalendarTool(Tool):
    def __init__(self):
        super().__init__(name="GoogleCalendar", function=self.get_upcoming_events)
        self.creds = authenticate()
        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_upcoming_events(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            max_results = int(context.get("n", 5))
            now = datetime.datetime.utcnow().isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
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


if __name__ == "__main__":
    print("🚀 Testing Google Calendar Tool...")
    tool = GoogleCalendarTool()
    result = tool.run({"n": 3})

    if "error" in result.get("GoogleCalendar", {}):
        print("❌ Error:", result["GoogleCalendar"]["error"])
    else:
        events = result.get("GoogleCalendar", {}).get("events", [])
        if not events:
            print("⚠️ No upcoming events found.")
        else:
            print("✅ Upcoming Events:")
            for i, event in enumerate(events, 1):
                print(f"{i}. {event['summary']} ({event['start']} ~ {event['end']})")
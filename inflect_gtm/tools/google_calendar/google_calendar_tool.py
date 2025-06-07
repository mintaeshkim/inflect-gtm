import datetime
from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from inflect_gtm.components.tool.tool import Tool
from inflect_gtm.tools.utils.google_auth import authenticate


class GoogleCalendarTool(Tool):
    def __init__(self):
        super().__init__(name="GoogleCalendar", function=self.get_upcoming_events)
        self.creds = authenticate()
        self.service = build("calendar", "v3", credentials=self.creds)

    def get_upcoming_events(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            max_results = int(context.get("n", 5))
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])
            formatted_events = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                formatted_events.append({
                    "summary": event.get("summary", "(No title)"),
                    "start": start,
                    "end": end
                })

            return {"events": formatted_events}
        except Exception as e:
            return {"error": str(e)}

    def find_matching_event(self, parsed_meeting: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a calendar event that matches the parsed meeting log."""
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])

        for event in events:
            summary = event.get("summary", "").lower()
            participants = [att.get("email", "").lower() for att in event.get("attendees", [])]
            if parsed_meeting["summary"].lower() in summary:
                return event
            if any(p.lower() in participants for p in parsed_meeting.get("participants", [])):
                return event
        return None

    def add_event_from_meeting(self, parsed_meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Add new event to Google Calendar based on parsed meeting log."""
        event = {
            "summary": parsed_meeting.get("summary", "Follow-up Meeting"),
            "start": {
                "dateTime": parsed_meeting["start_time"],
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": parsed_meeting["end_time"],
                "timeZone": "UTC",
            },
            "attendees": [{"email": email} for email in parsed_meeting.get("participants", [])]
        }
        created_event = self.service.events().insert(calendarId="primary", body=event).execute()
        return created_event

    def get_participants_from_event(self, event: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract name and email of attendees."""
        attendees = event.get("attendees", [])
        return [{"email": a.get("email", ""), "displayName": a.get("displayName", "")} for a in attendees]


# Unit test
if __name__ == "__main__":
    print("🚀 Testing Google Calendar Tool...")
    tool = GoogleCalendarTool()
    result = tool.get_upcoming_events({"n": 3})
    print(result)
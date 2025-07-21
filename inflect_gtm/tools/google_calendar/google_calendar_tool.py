import json
import datetime
from dateutil import parser as dt_parser
from difflib import SequenceMatcher
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

    def resolve_event(self, parsed_meeting: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])

        parsed_start = self._try_parse_time(parsed_meeting.get("start_time"))
        parsed_summary = parsed_meeting.get("subject", "").lower()

        for event in events:
            event_start = self._try_parse_time(event["start"].get("dateTime", event["start"].get("date")))
            event_summary = event.get("summary", "").lower()
            summary_score = SequenceMatcher(None, parsed_summary, event_summary).ratio()

            if event_start and parsed_start and abs((event_start - parsed_start).total_seconds()) < 1800:
                if summary_score > 0.6:
                    calendar_participants = self.get_participants_from_event(event)
                    emails = [p["email"] for p in calendar_participants if p["email"]]
                    names = [p["displayName"] for p in calendar_participants if p["displayName"]]
                    return {
                        "found": True,
                        "source": "calendar",
                        "subject": parsed_meeting.get("subject", event.get("summary", "")),
                        "start_time": event_start.isoformat(),
                        "end_time": self._try_parse_time(event["end"].get("dateTime", event["end"].get("date"))).isoformat(),
                        "participants": calendar_participants,
                        "emails": emails,
                        "names": names
                    }

        return {
            "found": False,
            "source": "log_only",
            "subject": parsed_meeting.get("subject", ""),
            "start_time": parsed_meeting.get("start_time", None),
            "end_time": parsed_meeting.get("end_time", None),
            "participants": [{"email": "", "displayName": name} for name in parsed_meeting.get("participants", [])],
            "emails": [],
            "names": parsed_meeting.get("participants", [])
        }

    def get_participants_from_event(self, event: Dict[str, Any]) -> List[Dict[str, str]]:
        attendees = event.get("attendees", [])
        return [{"email": a.get("email", ""), "displayName": a.get("displayName", "")} for a in attendees]

    def _try_parse_time(self, time_str: Optional[str]) -> Optional[datetime.datetime]:
        try:
            return dt_parser.parse(time_str)
        except Exception:
            return None


# Unit test
if __name__ == "__main__":
    print("🚀 Testing Google Calendar Tool...")
    tool = GoogleCalendarTool()
    parsed_meeting = {
        "subject": "Slack integration discussion",
        "start_time": "2025-06-06T22:00:00Z",
        "end_time": "2025-06-06T23:00:00Z",
        "participants": ["Sarah", "James"]
    }
    result = tool.resolve_event(parsed_meeting)
    print(json.dumps(result, indent=2))
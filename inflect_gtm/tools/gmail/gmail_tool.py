import os
import base64
from typing import Dict, Any, List
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from inflect_gtm.components import Tool
from dotenv import load_dotenv
from inflect_gtm.tools.utils.google_auth import authenticate


class GmailTool(Tool):
    def __init__(self):
        super().__init__(name="Gmail", function=self.send_email)
        self.creds = authenticate()

    def send_email(self, context: Dict[str, Any]) -> str:
        input_str = context.get("input", "")
        try:
            parts = dict(x.split(':', 1) for x in input_str.split('; '))
            to = parts['to'].strip()
            subject = parts['subject'].strip()
            body = parts['body'].strip()

            service = build('gmail', 'v1', credentials=self.creds)

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            service.users().messages().send(userId='me', body=raw_message).execute()

            return f"📧 Email sent to {to} with subject: {subject}"
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"

    def fetch_emails(self, context: Dict[str, Any]) -> List[str]:
        """
        Fetches the latest N email threads and returns a list of email bodies.
        """
        max_results = context.get("n", 10)
        query = context.get("query", "")  # e.g., "from:support@company.com"

        service = build('gmail', 'v1', credentials=self.creds)
        results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
        messages = results.get('messages', [])

        email_bodies = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            payload = msg_data.get("payload", {})
            parts = payload.get("parts", [])

            # Try plain text first
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body_data = part.get("body", {}).get("data", "")
                    if body_data:
                        decoded = base64.urlsafe_b64decode(body_data).decode("utf-8")
                        email_bodies.append(decoded)
                        break
            else:
                # Fallback to snippet
                snippet = msg_data.get("snippet", "")
                if snippet:
                    email_bodies.append(snippet)

        return email_bodies


if __name__ == "__main__":
    print("🚀 Testing Gmail tool...")

    gmail_tool = GmailTool()

    # Test sending
    test_context_send = {
        "input": "to:danielkahneman@rawintelligence.xyz; subject:Test Email; body:This is a test from unit test."
    }
    result_send = gmail_tool.send_email(test_context_send)
    print("📤 Send Result:", result_send)

    # Test fetching
    test_context_fetch = {"n": 3}
    fetched = gmail_tool.fetch_emails(test_context_fetch)
    print("\n📥 Fetched Emails:")
    for idx, email in enumerate(fetched, 1):
        print(f"\n--- Email {idx} ---\n{email}")
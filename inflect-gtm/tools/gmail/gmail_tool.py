import os
import base64
from typing import Dict, Any
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from inflect.components import Tool


SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailTool(Tool):
    def __init__(self):
        super().__init__(name="Gmail", function=self.send_email)

    def send_email(self, context: Dict[str, Any]) -> str:
        input_str = context.get("input", "")
        try:
            parts = dict(x.split(':', 1) for x in input_str.split('; '))
            to = parts['to'].strip()
            subject = parts['subject'].strip()
            body = parts['body'].strip()

            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    cred_path = os.path.join(os.path.dirname(__file__), './credentials.json')
                    flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('gmail', 'v1', credentials=creds)

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            service.users().messages().send(userId='me', body=raw_message).execute()

            return f"📧 Email sent to {to} with subject: {subject}"
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"


if __name__ == "__main__":
    print("🚀 Testing Gmail tool...")
    gmail_tool = GmailTool()
    test_context = {
        "input": "to:danielkahneman@rawintelligence.xyz; subject:Test Email; body:This is a test from unit test."
    }
    result = gmail_tool.run(test_context)
    print("🔍 Result:", result)
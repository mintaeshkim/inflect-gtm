import os
from typing import Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from inflect_gtm.components import Tool
from dotenv import load_dotenv

# Load environment variables from .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

class GoogleSheetsTool(Tool):
    def __init__(self):
        super().__init__(name="GoogleSheets", function=self.read_sheet)

    def get_credentials(self):
        cred_path = os.path.join(project_root, os.getenv("GOOGLE_CREDENTIALS_PATH"))
        token_path = os.path.join(project_root, os.getenv("GOOGLE_TOKEN_SHEETS_PATH"))

        creds = None
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
        return creds

    def read_sheet(self, context: Dict[str, Any]) -> str:
        input_str = context.get("input", "")
        try:
            parts = dict(x.split(':', 1) for x in input_str.split('; '))
            cell_range = parts['range'].strip()
            sheet_title = parts.get('sheet')
            spreadsheet_id = parts.get('id')

            creds = self.get_credentials()
            service = build('sheets', 'v4', credentials=creds)

            if not spreadsheet_id and sheet_title:
                drive_service = build('drive', 'v3', credentials=creds)
                response = drive_service.files().list(
                    q=f"mimeType='application/vnd.google-apps.spreadsheet' and name='{sheet_title}'",
                    spaces='drive',
                    fields='files(id, name, modifiedTime)',
                    orderBy='modifiedTime desc',
                    pageSize=1
                ).execute()
                files = response.get('files', [])
                if not files:
                    return f"❌ No spreadsheet found with title: {sheet_title}"
                spreadsheet_id = files[0]['id']

            if not spreadsheet_id:
                return "❌ Please provide either 'id' or 'sheet' in input."

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=cell_range
            ).execute()
            values = result.get('values', [])

            if not values:
                return f"📊 No data found in range {cell_range}."

            formatted = '\n'.join([', '.join(row) for row in values])
            return formatted

        except Exception as e:
            return f"❌ Failed to read Google Sheet: {str(e)}"

    def write_sheet(self, input_str: str) -> str:
        try:
            parts = dict(x.split(':', 1) for x in input_str.split('; '))
            sheet_title = parts["sheet"].strip()
            cell_range = parts["range"].strip()
            values = [cell.strip() for cell in parts["values"].split(',')]

            creds = self.get_credentials()
            service = build('sheets', 'v4', credentials=creds)

            spreadsheet = {
                'properties': {'title': sheet_title}
            }
            spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
            sheet_id = spreadsheet.get('spreadsheetId')

            body = {
                'values': [values]
            }
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=cell_range,
                valueInputOption="RAW",
                body=body
            ).execute()

            return f"📊 Sheet '{sheet_title}' created and updated. Link: https://docs.google.com/spreadsheets/d/{sheet_id}"

        except Exception as e:
            return f"❌ Failed to update Google Sheet: {str(e)}"

    def parse_sheet_text(self, sheet_text: str) -> list[dict]:
        lines = [line.strip() for line in sheet_text.strip().splitlines() if line.strip()]
        if not lines or len(lines) < 2:
            return []

        headers = [h.strip() for h in lines[0].split(',')]
        rows = []

        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            row_dict = dict(zip(headers, values))
            rows.append(row_dict)

        return rows

    def fetch_and_parse(self, context: Dict[str, Any]) -> dict:
        sheet_text = self.read_sheet(context)
        if sheet_text.startswith("❌"):
            return {"error": sheet_text}
        rows = self.parse_sheet_text(sheet_text)
        return {
            "output": f"Fetched {len(rows)} rows from sheet.",
            "data": rows
        }


if __name__ == "__main__":
    print("📊 Testing Google Sheets tool...")
    sheets_tool = GoogleSheetsTool()
    test_context = {"input": "sheet:DemoSheet; range:A1; values:Name, Age"}
    write_result = sheets_tool.write_sheet(test_context["input"])
    print("🔍 Write Result:", write_result)

    read_context = {"input": "sheet:customer_info; range:A1:F100"}
    print("🔍 Read Result:", sheets_tool.run(read_context))

    print("🔍 Fetch & Parse Result:", sheets_tool.fetch_and_parse(read_context))
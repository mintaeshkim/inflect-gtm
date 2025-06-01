import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import Dict, Any
from inflect.components import Tool


SCOPES = ['https://www.googleapis.com/auth/documents']

class GoogleDocsTool(Tool):
    def __init__(self):
        super().__init__(name="GoogleDocs", function=self.create_doc)

    def load_credentials(self):
        creds = None
        if os.path.exists('token_docs.json'):
            creds = Credentials.from_authorized_user_file('token_docs.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                cred_path = os.path.join(os.path.dirname(__file__), './credentials.json')
                flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token_docs.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def create_doc(self, context: Dict[str, Any]) -> str:
        try:
            parts = dict(x.split(':', 1) for x in context.get("input", "").split('; '))
            title = parts["title"].strip()
            content = parts["content"].strip()

            creds = self.load_credentials()
            service = build('docs', 'v1', credentials=creds)

            doc = service.documents().create(body={'title': title}).execute()
            document_id = doc['documentId']

            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]
            service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

            return f"📝 Google Doc '{title}' created. Link: https://docs.google.com/document/d/{document_id}"

        except Exception as e:
            return f"❌ Failed to create Google Doc: {str(e)}"

    def read_doc(self, document_id: str) -> str:
        try:
            creds = self.load_credentials()
            service = build('docs', 'v1', credentials=creds)
            doc = service.documents().get(documentId=document_id).execute()

            text = ''
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for p_element in element['paragraph'].get('elements', []):
                        text += p_element.get('textRun', {}).get('content', '')

            return f"📝 Content of document '{doc['title']}':\n{text.strip()}"
        except Exception as e:
            return f"❌ Failed to read Google Doc: {str(e)}"


if __name__ == "__main__":
    print("🚀 Testing Google Docs tool...")
    docs_tool = GoogleDocsTool()
    test_context = {"input": "title:Test Document; content:This document was created via the agent."}
    create_result = docs_tool.run(test_context)
    print("🔍 Create doc result:", create_result)

    doc_id = create_result.split("/d/")[-1] if "/d/" in create_result else None
    if doc_id:
        read_result = docs_tool.read_doc(doc_id.split("/")[0])
        print("🔍 Read doc result:", read_result)

import os
import ast
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv


# Load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

def authenticate():
    """
    Authenticate the user and return Google API credentials for the given scopes.
    Loads credentials from token or starts OAuth flow if needed.
    """
    cred_path = os.path.join(project_root, os.getenv("GOOGLE_CREDENTIALS_PATH"))
    token_path = os.path.join(project_root, os.getenv("GOOGLE_TOKEN_PATH"))
    scopes = ast.literal_eval(os.getenv("SCOPES"))

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


if __name__ == "__main__":
    print("🚀 Testing Google Authenticator...")
    authenticate()
    print("✅ Authentication succeeded.")
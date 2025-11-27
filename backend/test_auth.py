"""Step 1: Test authentication only"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Allow insecure transport for localhost
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """Authenticate and return Drive service"""
    creds = None

    # Check if we already have a token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print("✓ Found existing token.json")

    # If no valid credentials, need to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("No valid credentials found. Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            flow.redirect_uri = 'http://localhost'
            # Generate auth URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"\n1. Visit this URL in your browser:\n{auth_url}\n")
            print("2. After authorizing, copy the ENTIRE redirect URL from your browser")
            redirect_response = input("\nPaste the full redirect URL here: ")
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials

        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("✓ Saved credentials to token.json")

    return build('drive', 'v3', credentials=creds)

if __name__ == '__main__':
    try:
        service = authenticate()
        print("\n✓ Authentication successful!")
        print("✓ Drive service created")
    except Exception as e:
        print(f"\n✗ Error: {e}")

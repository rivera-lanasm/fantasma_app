"""Minimal test: List files in dan_wine folder"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """Load credentials from token.json"""
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('drive', 'v3', credentials=creds)

def find_folder(service, folder_name):
    """Find folder by name"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def list_files(service, folder_id):
    """List files in folder"""
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])

    print("\nFiles found:")
    for f in files:
        print(f"  - {f['name']}")

    return files

if __name__ == '__main__':
    service = authenticate()
    print("✓ Authenticated")

    folder_id = find_folder(service, 'Automation Demo Folder')
    if folder_id:
        print(f"✓ Found Automation Demo Folder")
        list_files(service, folder_id)
    else:
        print("✗ Folder 'Automation Demo Folder' not found")

"""Test Google Drive API access: list, read, write, download"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """Authenticate and return Drive service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def find_folder(service, folder_name):
    """Find folder by name and return its ID"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    folders = results.get('files', [])

    if not folders:
        print(f"Folder '{folder_name}' not found")
        return None

    print(f"Found folder: {folders[0]['name']} (ID: {folders[0]['id']})")
    return folders[0]['id']

def list_files_in_folder(service, folder_id):
    """List all files in folder"""
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
    files = results.get('files', [])

    print(f"\nFiles in folder:")
    for f in files:
        print(f"  - {f['name']} (ID: {f['id']})")

    return files

def download_file(service, file_id, file_name):
    """Download file from Drive"""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(file_name, 'wb') as f:
        f.write(fh.getvalue())

    print(f"\nDownloaded: {file_name}")

def upload_file(service, file_path, folder_id):
    """Upload file to Drive folder"""
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"\nUploaded: {file_path} (ID: {file.get('id')})")
    return file.get('id')

if __name__ == '__main__':
    # Authenticate
    service = authenticate()
    print("✓ Authentication successful\n")

    # Find dan_wine folder
    folder_id = find_folder(service, 'dan_wine')
    if not folder_id:
        exit(1)

    # List files in folder
    files = list_files_in_folder(service, folder_id)

    # Find test_file.docx
    test_file = next((f for f in files if 'test_file' in f['name'].lower()), None)
    if test_file:
        # Download test_file.docx
        download_file(service, test_file['id'], 'downloaded_test.docx')
    else:
        print("\ntest_file.docx not found in folder")

    # Test write: create and upload a simple text file
    with open('test_upload.txt', 'w') as f:
        f.write('Test upload from Python script')

    upload_file(service, 'test_upload.txt', folder_id)

    print("\n✓ All tests completed successfully")

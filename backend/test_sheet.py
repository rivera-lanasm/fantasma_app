"""Test reading product_data Google Sheet"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pandas as pd

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

def get_latest_xlsx(service, folder_id):
    """Get the most recently modified .xlsx file in folder"""
    query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = service.files().list(
        q=query,
        fields='files(id, name, mimeType, modifiedTime)',
        orderBy='modifiedTime desc'
    ).execute()
    files = results.get('files', [])
    return files[0] if files else None

def download_xlsx(service, file_id):
    """Download .xlsx file"""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    return fh

def analyze_sheet(file_handle):
    """Analyze sheet structure"""
    df = pd.read_excel(file_handle)

    print("\n=== SHEET ANALYSIS ===\n")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for col in df.columns:
        print(f"  - {col}")

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    return df

if __name__ == '__main__':
    service = authenticate()
    print("✓ Authenticated")

    folder_id = find_folder(service, 'Automation Demo Folder')
    print("✓ Found Automation Demo Folder")

    file_info = get_latest_xlsx(service, folder_id)
    if not file_info:
        print("✗ No Excel files found in folder")
        exit(1)

    print(f"✓ Found latest Excel: {file_info['name']}")
    print(f"  MimeType: {file_info['mimeType']}")
    print(f"  Last modified: {file_info.get('modifiedTime', 'Unknown')}")

    file_handle = download_xlsx(service, file_info['id'])
    print("✓ Downloaded xlsx")

    analyze_sheet(file_handle)

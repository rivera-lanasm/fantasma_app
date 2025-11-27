"""Search products by producer name"""

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

if __name__ == '__main__':
    import sys

    search_terms = sys.argv[1:] if len(sys.argv) > 1 else []

    service = authenticate()
    folder_id = find_folder(service, 'Automation Demo Folder')
    file_info = get_latest_xlsx(service, folder_id)
    if not file_info:
        print("No Excel files found in folder")
        sys.exit(1)
    file_handle = download_xlsx(service, file_info['id'])

    df = pd.read_excel(file_handle)

    for term in search_terms:
        matches = df[df['PRODUCER'].str.contains(term, case=False, na=False)]
        print(f"\n=== {term.upper()} MATCHES ({len(matches)} found) ===")
        if len(matches) > 0:
            for idx, row in matches.iterrows():
                print(f"Row {idx}: {row['PRODUCER']} - {row['CUVEE_NAME']} ({row['VINTAGE']})")
        else:
            print("No matches found")

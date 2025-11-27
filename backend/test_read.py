"""Test reading content from test_file"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from docx import Document
import io

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

def get_file(service, folder_id, file_name):
    """Get file info from folder"""
    query = f"'{folder_id}' in parents and name='{file_name}'"
    results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
    files = results.get('files', [])
    return files[0] if files else None

def download_docx(service, file_id, mime_type):
    """Download or export file as docx"""
    fh = io.BytesIO()

    # Check if it's a Google Doc (needs export) or regular docx (needs download)
    if mime_type == 'application/vnd.google-apps.document':
        print("  File is a Google Doc, exporting as .docx...")
        request = service.files().export_media(
            fileId=file_id,
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    else:
        print("  File is a .docx, downloading...")
        request = service.files().get_media(fileId=file_id)

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    return fh

def read_docx_content(file_handle):
    """Read text content from docx file"""
    doc = Document(file_handle)

    print("\nDocument content:")
    print("-" * 50)
    for para in doc.paragraphs:
        if para.text.strip():
            print(para.text)
    print("-" * 50)

if __name__ == '__main__':
    service = authenticate()
    print("✓ Authenticated")

    folder_id = find_folder(service, 'dan_wine')
    if not folder_id:
        print("✗ Folder not found")
        exit(1)

    print("✓ Found dan_wine folder")

    file_info = get_file(service, folder_id, 'test_file')
    if not file_info:
        print("✗ test_file not found")
        exit(1)

    print(f"✓ Found file: {file_info['name']}")
    print(f"  MimeType: {file_info['mimeType']}")

    file_handle = download_docx(service, file_info['id'], file_info['mimeType'])
    print("✓ Downloaded file")

    read_docx_content(file_handle)

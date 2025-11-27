"""Test if replacement actually works"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from docx import Document
import pandas as pd
import io

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('drive', 'v3', credentials=creds)

def find_folder(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def get_file(service, folder_id, file_name):
    query = f"'{folder_id}' in parents and name contains '{file_name}'"
    results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
    files = results.get('files', [])
    return files[0] if files else None

def download_file(service, file_id, mime_type):
    fh = io.BytesIO()
    if mime_type == 'application/vnd.google-apps.document':
        request = service.files().export_media(
            fileId=file_id,
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    else:
        request = service.files().get_media(fileId=file_id)

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

if __name__ == '__main__':
    service = authenticate()
    folder_id = find_folder(service, 'dan_wine')

    # Get template
    template_info = get_file(service, folder_id, 'template')
    template_handle = download_file(service, template_info['id'], template_info['mimeType'])
    template = Document(template_handle)

    # Get sheet
    sheet_info = get_file(service, folder_id, 'product_data')
    sheet_handle = download_file(service, sheet_info['id'], sheet_info['mimeType'])
    df = pd.read_excel(sheet_handle)

    # Test replacement on paragraph 1
    original = template.paragraphs[1].text
    first_row = df.iloc[0]

    print(f"Original text: {original}")
    print(f"\nTrying replacement with straight quotes...")
    test1 = original.replace('"PRODUCER"', first_row['PRODUCER'])
    print(f"Result: {test1}")

    print(f"\nTrying replacement with smart quotes...")
    test2 = original.replace('"PRODUCER"', first_row['PRODUCER'])
    print(f"Result: {test2}")

    print(f"\nAll characters in template:")
    for i, char in enumerate(original):
        print(f"  Position {i}: '{char}' (code: {ord(char)})")

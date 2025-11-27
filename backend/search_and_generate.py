"""Search for wines and generate tasting sheet based on natural language query"""

import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pandas as pd
import subprocess
from session_logger import start_session, log_message, end_session

SCOPES = ['https://www.googleapis.com/auth/drive']

def log_and_print(message, session_id=None):
    """Print message and log it"""
    print(message)
    sys.stdout.flush()
    if session_id:
        log_message(session_id, message)

def authenticate():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('drive', 'v3', credentials=creds)

def find_folder(service, folder_name):
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
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def search_producer(df, term):
    """Search for producer by term (case-insensitive, partial match)"""
    matches = df[df['PRODUCER'].str.contains(term, case=False, na=False)]
    return matches

def parse_query(query):
    """Parse natural language query into producer terms"""
    # Remove common filler words
    fillers = ['the', 'from', 'by', 'a', 'an']
    words = query.lower().split()

    # Extract producers by looking for 'both X' or 'all X' patterns
    producers = []
    i = 0
    while i < len(words):
        word = words[i]

        # Handle "both X" or "all X"
        if word in ['both', 'all'] and i + 1 < len(words):
            next_word = words[i + 1]
            if next_word not in ['and']:
                producers.append(next_word)
                i += 2
                continue

        # Handle standalone terms (not filler, not 'and')
        if word not in fillers and word != 'and':
            producers.append(word)

        i += 1

    return producers

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python search_and_generate.py <query>")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    # Start logging session
    session_id = start_session(query)

    try:
        # Authenticate
        log_and_print("🔐 Authenticating with Google Drive...", session_id)
        service = authenticate()
        log_and_print("✓ Authentication successful", session_id)

        # Find folder
        log_and_print("📁 Finding Automation Demo Folder...", session_id)
        folder_id = find_folder(service, 'Automation Demo Folder')
        log_and_print("✓ Folder found", session_id)

        # Download product data (latest xlsx)
        log_and_print("📥 Finding latest Excel file...", session_id)
        file_info = get_latest_xlsx(service, folder_id)
        if not file_info:
            log_and_print("❌ No Excel files found in folder!", session_id)
            end_session(session_id, success=False, error="No Excel files found")
            sys.exit(1)
        log_and_print(f"✓ Found: {file_info['name']}", session_id)
        file_handle = download_xlsx(service, file_info['id'])
        log_and_print("✓ Product data downloaded", session_id)

        # Read Excel file
        log_and_print("📖 Reading product data...", session_id)
        df = pd.read_excel(file_handle)
        log_and_print(f"✓ Loaded {len(df)} products", session_id)

        # Parse query
        log_and_print(f"🔍 Parsing query: '{query}'", session_id)
        producer_terms = parse_query(query)
        log_and_print(f"✓ Searching for: {', '.join(producer_terms)}", session_id)

        all_rows = []

        for term in producer_terms:
            log_and_print(f"🔎 Searching for '{term}'...", session_id)
            matches = search_producer(df, term)

            if len(matches) == 0:
                log_and_print(f"  → No exact match, trying fuzzy search...", session_id)
                # Try fuzzy search for similar names
                for idx, row in df.iterrows():
                    producer = str(row['PRODUCER']).lower()
                    cuvee = str(row['CUVEE_NAME']).lower()
                    if term in producer or term in cuvee:
                        matches = pd.concat([matches, df.iloc[[idx]]])

            if len(matches) > 0:
                log_and_print(f"✓ Found {len(matches)} wine(s) for '{term}':", session_id)
                for idx, row in matches.iterrows():
                    log_and_print(f"  • {row['PRODUCER']} - {row['CUVEE_NAME']} ({row['VINTAGE']})", session_id)
                    all_rows.append(idx)
            else:
                log_and_print(f"✗ No matches for '{term}'", session_id)

        if not all_rows:
            log_and_print("❌ No wines found!", session_id)
            end_session(session_id, success=False, error="No wines found")
            sys.exit(1)

        # Generate documents (tasting sheet + price list)
        log_and_print(f"\n📝 Generating documents for {len(all_rows)} wines...", session_id)
        result = subprocess.run(
            [sys.executable, 'generate_selected_wines.py'] + [str(r) for r in all_rows],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            log_and_print("✓ Tasting sheet generated!", session_id)
            log_and_print("✓ Price list generated!", session_id)
            # Parse output to show filenames
            for line in result.stdout.split('\n'):
                if 'Saved tasting sheet:' in line or 'Saved price list:' in line:
                    filename = line.split(': ')[-1]
                    log_and_print(f"  → {filename}", session_id)
            log_and_print("✓ Both documents uploaded to Google Drive", session_id)
            log_and_print("\n🎉 Done!", session_id)
            end_session(session_id, success=True)
        else:
            error_msg = f"❌ Error: {result.stderr}"
            log_and_print(error_msg, session_id)
            end_session(session_id, success=False, error=result.stderr)
            sys.exit(1)

    except Exception as e:
        error_msg = f"❌ Exception: {str(e)}"
        log_and_print(error_msg, session_id)
        end_session(session_id, success=False, error=str(e))
        sys.exit(1)

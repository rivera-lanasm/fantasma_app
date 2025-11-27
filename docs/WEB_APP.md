# Wine Tasting Sheet Web App

Minimal Svelte + Flask web interface for the tasting sheet generator.

## Running the App

### 1. Start Backend (Terminal 1)

```bash
cd /home/rivlanm/projects/google_auto
source .venv/bin/activate
cd backend
python app.py
```

Backend runs on http://localhost:5000

### 2. Start Frontend (Terminal 2)

```bash
cd /home/rivlanm/projects/google_auto/frontend
npm run dev
```

Frontend runs on http://localhost:5173

### 3. Use the App

1. Open http://localhost:5173 in browser
2. Enter query like "both scopa and both realce"
3. Click "Generate Sheet" or press Enter
4. View results and check Google Drive for generated document

## Project Structure

```
google_auto/
  backend/
    app.py                      # Flask API server
    search_and_generate.py      # Search + generation logic
    generate_selected_wines.py  # Document generator
    *.py                        # Other helper scripts
    credentials.json            # Google OAuth credentials
    token.json                  # Auth token
  frontend/
    src/
      App.svelte               # Main UI component
    package.json
```

## How It Works

1. Frontend sends POST to `/api/generate-sheet` with query
2. Backend runs `search_and_generate.py` with the query
3. Script searches product data, generates sheet, uploads to Drive
4. Real-time status messages stream to frontend via Server-Sent Events
5. All queries and messages logged to `backend/session_log.json`

## Viewing Session Logs

All user queries and system messages are automatically logged for review:

```bash
cd backend
python view_logs.py
```

This shows:
- All queries submitted
- Complete message history for each session
- Success/failure status
- Timestamps
- Any errors encountered

Log file: `backend/session_log.json` (JSON format, easy to process)

## User Feedback

Users can submit feedback directly in the app (feedback section at bottom). View all feedback:

```bash
cd backend
python view_feedback.py
```

Shows:
- All feedback messages
- Timestamps
- Associated query (if submitted after a search)

Log file: `backend/feedback_log.json` (JSON format)

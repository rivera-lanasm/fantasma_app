"""View session logs"""

import json
import os
from datetime import datetime

LOG_FILE = 'session_log.json'

def view_logs():
    """Display all logged sessions"""
    if not os.path.exists(LOG_FILE):
        print("No logs found yet.")
        return

    with open(LOG_FILE, 'r') as f:
        log = json.load(f)

    sessions = log.get('sessions', [])

    if not sessions:
        print("No sessions logged yet.")
        return

    print(f"\n{'='*80}")
    print(f"SESSION LOG - {len(sessions)} total sessions")
    print(f"{'='*80}\n")

    for session in sessions:
        status = "✓ SUCCESS" if session.get('success') else "✗ FAILED"
        print(f"Session #{session['id']} - {status}")
        print(f"Query: {session['query']}")
        print(f"Started: {session['timestamp']}")

        if session.get('completed_at'):
            print(f"Completed: {session['completed_at']}")

        if session.get('error'):
            print(f"Error: {session['error']}")

        print(f"\nMessages ({len(session['messages'])}):")
        for msg in session['messages']:
            print(f"  {msg['message']}")

        print(f"\n{'-'*80}\n")

if __name__ == '__main__':
    view_logs()

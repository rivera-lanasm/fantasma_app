"""Simple session logger for tracking queries and messages"""

import json
import os
from datetime import datetime

LOG_FILE = 'session_log.json'

def load_log():
    """Load existing log or create new one"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return {'sessions': []}

def save_log(log_data):
    """Save log to file"""
    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)

def start_session(query):
    """Start a new session"""
    log = load_log()
    session = {
        'id': len(log['sessions']) + 1,
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'messages': [],
        'success': None,
        'error': None
    }
    log['sessions'].append(session)
    save_log(log)
    return session['id']

def log_message(session_id, message):
    """Add a message to the session"""
    log = load_log()
    for session in log['sessions']:
        if session['id'] == session_id:
            session['messages'].append({
                'timestamp': datetime.now().isoformat(),
                'message': message
            })
            break
    save_log(log)

def end_session(session_id, success=True, error=None):
    """Mark session as complete"""
    log = load_log()
    for session in log['sessions']:
        if session['id'] == session_id:
            session['success'] = success
            session['error'] = error
            session['completed_at'] = datetime.now().isoformat()
            break
    save_log(log)

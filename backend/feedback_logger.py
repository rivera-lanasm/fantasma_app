"""Simple feedback logger"""

import json
import os
from datetime import datetime

FEEDBACK_FILE = 'feedback_log.json'

def load_feedback():
    """Load existing feedback or create new one"""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {'feedback': []}

def save_feedback(feedback_data):
    """Save feedback to file"""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=2)

def add_feedback(message, last_query=None):
    """Add user feedback"""
    feedback = load_feedback()
    entry = {
        'id': len(feedback['feedback']) + 1,
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'last_query': last_query
    }
    feedback['feedback'].append(entry)
    save_feedback(feedback)
    return entry['id']

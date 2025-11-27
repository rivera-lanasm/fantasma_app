"""View user feedback"""

import json
import os

FEEDBACK_FILE = 'feedback_log.json'

def view_feedback():
    """Display all user feedback"""
    if not os.path.exists(FEEDBACK_FILE):
        print("No feedback found yet.")
        return

    with open(FEEDBACK_FILE, 'r') as f:
        data = json.load(f)

    feedback_list = data.get('feedback', [])

    if not feedback_list:
        print("No feedback submitted yet.")
        return

    print(f"\n{'='*80}")
    print(f"USER FEEDBACK - {len(feedback_list)} total submissions")
    print(f"{'='*80}\n")

    for entry in feedback_list:
        print(f"Feedback #{entry['id']}")
        print(f"Submitted: {entry['timestamp']}")

        if entry.get('last_query'):
            print(f"Last Query: {entry['last_query']}")

        print(f"\nMessage:")
        print(f"{entry['message']}")

        print(f"\n{'-'*80}\n")

if __name__ == '__main__':
    view_feedback()

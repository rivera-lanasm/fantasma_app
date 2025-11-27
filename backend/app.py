"""Flask API for wine tasting sheet generation"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import subprocess
import sys
import json
from feedback_logger import add_feedback

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

def stream_output(process):
    """Stream process output line by line"""
    for line in iter(process.stdout.readline, ''):
        if line:
            yield f"data: {json.dumps({'message': line.strip()})}\n\n"

    process.wait()

    if process.returncode == 0:
        yield f"data: {json.dumps({'done': True, 'success': True})}\n\n"
    else:
        error = process.stderr.read()
        yield f"data: {json.dumps({'done': True, 'success': False, 'error': error})}\n\n"

@app.route('/api/generate-sheet', methods=['POST'])
def generate_sheet():
    """Generate tasting sheet from natural language query (streaming)"""
    try:
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Run the search with real-time output streaming
        process = subprocess.Popen(
            [sys.executable, 'search_and_generate.py', query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd='/home/rivlanm/projects/google_auto/backend'
        )

        return Response(
            stream_with_context(stream_output(process)),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        last_query = data.get('last_query', None)

        if not message.strip():
            return jsonify({'error': 'Feedback message is required'}), 400

        feedback_id = add_feedback(message, last_query)

        return jsonify({
            'success': True,
            'id': feedback_id,
            'message': 'Feedback received. Thank you!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Production: bind to localhost only, disable debug
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)

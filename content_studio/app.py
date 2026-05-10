"""
Content Studio - ElevenLabs-style UI for content creation
Flask app with left panel input, right panel results
"""

from flask import Flask, render_template, request, jsonify
import requests
import os
import base64
from pathlib import Path

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@app.route('/')
def index():
    """Main content studio page"""
    return render_template('studio.html')

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """Proxy generation request to FastAPI backend"""
    try:
        data = request.json
        
        # Forward to backend RAG generate endpoint
        response = requests.post(
            f"{BACKEND_URL}/api/rag/generate",
            json=data,
            timeout=120
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Backend generation failed"}), response.status_code
        
        result = response.json()
        return jsonify(result)
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Generation timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get generation history from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/generation-history")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)

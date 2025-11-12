import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

app = Flask(__name__, static_folder='public')
CORS(app)

# Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ can't find GEMINI_API_KEY in .env")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('models/gemini-2.5-flash')
except Exception as e:
    print(f"❌ problem in model initialization: {e}")
    model = None

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Chat API
@app.route('/api/chat', methods=['POST'])
def chat():
    if model is None:
        return jsonify({"error": "Model Gemini not initialized"}), 500

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message"}), 400

    message_text = data.get('message')
    history_data = data.get('history', [])

    try:
        formatted_history = []
        for h in history_data:
            role = "model" if h['role'] == 'assistant' else 'user'
            formatted_history.append({"role": role, "parts": [h['content']]})

        chat_session = model.start_chat(history=formatted_history)
        response = chat_session.send_message(message_text)
        return jsonify({"reply": response.text})

    except Exception as err:
        return jsonify({"error": "Problem in Gemini API", "detail": str(err)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Tải file .env
load_dotenv()

# Khởi tạo Flask App
# static_folder='public' nói với Flask rằng thư mục 'public' chứa các file tĩnh
app = Flask(__name__, static_folder='public')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
CORS(app)  # Bật CORS cho tất cả các route

# Cấu hình Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ can't find GEMINI_API_KEY in file .env")

genai.configure(api_key=api_key)

try:
    # Sử dụng model flash mới nhất, đã được xác nhận
    model = genai.GenerativeModel('models/gemini-2.5-flash')
except Exception as e:
    print(f"❌ problem in model initialization: {e}")
    print("Please check the model name and API key.")
    model = None

# Route 1: Phục vụ file index.html khi truy cập /
@app.route('/')
def serve_index():
    # Gửi file index.html từ thư mục 'public'
    return send_from_directory(app.static_folder, 'index.html')

# Route 2: Phục vụ các file tĩnh khác (style.css, chat-bot.js)
# Flask sẽ tự động xử lý việc này nhờ 'static_folder'
# Nhưng để cho chắc chắn, chúng ta có thể thêm route này:
@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# Route 3: API để chat
@app.route('/api/chat', methods=['POST'])
def chat():
    if model is None:
        return jsonify({"error": "Model Gemini has not been initialized"}), 500

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message"}), 400

    message_text = data.get('message')
    history_data = data.get('history', [])

    try:
        # Định dạng lại lịch sử chat cho Gemini API
        formatted_history = []
        for h in history_data:
            role = "model" if h['role'] == 'assistant' else 'user'
            formatted_history.append({
                "role": role,
                "parts": [h['content']]
            })

        # Bắt đầu session chat với lịch sử
        chat_session = model.start_chat(history=formatted_history)
        
        # Gửi tin nhắn mới
        response = chat_session.send_message(message_text)

        return jsonify({"reply": response.text})

    except Exception as err:
        print(f"❌ problem in Gemini API: {err}")
        return jsonify({"error": "Problem in Gemini API", "detail": str(err)}), 500

# Chạy server
if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    # Chạy server, debug=True sẽ tự khởi động lại khi bạn sửa code
    app.run(debug=True, port=port)
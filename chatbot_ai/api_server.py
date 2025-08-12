from flask import Flask, request, jsonify
from flask_cors import CORS
from semantic_chatbot import ImprovedChatbot

app = Flask(__name__)
CORS(app)

# Không cần sửa gì ở đây vì ImprovedChatbot đã tự động lấy dữ liệu từ DB nếu có
chatbot = ImprovedChatbot()
chatbot.load_data()
chatbot.load_model()
chatbot.ensure_index()

@app.route('/api/chatbot/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip() if data else ""

    if not question:
        return jsonify({'answer': '⚠️ Vui lòng nhập câu hỏi!'}), 400

    q_lower = question.lower()

    if q_lower == "reset":
        chatbot.memory.reset_session()
        return jsonify({'answer': '🔄 Đã xóa lịch sử chat!', 'reset': True})

    if q_lower == "help":
        return jsonify({'answer': (
            "💬 Bạn có thể hỏi:\n"
            "- Điểm chuẩn ngành CNTT\n"
            "- Chỉ tiêu ngành AI\n"
            "- Phân tích điểm KHMT các năm\n"
            "Lệnh: reset, help, exit"
        )})

    try:
        answer = chatbot.process_question(question)
        chatbot.memory.add_turn(question, answer)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f"❌ Lỗi hệ thống: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

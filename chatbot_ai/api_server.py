from flask import Flask, request, jsonify
from flask_cors import CORS
from semantic_chatbot import (
    SentenceTransformer, ensure_index, load_nganh_data, find_best_nganh, answer, generate_answer_with_llm, TOP_K
)
import numpy as np

app = Flask(__name__)
CORS(app)

# Khởi tạo model và dữ liệu 1 lần khi server start
model = SentenceTransformer("all-MiniLM-L6-v2")
nganhs = load_nganh_data()
embeddings, index, ids = ensure_index(model, nganhs)
history = []

@app.route('/api/chatbot/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').strip() if data else ''
    if not question:
        return jsonify({'answer': 'Vui lòng nhập câu hỏi!'}), 400
    q_lower = question.lower().strip()
    if q_lower == 'reset':
        history.clear()
        return jsonify({'answer': '🔄 Đã xóa lịch sử chat!', 'reset': True})
    if q_lower == 'help':
        return jsonify({'answer': 'HỎI: điểm chuẩn, chỉ tiêu, khoa, mô tả các ngành. Lệnh: reset, help, exit.'})
    # Trả lời từ dữ liệu nếu tìm được ngành phù hợp
    ng, score = find_best_nganh(question, model, index, nganhs, ids, top_k=1, min_score=0.5)
    if ng:
        ans = answer(question, ng, score)
        history.append({"question": question, "answer": ans})
        return jsonify({'answer': ans})
    # Nếu không tìm được ngành phù hợp, fallback sang LLM với top-k ngành gần nhất
    q_emb = model.encode([question], normalize_embeddings=True)
    q_emb = np.array(q_emb).astype('float32')
    if q_emb.ndim == 1:
        q_emb = np.expand_dims(q_emb, 0)
    D, I = index.search(q_emb, TOP_K)
    top_nganhs = [nganhs[ids[int(i)]] for i in I[0]]
    if not top_nganhs or D[0][0] < 0.5:
        return jsonify({'answer': 'Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. Bạn vui lòng nhập rõ hơn tên ngành, mã ngành hoặc mô tả chi tiết hơn?'})
    llm_answer = generate_answer_with_llm(question, top_nganhs, history)
    history.append({"question": question, "answer": llm_answer})
    return jsonify({'answer': llm_answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True) 
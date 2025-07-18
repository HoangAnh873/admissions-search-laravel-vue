import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import unicodedata
import re
import requests

DATA_FILE = "data_chatbot.json"
EMBEDDING_FILE = "nganh_embeddings.npy"
INDEX_FILE = "nganh_faiss.index"
ID_FILE = "nganh_ids.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# Alias mapping: alias (không dấu, viết thường) -> mã ngành
ALIAS_MAP = {
    'cntt': '7480201',
    'it': '7480201',
    'cong nghe thong tin': '7480201',
    'khmt': '7480101',
    'khoa hoc may tinh': '7480101',
    'ktpm': '7480103',
    'ky thuat phan mem': '7480103',
    'mmt': '7480102',
    'mang may tinh': '7480102',
    'ttnt': '7480107',
    'tri tue nhan tao': '7480107',
    # Thêm alias cho các ngành khác nếu muốn
}

# Tham số RAG
TOP_K = 3  # Số ngành lấy làm context cho LLM

# Helper: remove accents for better matching
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

def load_nganh_data():
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] File dữ liệu {DATA_FILE} không tồn tại!")
        exit(1)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['nganhs']

def get_nganh_by_ma(ma_nganh, nganhs):
    for ng in nganhs:
        if ng.get('ma_nganh') == ma_nganh:
            return ng
    return None

def build_embeddings_and_index(nganhs, model):
    texts = []
    ids = []
    for idx, ng in enumerate(nganhs):
        # Ghép tên + mô tả + mã ngành + alias
        alias_text = ''
        for alias, ma_nganh in ALIAS_MAP.items():
            if ng.get('ma_nganh') == ma_nganh:
                alias_text += f" {alias.upper()} {alias.lower()}"
        text = f"{ng.get('nganh', '')}. {ng.get('mo_ta', '')}. Mã ngành: {ng.get('ma_nganh', '')}.{alias_text}"
        texts.append(text)
        ids.append(idx)
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)
    if embeddings.shape[0] == 0:
        raise ValueError("Không có dữ liệu embedding để tạo FAISS index.")
    # FAISS expects 2D float32 array, linter warning here is a false positive
    print("Shape of embeddings to add to FAISS:", embeddings.shape)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)  # Linter warning is a false positive for FAISS
    return embeddings, index, ids

def save_index_and_embeddings(embeddings, index, ids):
    np.save(EMBEDDING_FILE, embeddings)
    faiss.write_index(index, INDEX_FILE)
    with open(ID_FILE, 'w', encoding='utf-8') as f:
        json.dump(ids, f)

def load_index_and_embeddings():
    embeddings = np.load(EMBEDDING_FILE)
    index = faiss.read_index(INDEX_FILE)
    with open(ID_FILE, 'r', encoding='utf-8') as f:
        ids = json.load(f)
    return embeddings, index, ids

def ensure_index(model, nganhs):
    if os.path.exists(EMBEDDING_FILE) and os.path.exists(INDEX_FILE) and os.path.exists(ID_FILE):
        return load_index_and_embeddings()
    embeddings, index, ids = build_embeddings_and_index(nganhs, model)
    save_index_and_embeddings(embeddings, index, ids)
    return embeddings, index, ids

def keyword_match_nganh(question, nganhs):
    q = question.lower()
    q_noaccent = remove_accents(q)
    # Ưu tiên tìm theo alias
    for alias, ma_nganh in ALIAS_MAP.items():
        if alias in q_noaccent:
            ng = get_nganh_by_ma(ma_nganh, nganhs)
            if ng:
                return ng
    # Ưu tiên tìm theo mã ngành
    for ng in nganhs:
        if ng.get('ma_nganh') and ng.get('ma_nganh') in q:
            return ng
    # So khớp tên ngành không dấu
    for ng in nganhs:
        if ng.get('nganh') and remove_accents(ng.get('nganh')) in q_noaccent:
            return ng
    return None

def find_best_nganh(question, model, index, nganhs, ids, top_k=1, min_score=0.5):
    # Keyword match trước
    ng = keyword_match_nganh(question, nganhs)
    if ng:
        return ng, 1.0
    # Semantic search nếu không keyword match
    q_emb = model.encode([question], normalize_embeddings=True)
    # Ensure correct shape for FAISS (2D array)
    q_emb = np.array(q_emb).astype('float32')
    if q_emb.ndim == 1:
        q_emb = np.expand_dims(q_emb, 0)
    D, I = index.search(q_emb, top_k)
    best_idx = ids[I[0][0]]
    score = D[0][0]
    if score < min_score:
        return None, score
    return nganhs[best_idx], score

def extract_year(question):
    m = re.search(r'(20\d{2})', question)
    return m.group(1) if m else None

def answer(question, ng, score):
    year = extract_year(question)
    q = question.lower()
    # Phân tích xu hướng điểm chuẩn qua các năm
    if any(kw in q for kw in ["phân tích", "đánh giá", "so sánh"]) and ("điểm chuẩn" in q or "điểm" in q):
        if not ng.get('diem_chuan'):
            return f"{ng.get('nganh')}: Không có dữ liệu điểm chuẩn để phân tích."
        ds = ng['diem_chuan']
        # Gom nhóm theo năm, mỗi năm lấy điểm cao nhất (nếu có nhiều phương thức)
        year_points = {}
        for d in ds:
            y = d.get('nam')
            diem = d.get('diem')
            if y is not None and diem is not None:
                if y not in year_points or diem > year_points[y]:
                    year_points[y] = diem
        if not year_points:
            return f"{ng.get('nganh')}: Không có dữ liệu điểm chuẩn để phân tích."
        years = sorted(year_points.keys())
        points = [year_points[y] for y in years]
        # Phân tích xu hướng
        trend = []
        for i in range(1, len(points)):
            if points[i] > points[i-1]:
                trend.append("tăng")
            elif points[i] < points[i-1]:
                trend.append("giảm")
            else:
                trend.append("giữ nguyên")
        # Nhận xét tổng quát
        if all(t == "tăng" for t in trend):
            nhanxet = "Điểm chuẩn có xu hướng tăng qua các năm."
        elif all(t == "giảm" for t in trend):
            nhanxet = "Điểm chuẩn có xu hướng giảm qua các năm."
        elif all(t == "giữ nguyên" for t in trend):
            nhanxet = "Điểm chuẩn giữ nguyên qua các năm."
        else:
            nhanxet = "Điểm chuẩn biến động qua các năm."
        # Chuẩn bị bảng điểm
        lines = [f"{ng.get('nganh')} - Năm {y}: {year_points[y]}" for y in years]
        return f"{'\n'.join(lines)}\nNhận xét: {nhanxet}"
    # Điểm chuẩn
    if 'điểm chuẩn' in q or 'điểm' in q:
        if not ng.get('diem_chuan'):
            return f"{ng.get('nganh')}: Không có dữ liệu điểm chuẩn."
        ds = [d for d in ng['diem_chuan'] if (not year or str(d.get('nam')) == year)]
        if not ds:
            return f"{ng.get('nganh')}: Không có điểm chuẩn năm {year}."
        lines = [f"{ng.get('nganh')} - {d.get('phuong_thuc', '')} {d.get('nam', '')}: {d.get('diem', '')}" for d in ds]
        return '\n'.join(lines)
    # Điểm sàn
    if 'điểm sàn' in q or 'tối thiểu' in q:
        diem_san = [
            {'nam': tc.get('nam'), 'diem_san': tc.get('diem_toi_thieu')}
            for tc in ng.get('tieu_chi_xet_tuyen', []) if tc.get('diem_toi_thieu')
        ]
        if not diem_san:
            return f"{ng.get('nganh')}: Không có dữ liệu điểm sàn."
        ds = [d for d in diem_san if (not year or str(d.get('nam')) == year)]
        if not ds:
            return f"{ng.get('nganh')}: Không có điểm sàn năm {year}."
        lines = [f"{ng.get('nganh')} - Năm {d.get('nam', '')}: {d.get('diem_san', '')}" for d in ds]
        return '\n'.join(lines)
    # Chỉ tiêu
    if 'chỉ tiêu' in q:
        chi_tieu = None
        if ng.get('chi_tieu'):
            chi_tieu = ng['chi_tieu']
        elif ng.get('mo_ta'):
            m = re.search(r'Chỉ tiêu: ?(\d+)', ng['mo_ta'])
            chi_tieu = m.group(1) if m else None
        return f"{ng.get('nganh')}: Chỉ tiêu {chi_tieu if chi_tieu else 'không rõ'} sinh viên."
    # Khoa
    if 'khoa' in q:
        return f"{ng.get('nganh')}: {ng.get('khoa') if ng.get('khoa') else 'Không rõ khoa.'}"
    # Tổng hợp
    if ng.get('diem_chuan'):
        newest = ng['diem_chuan'][-1]
        chi_tieu = ng.get('chi_tieu')
        if not chi_tieu and ng.get('mo_ta'):
            m = re.search(r'Chỉ tiêu: ?(\d+)', ng['mo_ta'])
            chi_tieu = m.group(1) if m else None
        return f"{ng.get('nganh')} (Mã: {ng.get('ma_nganh')})\nKhoa: {ng.get('khoa')}\nChỉ tiêu: {chi_tieu if chi_tieu else 'không rõ'}\nĐiểm chuẩn mới nhất: {newest.get('diem', '')} ({newest.get('nam', '')})"
    return f"{ng.get('nganh')} (Mã: {ng.get('ma_nganh')})\nKhoa: {ng.get('khoa')}\nChỉ tiêu: {ng.get('chi_tieu') if ng.get('chi_tieu') else 'không rõ'}"

# Hàm sinh câu trả lời bằng LLM (Ollama local)
def generate_answer_with_llm(question, top_nganhs, history=None):
    # Chuẩn bị context ngành (system message)
    context = "\n".join([
        f"{ng.get('nganh', '')} (Mã: {ng.get('ma_nganh', '')}): {ng.get('mo_ta', '')} | Điểm chuẩn: {ng.get('diem_chuan', '') if ng.get('diem_chuan') else 'Không có'}"
        for ng in top_nganhs
    ])
    messages = []
    # Thêm system/context vào đầu (chỉ 1 lần)
    messages.append({"role": "system", "content": "Bạn là trợ lý tuyển sinh đại học, hãy trả lời NGẮN GỌN, CHÍNH XÁC bằng tiếng Việt, chỉ dựa trên thông tin context bên dưới. Nếu context không có thông tin, hãy trả lời 'Không có dữ liệu'.\n\nContext:\n" + context})
    # Thêm lịch sử hội thoại (user/assistant)
    if history:
        for turn in history[-10:]:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
    # Nếu câu hỏi mới quá ngắn hoặc mơ hồ, nối thêm câu hỏi trước vào prompt
    def is_vague(q):
        keywords = ["ngành", "điểm", "mã ngành", "tên ngành", "khoa", "chỉ tiêu", "năm", "mô tả"]
        return len(q.strip()) < 10 or not any(k in q.lower() for k in keywords)
    if history and is_vague(question):
        prev_q = history[-1]["question"]
        prev_a = history[-1]["answer"]
        user_prompt = f"Câu hỏi trước: {prev_q}\nTrả lời trước: {prev_a}\nCâu hỏi hiện tại: {question}"
    else:
        user_prompt = question
    messages.append({"role": "user", "content": user_prompt})
    try:
        requests.get("http://localhost:11434/", timeout=3)
    except Exception:
        return "[LLM ERROR] Không thể kết nối tới Ollama server (http://localhost:11434). Bạn hãy chạy lệnh 'ollama serve' trong terminal trước khi hỏi chatbot."
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "mistral",
                "messages": messages,
                "stream": False
            },
            timeout=120
        )
        data = response.json()
        return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"[LLM ERROR] {e}"

def print_help():
    print("""
HƯỚNG DẪN SỬ DỤNG CHATBOT:
- Hỏi về điểm chuẩn, chỉ tiêu, khoa, mô tả các ngành (VD: điểm chuẩn cntt 2022)
- Có thể hỏi tiếp tục, chatbot sẽ nhớ ngữ cảnh các câu trước
- Lệnh đặc biệt:
  + reset: Xóa toàn bộ lịch sử hội thoại
  + help: Hiển thị hướng dẫn này
  + exit: Thoát chatbot
""")

# Sửa hàm main để dùng RAG

def main():
    print("🤖 Chatbot Tuyển Sinh (Semantic Search + RAG LLM) - Tìm ngành thông minh!")
    print("=" * 60)
    print("Gõ 'help' để xem hướng dẫn.")
    model = SentenceTransformer(MODEL_NAME)
    nganhs = load_nganh_data()
    embeddings, index, ids = ensure_index(model, nganhs)
    history = []  # Lưu lịch sử chat
    while True:
        try:
            question = input("\n❓ Câu hỏi (hoặc 'exit', 'reset', 'help'): ").strip()
            q_lower = question.lower().strip()
            # Xử lý lệnh đặc biệt NGAY SAU KHI NHẬN INPUT
            if q_lower == 'exit':
                print("👋 Tạm biệt!")
                break
            if q_lower == 'reset':
                history = []
                print("🔄 Đã xóa lịch sử chat!")
                continue
            if q_lower == 'help':
                print_help()
                continue
            if not question:
                print("💡 Vui lòng nhập câu hỏi!")
                continue
            # Nếu là câu đầu tiên mà mơ hồ, yêu cầu nhập rõ hơn
            def is_vague(q):
                keywords = ["ngành", "điểm", "mã ngành", "tên ngành", "khoa", "chỉ tiêu", "năm", "mô tả"]
                return len(q.strip()) < 10 or not any(k in q.lower() for k in keywords)
            if not history and is_vague(question):
                print("🤖 Bạn vui lòng nhập rõ hơn tên ngành, mã ngành, năm hoặc mô tả chi tiết hơn!")
                continue
            # Trả lời từ dữ liệu nếu tìm được ngành phù hợp
            ng, score = find_best_nganh(question, model, index, nganhs, ids, top_k=1, min_score=0.5)
            if ng:
                ans = answer(question, ng, score)
                print(f"\n🤖 {ans}")
                history.append({"question": question, "answer": ans})
                continue
            # Nếu không tìm được ngành phù hợp, fallback sang LLM với top-k ngành gần nhất
            q_emb = model.encode([question], normalize_embeddings=True)
            q_emb = np.array(q_emb).astype('float32')
            if q_emb.ndim == 1:
                q_emb = np.expand_dims(q_emb, 0)
            D, I = index.search(q_emb, TOP_K)
            top_nganhs = [nganhs[ids[i]] for i in I[0]]
            if not top_nganhs or D[0][0] < 0.5:
                print("\n🤖 Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. Bạn vui lòng nhập rõ hơn tên ngành, mã ngành hoặc mô tả chi tiết hơn?")
                continue
            llm_answer = generate_answer_with_llm(question, top_nganhs, history)
            if llm_answer:
                print(f"\n🤖 [RAG LLM] {llm_answer}")
                history.append({"question": question, "answer": llm_answer})
            else:
                ng = top_nganhs[0]
                score = D[0][0]
                ans = answer(question, ng, score)
                print(f"\n[Score: {score:.3f}] {ans}")
                history.append({"question": question, "answer": ans})
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            print("💡 Thử câu hỏi khác")

if __name__ == "__main__":
    main() 
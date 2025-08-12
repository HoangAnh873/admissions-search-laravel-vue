import requests
import os

# Địa chỉ endpoint export của Laravel (sửa lại nếu deploy lên server thật)
EXPORT_URL = 'http://127.0.0.1:8000/export-chatbot-data'

# Đường dẫn file output (luôn lưu vào chatbot_ai/data_chatbot.json)
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'data_chatbot.json')

# Danh sách file cache cần xóa
CACHE_FILES = [
    'nganh_embeddings.npy',
    'nganh_faiss.index',
    'nganh_ids.json',
]

def update_data_chatbot():
    try:
        response = requests.get(EXPORT_URL, timeout=30)
        if response.status_code == 200:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ Đã cập nhật {OUTPUT_FILE} thành công!")
            # Xóa cache embeddings/index
            for fname in CACHE_FILES:
                fpath = os.path.join(os.path.dirname(__file__), fname)
                if os.path.exists(fpath):
                    os.remove(fpath)
                    print(f"🗑️  Đã xóa cache: {fname}")
        else:
            print(f"❌ Lỗi khi lấy dữ liệu: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi khi kết nối tới API: {e}")

if __name__ == '__main__':
    update_data_chatbot() 
# 🤖 Chatbot Tuyển Sinh - Sentence Transformers + FAISS

Chatbot thông minh sử dụng **sentence-transformers** và **FAISS** để tìm kiếm thông tin tuyển sinh đại học.

## ✨ Tính năng

- 🔍 **Tìm kiếm thông minh**: Sử dụng sentence-transformers đa ngôn ngữ
- ⚡ **Tốc độ nhanh**: FAISS vector search
- 💰 **Miễn phí**: Không cần API key OpenAI
- 🇻🇳 **Hỗ trợ tiếng Việt**: Model đa ngôn ngữ
- 📊 **Dữ liệu phong phú**: Thông tin tuyển sinh chi tiết

## 🚀 Cài đặt

### Phiên bản 1: Sentence Transformers (Khuyến nghị)

1. **Cài đặt thư viện**:
```bash
pip install -r requirements.txt
```

2. **Chạy chatbot**:
```bash
python demo.py
```

### Phiên bản 2: Tìm kiếm đơn giản (Không cần cài đặt thêm)

Nếu gặp lỗi NumPy, sử dụng phiên bản đơn giản:

```bash
python demo_simple.py
```

## 🔧 Khắc phục lỗi

### Lỗi NumPy
Nếu gặp lỗi `RuntimeError: Numpy is not available` hoặc lỗi tương thích NumPy:

**Giải pháp 1**: Sử dụng phiên bản đơn giản
```bash
python demo_simple.py
```

**Giải pháp 2**: Cài đặt lại NumPy
```bash
pip uninstall numpy -y
pip install numpy==2.0.0
```

**Giải pháp 3**: Sử dụng virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 💡 Cách sử dụng

Chatbot hỗ trợ các loại câu hỏi:

- **Điểm chuẩn**: "Điểm chuẩn ngành Khoa học máy tính năm 2023?"
- **Thông tin ngành**: "Ngành Công nghệ thông tin học gì?"
- **Chỉ tiêu**: "Chỉ tiêu ngành Nông học bao nhiêu?"
- **Khoa**: "Khoa nào đào tạo ngành IT?"

## 🔧 Cấu hình

### Kết nối CSDL MySQL (mới)
- Tạo file `db_config.py` trong thư mục `chatbot_ai/` với nội dung:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_db',
    'port': 3306
}
```
- Đảm bảo đã tạo các bảng ngành, điểm chuẩn, chỉ tiêu... trong CSDL.
- Thay đổi chatbot để lấy dữ liệu từ CSDL thay vì file tĩnh.

### Model Embedding (demo.py)
- **Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Đặc điểm**: Đa ngôn ngữ, nhẹ, nhanh
- **Device**: CPU (có thể chuyển sang GPU nếu có)

### Tìm kiếm đơn giản (demo_simple.py)
- **Engine**: Tìm kiếm từ khóa thông thường
- **Ưu điểm**: Không cần cài đặt thêm thư viện
- **Nhược điểm**: Độ chính xác thấp hơn

## 📁 Cấu trúc dự án

```
chatbot_ai/
├── demo.py              # Chatbot với sentence-transformers
├── demo_simple.py       # Chatbot đơn giản (không cần cài đặt)
├── data_chatbot.txt     # Dữ liệu tuyển sinh
├── requirements.txt     # Thư viện cần thiết
└── README.md           # Hướng dẫn này
```

## 🎯 So sánh hai phiên bản

| Tính năng | demo.py | demo_simple.py |
|-----------|---------|----------------|
| **Độ chính xác** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Tốc độ** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cài đặt** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Tương thích** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Dung lượng** | ~500MB | ~1MB |

## 🛠️ Tùy chỉnh

### Thay đổi model embedding (demo.py):
```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # Model khác
    model_kwargs={'device': 'cuda'},  # Sử dụng GPU
)
```

### Thay đổi số kết quả tìm kiếm (demo_simple.py):
```python
results = self.search(query, top_k=5)  # 5 kết quả
```

## 📝 Ghi chú

- **demo.py**: Lần đầu chạy sẽ tải model (~100MB)
- **demo_simple.py**: Không cần tải model, chạy ngay
- Cả hai đều cần kết nối internet để tải model lần đầu (demo.py)
- Dữ liệu được lưu trong vector store để tìm kiếm nhanh

## 🆘 Hỗ trợ

Nếu gặp lỗi:
1. Thử `python demo_simple.py` trước
2. Kiểm tra Python version (khuyến nghị 3.8-3.11)
3. Cài đặt lại thư viện: `pip install -r requirements.txt --force-reinstall` 
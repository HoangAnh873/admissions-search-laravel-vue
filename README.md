# 🎓 Hệ thống Tra cứu Thông tin Tuyển sinh - Trường Đại học Cần Thơ

## 📌 Giới thiệu
Đề tài này được phát triển nhằm hỗ trợ thí sinh tra cứu thông tin tuyển sinh của Trường Đại học Cần Thơ một cách **nhanh chóng, chính xác và trực quan**.  
Hệ thống tích hợp **chatbot AI** để tư vấn tuyển sinh tự động 24/7, giúp thí sinh dễ dàng tiếp cận thông tin cần thiết.

## 🚀 Tính năng chính
### 👨‍🎓 Dành cho thí sinh (Public User)
- Tra cứu ngành học theo **mã ngành, tên ngành**.  
- Xem **điểm chuẩn, chỉ tiêu** theo năm và phương thức xét tuyển.  
- Tìm kiếm theo **tổ hợp môn, khoảng điểm**.  
- Tư vấn tự động qua **Chatbot AI (RAG + LangChain + FAISS)**.  
- Xem chi tiết mô tả ngành, cơ hội việc làm, chương trình đào tạo.  

### 🛠️ Dành cho quản trị viên (Admin)
- Quản lý thông tin ngành học, điểm chuẩn, phương thức xét tuyển.  
- Quản lý dữ liệu huấn luyện chatbot.  
- Thêm/sửa/xóa dữ liệu dễ dàng qua giao diện web.  
- Báo cáo thống kê, giám sát hiệu quả chatbot.  

## 🏗️ Kiến trúc hệ thống
- **Frontend:** Vue.js 3, HTML5, CSS3, JavaScript.  
- **Backend:** Laravel 10 (PHP 8.x).  
- **Database:** MySQL 8.0.  
- **Chatbot AI:** Python 3.12, LangChain, FAISS, MySQL Connector.  
- **Web server:** Apache (OSPanel).  

## ⚙️ Cách cài đặt
```bash
# Clone project
git clone https://github.com/HoangAnh873/admissions-search-laravel-vue.git

# Cài đặt backend (Laravel)
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate --seed
php artisan serve

# Cài đặt frontend (Vue.js)
cd vuejsversion1
npm install
npm run dev

# Cài đặt chatbot (Python)
cd chatbot_ai
pip install -r requirements.txt
python api_server.py

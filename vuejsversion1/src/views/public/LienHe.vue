<template>
  <public-layout>
    <div class="page-container">
      <h1 class="page-title">Liên hệ</h1>
      
      <div class="lien-he-content">
        <section class="info-section">
          <h2 class="section-title">Thông tin liên hệ</h2>
          <div class="grid-container">
            <div class="card">
              <div class="contact-info">
                <div class="info-item">
                  <i class="fas fa-map-marker-alt"></i>
                  <div class="info-content">
                    <h3 class="card-title">Địa chỉ</h3>
                    <p class="card-text">Khu II, Đường 3/2, P. Xuân Khánh, Q. Ninh Kiều, TP. Cần Thơ</p>
                  </div>
                </div>
                <div class="info-item">
                  <i class="fas fa-phone"></i>
                  <div class="info-content">
                    <h3 class="card-title">Điện thoại</h3>
                    <p class="card-text">(0292) 3 872 157</p>
                  </div>
                </div>
                <div class="info-item">
                  <i class="fas fa-envelope"></i>
                  <div class="info-content">
                    <h3 class="card-title">Email</h3>
                    <p class="card-text">dhct@ctu.edu.vn</p>
                  </div>
                </div>
                <div class="info-item">
                  <i class="fas fa-clock"></i>
                  <div class="info-content">
                    <h3 class="card-title">Giờ làm việc</h3>
                    <p class="card-text">Thứ 2 - Thứ 6: 7:00 - 17:00</p>
                  </div>
                </div>
                <div class="info-item">
                  <i class="fas fa-globe"></i>
                  <div class="info-content">
                    <h3 class="card-title">Website</h3>
                    <p class="card-text">
                      <a href="https://www.ctu.edu.vn" target="_blank">www.ctu.edu.vn</a>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div class="card">
              <h3 class="card-title">Gửi tin nhắn</h3>
              <form class="contact-form">
                <div class="form-group">
                  <input type="text" class="form-control" placeholder="Họ và tên" required>
                </div>
                <div class="form-group">
                  <input type="email" class="form-control" placeholder="Email" required>
                </div>
                <div class="form-group">
                  <input type="tel" class="form-control" placeholder="Số điện thoại" required>
                </div>
                <div class="form-group">
                  <select class="form-control" required>
                    <option value="">Chọn khoa/ban liên hệ</option>
                    <option value="1">Phòng Đào tạo</option>
                    <option value="2">Phòng Công tác Sinh viên</option>
                    <option value="3">Phòng Khoa học Công nghệ</option>
                    <option value="4">Phòng Hợp tác Quốc tế</option>
                    <option value="5">Phòng Tổ chức Hành chính</option>
                    <option value="6">Phòng Kế hoạch Tài chính</option>
                    <option value="7">Phòng Quản lý Đào tạo</option>
                  </select>
                </div>
                <div class="form-group">
                  <textarea class="form-control" rows="3" placeholder="Nội dung tin nhắn" required></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Gửi tin nhắn</button>
              </form>
            </div>
          </div>
        </section>

        <section class="map-section">
          <h2 class="section-title">Bản đồ</h2>
          <div class="card">
            <iframe 
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3928.841123355135!2d105.7699534!3d10.029408!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31a0883d69f0a5f5%3A0xfcfc6e5d7c0557a3!2zVHLGsOG7nW5nIMSQ4bqhaSBo4buNYyBD4bqnbiBUaMah!5e0!3m2!1svi!2s!4v1647881234567!5m2!1svi!2s&zoom=14&center=10.0389,105.7761&markers=color:red%7Clabel:CTU%7C10.029408,105.7699534" 
              width="100%" 
              height="450" 
              style="border:0;" 
              allowfullscreen="" 
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade">
            </iframe>
          </div>
        </section>
      </div>
    </div>
  </public-layout>
</template>

<script>
import PublicLayout from '@/components/public/layout.vue'
import '@/assets/public/css/common.css'

export default {
  name: 'LienHePage',
  components: {
    PublicLayout
  }
}
</script>

<style scoped>
.lien-he-content {
  max-width: 1000px;
  margin: 0 auto;
}

.info-section, .map-section {
  margin-bottom: 4rem;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.card {
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-title {
  color: #333;
  margin-bottom: 1rem;
}

.card-text {
  color: #666;
  margin-bottom: 0.5rem;
}

.contact-info {
  display: grid;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.info-item i {
  color: #007bff;
  width: 24px;
  font-size: 1.2rem;
  margin-top: 0.25rem;
}

.info-content {
  flex: 1;
}

.info-content a {
  color: #007bff;
  text-decoration: none;
}

.info-content a:hover {
  text-decoration: underline;
}

.contact-form {
  display: grid;
  gap: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #e9ecef;
  border-radius: 4px;
  transition: border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
}

.btn-primary {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  border: none;
  cursor: pointer;
  width: 100%;
  font-size: 1rem;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.map-section .card {
  padding: 0;
  overflow: hidden;
}

.map-section iframe {
  display: block;
  width: 100%;
  height: 450px;
  border: none;
}

@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
  
  .card {
    padding: 1.5rem;
  }
  
  .info-item {
    gap: 0.8rem;
  }
  
  .info-content .card-title {
    font-size: 1rem;
  }
  
  .info-content .card-text {
    font-size: 0.9rem;
  }
  
  .form-control {
    padding: 0.7rem;
    font-size: 0.9rem;
  }
  
  .btn-primary {
    padding: 0.7rem 1.2rem;
    font-size: 0.95rem;
  }
}
</style> 
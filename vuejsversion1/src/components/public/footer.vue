<template>
  <footer class="public-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h3>Về chúng tôi</h3>
          <p>Hệ thống thông tin tuyển sinh đại học, cung cấp thông tin chi tiết về các ngành học, tiêu chuẩn tuyển sinh và quy trình đăng ký.</p>
        </div>
        <div class="footer-section">
          <h3>Liên kết nhanh</h3>
          <ul>
            <li><router-link to="/">Trang chủ</router-link></li>
            <li><router-link to="/tuyen-sinh">Tuyển sinh</router-link></li>
            <li><router-link to="/nganh-hoc">Ngành học</router-link></li>
            <li><router-link to="/tieu-chuan">Tiêu chuẩn</router-link></li>
            <li><router-link to="/lien-he">Liên hệ</router-link></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3>Thông tin liên hệ</h3>
          <p>Email: tuyensinh@example.com</p>
          <p>Điện thoại: 038 278 7268</p>
          <p>Địa chỉ: Đường 3/2, Phường An Khánh, Quận Ninh Kiều, TP. Cần Thơ</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>Hệ thống thông tin tuyển sinh 2025 </p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'PublicFooter'
}
</script>

<style scoped>
.public-footer {
  background-color: #f8f9fa;
  padding: 3rem 0 1rem;
  margin-top: auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3 {
  color: #333;
  margin-bottom: 1rem;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 0.5rem;
}

.footer-section a {
  text-decoration: none;
  color: #666;
  transition: color 0.3s ease;
}

.footer-section a:hover {
  color: #007bff;
}

.footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid #dee2e6;
  color: #666;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
  }
}
</style> 
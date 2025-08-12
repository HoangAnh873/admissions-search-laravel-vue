<template>
  <public-layout>
    <!-- Hero Banner Section -->
    <section class="hero-banner">
      <div class="hero-overlay">
        <div class="hero-content">
          <h1 class="hero-title">Thông tin tuyển sinh đại học Cần Thơ</h1>
          <p class="hero-subtitle">Hệ thống thông tin tra cứu tuyển sinh - Cổng thông tin của Đại học Cần Thơ</p>
          <div class="hero-buttons">
            <router-link to="/tuyen-sinh" class="btn btn-primary btn-large">Tìm hiểu tuyển sinh</router-link>
            <router-link to="/diem-chuan-tieu-chuan" class="btn btn-outline btn-large">Tra cứu điểm chuẩn & tiêu chuẩn</router-link>
          </div>
        </div>
      </div>
    </section>

    <div class="page-container">
      <div class="home-content">
        <section class="features-section">
          <h2 class="section-title">Tính năng chính</h2>
          <div class="grid-container">
            <div class="card">
              <h3 class="card-title">Tuyển sinh</h3>
              <p class="card-text">Thông tin chi tiết về các phương thức tuyển sinh và quy trình đăng ký</p>
              <router-link to="/tuyen-sinh" class="btn btn-primary">Xem thêm</router-link>
            </div>
            <div class="card">
              <h3 class="card-title">Ngành học</h3>
              <p class="card-text">Danh sách các ngành học và thông tin chi tiết về từng ngành</p>
              <router-link to="/nganh-hoc" class="btn btn-primary">Xem thêm</router-link>
            </div>
            <div class="card">
              <h3 class="card-title">Điểm chuẩn</h3>
              <p class="card-text">Tra cứu điểm chuẩn và tiêu chuẩn xét tuyển các năm theo ngành học</p>
              <router-link to="/diem-chuan-tieu-chuan" class="btn btn-primary">Xem thêm</router-link>
            </div>
          </div>
        </section>
      </div>
    </div>
    <div style="position: fixed; bottom: 32px; right: 32px; z-index: 9999;">
      <Chatbot />
    </div>
  </public-layout>
</template>

<script>
import PublicLayout from '@/components/public/layout.vue'
import Chatbot from '@/components/public/Chatbot.vue'
import '@/assets/public/css/common.css'

export default {
  name: 'HomePage',
  components: {
    PublicLayout,
    Chatbot
  }
}
</script>

<style scoped>
.home-content {
  max-width: 1000px;
  margin: 0 auto;
}

.features-section {
  margin-bottom: 4rem;
}

.card {
  text-align: center;
  padding: 2rem;
}

.card-title {
  color: #333;
  margin-bottom: 1rem;
}

.card-text {
  color: #666;
  margin-bottom: 1.5rem;
}

.btn-primary {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #0056b3;
}
</style> 
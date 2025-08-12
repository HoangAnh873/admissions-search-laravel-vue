<template>
  <header class="public-header">
    <nav class="navbar">
      <div class="container">
        <div class="navbar-menu">
          <router-link to="/" class="nav-item">
            <i class="fas fa-home"></i>
            <span>Trang chủ</span>
          </router-link>
          <router-link to="/tuyen-sinh" class="nav-item">
            <i class="fas fa-graduation-cap"></i>
            <span>Tuyển sinh</span>
          </router-link>
          <router-link to="/nganh-hoc" class="nav-item">
            <i class="fas fa-book"></i>
            <span>Ngành học</span>
          </router-link>
          <router-link to="/diem-chuan-tieu-chuan" class="nav-item">
            <i class="fas fa-check-circle"></i>
            <span>Điểm chuẩn</span>
          </router-link>
          <router-link to="/lien-he" class="nav-item">
            <i class="fas fa-envelope"></i>
            <span>Liên hệ</span>
          </router-link>
        </div>
        <div class="navbar-brand">
          <router-link to="/" class="logo">
            <img src="/logo-ctu2.png" alt="Logo" class="logo">
          </router-link>
        </div>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'PublicHeader'
}
</script>

<style scoped>
.public-header {
  background-color: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
}

.navbar {
  padding: 1rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand {
  display: flex;
  align-items: center;
}

.logo img {
  height: 60px;
  width: auto;
  max-width: 200px;
  transition: transform 0.2s ease;
}

.logo:hover img {
  transform: scale(1.05);
}

.navbar-menu {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-item {
  text-decoration: none;
  color: #2c3e50;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
}

.nav-item i {
  font-size: 1rem;
  color: #007bff;
  transition: transform 0.3s ease;
}

.nav-item:hover {
  color: #007bff;
  background: #f8f9fa;
}

.nav-item:hover i {
  transform: translateY(-2px);
}

.nav-item.router-link-active {
  color: #007bff;
  background: #f8f9fa;
}

.nav-item.router-link-active i {
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .navbar-menu {
    display: none;
  }
  
  .container {
    justify-content: center;
  }
  
  .navbar-brand {
    margin: 0 auto;
  }
}
</style> 
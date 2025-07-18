<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router';
import { useStore } from 'vuex'


const email = ref('')
const password = ref('')
const emailError = ref('')
const passwordError = ref('')
const router = useRouter()
const store = useStore()


const handleLogin = async () => {
  
  emailError.value = '';
  passwordError.value = '';

  if (!email.value) {
    emailError.value = 'Vui lòng nhập email';
    return;
  }
  if (!password.value) {
    passwordError.value = 'Vui lòng nhập mật khẩu';
    return;
  }

  try {
    const result = await store.dispatch('auth/login', {
      email: email.value,
      password: password.value,
    })

    if (result.success) {
      sessionStorage.setItem('showLoginSuccess', true) // gửi yêu cầu thông báo qua dashboard
      router.push({ name: 'dashboard.index' }) 
    }
  } catch (err) {
    console.error(err);
    if (err.response) {
      const errors = err.response.data?.data || {};
      if (errors.email) emailError.value = errors.email[0];
      if (errors.password) passwordError.value = errors.password[0];
      if (!errors.email && !errors.password && err.response.status === 401) {
        emailError.value = 'Email hoặc mật khẩu không đúng.';
      } else if (err.response.status === 419) {
        emailError.value = 'Phiên làm việc hết hạn, vui lòng tải lại trang.';
      }
    } else {
      emailError.value = 'Đã xảy ra lỗi, vui lòng thử lại.';
    }
  }
}

</script>

<template>
  <div class="login-container">
    <h2>ĐĂNG NHẬP</h2>
    <div class="welcome-text">Hệ thống tuyển sinh trường Đại Học Cần Thơ</div>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">Email</label>
        <input type="text" id="email" v-model="email"  autocomplete="username"/>
        <div v-if="emailError" class="error-message">{{ emailError }}</div>
      </div>

      <div class="form-group">
        <label for="password">Mật khẩu</label>
        <input type="password" id="password" v-model="password" autocomplete="current-password"/>
        <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
      </div>

      <div class="button-wrapper">
        <button type="submit">Đăng nhập</button>
        <router-link to="/dashboard" class="forgot-password">Quên mật khẩu</router-link>
      </div>
    </form>
  </div>
</template>


<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f0f0f0;
}

h2 {
  text-align: center;
  /* margin-bottom: 0px; */
}
.welcome-text {
  text-align: center;
  margin-bottom: 24px;
  margin-top: 0px;
  font-weight: 500;
  color: #3b82f6;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.button-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px; /* khoảng cách giữa nút và liên kết */
  margin-top: 20px;
}

.forgot-password{
  color: #3b82f6;
}

button {
  padding: 8px 24px;
  font-size: 14px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

button:hover {
  background-color: #2563eb;
  transform: scale(1.05);
}

input:focus {
  outline: none;
}


</style>

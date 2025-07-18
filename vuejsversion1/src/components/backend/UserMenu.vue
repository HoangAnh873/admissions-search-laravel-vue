<script setup>
import { ref } from 'vue'
import loopyImg from '@/assets/backend/img/avatar2.jpg'
const showDropdown = ref(false)
</script>

<template>
  <div class="user-menu" @click="showDropdown = !showDropdown">
    <img :src="loopyImg" alt="Avatar" class="avatar" />
    <div v-if="showDropdown" class="dropdown">
      <ul>
        <li><a href="#">Thông tin</a></li>
        <li><a href="#">Cài đặt</a></li>
        <li><a href="#" @click="$emit('logout')">Đăng xuất</a></li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #e5e7eb;
  object-fit: cover;
  transition: box-shadow 0.3s;
}

.avatar:hover {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.5); /* ring green-500 */
}

.dropdown {
  position: absolute;
  top: 115%;
  right: 0;
  min-width: 180px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  z-index: 100;
  animation: fadeIn 0.2s ease-in-out;
}

.dropdown::before {
  content: '';
  position: absolute;
  top: -8px;
  right: 14px;
  border-width: 8px;
  border-style: solid;
  border-color: transparent transparent #ffffff transparent;
}

.dropdown ul {
  list-style: none;
  margin: 0;
  padding: 8px 0;
}

.dropdown li {
  padding: 10px 16px;
  font-size: 14px;
  color: #374151; /* gray-700 */
  transition: background-color 0.2s, color 0.2s;
}

.dropdown li:hover {
  background-color: #f3f4f6; /* gray-100 */
  color: #1f2937; /* gray-800 */
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown a {
  display: block;
  width: 100%;
  text-decoration: none;
  color: #374151; /* gray-700 */
  font-weight: 500;
  transition: background-color 0.2s, color 0.2s;
}

.dropdown a:hover {
  background-color: #f9fafb; /* light hover */
  color: #1f2937; /* gray-800 */
}

</style>

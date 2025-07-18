<script setup>
import { ref } from 'vue'

const showDropdown = ref(false)

const notifications = ref([
  { id: 1, message: 'Bạn có hợp đồng mới cần duyệt.' },
  { id: 2, message: 'Khách thuê đã thanh toán tiền phòng.' },
  { id: 3, message: 'Hệ thống sẽ bảo trì lúc 22h.' },
])
</script>

<template>
  <div class="notification-wrapper" @click="showDropdown = !showDropdown">
    <button class="bell" aria-label="Thông báo">
      <svg
        class="icon"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <span class="badge">{{ notifications.length }}</span>
    </button>

    <div v-if="showDropdown" class="dropdown">
      <ul>
        <li v-for="n in notifications" :key="n.id">
          {{ n.message }}
        </li>
        <li v-if="notifications.length === 0" class="no-notification">
          Không có thông báo nào.
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.notification-wrapper {
  position: relative;
}

.bell {
  position: relative;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  padding: 8px;  /* Giảm padding để chuông nhỏ lại */
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bell:hover {
  background-color: #f3f4f6;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.5); /* ring green-500 */
}


.icon {
  width: 20px;
  height: 20px;
  color: #374151;
}

.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 9999px;
  line-height: 1;
}

/* Dropdown */
.dropdown {
  position: absolute;
  top: 120%;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 6px;
  width: 240px;
  z-index: 10;
}

.dropdown ul {
  list-style: none;
  margin: 0;
  padding: 8px 0;
  max-height: 260px;
  overflow-y: auto;
}

.dropdown li {
  padding: 10px 16px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown li:hover {
  background-color: #f9fafb;
}

.no-notification {
  text-align: center;
  color: #9ca3af;
  font-style: italic;
}
</style>

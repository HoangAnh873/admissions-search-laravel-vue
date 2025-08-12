<!-- src/components/backend/Navbar.vue -->
<script setup>
import Breadcrumb from './Breadcrumb.vue'
import NotificationBell from './NotificationBell.vue'
import UserMenu from './UserMenu.vue'

import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

// Cập nhật breadcrumbItems và title động dựa trên route
const routeMeta = {
  'dashboard': {
    title: 'Dashboard',
    breadcrumbs: [
      { label: 'Home', to: '/' },
      { label: 'Dashboard', to: '/dashboard' }
    ]
  },
  'tuyen-sinh': {
    title: 'Tuyển sinh',
    breadcrumbs: [
      { label: 'Home', to: '/' },
      { label: 'Tuyển sinh', to: '/tuyen-sinh' }
    ]
  },
  'danh-muc': {
    title: 'Danh mục hệ thống',
    breadcrumbs: [
      { label: 'Home', to: '/' },
      { label: 'Danh mục', to: '/danh-muc' }
    ]
  },
  'thong-ke': {
    title: 'Thống kê',
    breadcrumbs: [
      { label: 'Home', to: '/' },
      { label: 'Thống kê', to: '/thong-ke' }
    ]
  }
}

const breadcrumbItems = computed(() => {
  const currentRoute = route.name || 'dashboard'
  return routeMeta[currentRoute]?.breadcrumbs || [
    { label: 'Home', to: '/' },
    { label: 'Dashboard', to: '/dashboard' }
  ]
})

const pageTitle = computed(() => {
  const currentRoute = route.name || 'dashboard'
  return routeMeta[currentRoute]?.title || 'Dashboard'
})
</script>

<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Trái: Tiêu đề + breadcrumb -->
      <div class="navbar-left">
        <h1 class="navbar-title">{{ pageTitle }}</h1>
        <Breadcrumb :items="breadcrumbItems" />
      </div>

      <!-- Phải: Các action -->
      <div class="navbar-right">
        <NotificationBell />
        <UserMenu @logout="$emit('logout')" />
      </div>
    </div>
  </nav>
</template>


<style scoped>
.navbar {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 12px 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-left {
  display: flex;
  flex-direction: column;
}

.navbar-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>

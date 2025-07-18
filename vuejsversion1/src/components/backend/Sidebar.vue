<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'

import loopyImg from '@/assets/backend/img/avatar2.jpg'
import vnSidebar from '@/lang/vn/sidebar'
import enSidebar from '@/lang/en/sidebar'

// Lấy router và i18n
const router = useRouter()
const route = useRoute()
const { locale } = useI18n()
const emit = defineEmits(['update-title'])

// Tùy theo locale, lấy đúng file sidebar
const sidebars = {
  vn: vnSidebar,
  en: enSidebar
}

const menuItems = ref([])
const openMenu = ref(null)

// Gán menuItems theo ngôn ngữ hiện tại
const loadSidebar = () => {
  menuItems.value = sidebars[locale.value] || vnSidebar
  // Sau khi load menu, kiểm tra và mở menu cha nếu cần
  checkAndOpenParentMenu()
}

// Hàm kiểm tra và mở menu cha
const checkAndOpenParentMenu = () => {
  for (const item of menuItems.value) {
    if (item.children) {
      const found = item.children.some(child => child.link === route.path)
      if (found) {
        openMenu.value = item.name
        break
      }
    }
  }
}

// Load ban đầu
onMounted(() => {
  loadSidebar()
})

// Khi đổi ngôn ngữ thì cập nhật lại menu
watch(locale, () => {
  loadSidebar()
})

// Watch route để tự động mở menu cha khi route thay đổi
watch(() => route.path, () => {
  checkAndOpenParentMenu()
}, { immediate: true })

// Thông tin user
const user = {
  name: 'Hoàng Anh',
  avatar: loopyImg
}

// Kiểm tra xem menu item có active không
const isMenuItemActive = (item) => {
  if (item.link) {
    return route.path === item.link
  }
  if (item.children) {
    return item.children.some(child => route.path === child.link)
  }
  return false
}

// Kiểm tra xem submenu item có active không
const isSubMenuItemActive = (link) => {
  return route.path === link
}

// Hàm khi click menu
const handleMenuClick = (item) => {
  if (item.children) {
    openMenu.value = openMenu.value === item.name ? null : item.name
  } else {
    emit('update-title', item.name) //  emit tên menu
    router.push(item.link)
  }
}

const handleChildClick = (link, name) => {
  emit('update-title', name) //  emit tên submenu
  router.push(link)
}

// Thêm computed property để tìm menu cha của route hiện tại
const findParentMenu = computed(() => {
  for (const item of menuItems.value) {
    if (item.children) {
      const found = item.children.some(child => child.link === route.path)
      if (found) {
        return item.name
      }
    }
  }
  return null
})

// Watch route để tự động mở menu cha khi route thay đổi
watch(() => route.path, (newPath) => {
  const parentMenu = findParentMenu.value
  if (parentMenu) {
    openMenu.value = parentMenu
  }
}, { immediate: true })
</script>

<template>
  <aside id="sidebar" class="app-sidebar">
    <!-- Phần user info -->
    <div class="user-info">
      <img :src="user.avatar" alt="Avatar" class="avatar" />
      <div class="username">{{ user.name }}</div>
      <div>Admin</div>
    </div>

    <hr class="divider" />

    <!-- Menu -->
    <h2 class="sidebar-title">Menu</h2>

    <ul class="sidebar-menu">
      <li 
        v-for="item in menuItems" 
        :key="item.name" 
        class="sidebar-item"
        :class="{ 'active': isMenuItemActive(item) }"
      >
        <div 
          class="uk-flex uk-flex-middle uk-text-white cursor-pointer" 
          @click="handleMenuClick(item)"
        >
          <span :uk-icon="item.icon" class="uk-margin-small-right"></span>
          <span class="label">{{ item.name }}</span>

          <template v-if="item.children">
            <span 
              class="uk-icon uk-margin-small-left chevron"
              :uk-icon="openMenu === item.name ? 'chevron-down' : 'chevron-left'"
            ></span>
          </template>
        </div>

        <!-- Submenu -->
        <transition name="slide-fade">
          <ul 
            v-if="item.children && openMenu === item.name" 
            class="sidebar-submenu"
          >
            <li 
              v-for="child in item.children" 
              :key="child.name" 
              class="sidebar-subitem"
              :class="{ 'active': isSubMenuItemActive(child.link) }"
              @click="handleChildClick(child.link, child.name)"
            >
              <div class="sidebar-subitem-label">
                {{ child.name }}
              </div>
            </li>
          </ul>
        </transition>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
/* ==== Sidebar chính ==== */
.app-sidebar {
  width: 260px;
  height: 100vh;
  background-color: #1e293b;
  color: white;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

/* ==== Thông tin người dùng ==== */
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 16px;
  flex-shrink: 0;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid white;
  margin-bottom: 8px;
  object-fit: cover;
}

.username {
  font-size: 15px;
  font-weight: 500;
  text-align: center;
  color: #fff;
}

/* ==== Đường gạch phân cách ==== */
.divider {
  border: none;
  height: 1px;
  background-color: #334155;
  margin: 0;
  flex-shrink: 0;
}

/* ==== Tiêu đề menu ==== */
.sidebar-title {
  font-size: 16px;
  font-weight: bold;
  padding: 14px 16px;
  margin: 0;
  color: #b0c4d0;
  flex-shrink: 0;
}

/* ==== Danh sách menu chính ==== */
.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ==== Item của menu chính ==== */
.sidebar-item {
  padding: 10px 16px;
  border-radius: 6px;
  transition: background 0.3s ease, color 0.3s ease;
  position: relative;
  cursor: pointer;
  margin: 4px 8px;
}

.sidebar-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #c1d3e4;
}

.sidebar-item .uk-icon:first-child {
  margin-right: 12px;
  font-size: 18px;
  flex-shrink: 0;
  transition: transform 0.2s;
  vertical-align: middle;
}

/* ==== Nhãn văn bản của item ==== */
.label {
  flex-grow: 1;
  font-size: 15px;
  padding-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ==== Icon mũi tên mở rộng menu con ==== */
.chevron {
  opacity: 0.7;
  transition: transform 0.3s, opacity 0.3s;
  vertical-align: middle;
  position: absolute;
  right: 16px;
}

/* ==== Link bên trong menu (ít dùng trong file này) ==== */
.sidebar-item a {
  color: inherit;
  text-decoration: none;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.sidebar-item a:hover {
  background-color: #334155; /* Hover menu */
}

.icon {
  margin-right: 12px;
  font-size: 18px;
  vertical-align: middle;
}

/* ==== Submenu (menu con) ==== */
.sidebar-submenu {
  padding-left: 20px;
  margin-top: 6px;
  list-style: none;
}

/* ==== Item trong submenu ==== */
.sidebar-subitem {
  margin: 4px 0;
  border-radius: 8px;
  transition: background-color 0.25s, padding-left 0.25s;
  cursor: pointer;
}

.sidebar-subitem:hover {
  background-color: rgba(255, 255, 255, 0.08);
  padding-left: 2px;
}

/* ==== Nhãn văn bản của item con ==== */
.sidebar-subitem-label {
  font-size: 14px;
  color: #ffffff;
  padding: 8px 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ==== Trạng thái active cho menu chính ==== */
.sidebar-item.active {
  background-color: rgba(255, 255, 255, 0.15);
}

.sidebar-item.active > div {
  color: #60a5fa;
}

/* ==== Trạng thái active cho submenu ==== */
.sidebar-subitem.active {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-subitem.active .sidebar-subitem-label {
  color: #60a5fa;
}

/* ==== Custom scrollbar ==== */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* ==== Hiệu ứng mở rộng submenu ==== */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

<!-- src/components/backend/Breadcrump.vue -->
<script setup>
const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => [],
  },
})
</script>

<template>
  <ul class="breadcrumb">
    <li v-for="(item, index) in items" :key="index">
      <router-link :to="item.to">{{ item.label }}</router-link>
    </li>
  </ul>
</template>

<style scoped>
.breadcrumb {
  display: flex;
  gap: 0.5rem;
  list-style: none;
  font-size: 14px;
  padding: 0;
  margin: 0;
}

.breadcrumb li {
  display: inline-flex;
}

.breadcrumb li a {
  color: #6b7280; /* Màu nhạt cho các link */
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb li a:hover {
  color: #3b82f6; /* Màu khi hover để nổi bật */
}

.breadcrumb li.router-link-active a {
  color: #1e293b; /* Màu đậm cho trang đang ở */
  font-weight: 600; /* Làm đậm chữ khi đang ở trang này */
}

.breadcrumb li::after {
  content: '/';
  margin: 0 0.5rem;
  color: #d1d5db;
}

.breadcrumb li:last-child::after {
  content: '';
}
</style>

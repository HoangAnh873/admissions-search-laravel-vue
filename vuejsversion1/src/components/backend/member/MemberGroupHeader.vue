<script setup>
const emit = defineEmits(['toggle-dropdown', 'select-all', 'delete-all'])
const props = defineProps({
  showDropdown: Boolean
})

const handleSelectAll = () => emit('select-all')
const handleDeleteAll = () => emit('delete-all')
</script>

<template>
  <div class="header">
    <h2>Quản lý nhóm thành viên</h2>
    <div class="settings-dropdown">
      <button class="settings-btn" @click="$emit('toggle-dropdown')">
        <i class="bx bx-cog"></i>
      </button>
      <transition name="fade">
        <ul v-if="showDropdown" class="dropdown-menu">
          <li @click="handleSelectAll">✔ Chọn tất cả</li>
          <li @click="handleDeleteAll">🗑 Xóa các thành viên đã chọn</li>
        </ul>
      </transition>
    </div>
  </div>
</template>

<style scoped>
/* Thêm style nếu cần */
</style>

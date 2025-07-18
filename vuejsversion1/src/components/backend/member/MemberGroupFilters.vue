<!-- src/components/backend/member/MemberGroupFilters.vue -->
<script setup>
import { computed } from 'vue'

// Định nghĩa các props mà component nhận từ component cha
const props = defineProps(['itemsPerPage', 'selectedStatus', 'searchQuery'])

// Định nghĩa các sự kiện mà component này có thể phát ra cho component cha
const emit = defineEmits(['update:itemsPerPage', 'update:selectedStatus', 'update:searchQuery', 'search', 'add'])

// Tạo computed property cho itemsPerPage, khi giá trị thay đổi, sự kiện update sẽ được phát ra
const localItemsPerPage = computed({
  get: () => props.itemsPerPage, // Lấy giá trị từ prop itemsPerPage
  set: val => emit('update:itemsPerPage', val) // Khi giá trị thay đổi, emit sự kiện update:itemsPerPage
})

// Tạo computed property cho selectedStatus, khi giá trị thay đổi, sự kiện update sẽ được phát ra
const localSelectedStatus = computed({
  get: () => props.selectedStatus, // Lấy giá trị từ prop selectedStatus
  set: val => emit('update:selectedStatus', val) // Khi giá trị thay đổi, emit sự kiện update:selectedStatus
})

// Tạo computed property cho searchQuery, khi giá trị thay đổi, sự kiện update sẽ được phát ra
const localSearchQuery = computed({
  get: () => props.searchQuery, // Lấy giá trị từ prop searchQuery
  set: val => emit('update:searchQuery', val) // Khi giá trị thay đổi, emit sự kiện update:searchQuery
})

// Hàm handleSearch sẽ phát ra sự kiện 'search' khi được gọi, dùng để thực hiện tìm kiếm
const handleSearch = () => emit('search')

// Hàm addNewMember sẽ phát ra sự kiện 'add' khi được gọi, dùng để thêm thành viên mới
const addNewMember = () => emit('add')
</script>

<template>
  <div class="controls">
    <div class="left-controls">
      <label>
        <!-- Dropdown cho phép chọn số lượng bản ghi cần hiển thị trên trang -->
        <select v-model="localItemsPerPage">
          <option value="5">5 bản ghi</option>
          <option value="10">10 bản ghi</option>
          <option value="20">20 bản ghi</option>
        </select>
      </label>
    </div>
    <div class="right-controls">
    <!-- Dropdown cho phép chọn trạng thái của nhóm thành viên -->
      <select v-model="localSelectedStatus">
        <option value="">-- Tất cả trạng thái --</option>
        <option value="Đang hoạt động">Đang hoạt động</option>
        <option value="Ngưng hoạt động">Ngưng hoạt động</option>
      </select>

      <div class="search-box">
         <!-- Input để tìm kiếm theo tên nhóm thành viên -->
        <input
          type="text"
          v-model="localSearchQuery"
          placeholder="Tìm theo tên nhóm thành viên..."
          @input="handleSearch"
        />
      </div>

       <!-- Nút để thêm mới nhóm thành viên -->
      <button class="btn btn-primary" @click="addNewMember">
        <i class="bx bx-plus"></i> Thêm mới
      </button>
    </div>
  </div>
</template>

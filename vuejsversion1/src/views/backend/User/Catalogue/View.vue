<script setup>
import Layout from '@/components/backend/layout.vue'
import MemberGroupHeader from '@/components/backend/member/MemberGroupHeader.vue'
import MemberGroupFilters from '@/components/backend/member/MemberGroupFilters.vue'
import MemberGroupTable from '@/components/backend/member/MemberGroupTable.vue'
import Pagination from '@/components/backend/common/Pagination.vue'
import { ref, computed } from 'vue'
import router from '@/router';
import { onMounted } from 'vue'
import { useStore } from 'vuex'

const members = ref([
  { name: 'Quản trị viên', quantity: '2 thành viên', role: 'Có toàn bộ quyền', status: 'Đang hoạt động' },
  { name: 'Thành viên', quantity: '20 thành viên', role: 'Có một số quyền', status: 'Ngưng hoạt động' },
])

// Cài đặt các biến kiểm soát giao diện
const showDropdown = ref(false) // Kiểm tra trạng thái hiển thị dropdown
const selectedMembers = ref([]) // Lưu trữ các thành viên đã chọn
const itemsPerPage = ref(10) // Số bản ghi trên mỗi trang
const selectedStatus = ref('') // Lọc theo trạng thái
const searchQuery = ref('') // Lọc theo tên nhóm thành viên

// Computed property để lọc danh sách thành viên theo trạng thái và tìm kiếm
const filteredMembers = computed(() => {
  return members.value
    .filter(m =>
      (!selectedStatus.value || m.status === selectedStatus.value) &&
      (!searchQuery.value || m.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
    )
    .slice(0, itemsPerPage.value) // Cắt dữ liệu theo số lượng bản ghi
})

// Hàm để toggle trạng thái của dropdown
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

// Hàm chọn tất cả thành viên
function selectAll() {
  selectedMembers.value = filteredMembers.value.map((_, index) => index)
  showDropdown.value = false
}

// Hàm xóa tất cả thành viên đã chọn
const deleteAll = () => {
  if (confirm('Bạn có chắc chắn muốn xóa tất cả thành viên đã chọn?')) {
    members.value = members.value.filter((_, index) => !selectedMembers.value.includes(index))
    selectedMembers.value = []
  }
  showDropdown.value = false
}

// Hàm chỉnh sửa thành viên
const editMember = (index) => {
  alert(`Chỉnh sửa thành viên: ${members.value[index].name}`)
}

// Hàm xóa thành viên
const deleteMember = (index) => {
  if (confirm(`Bạn có chắc chắn muốn xóa ${members.value[index].name}?`)) {
    members.value.splice(index, 1)
    selectedMembers.value = selectedMembers.value.filter(i => i !== index)
  }
}

// Hàm thêm mới thành viên
function addNewMember() {
  router.push({ name: 'user.catalogue.create' });
}

// Hàm tìm kiếm thành viên
function handleSearch() {
  console.log("Đang tìm kiếm:", searchQuery);
  // Thêm logic lọc hoặc gọi API ở đây
}

// Hàm toggle việc chọn thành viên
const toggleSelect = (index) => {
  const i = selectedMembers.value.indexOf(index)
  if (i > -1) selectedMembers.value.splice(i, 1)
  else selectedMembers.value.push(index)
}

onMounted(() => {
    const store = useStore()
    const toastMessage = sessionStorage.getItem('showSuccessToast')
    if (toastMessage) {
        store.dispatch('toast/success', toastMessage)
        sessionStorage.removeItem('showSuccessToast')
    }
})
</script>

<template>
  <Layout>
    <template #template>
      <div class="table-container">
        <!-- Header -->
        <MemberGroupHeader
          :showDropdown="showDropdown"
          @toggle-dropdown="toggleDropdown"
          @select-all="selectAll"
          @delete-all="deleteAll"
        />

        <!-- Component lọc/tìm kiếm -->
        <MemberGroupFilters
          :itemsPerPage="itemsPerPage" 
          :selectedStatus="selectedStatus"
          :searchQuery="searchQuery"
          @update:itemsPerPage="val => itemsPerPage = val"
          @update:selectedStatus="val => selectedStatus = val"
          @update:searchQuery="val => searchQuery = val"
          @search="handleSearch"
          @add="addNewMember"
        />

        <!-- Component bảng -->
        <MemberGroupTable
          :members="filteredMembers"
          :selectedMembers="selectedMembers"
          @edit="editMember"
          @delete="deleteMember"
        />

        <!-- phân trang -->
        <Pagination
          :currentPage="currentPage"
          :totalItems="filteredMembers.length"
          :pageSize="pageSize"
          @update:page="handlePageChange"
        />

      </div>
    </template>
  </Layout>
</template>

<style scoped>


</style>


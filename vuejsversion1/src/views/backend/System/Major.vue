<script setup>
import Layout from '@/components/backend/layout.vue'
import { onMounted, ref, computed, watch } from 'vue'
import axios from '@/config/axios'
import { useStore } from 'vuex'
import csrf from '@/config/csrf'
import MajorForm from '@/components/backend/System/MajorForm.vue'
import '@/assets/backend/css/Main.css'

const store = useStore()
const list = ref([])
const loading = ref(false)
const showModal = ref(false)
const editData = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(5)
const selectedItems = ref([])
const selectAll = ref(false)

// Thêm các ref cho bộ lọc
const filters = ref({
  khoa_id: '',
  search: ''
})

// Thêm ref cho danh sách options
const khoas = ref([])

// Thêm options cho số lượng items trên mỗi trang
const pageSizeOptions = [
  { value: 5, label: '5 mục' },
  { value: 10, label: '10 mục' },
  { value: 15, label: '15 mục' },
  { value: 20, label: '20 mục' },
  { value: -1, label: 'Tất cả' }
]

// Hàm load danh sách options cho bộ lọc
const loadFilterOptions = async () => {
  try {
    console.log('Đang tải danh sách khoa...')
    const response = await axios.get('/api/khoas')
    console.log('Response từ API khoa:', response)

    if (response) {
      khoas.value = response
      console.log('Danh sách khoa sau khi xử lý:', khoas.value)
    } else {
      console.warn('Không có dữ liệu khoa trong response:', response)
      khoas.value = []
    }
  } catch (error) {
    console.error('Lỗi khi tải options cho bộ lọc:', error)
    store.dispatch('toast/error', `Không thể tải dữ liệu cho bộ lọc: ${error.response?.data?.message || error.message}`)
    khoas.value = []
  }
}

// Computed property để lọc danh sách
const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchKhoa = !filters.value.khoa_id || item.khoa?.id === parseInt(filters.value.khoa_id)
    const searchTerm = filters.value.search.toLowerCase()
    const matchSearch = !searchTerm || 
      item.tenNganh.toLowerCase().includes(searchTerm) ||
      item.maNganh.toLowerCase().includes(searchTerm)
    return matchKhoa && matchSearch
  })
})

// Computed properties cho phân trang
const totalItems = computed(() => filteredList.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, totalItems.value))
const paginatedList = computed(() => {
  const start = startIndex.value
  const end = endIndex.value
  return filteredList.value.slice(start, end)
})

const displayedPages = computed(() => {
  const pages = []
  const maxDisplayedPages = 5
  
  if (totalPages.value <= maxDisplayedPages) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    let start = Math.max(1, currentPage.value - 2)
    let end = Math.min(totalPages.value, start + maxDisplayedPages - 1)
    
    if (end - start + 1 < maxDisplayedPages) {
      start = Math.max(1, end - maxDisplayedPages + 1)
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }
  
  return pages
})

// Watch để reset về trang 1 khi thay đổi bộ lọc
watch([() => filters.value.khoa_id], () => {
  currentPage.value = 1
})

// Watch để reset về trang 1 khi thay đổi số lượng items trên mỗi trang
watch(itemsPerPage, () => {
  currentPage.value = 1
})

// Watch để reset selectedItems khi thay đổi bộ lọc hoặc load lại dữ liệu
watch([() => filters.value.khoa_id], () => {
  selectedItems.value = []
  selectAll.value = false
})

// Watch để reset selectedItems khi thay đổi trang
watch(currentPage, () => {
  // Không reset selectedItems khi chuyển trang
  // Chỉ cập nhật trạng thái selectAll
  const currentPageIds = paginatedList.value.map(item => item.id)
  selectAll.value = currentPageIds.length > 0 && currentPageIds.every(id => selectedItems.value.includes(id))
})

// Thêm methods cho chọn tất cả và xóa hàng loạt
const toggleSelectAll = () => {
  if (selectAll.value) {
    // Bỏ chọn tất cả các items trong trang hiện tại
    selectedItems.value = []
  } else {
    // Chọn tất cả các items trong trang hiện tại
    selectedItems.value = paginatedList.value.map(item => item.id)
  }
  
  // Cập nhật lại trạng thái selectAll
  selectAll.value = !selectAll.value
}

const toggleSelectItem = (itemId) => {
  const index = selectedItems.value.indexOf(itemId)
  if (index === -1) {
    selectedItems.value.push(itemId)
  } else {
    selectedItems.value.splice(index, 1)
  }
  
  // Cập nhật trạng thái selectAll dựa trên tất cả items trong trang hiện tại
  const currentPageIds = paginatedList.value.map(item => item.id)
  selectAll.value = currentPageIds.length > 0 && currentPageIds.every(id => selectedItems.value.includes(id))
}

// Thêm hàm xử lý xóa hàng loạt
const handleBulkDelete = async () => {
  if (selectedItems.value.length === 0) return

  const confirmMessage = `Bạn có chắc chắn muốn xóa ${selectedItems.value.length} ngành đã chọn?`
  
  if (confirm(confirmMessage)) {
    loading.value = true
    try {
      await csrf.getCookie()
      const results = await Promise.allSettled(
        selectedItems.value.map(id => 
          axios.delete(`/api/nganhs/${id}`)
        )
      )
      
      // Kiểm tra kết quả xóa
      const successCount = results.filter(r => r.status === 'fulfilled').length
      const failedCount = results.filter(r => r.status === 'rejected').length
      
      if (failedCount > 0) {
        // Nếu có lỗi, hiển thị thông báo chi tiết
        store.dispatch('toast/error', `Không thể xóa ${failedCount} ngành do có dữ liệu liên quan đến tiêu chí xét tuyển`)
      }
      
      if (successCount > 0) {
        store.dispatch('toast/success', `Đã xóa thành công ${successCount} ngành`)
      }
      
      selectedItems.value = []
      selectAll.value = false
      await loadData()
    } catch (error) {
      console.error('Lỗi khi xóa hàng loạt:', error)
      store.dispatch('toast/error', 'Không thể xóa một số ngành do có dữ liệu liên quan đến tiêu chí xét tuyển')
    } finally {
      loading.value = false
    }
  }
}

// Hàm reset bộ lọc
const resetFilters = () => {
  filters.value = {
    khoa_id: '',
    search: ''
  }
}

const loadData = async () => {
  loading.value = true
  try {
    console.log('Đang tải danh sách ngành...')
    const response = await axios.get('/api/nganhs')
    console.log('Response từ API:', response)

    if (response) {
      list.value = response.map(item => ({
        id: item.id,
        maNganh: item.maNganh || '',
        tenNganh: item.tenNganh || '',
        khoa: {
          id: item.khoa?.id,
          tenKhoa: item.khoa?.tenKhoa || 'N/A'
        },
        moTa: item.moTa || ''
      }))
      console.log('Danh sách ngành sau khi xử lý:', list.value)
    } else {
      console.warn('Không có dữ liệu ngành trong response:', response)
      list.value = []
    }
  } catch (error) {
    console.error('Lỗi khi tải danh sách:', error)
    store.dispatch('toast/error', `Không thể tải danh sách ngành: ${error.response?.data?.message || error.message}`)
    list.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editData.value = null
  showModal.value = true
}

const handleClose = () => {
  showModal.value = false
  editData.value = null
}

const handleSuccess = () => {
  loadData()
}

const handleEdit = (item) => {
  editData.value = {
    id: item.id,
    maNganh: item.maNganh,
    tenNganh: item.tenNganh,
    khoa: {
      id: item.khoa?.id,
      tenKhoa: item.khoa?.tenKhoa
    },
    moTa: item.moTa
  }
  showModal.value = true
}

const handleDelete = async (item) => {
  try {
    const confirmMessage = `Bạn có chắc chắn muốn xóa ngành này?\n\n` +
      `Mã ngành: ${item.maNganh}\n` +
      `Tên ngành: ${item.tenNganh}\n` +
      `Khoa: ${item.khoa?.tenKhoa || 'N/A'}`

    if (confirm(confirmMessage)) {
      loading.value = true
      await csrf.getCookie()
      
      console.log('Đang xóa ngành:', item.id)
      const response = await axios.delete(`/api/nganhs/${item.id}`)
      console.log('Response sau khi xóa:', response)
      
      store.dispatch('toast/success', 'Xóa ngành thành công')
      await loadData() // Tải lại danh sách sau khi xóa
    }
  } catch (error) {
    console.error('Lỗi khi xóa ngành:', error)
    const errorMessage = error.response?.data?.message || error.message
    store.dispatch('toast/error', errorMessage)
  } finally {
    loading.value = false
  }
}

// Thêm computed property để kiểm tra xem có item nào được chọn trong trang hiện tại không
const hasSelectedItemsInCurrentPage = computed(() => {
  return paginatedList.value.some(item => selectedItems.value.includes(item.id))
})

// Thêm computed property để kiểm tra xem tất cả items trong trang hiện tại có được chọn không
const areAllItemsInCurrentPageSelected = computed(() => {
  return paginatedList.value.length > 0 && paginatedList.value.every(item => selectedItems.value.includes(item.id))
})

onMounted(async () => {
  try {
    await Promise.all([loadData(), loadFilterOptions()])
  } catch (error) {
    console.error('Lỗi khi khởi tạo component:', error)
    store.dispatch('toast/error', 'Có lỗi xảy ra khi tải dữ liệu')
  }
})
</script>

<template>
  <Layout>
    <template #template>
      <div class="admission-page">
        <div class="dashboard-header">
          <div class="uk-container">
            <div class="header-content">
              <div class="header-left">
                <h1 class="dashboard-title">Quản lý ngành</h1>
                <p class="uk-text-muted">Danh sách các ngành</p>
              </div>
              <div class="header-right">
                <div class="header-actions">
                  <button 
                    v-if="selectedItems.length > 0"
                    class="uk-button uk-button-danger uk-button-small bulk-delete-button" 
                    @click="handleBulkDelete"
                  >
                    <span uk-icon="trash"></span>
                    Xóa đã chọn ({{ selectedItems.length }})
                  </button>
                  <button class="uk-button uk-button-primary uk-button-small add-button" @click="handleAdd">
                    <span uk-icon="plus"></span>
                    Thêm mới
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="dashboard-content">
          <div class="uk-card uk-card-default">
            <div class="uk-card-header">
              <div class="uk-grid-small" uk-grid>
                <div class="uk-width-expand">
                  <div class="uk-flex uk-flex-middle">
                    <span uk-icon="icon: table; ratio: 1.2" class="uk-margin-small-right"></span>
                  </div>
                </div>
                <div class="uk-width-auto">
                  <div class="uk-flex uk-flex-middle filter-container">
                    <div class="uk-search uk-search-default uk-margin-small-right" style="width: 200px;">
                      <span uk-search-icon></span>
                      <input 
                        class="uk-search-input uk-form-small" 
                        type="search" 
                        v-model="filters.search"
                        placeholder="Tìm theo tên hoặc mã ngành..."
                      >
                    </div>
                    <select v-model="filters.khoa_id" class="uk-select uk-form-small uk-margin-small-right" style="width: 180px;">
                      <option value="">Tất cả khoa</option>
                      <option v-for="khoa in khoas" :key="khoa.id" :value="khoa.id">
                        {{ khoa.tenKhoa }}
                      </option>
                    </select>
                    <button class="uk-button uk-button-default uk-button-small" @click="resetFilters">
                      <span uk-icon="refresh"></span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="uk-card-body">
              <div v-if="loading" class="uk-text-center uk-padding">
                <div uk-spinner="ratio: 1"></div>
                <p class="uk-margin-small-top">Đang tải dữ liệu...</p>
              </div>
              <div v-else class="uk-overflow-auto">
                <table class="uk-table uk-table-hover uk-table-middle uk-table-divider fixed-table">
                  <thead>
                    <tr>
                      <th class="checkbox-column">
                        <input 
                          type="checkbox" 
                          class="uk-checkbox" 
                          :checked="selectAll"
                          :indeterminate="hasSelectedItemsInCurrentPage && !areAllItemsInCurrentPageSelected"
                          @change="toggleSelectAll"
                        >
                      </th>
                      <th style="width: 20%">Mã ngành</th>
                      <th style="width: 30%">Tên ngành</th>
                      <th style="width: 30%">Khoa</th>
                      <th style="width: 20%" class="uk-text-center">Hành động</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in paginatedList" :key="item.id">
                      <td class="checkbox-column">
                        <input 
                          type="checkbox" 
                          class="uk-checkbox" 
                          :checked="selectedItems.includes(item.id)"
                          @change="toggleSelectItem(item.id)"
                        >
                      </td>
                      <td>{{ item.maNganh }}</td>
                      <td>{{ item.tenNganh }}</td>
                      <td>{{ item.khoa?.tenKhoa }}</td>
                      <td class="uk-text-center">
                        <div class="uk-button-group">
                          <button class="uk-button uk-button-small uk-button-primary" @click="handleEdit(item)">
                            <span uk-icon="pencil"></span>
                          </button>
                          <button class="uk-button uk-button-small uk-button-danger" @click="handleDelete(item)">
                            <span uk-icon="trash"></span>
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="paginatedList.length === 0">
                      <td colspan="5" class="uk-text-center">
                        <div class="uk-alert-primary" uk-alert>
                          <p>Không tìm thấy dữ liệu phù hợp với bộ lọc</p>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>

                <!-- Phân trang -->
                <div v-if="totalPages > 1 || itemsPerPage !== -1" class="pagination-container">
                  <div class="pagination-wrapper">
                    <div class="page-size-selector">
                      <span class="page-size-label">Hiển thị:</span>
                      <select v-model="itemsPerPage" class="uk-select uk-form-small">
                        <option v-for="option in pageSizeOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                    </div>
                    <div class="pagination">
                      <button 
                        class="uk-button uk-button-default uk-button-small" 
                        :disabled="currentPage === 1"
                        @click="currentPage--"
                      >
                        &laquo;
                      </button>
                      
                      <div class="page-numbers">
                        <button 
                          v-for="page in displayedPages" 
                          :key="page"
                          class="uk-button uk-button-small"
                          :class="{ 'uk-button-primary': currentPage === page }"
                          @click="currentPage = page"
                        >
                          {{ page }}
                        </button>
                      </div>

                      <button 
                        class="uk-button uk-button-default uk-button-small" 
                        :disabled="currentPage === totalPages"
                        @click="currentPage++"
                      >
                        &raquo;
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <MajorForm 
        :show="showModal"
        :edit-data="editData"
        @close="handleClose"
        @success="handleSuccess"
      />
    </template>
  </Layout>
</template>

<style scoped>
.dashboard-title {
  margin: 0;
  padding: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1e293b;
}

.uk-text-muted {
  margin: 0;
  padding: 0;
  font-size: 0.875rem;
  color: #64748b;
}

.uk-card-body {
  padding: 0;
  min-height: 400px;
}

.uk-overflow-auto {
  position: relative;
}

.fixed-table {
  table-layout: fixed;
  width: 100%;
  border-collapse: collapse;
}

.fixed-table th,
.fixed-table td {
  white-space: normal;
  word-wrap: break-word;
  min-width: 0;
  padding: 12px 16px;
  vertical-align: middle;
}

.fixed-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
  background: white;
}

.fixed-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: white;
  border-bottom: 2px solid #e2e8f0;
}

/* Pagination styles */
.pagination-container {
  margin-top: 1.5rem;
  padding: 1rem;
  background: white;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
}

.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-size-selector {
  display: flex;
  align-items: center;
}

.page-size-label {
  margin-right: 0.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.uk-button-small {
  min-width: 32px;
  height: 32px;
  padding: 0;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.uk-button-small:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.uk-button-primary {
  background: #3b82f6;
  color: white;
  border: none;
}

.uk-button-primary:hover:not(:disabled) {
  background: #2563eb;
}

.uk-button-default {
  background: white;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.uk-button-default:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.uk-button-default:disabled {
  background: #f1f5f9;
  color: #94a3b8;
  border-color: #e2e8f0;
  cursor: not-allowed;
}

.add-button {
  min-width: 120px;
  height: 32px;
  padding: 0 16px;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 4px;
  background: #3b82f6;
  color: white;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.add-button:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.add-button [uk-icon] {
  width: 14px;
  height: 14px;
}

.checkbox-column {
  width: 40px !important;
  min-width: 40px !important;
  max-width: 40px !important;
  padding: 0 8px !important;
  text-align: center !important;
  box-sizing: border-box !important;
}

.uk-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: inline-block;
  vertical-align: middle;
  margin: 0;
  box-sizing: border-box;
  flex-shrink: 0;
}

.uk-checkbox:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.uk-checkbox:checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(45deg);
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  box-sizing: border-box;
}

.uk-checkbox:hover:not(:checked) {
  border-color: #3b82f6;
}

.bulk-delete-button {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0 16px;
  height: 32px;
  line-height: 30px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.bulk-delete-button:hover:not(:disabled) {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
}

@media (max-width: 640px) {
  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .page-numbers {
    order: 2;
    width: 100%;
    justify-content: center;
    margin-top: 0.5rem;
  }
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.uk-search {
  position: relative;
  width: 200px;
}

.uk-search-input {
  width: 100%;
  padding-left: 30px;
}

.uk-select {
  min-width: 180px;
  width: 180px;
}

@media (max-width: 640px) {
  .filter-container {
    flex-wrap: wrap;
  }
  
  .uk-search,
  .uk-select {
    width: 100%;
    min-width: 100%;
  }
}
</style>

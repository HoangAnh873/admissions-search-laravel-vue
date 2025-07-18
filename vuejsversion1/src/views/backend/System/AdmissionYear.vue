<script setup>
import Layout from '@/components/backend/layout.vue'
import { onMounted, ref, computed, watch } from 'vue'
import axios from '@/config/axios'
import { useStore } from 'vuex'
import csrf from '@/config/csrf'
import AdmissionYearForm from '@/components/backend/System/AdmissionYearForm.vue'
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
  status: '',
  search: ''
})

// Thêm options cho số lượng items trên mỗi trang
const pageSizeOptions = [
  { value: 5, label: '5 mục' },
  { value: 10, label: '10 mục' },
  { value: 15, label: '15 mục' },
  { value: 20, label: '20 mục' },
  { value: -1, label: 'Tất cả' }
]

// Computed property để lọc danh sách
const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchStatus = !filters.value.status || item.status === (filters.value.status === 'true')
    const matchSearch = !filters.value.search || item.nam.toLowerCase().includes(filters.value.search.toLowerCase())
    return matchStatus && matchSearch
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
watch([() => filters.value.status, () => filters.value.search], () => {
  currentPage.value = 1
  selectedItems.value = []
  selectAll.value = false
})

// Watch để reset về trang 1 khi thay đổi số lượng items trên mỗi trang
watch(itemsPerPage, () => {
  currentPage.value = 1
})

// Hàm reset bộ lọc
const resetFilters = () => {
  filters.value = {
    status: '',
    search: ''
  }
}

const loadData = async () => {
  loading.value = true
  try {
    console.log('Đang tải danh sách năm tuyển sinh...')
    const response = await axios.get('/api/nam-xet-tuyens')
    console.log('Response từ API:', response)

    if (response) {
      list.value = response.map(item => ({
        id: item.id,
        nam: item.nam || ''
      }))
      console.log('Danh sách năm tuyển sinh sau khi xử lý:', list.value)
    } else {
      console.warn('Không có dữ liệu năm tuyển sinh trong response:', response)
      list.value = []
    }
  } catch (error) {
    console.error('Lỗi khi tải danh sách:', error)
    store.dispatch('toast/error', `Không thể tải danh sách năm tuyển sinh: ${error.response?.data?.message || error.message}`)
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
    nam: item.nam
  }
  showModal.value = true
}

const handleDelete = async (item) => {
  try {
    const confirmMessage = `Bạn có chắc chắn muốn xóa năm tuyển sinh này?\n\n` +
      `Năm: ${item.nam}`

    if (confirm(confirmMessage)) {
      loading.value = true
      await csrf.getCookie()
      
      console.log('Đang xóa năm tuyển sinh:', item.id)
      const response = await axios.delete(`/api/nam-xet-tuyens/${item.id}`)
      console.log('Response sau khi xóa:', response)
      
      store.dispatch('toast/success', 'Xóa năm tuyển sinh thành công')
      await loadData() // Tải lại danh sách sau khi xóa
    }
  } catch (error) {
    console.error('Lỗi khi xóa năm tuyển sinh:', error)
    const errorMessage = error.response?.data?.message || error.message
    store.dispatch('toast/error', errorMessage)
  } finally {
    loading.value = false
  }
}

// Thêm methods cho chọn tất cả và xóa hàng loạt
const toggleSelectAll = () => {
  console.log('Toggle Select All:', { selectAll: selectAll.value, currentPageItems: paginatedList.value })
  
  if (selectAll.value) {
    // Bỏ chọn tất cả các items trong trang hiện tại
    const currentPageIds = paginatedList.value.map(item => item.id)
    selectedItems.value = selectedItems.value.filter(id => !currentPageIds.includes(id))
  } else {
    // Chọn tất cả các items trong trang hiện tại
    const currentPageIds = paginatedList.value.map(item => item.id)
    // Thêm các items mới vào selectedItems mà không trùng lặp
    currentPageIds.forEach(id => {
      if (!selectedItems.value.includes(id)) {
        selectedItems.value.push(id)
      }
    })
  }
  
  // Cập nhật lại trạng thái selectAll
  selectAll.value = !selectAll.value
  
  console.log('After Toggle:', { 
    selectedItems: selectedItems.value,
    selectAll: selectAll.value,
    currentPageIds: paginatedList.value.map(item => item.id)
  })
}

const toggleSelectItem = (itemId) => {
  console.log('Toggle Item:', { itemId, currentSelectedItems: selectedItems.value })
  
  const index = selectedItems.value.indexOf(itemId)
  if (index === -1) {
    selectedItems.value.push(itemId)
  } else {
    selectedItems.value.splice(index, 1)
  }
  
  // Cập nhật trạng thái selectAll dựa trên tất cả items trong trang hiện tại
  const currentPageIds = paginatedList.value.map(item => item.id)
  selectAll.value = currentPageIds.length > 0 && currentPageIds.every(id => selectedItems.value.includes(id))
  
  console.log('After Toggle Item:', { 
    selectedItems: selectedItems.value,
    selectAll: selectAll.value,
    currentPageIds
  })
}

// Watch để reset selectedItems khi thay đổi trang
watch(currentPage, () => {
  // Không reset selectedItems khi chuyển trang
  // Chỉ cập nhật trạng thái selectAll
  const currentPageIds = paginatedList.value.map(item => item.id)
  selectAll.value = currentPageIds.length > 0 && currentPageIds.every(id => selectedItems.value.includes(id))
})

// Thêm computed property để kiểm tra xem có item nào được chọn trong trang hiện tại không
const hasSelectedItemsInCurrentPage = computed(() => {
  return paginatedList.value.some(item => selectedItems.value.includes(item.id))
})

// Thêm computed property để kiểm tra xem tất cả items trong trang hiện tại có được chọn không
const areAllItemsInCurrentPageSelected = computed(() => {
  return paginatedList.value.length > 0 && paginatedList.value.every(item => selectedItems.value.includes(item.id))
})

// Thêm hàm xử lý xóa hàng loạt
const handleBulkDelete = async () => {
  if (selectedItems.value.length === 0) return

  const confirmMessage = `Bạn có chắc chắn muốn xóa ${selectedItems.value.length} năm đã chọn?`
  
  if (confirm(confirmMessage)) {
    loading.value = true
    try {
      await csrf.getCookie()
      await Promise.all(selectedItems.value.map(id => axios.delete(`/api/nam-xet-tuyens/${id}`)))
      store.dispatch('toast/success', 'Xóa năm thành công')
      selectedItems.value = []
      selectAll.value = false
      await loadData()
    } catch (error) {
      console.error('Lỗi khi xóa hàng loạt:', error)
      store.dispatch('toast/error', 'Không thể xóa một số năm')
    } finally {
      loading.value = false
    }
  }
}

onMounted(async () => {
  try {
    await loadData()
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
            <h1 class="dashboard-title">Danh sách năm tuyển sinh</h1>
            <p class="uk-text-muted">Quản lý thông tin các năm tuyển sinh</p>
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
                  <div class="uk-flex uk-flex-middle">
                    <button 
                      v-if="selectedItems.length > 0"
                      class="uk-button uk-button-danger uk-button-small bulk-delete-button" 
                      @click="handleBulkDelete"
                    >
                      <span uk-icon="trash"></span>
                      Xóa đã chọn ({{ selectedItems.length }})
                    </button>
                    <button class="uk-button uk-button-primary add-button" @click="handleAdd">
                      <span uk-icon="plus"></span>
                      Thêm mới
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
              <div v-else-if="list.length === 0" class="uk-text-center uk-padding">
                <p class="uk-text-muted">Không có dữ liệu năm tuyển sinh</p>
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
                      <th class="uk-width-4-5">Năm tuyển sinh</th>
                      <th class="uk-width-1-5 uk-text-center">Hành động</th>
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
                      <td>{{ item.nam }}</td>
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
                      <td colspan="3" class="uk-text-center">
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
      
      <AdmissionYearForm
        :show="showModal"
        :edit-data="editData"
        @close="handleClose"
        @success="handleSuccess"
      />
    </template>
  </Layout>
</template>

<style scoped>
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
  gap: 0.5rem;
}

.page-size-label {
  font-weight: 500;
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
</style>

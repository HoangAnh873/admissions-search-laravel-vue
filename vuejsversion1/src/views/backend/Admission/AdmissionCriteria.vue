<script setup>
import Layout from '@/components/backend/layout.vue'
import { onMounted, ref, computed, watch } from 'vue'
import axios from '@/config/axios'
import { useStore } from 'vuex'
import csrf from '@/config/csrf'
import AdmissionCriteriaForm from '@/components/backend/Admission/AdmissionCriteriaForm.vue'
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
  nganh_id: '',
  nam_id: ''
})

// Thêm ref cho danh sách options
const nganhs = ref([])
const years = ref([])
const khoas = ref([])

const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second

// Hàm retry cho API calls
const retryApiCall = async (apiCall, retries = MAX_RETRIES) => {
  try {
    return await apiCall()
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
      return retryApiCall(apiCall, retries - 1)
    }
    throw error
  }
}

// Hàm load danh sách options cho bộ lọc
const loadFilterOptions = async () => {
  loading.value = true
  try {
    // Thêm delay nhỏ giữa các request
    const [khoaRes, nganhRes, namRes] = await Promise.all([
      axios.get('/api/khoas'),
      new Promise(resolve => setTimeout(() => resolve(axios.get('/api/nganhs')), 100)),
      new Promise(resolve => setTimeout(() => resolve(axios.get('/api/nam-xet-tuyens')), 200))
    ])
    
    khoas.value = khoaRes || []
    // Map lại để đảm bảo có trường khoa_id
    nganhs.value = (nganhRes || []).map(nganh => ({
      ...nganh,
      khoa_id: nganh.khoa_id || nganh.khoa?.id || null
    }))
    years.value = namRes || []
  } catch (error) {
    console.error('Lỗi khi tải options:', error)
    if (error.response?.status === 429) {
      store.dispatch('toast/error', 'Quá nhiều yêu cầu. Vui lòng thử lại sau ít phút')
    } else {
      store.dispatch('toast/error', 'Không thể tải dữ liệu cho bộ lọc')
    }
    khoas.value = []
    nganhs.value = []
    years.value = []
  } finally {
    loading.value = false
  }
}

// Khi chọn khoa, lọc lại ngành cho filter
const filteredNganhs = computed(() => {
  if (!filters.value.khoa_id) return nganhs.value
  return nganhs.value.filter(nganh => String(nganh.khoa_id) === String(filters.value.khoa_id))
})

// Lọc danh sách theo khoa/ngành/năm
const filteredList = computed(() => {
  if (!list.value || !Array.isArray(list.value)) return []
  
  return list.value.filter(item => {
    if (!item || !item.nganh) return false
    
    const itemKhoaId = item.nganh?.khoa?.id
    const matchKhoa = !filters.value.khoa_id || String(itemKhoaId) === String(filters.value.khoa_id)
    const matchNganh = !filters.value.nganh_id || String(item.nganh?.id) === String(filters.value.nganh_id)
    const matchNam = !filters.value.nam_id || String(item.nam?.id) === String(filters.value.nam_id)
    return matchKhoa && matchNganh && matchNam
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
watch([() => filters.value.khoa_id, () => filters.value.nganh_id, () => filters.value.nam_id], () => {
  currentPage.value = 1
})

// Watch khoa_id để reset ngành khi đổi khoa
watch(() => filters.value.khoa_id, async (newKhoaId) => {
  filters.value.nganh_id = ''
  loading.value = true
  try {
    // Thêm delay nhỏ trước khi gọi API
    await new Promise(resolve => setTimeout(resolve, 100))
    const response = await axios.get(newKhoaId ? `/api/nganhs/khoa/${newKhoaId}` : '/api/nganhs')
    // Map lại để đảm bảo có trường khoa_id
    nganhs.value = (response || []).map(nganh => ({
      ...nganh,
      khoa_id: nganh.khoa_id || nganh.khoa?.id || null
    }))
  } catch (error) {
    console.error('Lỗi khi tải ngành:', error)
    if (error.response?.status === 429) {
      store.dispatch('toast/error', 'Quá nhiều yêu cầu. Vui lòng thử lại sau ít phút')
    } else {
      store.dispatch('toast/error', 'Không thể tải danh sách ngành')
    }
    nganhs.value = []
  } finally {
    loading.value = false
  }
})

// Hàm reset bộ lọc
const resetFilters = () => {
  filters.value = {
    khoa_id: '',
    nganh_id: '',
    nam_id: ''
  }
  // Load lại tất cả ngành khi reset
  axios.get('/api/nganhs')
    .then(response => {
      if (response && Array.isArray(response)) {
        // Map lại để đảm bảo có trường khoa_id
        nganhs.value = response.map(nganh => ({
          ...nganh,
          khoa_id: nganh.khoa_id || nganh.khoa?.id || null
        }))
      }
    })
    .catch(error => {
      console.error('Lỗi khi tải danh sách ngành:', error)
      store.dispatch('toast/error', 'Không thể tải danh sách ngành')
    })
}

const loadData = async () => {
  loading.value = true
  try {
    // Thêm delay nhỏ trước khi gọi API
    await new Promise(resolve => setTimeout(resolve, 100))
    const res = await axios.get('/api/tieu-chuan-xet-tuyens')
    if (res) {
      list.value = res.map(item => ({
        id: item.id,
        nganh: {
          id: item.nganh?.id,
          tenNganh: item.nganh?.tenNganh || 'N/A',
          khoa: {
            id: item.nganh?.khoa?.id,
            tenKhoa: item.nganh?.khoa?.tenKhoa || 'N/A'
          }
        },
        nam: {
          id: item.nam?.id,
          nam: item.nam?.nam || new Date().getFullYear()
        },
        toHop: item.toHop || '',
        diemToiThieu: item.diemToiThieu || 0,
        ghiChu: item.ghiChu || ''
      }))
      // Sắp xếp theo id giảm dần (mới nhất lên đầu)
      list.value.sort((a, b) => b.id - a.id)
    } else {
      list.value = []
    }
  } catch (error) {
    console.error('Lỗi khi tải danh sách:', error)
    if (error.response?.status === 429) {
      store.dispatch('toast/error', 'Quá nhiều yêu cầu. Vui lòng thử lại sau ít phút')
    } else {
      store.dispatch('toast/error', 'Không thể tải danh sách tiêu chuẩn xét tuyển')
    }
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
    nganh: {
      id: item.nganh?.id,
      tenNganh: item.nganh?.tenNganh
    },
    nam: {
      id: item.nam?.id,
      nam: item.nam?.nam
    },
    toHop: item.toHop,
    diemToiThieu: item.diemToiThieu,
    ghiChu: item.ghiChu
  }
  showModal.value = true
}

const handleDelete = async (item) => {
  try {
    const confirmMessage = `Bạn có chắc chắn muốn xóa tiêu chuẩn xét tuyển này?\n\n` +
      `Ngành: ${item.nganh.tenNganh}\n` +
      `Năm: ${item.nam.nam}\n` +
      `Tổ hợp môn: ${item.toHop}`

    if (confirm(confirmMessage)) {
      loading.value = true
      await csrf.getCookie()
      await axios.delete(`/api/tieu-chuan-xet-tuyens/${item.id}`)
      store.dispatch('toast/success', 'Xóa tiêu chuẩn xét tuyển thành công')
      await loadData()
    }
  } catch (error) {
    console.error('Lỗi khi xóa tiêu chuẩn xét tuyển:', error)
    store.dispatch('toast/error', `Không thể xóa tiêu chuẩn xét tuyển: ${error.response?.data?.message || error.message}`)
  } finally {
    loading.value = false
  }
}

// Thêm error boundary
const handleError = (error) => {
  console.error('Lỗi không xác định:', error)
  store.dispatch('toast/error', 'Đã xảy ra lỗi. Vui lòng thử lại sau.')
  loading.value = false
}

// Thêm options cho số lượng items trên mỗi trang
const pageSizeOptions = [
  { value: 5, label: '5 mục' },
  { value: 10, label: '10 mục' },
  { value: 15, label: '15 mục' },
  { value: 20, label: '20 mục' },
  { value: -1, label: 'Tất cả' }
]

// Watch để reset về trang 1 khi thay đổi số lượng items trên mỗi trang
watch(itemsPerPage, () => {
  currentPage.value = 1
})

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

// Watch để reset selectedItems khi thay đổi bộ lọc hoặc load lại dữ liệu
watch([() => filters.value.khoa_id, () => filters.value.nganh_id, () => filters.value.nam_id], () => {
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

  const confirmMessage = `Bạn có chắc chắn muốn xóa ${selectedItems.value.length} tiêu chí đã chọn?`
  
  if (confirm(confirmMessage)) {
    loading.value = true
    try {
      await csrf.getCookie()
      await Promise.all(selectedItems.value.map(id => axios.delete(`/api/tieu-chuan-xet-tuyens/${id}`)))
      store.dispatch('toast/success', 'Xóa tiêu chí thành công')
      selectedItems.value = []
      selectAll.value = false
      await loadData()
    } catch (error) {
      console.error('Lỗi khi xóa hàng loạt:', error)
      store.dispatch('toast/error', 'Không thể xóa một số tiêu chí')
    } finally {
      loading.value = false
    }
  }
}

onMounted(() => {
  loadData()
  loadFilterOptions()
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
                <h1 class="dashboard-title">Tiêu chuẩn xét tuyển</h1>
                <p class="uk-text-muted">Quản lý tiêu chuẩn xét tuyển các ngành</p>
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
                <div class="uk-width-1-1">
                  <div class="filter-container">
                    <div class="filter-group">
                      <select v-model="filters.khoa_id" class="uk-select uk-form-small">
                        <option value="">Tất cả khoa</option>
                        <option v-for="khoa in khoas" :key="khoa.id" :value="khoa.id">
                          {{ khoa.tenKhoa }}
                        </option>
                      </select>
                    </div>
                    <div class="filter-group">
                      <select v-model="filters.nganh_id" class="uk-select uk-form-small">
                        <option value="">Tất cả ngành</option>
                        <option v-for="nganh in filteredNganhs" :key="nganh.id" :value="nganh.id">
                          {{ nganh.tenNganh }}
                        </option>
                      </select>
                    </div>
                    <div class="filter-group">
                      <select v-model="filters.nam_id" class="uk-select uk-form-small">
                        <option value="">Tất cả năm</option>
                        <option v-for="year in years" :key="year.id" :value="year.id">
                          {{ year.nam }}
                        </option>
                      </select>
                    </div>
                    <div class="filter-actions">
                      <button class="uk-button uk-button-default uk-button-small" @click="resetFilters">
                        <span uk-icon="refresh"></span>
                      </button>
                    </div>
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
                      <th style="width: 30%">Ngành</th>
                      <th style="width: 15%" class="uk-text-center">Năm</th>
                      <th style="width: 20%" class="uk-text-center">Tổ hợp môn</th>
                      <th style="width: 15%" class="uk-text-center">Điểm tối thiểu</th>
                      <th style="width: 10%">Ghi chú</th>
                      <th style="width: 10%" class="uk-text-center">Hành động</th>
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
                      <td>{{ item.nganh.tenNganh }}</td>
                      <td class="uk-text-center">{{ item.nam.nam }}</td>
                      <td class="uk-text-center">{{ item.toHop }}</td>
                      <td class="uk-text-center">{{ item.diemToiThieu }}</td>
                      <td>{{ item.ghiChu }}</td>
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
                      <td colspan="7" class="uk-text-center">
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

      <AdmissionCriteriaForm 
        :show="showModal"
        :edit-data="editData"
        @close="handleClose"
        @success="handleSuccess"
      />
    </template>
  </Layout>
</template>

<style scoped>
.filter-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr) auto;
  gap: 1rem;
  align-items: center;
  width: 100%;
}

.filter-group {
  width: 100%;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  white-space: nowrap;
}

.uk-select {
  width: 100%;
}

.uk-button-small {
  padding: 0 10px;
  height: 32px;
  line-height: 30px;
}

.fixed-table {
  table-layout: fixed;
  width: 100%;
  min-height: 200px;
  border-collapse: collapse;
}

.fixed-table th,
.fixed-table td {
  white-space: normal;
  word-wrap: break-word;
  min-width: 0;
  padding: 8px;
  vertical-align: middle;
  height: 40px;
}

.fixed-table td {
  line-height: 1.4;
}

.fixed-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
}

.fixed-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
}

.uk-overflow-auto {
  min-height: 200px;
  position: relative;
}

@media (max-width: 1200px) {
  .filter-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-actions {
    grid-column: 1 / -1;
    justify-content: flex-end;
  }
}

@media (max-width: 640px) {
  .filter-container {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    grid-column: 1;
  }
}

.uk-card-body {
  padding: 0;
  min-height: 400px;
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
</style>

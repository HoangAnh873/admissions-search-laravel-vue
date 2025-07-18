<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from '@/config/axios'
import { useStore } from 'vuex'
import csrf from '@/config/csrf'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  editData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const store = useStore()
const loading = ref(false)
const formLoading = ref(false)
const nganhs = ref([])
const years = ref([])
const phuongThucs = ref([])
const khoas = ref([])

const formData = ref({
  nganh_id: '',
  nam_id: '',
  toHop: '',
  diemToiThieu: '',
  ghiChu: ''
})

const errors = ref({})

// Danh sách các môn học
const subjects = [
  'Toán',
  'Lý',
  'Hóa',
  'Sinh',
  'Văn',
  'Sử',
  'Địa',
  'Tiếng Anh',
  'GDCD'
]

const loadOptions = async () => {
  try {
    console.log('Đang tải danh sách options...')
    const [khoaRes, nganhRes, namRes] = await Promise.all([
      axios.get('/api/khoas'),
      axios.get('/api/nganhs'),
      axios.get('/api/nam-xet-tuyens')
    ])

    if (khoaRes && Array.isArray(khoaRes)) {
      khoas.value = khoaRes
    }
    if (nganhRes && Array.isArray(nganhRes)) {
      nganhs.value = nganhRes
    }
    if (namRes && Array.isArray(namRes)) {
      years.value = namRes
    }
  } catch (error) {
    store.dispatch('toast/error', 'Không thể tải dữ liệu cho form')
  }
}

// Watch editData để set đúng ngành khi edit
watch(() => props.editData, async (newVal) => {
  if (newVal) {
    formLoading.value = true
    try {
      // Load lại danh sách ngành
      const nganhRes = await axios.get('/api/nganhs')
      if (nganhRes && Array.isArray(nganhRes)) {
        nganhs.value = nganhRes
      }
      
      formData.value = {
        nganh_id: newVal.nganh?.id || '',
        nam_id: newVal.nam?.id || '',
        toHop: newVal.toHop || '',
        diemToiThieu: newVal.diemToiThieu || '',
        ghiChu: newVal.ghiChu || ''
      }
    } catch (error) {
      console.error('Lỗi khi tải dữ liệu:', error)
      store.dispatch('toast/error', 'Không thể tải dữ liệu cho form')
    } finally {
      formLoading.value = false
    }
  } else {
    resetForm()
  }
}, { immediate: true })

const resetForm = () => {
  formData.value = {
    nganh_id: '',
    nam_id: '',
    toHop: '',
    diemToiThieu: '',
    ghiChu: ''
  }
  errors.value = {}
}

// Update modal title based on edit mode
const modalTitle = computed(() => {
  return props.editData ? 'Sửa tiêu chuẩn xét tuyển' : 'Thêm tiêu chuẩn xét tuyển mới'
})

const validateField = (field) => {
  errors.value[field] = ''
  
  switch (field) {
    case 'nganh_id':
      if (!formData.value.nganh_id) {
        errors.value.nganh_id = 'Vui lòng chọn ngành'
      }
      break
    case 'nam_id':
      if (!formData.value.nam_id) {
        errors.value.nam_id = 'Vui lòng chọn năm'
      }
      break
    case 'toHop':
      if (!formData.value.toHop) {
        errors.value.toHop = 'Vui lòng nhập tổ hợp môn'
      } else {
        // Cho phép nhiều tổ hợp, phân tách bởi dấu phẩy
        const toHopArr = formData.value.toHop.split(',').map(s => s.trim()).filter(Boolean)
        const invalid = toHopArr.find(val => !/^[A-Z]\d{2}$/.test(val))
        if (invalid) {
          errors.value.toHop = `Tổ hợp môn không hợp lệ: ${invalid}. Mỗi tổ hợp phải có định dạng A00, B00, C00... và cách nhau bởi dấu phẩy.`
        }
      }
      break
    case 'diemToiThieu':
      if (!formData.value.diemToiThieu) {
        errors.value.diemToiThieu = 'Vui lòng nhập điểm tối thiểu'
      } else if (formData.value.diemToiThieu < 0) {
        errors.value.diemToiThieu = 'Điểm tối thiểu không được âm'
      } else if (formData.value.diemToiThieu > 30) {
        errors.value.diemToiThieu = 'Điểm tối thiểu không được vượt quá 30'
      }
      break
  }
}

// Watch for form data changes and validate
watch(() => formData.value.nganh_id, () => validateField('nganh_id'))
watch(() => formData.value.nam_id, () => validateField('nam_id'))
watch(() => formData.value.toHop, () => validateField('toHop'))
watch(() => formData.value.diemToiThieu, () => validateField('diemToiThieu'))

const validateForm = async () => {
  validateField('nganh_id')
  validateField('nam_id')
  validateField('toHop')
  validateField('diemToiThieu')
  
  // Kiểm tra trùng lặp dữ liệu
  if (!errors.value.nganh_id && !errors.value.nam_id) {
    try {
      const response = await axios.get('/api/tieu-chuan-xet-tuyens/check-duplicate', {
        params: {
          nganh_id: formData.value.nganh_id,
          nam_id: formData.value.nam_id,
          id: props.editData?.id // Truyền id nếu đang edit để loại trừ bản ghi hiện tại
        }
      })
      
      if (response.exists) {
        errors.value.nganh_id = 'Đã tồn tại tiêu chuẩn xét tuyển cho ngành này trong năm đã chọn'
        return false
      }
    } catch (error) {
      console.error('Lỗi khi kiểm tra trùng lặp:', error)
      const errorMessage = error.message || 'Không thể kiểm tra trùng lặp dữ liệu'
      store.dispatch('toast/error', errorMessage)
      return false
    }
  }
  
  return !Object.values(errors.value).some(error => error !== '')
}

const handleSubmit = async () => {
  try {
    if (!await validateForm()) {
      return
    }

    loading.value = true
    await csrf.getCookie()

    // Chuẩn bị dữ liệu gửi đi
    const dataToSend = {
      nganh_id: formData.value.nganh_id,
      nam_id: formData.value.nam_id.toString(),
      toHop: formData.value.toHop,
      diemToiThieu: formData.value.diemToiThieu,
      ghiChu: formData.value.ghiChu || ''
    }

    console.log('Data being sent:', dataToSend)

    if (props.editData) {
      // Update
      const response = await axios.put(`/api/tieu-chuan-xet-tuyens/${props.editData.id}`, dataToSend)
      console.log('Update response:', response)
      store.dispatch('toast/success', 'Cập nhật tiêu chuẩn xét tuyển thành công')
    } else {
      // Create
      const response = await axios.post('/api/tieu-chuan-xet-tuyens', dataToSend)
      console.log('Create response:', response)
      store.dispatch('toast/success', 'Thêm tiêu chuẩn xét tuyển thành công')
    }

    // Emit success và đóng form
    emit('success')
    handleClose()
  } catch (error) {
    console.error('Error:', error.response?.data || error)
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      store.dispatch('toast/error', `Không thể lưu tiêu chuẩn xét tuyển: ${error.response?.data?.message || error.message}`)
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  resetForm()
  emit('close')
}

// Add watch for form data changes
watch(formData, (newVal) => {
  console.log('Form data changed:', newVal)
}, { deep: true })

onMounted(() => {
  loadOptions()
})
</script>

<template>
  <div v-if="show" class="uk-modal uk-open" style="display: block;">
    <div class="uk-modal-dialog uk-modal-body">
      <button class="uk-modal-close-default" type="button" uk-close @click="handleClose"></button>
      <h2 class="uk-modal-title">{{ modalTitle }}</h2>

      <div v-if="formLoading" class="form-loading">
        <div class="loading-spinner">
          <span uk-spinner="ratio: 1"></span>
          <p>Đang tải dữ liệu...</p>
        </div>
      </div>

      <form v-else @submit.prevent="handleSubmit">
        <div class="uk-margin">
          <label class="uk-form-label">Ngành <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <select 
              v-model="formData.nganh_id" 
              class="uk-select" 
              :class="{ 'uk-form-danger': errors.nganh_id }"
              @blur="validateField('nganh_id')"
            >
              <option value="">Chọn ngành</option>
              <option 
                v-for="nganh in nganhs" 
                :key="nganh.id" 
                :value="nganh.id"
              >
                {{ nganh.tenNganh }}
              </option>
            </select>
            <transition name="fade">
              <div v-if="errors.nganh_id" class="error-message">{{ errors.nganh_id }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Năm <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <select 
              v-model="formData.nam_id" 
              class="uk-select" 
              :class="{ 'uk-form-danger': errors.nam_id }"
              @blur="validateField('nam_id')"
            >
              <option value="">Chọn năm</option>
              <option v-for="year in years" :key="year.id" :value="year.id">
                {{ year.nam }}
              </option>
            </select>
            <transition name="fade">
              <div v-if="errors.nam_id" class="error-message">{{ errors.nam_id }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Tổ hợp môn <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              type="text" 
              v-model="formData.toHop" 
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.toHop }"
              placeholder="Nhập tổ hợp môn (ví dụ: A00, B00, C00...)"
              @blur="validateField('toHop')"
            >
            <transition name="fade">
              <div v-if="errors.toHop" class="error-message">{{ errors.toHop }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Điểm tối thiểu <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              type="number" 
              v-model="formData.diemToiThieu" 
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.diemToiThieu }"
              placeholder="Nhập điểm tối thiểu"
              min="0"
              max="30"
              step="0.1"
              @blur="validateField('diemToiThieu')"
            >
            <transition name="fade">
              <div v-if="errors.diemToiThieu" class="error-message">{{ errors.diemToiThieu }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Ghi chú</label>
          <div class="uk-form-controls">
            <textarea v-model="formData.ghiChu" class="uk-textarea" rows="3" placeholder="Nhập ghi chú (nếu có)"></textarea>
          </div>
        </div>

        <div class="uk-modal-footer uk-text-right">
          <button type="button" class="uk-button uk-button-default uk-margin-small-right" @click="handleClose">
            Hủy
          </button>
          <button type="submit" class="uk-button uk-button-primary" :disabled="loading">
            <span v-if="loading" uk-spinner="ratio: 0.6"></span>
            <span v-else>{{ editData ? 'Cập nhật' : 'Thêm mới' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.uk-modal {
  background: rgba(0, 0, 0, 0.6);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.uk-modal-dialog {
  max-width: 500px;
  margin: 50px auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.uk-modal-body {
  padding: 20px;
}

.uk-modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
}

.uk-form-label {
  font-weight: 500;
  color: #334155;
  margin-bottom: 8px;
  display: block;
}

.uk-input,
.uk-select,
.uk-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
}

.uk-input:focus,
.uk-select:focus,
.uk-textarea:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  outline: none;
}

.uk-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  font-size: 14px;
  min-width: 80px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.uk-button-primary {
  background: #3b82f6;
  color: white;
  border: none;
}

.uk-button-primary:hover {
  background: #2563eb;
}

.uk-button-default {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  margin-right: 8px;
}

.uk-button-default:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.uk-modal-close-default {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px;
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
}

.uk-modal-close-default:hover {
  color: #1e293b;
}

.uk-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
}

.uk-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  outline: none;
}

.uk-select option {
  padding: 8px;
}

.uk-margin.uk-text-right {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.uk-text-danger {
  color: #f0506e;
}

.uk-form-danger {
  border-color: #f0506e !important;
  box-shadow: 0 0 0 1px #f0506e !important;
}

.uk-form-danger:focus {
  border-color: #f0506e !important;
  box-shadow: 0 0 0 2px rgba(240, 80, 110, 0.1) !important;
}

.uk-select.uk-form-danger,
.uk-input.uk-form-danger {
  background-color: #fff5f5;
}

.uk-modal-footer {
  border-top: 1px solid #e5e5e5;
  padding-top: 1rem;
  margin-top: 1.5rem;
}

.uk-checkbox {
  margin-right: 8px;
}

.uk-textarea {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  color: #f0506e;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  padding: 0.25rem 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.form-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading-spinner {
  text-align: center;
}

.loading-spinner p {
  margin-top: 10px;
  color: #64748b;
  font-size: 14px;
}
</style> 
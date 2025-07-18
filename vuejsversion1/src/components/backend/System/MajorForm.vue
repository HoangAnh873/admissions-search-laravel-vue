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
const khoas = ref([])

const formData = ref({
  maNganh: '',
  tenNganh: '',
  khoa_id: '',
  moTa: ''
})

const errors = ref({})

// Update modal title based on edit mode
const modalTitle = computed(() => {
  return props.editData ? 'Sửa ngành' : 'Thêm ngành mới'
})

const loadOptions = async () => {
  try {
    console.log('Đang tải danh sách khoa...')
    const response = await axios.get('/api/khoas')
    console.log('Response từ API khoa:', response)

    if (response) {
      khoas.value = response
      console.log('Danh sách khoa sau khi xử lý:', khoas.value)
    } else {
      console.warn('Không có dữ liệu khoa trong response:', response)
      store.dispatch('toast/error', 'Không có dữ liệu khoa')
      khoas.value = []
    }
  } catch (error) {
    console.error('Lỗi khi tải options:', error)
    store.dispatch('toast/error', `Không thể tải dữ liệu cho form: ${error.response?.data?.message || error.message}`)
    khoas.value = []
  }
}

const resetForm = () => {
  formData.value = {
    maNganh: '',
    tenNganh: '',
    khoa_id: '',
    moTa: ''
  }
  errors.value = {}
}

const validateField = (field) => {
  errors.value[field] = ''
  
  switch (field) {
    case 'maNganh':
      if (!formData.value.maNganh.trim()) {
        errors.value.maNganh = 'Vui lòng nhập mã ngành'
      } else if (formData.value.maNganh.length > 20) {
        errors.value.maNganh = 'Mã ngành không được vượt quá 20 ký tự'
      }
      break
    case 'tenNganh':
      if (!formData.value.tenNganh.trim()) {
        errors.value.tenNganh = 'Vui lòng nhập tên ngành'
      } else if (formData.value.tenNganh.length > 255) {
        errors.value.tenNganh = 'Tên ngành không được vượt quá 255 ký tự'
      }
      break
    case 'khoa_id':
      if (!formData.value.khoa_id) {
        errors.value.khoa_id = 'Vui lòng chọn khoa'
      }
      break
  }
}

// Watch for form data changes and validate
watch(() => formData.value.maNganh, () => validateField('maNganh'))
watch(() => formData.value.tenNganh, () => validateField('tenNganh'))
watch(() => formData.value.khoa_id, () => validateField('khoa_id'))

const validateForm = () => {
  validateField('maNganh')
  validateField('tenNganh')
  validateField('khoa_id')
  
  return !Object.values(errors.value).some(error => error !== '')
}

const handleSubmit = async () => {
  try {
    if (!validateForm()) {
      return
    }

    loading.value = true
    await csrf.getCookie()

    // Chuẩn bị dữ liệu gửi đi
    const dataToSend = {
      maNganh: formData.value.maNganh.trim(),
      tenNganh: formData.value.tenNganh.trim(),
      khoa_id: formData.value.khoa_id,
      moTa: formData.value.moTa?.trim() || ''
    }

    console.log('Data being sent:', dataToSend)

    if (props.editData) {
      // Update
      const response = await axios.put(`/api/nganhs/${props.editData.id}`, dataToSend)
      console.log('Update response:', response)
      store.dispatch('toast/success', 'Cập nhật ngành thành công')
    } else {
      // Create
      const response = await axios.post('/api/nganhs', dataToSend)
      console.log('Create response:', response)
      store.dispatch('toast/success', 'Thêm ngành thành công')
    }

    // Emit success và đóng form
    emit('success')
    handleClose()
  } catch (error) {
    console.error('Error:', error.response?.data || error)
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      store.dispatch('toast/error', `Không thể lưu ngành: ${error.response?.data?.message || error.message}`)
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  resetForm()
  emit('close')
}

// Watch for editData changes
watch(() => props.editData, (newVal) => {
  console.log('Edit data received in form:', newVal)
  if (newVal) {
    formData.value = {
      maNganh: newVal.maNganh || '',
      tenNganh: newVal.tenNganh || '',
      khoa_id: newVal.khoa?.id || '',
      moTa: newVal.moTa || ''
    }
    console.log('Form data after update:', formData.value)
  } else {
    resetForm()
  }
}, { immediate: true })

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

      <form @submit.prevent="handleSubmit">
        <div class="uk-margin">
          <label class="uk-form-label">Mã ngành <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              v-model="formData.maNganh"
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.maNganh }"
              type="text"
              placeholder="Nhập mã ngành"
              maxlength="20"
              @blur="validateField('maNganh')"
            >
            <transition name="fade">
              <div v-if="errors.maNganh" class="error-message">{{ errors.maNganh }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Tên ngành <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              v-model="formData.tenNganh"
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.tenNganh }"
              type="text"
              placeholder="Nhập tên ngành"
              maxlength="255"
              @blur="validateField('tenNganh')"
            >
            <transition name="fade">
              <div v-if="errors.tenNganh" class="error-message">{{ errors.tenNganh }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Khoa <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <select 
              v-model="formData.khoa_id"
              class="uk-select"
              :class="{ 'uk-form-danger': errors.khoa_id }"
              @blur="validateField('khoa_id')"
            >
              <option value="">Chọn khoa</option>
              <option v-for="khoa in khoas" :key="khoa.id" :value="khoa.id">
                {{ khoa.tenKhoa }}
              </option>
            </select>
            <transition name="fade">
              <div v-if="errors.khoa_id" class="error-message">{{ errors.khoa_id }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Mô tả</label>
          <div class="uk-form-controls">
            <textarea 
              v-model="formData.moTa"
              class="uk-textarea"
              :class="{ 'uk-form-danger': errors.moTa }"
              rows="3"
              placeholder="Nhập mô tả ngành"
            ></textarea>
            <transition name="fade">
              <div v-if="errors.moTa" class="error-message">{{ errors.moTa }}</div>
            </transition>
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
  border-color: #f0506e;
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

/* Responsive styles */
@media (max-width: 640px) {
  .uk-modal-dialog {
    margin: 10px;
  }

  .uk-modal-body {
    padding: 15px;
  }

  .uk-modal-title {
    font-size: 1.25rem;
  }

  .uk-button {
    min-width: 70px;
    padding: 6px 12px;
  }
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

.uk-form-danger {
  border-color: #f0506e !important;
  box-shadow: 0 0 0 1px #f0506e !important;
}

.uk-form-danger:focus {
  border-color: #f0506e !important;
  box-shadow: 0 0 0 2px rgba(240, 80, 110, 0.1) !important;
}

.uk-select.uk-form-danger,
.uk-input.uk-form-danger,
.uk-textarea.uk-form-danger {
  background-color: #fff5f5;
}
</style>

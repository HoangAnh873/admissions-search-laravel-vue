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

const formData = ref({
  tenGiaiDoan: '',
  thuTu: '',
  ghiChu: ''
})

const errors = ref({})

const resetForm = () => {
  formData.value = {
    tenGiaiDoan: '',
    thuTu: '',
    ghiChu: ''
  }
  errors.value = {}
}

// Update modal title based on edit mode
const modalTitle = computed(() => {
  return props.editData ? 'Sửa giai đoạn xét tuyển' : 'Thêm giai đoạn xét tuyển mới'
})

const validateField = (field) => {
  errors.value[field] = ''
  
  switch (field) {
    case 'tenGiaiDoan':
      if (!formData.value.tenGiaiDoan.trim()) {
        errors.value.tenGiaiDoan = 'Vui lòng nhập tên giai đoạn xét tuyển'
      } else if (formData.value.tenGiaiDoan.length > 255) {
        errors.value.tenGiaiDoan = 'Tên giai đoạn không được vượt quá 255 ký tự'
      }
      break
    case 'thuTu':
      if (!formData.value.thuTu) {
        errors.value.thuTu = 'Vui lòng nhập thứ tự'
      } else if (isNaN(formData.value.thuTu) || formData.value.thuTu < 1) {
        errors.value.thuTu = 'Thứ tự phải là số và lớn hơn 0'
      }
      break
  }
}

// Watch for form data changes and validate
watch(() => formData.value.tenGiaiDoan, () => validateField('tenGiaiDoan'))
watch(() => formData.value.thuTu, () => validateField('thuTu'))

const validateForm = () => {
  validateField('tenGiaiDoan')
  validateField('thuTu')
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
      tenGiaiDoan: formData.value.tenGiaiDoan,
      thuTu: parseInt(formData.value.thuTu),
      ghiChu: formData.value.ghiChu
    }

    console.log('Data being sent:', dataToSend)

    if (props.editData) {
      // Update
      const response = await axios.put(`/api/giai-doan-tuyen-sinhs/${props.editData.id}`, dataToSend)
      console.log('Update response:', response)
      store.dispatch('toast/success', 'Cập nhật giai đoạn xét tuyển thành công')
    } else {
      // Create
      const response = await axios.post('/api/giai-doan-tuyen-sinhs', dataToSend)
      console.log('Create response:', response)
      store.dispatch('toast/success', 'Thêm giai đoạn xét tuyển thành công')
    }
 
    // Emit success và đóng form
    emit('success')
    handleClose()
  } catch (error) {
    console.error('Error:', error.response?.data || error)
    if (error.response?.data?.errors) {
      // Cập nhật errors với dữ liệu từ server
      errors.value = error.response.data.errors
    } else {
      store.dispatch('toast/error', `Không thể lưu giai đoạn xét tuyển: ${error.response?.data?.message || error.message}`)
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
      tenGiaiDoan: newVal.tenGiaiDoan || '',
      thuTu: newVal.thuTu || '',
      ghiChu: newVal.ghiChu || ''
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
</script>

<template>
  <div v-if="show" class="uk-modal uk-open" style="display: block;">
    <div class="uk-modal-dialog uk-modal-body">
      <button class="uk-modal-close-default" type="button" uk-close @click="handleClose"></button>
      <h2 class="uk-modal-title">{{ modalTitle }}</h2>

      <form @submit.prevent="handleSubmit">
        <div class="uk-margin">
          <label class="uk-form-label">Tên giai đoạn xét tuyển <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              type="text" 
              v-model="formData.tenGiaiDoan" 
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.tenGiaiDoan }"
              placeholder="Nhập tên giai đoạn xét tuyển"
              maxlength="255"
              @blur="validateField('tenGiaiDoan')"
            >
            <transition name="fade">
              <div v-if="errors.tenGiaiDoan" class="error-message">{{ errors.tenGiaiDoan }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Thứ tự <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              type="number" 
              v-model="formData.thuTu" 
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.thuTu }"
              placeholder="Nhập thứ tự"
              min="1"
              @blur="validateField('thuTu')"
            >
            <transition name="fade">
              <div v-if="errors.thuTu" class="error-message">{{ errors.thuTu }}</div>
            </transition>
          </div>
        </div>

        <div class="uk-margin">
          <label class="uk-form-label">Ghi chú</label>
          <div class="uk-form-controls">
            <textarea 
              v-model="formData.ghiChu" 
              class="uk-textarea" 
              rows="3"
              placeholder="Nhập ghi chú (nếu có)"
            ></textarea>
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

.uk-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
}

.uk-input:focus {
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

.uk-input.uk-form-danger {
  background-color: #fff5f5;
}

.uk-modal-footer {
  border-top: 1px solid #e5e5e5;
  padding-top: 1rem;
  margin-top: 1.5rem;
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
</style>

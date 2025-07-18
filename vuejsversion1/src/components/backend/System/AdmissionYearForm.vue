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
  nam: ''
})

const errors = ref({})

const resetForm = () => {
  formData.value = {
    nam: ''
  }
  errors.value = {}
}

// Update modal title based on edit mode
const modalTitle = computed(() => {
  return props.editData ? 'Sửa năm tuyển sinh' : 'Thêm năm tuyển sinh mới'
})

const validateField = (field) => {
  errors.value[field] = ''
  
  switch (field) {
    case 'nam':
      if (!formData.value.nam) {
        errors.value.nam = 'Vui lòng nhập năm tuyển sinh'
      } else if (!/^\d{4}$/.test(formData.value.nam)) {
        errors.value.nam = 'Năm tuyển sinh phải là 4 chữ số'
      } else {
        const year = parseInt(formData.value.nam)
        const currentYear = new Date().getFullYear()
        if (year < 2000 || year > currentYear + 1) {
          errors.value.nam = `Năm tuyển sinh phải từ 2000 đến ${currentYear + 1}`
        }
      }
      break
  }
}

// Watch for form data changes and validate
watch(() => formData.value.nam, () => validateField('nam'))

const validateForm = () => {
  validateField('nam')
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
      nam: formData.value.nam
    }

    console.log('Data being sent:', dataToSend)

    if (props.editData) {
      // Update
      const response = await axios.put(`/api/nam-xet-tuyens/${props.editData.id}`, dataToSend)
      console.log('Update response:', response)
      store.dispatch('toast/success', 'Cập nhật năm tuyển sinh thành công')
    } else {
      // Create
      const response = await axios.post('/api/nam-xet-tuyens', dataToSend)
      console.log('Create response:', response)
      store.dispatch('toast/success', 'Thêm năm tuyển sinh thành công')
    }

    // Emit success và đóng form
    emit('success')
    handleClose()
  } catch (error) {
    console.error('Error:', error.response?.data || error)
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      store.dispatch('toast/error', `Không thể lưu năm tuyển sinh: ${error.response?.data?.message || error.message}`)
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
      nam: newVal.nam || ''
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
          <label class="uk-form-label">Năm tuyển sinh <span class="uk-text-danger">*</span></label>
          <div class="uk-form-controls">
            <input 
              type="text" 
              v-model="formData.nam" 
              class="uk-input" 
              :class="{ 'uk-form-danger': errors.nam }"
              placeholder="Nhập năm tuyển sinh (VD: 2024)"
              maxlength="4"
              @blur="validateField('nam')"
            >
            <transition name="fade">
              <div v-if="errors.nam" class="error-message">{{ errors.nam }}</div>
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

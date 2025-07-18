<script setup>
import { ref, watch } from 'vue'
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
const form = ref({
  tenKhoa: ''
})

const errors = ref({})

// Reset form và errors khi modal đóng
watch(() => props.show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

// Cập nhật form khi có dữ liệu edit
watch(() => props.editData, (newVal) => {
  if (newVal) {
    form.value = { ...newVal }
  }
}, { immediate: true })

const resetForm = () => {
  form.value = {
    tenKhoa: ''
  }
  errors.value = {}
}

const validateForm = () => {
  errors.value = {}
  let isValid = true

  if (!form.value.tenKhoa) {
    errors.value.tenKhoa = 'Tên khoa không được để trống'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    loading.value = true
    await csrf.getCookie()

    if (props.editData) {
      // Cập nhật khoa
      await axios.put(`/api/khoas/${props.editData.id}`, form.value)
      store.dispatch('toast/success', 'Cập nhật khoa thành công')
    } else {
      // Thêm khoa mới
      await axios.post('/api/khoas', form.value)
      store.dispatch('toast/success', 'Thêm khoa mới thành công')
    }

    emit('success')
    emit('close')
  } catch (error) {
    console.error('Lỗi khi lưu khoa:', error)
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      store.dispatch('toast/error', `Không thể lưu khoa: ${error.response?.data?.message || error.message}`)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="show" class="uk-modal uk-open" style="display: block;">
    <div class="uk-modal-dialog">
      <button class="uk-modal-close-default" type="button" uk-close @click="emit('close')"></button>
      
      <div class="uk-modal-header">
        <h2 class="uk-modal-title">{{ editData ? 'Sửa khoa' : 'Thêm khoa mới' }}</h2>
      </div>

      <div class="uk-modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- Tên khoa -->
          <div class="uk-margin">
            <label class="uk-form-label">Tên khoa <span class="uk-text-danger">*</span></label>
            <div class="uk-form-controls">
              <input
                v-model="form.tenKhoa"
                class="uk-input"
                :class="{ 'uk-form-danger': errors.tenKhoa }"
                type="text"
                placeholder="Nhập tên khoa"
              >
              <div v-if="errors.tenKhoa" class="uk-text-danger uk-text-small">
                {{ errors.tenKhoa }}
              </div>
            </div>
          </div>
        </form>
      </div>

      <div class="uk-modal-footer uk-text-right">
        <button
          class="uk-button uk-button-default uk-margin-small-right"
          @click="emit('close')"
          :disabled="loading"
        >
          Hủy
        </button>
        <button
          class="uk-button uk-button-primary"
          @click="handleSubmit"
          :disabled="loading"
        >
          <span v-if="loading" uk-spinner="ratio: 0.6"></span>
          <span v-else>{{ editData ? 'Cập nhật' : 'Thêm mới' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.uk-modal {
  background: rgba(0, 0, 0, 0.6);
}
.uk-modal-dialog {
  width: 500px;
  max-width: 90vw;
}
.uk-form-label {
  font-weight: 500;
}
.uk-text-danger {
  color: #f0506e;
}
</style>

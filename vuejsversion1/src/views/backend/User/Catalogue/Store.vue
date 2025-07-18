<script setup>
import Layout from '@/components/backend/layout.vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/config/axios'
import csrf from '@/config/csrf'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()
const formData = ref({
  name: '',
  description: ''
})

const formErrorMessage = ref({})

const handleSubmit = async () => {
  formErrorMessage.value = {}

  try {
    await csrf.getCookie()

    const response = await axios.post(
      '/api/user/catalogue/store',
      formData.value,
      {
        validateStatus: () => true // Luôn cho phép nhận response kể cả khi status là lỗi
      }
    )

    sessionStorage.setItem('showSuccessToast', response.message)
    router.push({ name: 'user.catalogue.index' })

    // Nếu có lỗi từ Laravel validation
    if (response.errors) {
      Object.keys(response.errors).forEach(key => {
        formErrorMessage.value[key] = response.errors[key][0]
      })
      return
    }

    // Nếu thành công, có thể redirect hoặc hiển thị thông báo
    console.log('Tạo nhóm thành công:', response)
    // router.push({ name: 'user.catalogue.index' })

  } catch (error) {
    // Trường hợp lỗi không mong muốn (ví dụ: không kết nối được)
    formErrorMessage.value.message = error.message || 'Đã có lỗi xảy ra.'
  }
}
</script>



<template>
    <Layout>
      <template #template>
        <div class="table-container">
          <div class="header">
            <h2>Thêm mới nhóm thành viên</h2>
          </div>
  
          <form @submit.prevent="handleSubmit" class="uk-form-stacked">
            <!-- Tên nhóm -->
            <div class="uk-margin">
              <label class="uk-form-label">Tên nhóm</label>
              <input
                v-model="formData.name"
                class="uk-input"
                type="text"
                placeholder="Nhập tên nhóm"
                style="padding: 10px 14px; border-radius: 6px; border: 1px solid #ccc;"
              />
              <div v-if="formErrorMessage.name" class="error-message">{{ formErrorMessage.name }}</div>
            </div>
  
            <!-- Vai trò -->
            <div class="uk-margin">
              <label class="uk-form-label">Vai trò</label>
              <input
                v-model="formData.description"
                class="uk-input"
                type="text"
                placeholder="Nhập vai trò của nhóm"
                style="padding: 10px 14px; border-radius: 6px; border: 1px solid #ccc;"
              />
              <div v-if="formErrorMessage.role" class="error-message">{{ formErrorMessage.role }}</div>
            </div>
  
            <!-- Trạng thái -->
            <!-- <div class="uk-margin">
              <label class="uk-form-label">Trạng thái</label>
              <select
                v-model="formData.status"
                class="uk-select"
                style="padding: 10px 14px; border-radius: 6px; border: 1px solid #ccc;"
              >
                <option value="Đang hoạt động">Đang hoạt động</option>
                <option value="Ngưng hoạt động">Ngưng hoạt động</option>
              </select>
            </div> -->
  
            <!-- Nút hành động -->
            <div class="uk-margin uk-flex uk-flex-right" style="gap: 10px;">
              <router-link
                :to="{ name: 'user.catalogue.index' }"
                class="uk-button btn btn-danger"
                style="border-radius: 6px;"
              >
                Hủy
              </router-link>
              <button type="submit" class="uk-button btn btn-primary" style="border-radius: 6px;">
                <i class="fas fa-save"></i> Lưu nhóm
              </button>
            </div>
            
          </form>
        </div>
      </template>
    </Layout>
  </template>

<script setup>
import Layout from '@/components/backend/layout.vue'
import { onMounted, ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import axios from '@/config/axios'
import ApexCharts from 'vue3-apexcharts'
import '@/assets/backend/css/dashboard.css'

const store = useStore()
const loading = ref(true)
const thongKe = ref({
    tong_nganh: 0,
    tong_chi_tieu: 0,
    diem_tb: 0
})

const namId = ref(null)
const namGanNhat = ref(null)

const phuongThucCategories = ref([])
const phuongThucSeries = ref([])

const phuongThucChartOptions = ref({
  chart: {
    id: 'bar-phuong-thuc',
    toolbar: { show: false },
  },
  xaxis: {
    categories: phuongThucCategories.value,
  },
  dataLabels: { enabled: false },
  colors: ['#6366f1'],
  tooltip: { enabled: true },
  plotOptions: {
    bar: {
      borderRadius: 4,
      horizontal: false,
    }
  },
})

watch(phuongThucCategories, (newVal) => {
  phuongThucChartOptions.value = {
    ...phuongThucChartOptions.value,
    xaxis: {
      categories: newVal
    }
  }
})

const loadNamGanNhat = async () => {
    try {
        const res = await axios.get('/api/thong-ke/nam-gan-nhat')
        if (res && res.success && res.data) {
            namId.value = res.data.id
            namGanNhat.value = res.data
        } else {
            namId.value = 9
            namGanNhat.value = { id: 9, nam: 2024 }
        }
    } catch (error) {
        console.error('Lỗi lấy năm gần nhất:', error)
        namId.value = 9
        namGanNhat.value = { id: 9, nam: 2024 }
    }
}

const loadThongKe = async () => {
    if (!namId.value) return
    
    loading.value = true
    try {
        const data = await axios.get(`/api/thong-ke/nam/${namId.value}`)
        if (data && Object.keys(data).length > 0) {
            thongKe.value = {
                tong_nganh: data.tong_nganh ?? thongKe.value.tong_nganh,
                tong_chi_tieu: data.tong_chi_tieu ?? thongKe.value.tong_chi_tieu,
                diem_tb: data.diem_tb ?? thongKe.value.diem_tb
            }
        }
    } catch (err) {
        console.error('Lỗi tải thống kê:', err)
        store.dispatch('toast/error', 'Không thể tải dữ liệu thống kê')
    } finally {
        loading.value = false
    }
}

const loadThongKePhuongThuc = async () => {
  if (!namId.value) return

  try {
    const data = await axios.get(`/api/thong-ke/phuong-thuc/${namId.value}`)
    if (Array.isArray(data) && data.length > 0) {
      phuongThucCategories.value = data.map(item => item.phuongThuc?.tenPhuongThuc || `Phương thức ${item.phuong_thuc_id}`)
      phuongThucSeries.value = [{
        name: 'Chỉ tiêu',
        data: data.map(item => item.tong_chi_tieu || 0)
      }]
    } else {
      phuongThucCategories.value = []
      phuongThucSeries.value = []
    }
  } catch (err) {
    console.error('Lỗi tải thống kê theo phương thức:', err)
    store.dispatch('toast/error', 'Không thể tải dữ liệu thống kê theo phương thức')
  }
}

const currentYearName = computed(() => namGanNhat.value ? namGanNhat.value.nam : '2024')

onMounted(async () => {
    await loadNamGanNhat()
    const showToast = sessionStorage.getItem('showLoginSuccess')
    if (showToast) {
        store.dispatch('toast/success', 'Đăng nhập thành công!')
        sessionStorage.removeItem('showLoginSuccess')
    }
    await loadThongKe()
    await loadThongKePhuongThuc()
})
</script>

<template>
  <Layout>
    <template #template>
      <div class="dashboard-container">
        <div class="dashboard-header">
          <div class="header-content">
            <div class="header-text">
              <h1 class="dashboard-title">Dashboard Tuyển Sinh</h1>
              <p class="dashboard-subtitle">Thống kê tổng quan năm học {{ currentYearName }}</p>
            </div>
            <div class="header-badge">
              <span class="status-badge">Năm học {{ currentYearName }}</span>
            </div>
          </div>
        </div>

        <div class="dashboard-content">
          <div v-if="loading" class="dashboard-loading">
            <div class="loading-content">
              <div class="loading-spinner"><div class="spinner"></div></div>
              <div class="loading-text">
                <h3>Đang tải dữ liệu thống kê</h3>
                <p>Vui lòng đợi trong giây lát...</p>
              </div>
            </div>
          </div>

          <div v-else class="dashboard-main">
            <!-- Thống kê tổng quan -->
            <div class="stats-grid">
              <div class="stat-card stat-card-primary">
                <div class="stat-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                    <path d="M2 17L12 22L22 17"/>
                    <path d="M2 12L12 17L22 12"/>
                  </svg>
                </div>
                <div class="stat-content">
                  <h3 class="stat-title">Tổng ngành</h3>
                  <p class="stat-value">{{ thongKe.tong_nganh }}</p>
                  <span class="stat-label">Ngành đào tạo</span>
                </div>
              </div>

              <div class="stat-card stat-card-success">
                <div class="stat-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21V19A4 4 0 0 0 13 15H5A4 4 0 0 0 1 19V21"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21V19A4 4 0 0 0 16.5 15.5L23 21Z"/>
                    <path d="M16 3.13A4 4 0 0 1 16 10.87"/>
                  </svg>
                </div>
                <div class="stat-content">
                  <h3 class="stat-title">Tổng chỉ tiêu</h3>
                  <p class="stat-value">{{ thongKe.tong_chi_tieu.toLocaleString() }}</p>
                  <span class="stat-label">Sinh viên</span>
                </div>
              </div>
            </div>

            <!-- Biểu đồ chỉ tiêu theo phương thức tuyển sinh nằm dưới -->
            <div class="chart-container" style="max-width: 700px; margin: 40px auto;">
              <h3>Biểu đồ số lượng chỉ tiêu theo phương thức tuyển sinh</h3>
              <ApexCharts
                type="bar"
                :options="phuongThucChartOptions"
                :series="phuongThucSeries"
                height="360"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </Layout>
</template>

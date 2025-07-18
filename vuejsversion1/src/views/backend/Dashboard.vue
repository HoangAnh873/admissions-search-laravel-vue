<script setup>
    import Layout from '@/components/backend/layout.vue'
    import { onMounted, ref } from 'vue'
    import { useStore } from 'vuex'
    import axios from '@/config/axios'
    import '@/assets/backend/css/dashboard.css'

    // Chart.js imports
    import { Line } from 'vue-chartjs'
    import {
      Chart,
      LineElement,
      PointElement,
      CategoryScale,
      LinearScale,
      Title,
      Tooltip,
      Legend
    } from 'chart.js'
    Chart.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend)

    const store = useStore()
    const loading = ref(true)
    const thongKe = ref({
        tong_nganh: 0,
        tong_chi_tieu: 0,
        diem_tb: 0
    })

    // Dữ liệu mẫu cho nhiều năm (có thể lấy từ API nếu backend hỗ trợ)
    const years = ref([])
    const diemTBs = ref([])
    const chiTieuArr = ref([])

    const namId = 8 // ví dụ: năm 2023

    const loadThongKe = async () => {
        loading.value = true
        try {
            const data = await axios.get(`/api/thong-ke/nam/${namId}`)
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

    const loadThongKeNhieuNam = async () => {
      try {
        const res = await axios.get('/api/thong-ke/nhieu-nam')
        console.log('API nhieu-nam:', res)
        if (Array.isArray(res)) {
          years.value = res.map(item => String(item.nam ?? ''))
          diemTBs.value = res.map(item => Number(item.diem_tb ?? 0))
          chiTieuArr.value = res.map(item => Number(item.chi_tieu ?? 0))
          console.log('years', years.value)
          console.log('diemTBs', diemTBs.value)
          console.log('chiTieuArr', chiTieuArr.value)
        }
      } catch (e) {
        console.error('Lỗi lấy dữ liệu nhiều năm:', e)
      }
    }

    onMounted(() => {
        loadThongKeNhieuNam()
        const showToast = sessionStorage.getItem('showLoginSuccess')
        if (showToast) {
            store.dispatch('toast/success', 'Đăng nhập thành công!')
            sessionStorage.removeItem('showLoginSuccess')
        }
        loadThongKe()
    })
</script>

<template>
    <Layout>
        <template #template>
            <div class="dashboard-container">
                <!-- Header Section -->
                <div class="dashboard-header">
                    <div class="header-content">
                        <div class="header-text">
                            <h1 class="dashboard-title">Dashboard Tuyển Sinh</h1>
                            <p class="dashboard-subtitle">Thống kê tổng quan năm học 2023</p>
                        </div>
                        <div class="header-badge">
                            <span class="status-badge">Năm học 2023</span>
                        </div>
                    </div>
                </div>

                <div class="dashboard-content">
                    <!-- Loading State -->
                    <div v-if="loading" class="dashboard-loading">
                        <div class="loading-content">
                            <div class="loading-spinner">
                                <div class="spinner"></div>
                            </div>
                            <div class="loading-text">
                                <h3>Đang tải dữ liệu thống kê</h3>
                                <p>Vui lòng đợi trong giây lát...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Main Content -->
                    <div v-else class="dashboard-main">
                        <!-- Stats Cards -->
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

                        <!-- Charts Section -->
                        <div v-if="years.length && diemTBs.length && chiTieuArr.length && years.length === diemTBs.length && years.length === chiTieuArr.length" class="charts-section">
                            <div class="chart-card">
                                <div class="chart-header">
                                    <h3 class="chart-title">Xu hướng điểm trung bình</h3>
                                    <div class="chart-period">2021 - 2023</div>
                                </div>
                                <div class="chart-content">
                                    <Line
                                      :data="{
                                        labels: years,
                                        datasets: [
                                          {
                                            label: 'Điểm TB',
                                            data: diemTBs,
                                            borderColor: '#3b82f6',
                                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                            tension: 0.4,
                                            fill: true,
                                            pointBackgroundColor: '#3b82f6',
                                            pointBorderColor: '#ffffff',
                                            pointBorderWidth: 2,
                                            pointRadius: 6,
                                            pointHoverRadius: 8,
                                            borderWidth: 3
                                          }
                                        ]
                                      }"
                                      :options="{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: {
                                          legend: { 
                                            display: false
                                          },
                                          title: { display: false }
                                        },
                                        scales: {
                                          y: {
                                            beginAtZero: false,
                                            min: 17,
                                            max: 22,
                                            title: { 
                                              display: true, 
                                              text: 'Điểm trung bình',
                                              font: { size: 12, weight: 'bold' }
                                            },
                                            grid: {
                                              color: '#f1f5f9'
                                            }
                                          },
                                          x: {
                                            title: { 
                                              display: true, 
                                              text: 'Năm học',
                                              font: { size: 12, weight: 'bold' }
                                            },
                                            grid: {
                                              display: false
                                            }
                                          }
                                        },
                                        interaction: {
                                          intersect: false,
                                          mode: 'index'
                                        }
                                      }"
                                    />
                                </div>
                            </div>

                            <div class="chart-card">
                                <div class="chart-header">
                                    <h3 class="chart-title">Xu hướng chỉ tiêu tuyển sinh</h3>
                                    <div class="chart-period">2021 - 2023</div>
                                </div>
                                <div class="chart-content">
                                    <Line
                                      :data="{
                                        labels: years,
                                        datasets: [
                                          {
                                            label: 'Tổng chỉ tiêu',
                                            data: chiTieuArr,
                                            borderColor: '#10b981',
                                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                            tension: 0.4,
                                            fill: true,
                                            pointBackgroundColor: '#10b981',
                                            pointBorderColor: '#ffffff',
                                            pointBorderWidth: 2,
                                            pointRadius: 6,
                                            pointHoverRadius: 8,
                                            borderWidth: 3
                                          }
                                        ]
                                      }"
                                      :options="{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: {
                                          legend: { 
                                            display: false
                                          },
                                          title: { display: false }
                                        },
                                        scales: {
                                          y: {
                                            beginAtZero: false,
                                            min: 1000,
                                            max: 1600,
                                            title: { 
                                              display: true, 
                                              text: 'Chỉ tiêu (sinh viên)',
                                              font: { size: 12, weight: 'bold' }
                                            },
                                            grid: {
                                              color: '#f1f5f9'
                                            }
                                          },
                                          x: {
                                            title: { 
                                              display: true, 
                                              text: 'Năm học',
                                              font: { size: 12, weight: 'bold' }
                                            },
                                            grid: {
                                              display: false
                                            }
                                          }
                                        },
                                        interaction: {
                                          intersect: false,
                                          mode: 'index'
                                        }
                                      }"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </Layout>
</template>
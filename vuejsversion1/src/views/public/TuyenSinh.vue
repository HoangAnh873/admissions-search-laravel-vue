<template>
  <public-layout>
    <div class="page-container">
      <h1 class="page-title">Thông tin tuyển sinh</h1>
      
      <div class="tuyen-sinh-content">
        <div v-if="loading" class="loading">Đang tải dữ liệu...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        
        <template v-else>
          <section class="info-section">
            <h2 class="section-title">Phương thức tuyển sinh</h2>
            <div class="grid-container">
              <div class="card" v-for="method in phuongThuc" :key="method.id">
                <h3 class="card-title">{{ method.tenPhuongThuc }}</h3>
                <p class="card-text">{{ method.ghiChu }}</p>
              </div>
            </div>
          </section>

          <section class="timeline-section">
            <h2 class="section-title">Quy trình tuyển sinh</h2>
            <div class="timeline">
              <div class="timeline-item" v-for="stage in giaiDoan" :key="stage.id">
                <div class="timeline-date">Bước {{ stage.thuTu }}</div>
                <div class="timeline-content">
                  <h3 class="card-title">{{ stage.tenGiaiDoan }}</h3>
                  <p class="card-text">{{ stage.ghiChu }}</p>
                </div>
              </div>
            </div>
          </section>
        </template>
      </div>
      <!-- Section trạng thái ngành -->
      <section class="status-section">
        <h2 class="section-title">Trạng thái ngành xét tuyển</h2>
        <div v-if="trangThaiNganh.length" class="grid-container">
          <div class="card" v-for="item in trangThaiNganh" :key="item.id">
            <h3 class="card-title">{{ item.nganh?.tenNganh }}</h3>
            <p class="card-text"><strong>Năm:</strong> {{ item.nam?.nam }}</p>
            <p class="card-text"><strong>Phương thức:</strong> {{ item.phuong_thuc?.tenPhuongThuc }}</p>
            <p class="card-text"><strong>Giai đoạn:</strong> {{ item.giai_doan?.tenGiaiDoan }}</p>
            <p class="card-text"><strong>Ghi chú:</strong> {{ item.ghiChu }}</p>
            <p class="card-text"><strong>Ngày cập nhật:</strong> {{ item.ngayCapNhat }}</p>
          </div>
        </div>
        <div v-else>Không có dữ liệu trạng thái ngành.</div>
      </section>
    </div>
  </public-layout>
</template>

<script>
import PublicLayout from '@/components/public/layout.vue'
import '@/assets/public/css/common.css'
import axios from '@/config/axios'

export default {
  name: 'TuyenSinhPage',
  components: {
    PublicLayout
  },
  data() {
    return {
      phuongThuc: [],
      giaiDoan: [],
      trangThaiNganh: [], // Thêm dòng này
      loading: false,
      error: null
    }
  },
  async created() {
    await this.fetchData()
    await this.fetchTrangThaiNganh() // Thêm dòng này
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const response = await axios.get('/api/public/tuyen-sinh')
        console.log('API Response:', response) // Debug log
        
        if (response && response.success && response.data) {
          this.phuongThuc = response.data.phuongThuc
          this.giaiDoan = response.data.giaiDoan
          console.log('Processed data:', { phuongThuc: this.phuongThuc, giaiDoan: this.giaiDoan }) // Debug log
        } else {
          this.error = 'Dữ liệu không hợp lệ'
        }
      } catch (error) {
        console.error('Error details:', error) // Debug log
        this.error = 'Không thể tải dữ liệu tuyển sinh'
      } finally {
        this.loading = false
      }
    },
    async fetchTrangThaiNganh() {
      try {
        const response = await axios.get('/api/public/trang-thai')
        if (response && response.success) {
          this.trangThaiNganh = response.data
        }
      } catch (e) {
        // Xử lý lỗi nếu muốn
      }
    }
  }
}
</script>

<style scoped>
.tuyen-sinh-content {
  max-width: 1000px;
  margin: 0 auto;
}

.info-section, .timeline-section {
  margin-bottom: 4rem;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.card {
  padding: 2rem;
  /* background: #fff; */
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-title {
  color: #333;
  margin-bottom: 1rem;
}

.card-text {
  color: #666;
  margin-bottom: 0.5rem;
}

/* Timeline styles */
.timeline {
  position: relative;
  padding: 2rem 0;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 100%;
  background-color: #dee2e6;
}

.timeline-item {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 3rem;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-date {
  background: #007bff;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-right: 2rem;
}

.timeline-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex: 0 1 400px;
}

.timeline-content .card-title {
  color: #333;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.timeline-content .card-text {
  color: #666;
  line-height: 1.5;
  margin: 0;
}

.timeline-content .card-text.note {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  color: #666;
  font-style: italic;
}

.timeline-content .card-text.note strong {
  color: #333;
  font-style: normal;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
}

.status-section {
  margin-bottom: 4rem;
}
.status-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: #fff;
}
.status-table th, .status-table td {
  border: 1px solid #eee;
  padding: 0.5rem 1rem;
  text-align: left;
}
.status-table th {
  background: #f8f9fa;
}
.status-table tr:nth-child(even) {
  background: #f6f6f6;
}

@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }

  .timeline::before {
    left: 0;
  }

  .timeline-item {
    flex-direction: column;
    align-items: flex-start;
    padding-left: 2rem;
  }

  .timeline-date {
    margin-bottom: 1rem;
    margin-right: 0;
  }

  .timeline-content {
    width: 100%;
  }
}
</style> 
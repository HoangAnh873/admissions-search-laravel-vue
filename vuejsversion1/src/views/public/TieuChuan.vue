<template>
  <public-layout>
    <div class="page-container">
      <h1 class="page-title">Tiêu chuẩn xét tuyển</h1>
      
      <div class="tieu-chuan-content">
        <section class="search-section">
          <div class="card">
            <div class="search-filters">
              <div class="form-group">
                <select v-model="selectedYear" class="form-input">
                  <option value="">Tất cả các năm</option>
                  <option v-for="year in years" :key="year.id" :value="year.id">
                    {{ year.nam }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <select v-model="selectedFaculty" class="form-input">
                  <option value="">Tất cả các khoa</option>
                  <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                    {{ faculty.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <input type="text" v-model="searchQuery" class="form-input" placeholder="Tìm kiếm ngành học...">
              </div>
            </div>
          </div>
        </section>

        <div v-if="loading" class="loading">Đang tải dữ liệu...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        
        <section v-else-if="faculties.length > 0" class="faculty-section" v-for="faculty in filteredFaculties" :key="faculty.id">
          <h2 class="section-title">{{ faculty.name }}</h2>
          <div class="grid-container">
            <div class="card" v-for="major in faculty.nganh" :key="major.id">
              <h3 class="card-title">{{ major.tenNganh }}</h3>
              <div class="major-details">
                <p class="card-text"><strong>Mã ngành:</strong> {{ major.maNganh }}</p>
                
                <div class="admission-criteria">
                  <h4 class="criteria-title">Bảng tiêu chuẩn xét tuyển</h4>
                  <div v-if="major.tieuChuan && major.tieuChuan.length > 0">
                    <table class="criteria-table">
                      <thead>
                        <tr>
                          <th>Năm</th>
                          <th>Tổ hợp môn</th>
                          <th>Điểm tối thiểu</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(criteria, index) in sortedTieuChuan(major.tieuChuan)" :key="index">
                          <td>{{ criteria.nam.nam }}</td>
                          <td>{{ criteria.toHop }}</td>
                          <td><strong>{{ criteria.diemToiThieu }}</strong></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="no-criteria">
                    Chưa có thông tin tiêu chuẩn xét tuyển
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        <div v-else class="no-data">Không có dữ liệu ngành học</div>
      </div>
    </div>
  </public-layout>
</template>

<script>
import PublicLayout from '@/components/public/layout.vue'
import '@/assets/public/css/common.css'
import axios from '@/config/axios'

export default {
  name: 'TieuChuanPage',
  components: {
    PublicLayout
  },
  data() {
    return {
      searchQuery: '',
      selectedYear: '',
      selectedFaculty: '',
      faculties: [],
      admissionCriteria: [],
      years: [],
      loading: true,
      error: null
    }
  },
  watch: {
    selectedYear() {
      this.fetchAdmissionCriteria()
    }
  },
  computed: {
    filteredFaculties() {
      let faculties = this.faculties
      if (this.selectedFaculty) {
        faculties = faculties.filter(faculty => faculty.id === this.selectedFaculty)
      }
      if (!this.searchQuery) return faculties
      const query = this.searchQuery.toLowerCase()
      return faculties.map(faculty => ({
        ...faculty,
        nganh: faculty.nganh.filter(major => 
          major.tenNganh.toLowerCase().includes(query) ||
          major.maNganh.toLowerCase().includes(query)
        )
      })).filter(faculty => faculty.nganh.length > 0)
    }
  },
  async created() {
    await Promise.all([
      this.fetchFaculties(),
      this.fetchYears(),
      this.fetchAdmissionCriteria()
    ])
    // Không chọn mặc định năm hay khoa
    this.selectedYear = ''
    this.selectedFaculty = ''
    await this.fetchAdmissionCriteria()
  },
  methods: {
    async fetchYears() {
      try {
        const response = await axios.get('/api/public/nam')
        this.years = response.data.sort((a, b) => b.nam - a.nam)
      } catch (error) {
        console.error('Lỗi khi tải dữ liệu năm:', error)
        this.error = 'Không thể tải dữ liệu năm'
      }
    },

    async fetchFaculties() {
      try {
        const response = await axios.get('/api/public/nganh')
        const groupedByKhoa = response.data.reduce((acc, nganh) => {
          const khoa = nganh.khoa
          if (!acc[khoa.id]) {
            acc[khoa.id] = {
              id: khoa.id,
              name: khoa.tenKhoa,
              nganh: []
            }
          }
          acc[khoa.id].nganh.push({
            id: nganh.id,
            tenNganh: nganh.tenNganh,
            maNganh: nganh.maNganh,
            tieuChuan: []
          })
          return acc
        }, {})
        
        this.faculties = Object.values(groupedByKhoa)
      } catch (error) {
        console.error('Lỗi khi tải dữ liệu ngành:', error)
        this.error = 'Không thể tải dữ liệu ngành học'
      }
    },

    async fetchAdmissionCriteria() {
      try {
        this.loading = true
        const params = {}
        if (this.selectedYear) {
          params.nam_id = this.selectedYear
        }
        const response = await axios.get('/api/public/tieu-chuan', { params })
        this.admissionCriteria = response.data
        // Cập nhật lại dữ liệu tiêu chuẩn cho các ngành
        if (this.faculties.length > 0) {
          this.faculties.forEach(faculty => {
            faculty.nganh.forEach(major => {
              major.tieuChuan = this.admissionCriteria
                .filter(c => c.nganh_id === major.id)
                .map(c => ({
                  nam: c.nam,
                  toHop: c.toHop,
                  diemToiThieu: c.diemToiThieu,
                  ghiChu: c.ghiChu
                }))
            })
          })
        }
      } catch (error) {
        console.error('Lỗi khi tải tiêu chuẩn xét tuyển:', error)
        this.error = 'Không thể tải dữ liệu tiêu chuẩn xét tuyển'
      } finally {
        this.loading = false
      }
    },
    sortedTieuChuan(tieuChuanArr) {
      if (!Array.isArray(tieuChuanArr)) return [];
      return [...tieuChuanArr].sort((a, b) => b.nam.nam - a.nam.nam);
    }
  }
}
</script>

<style scoped>
.tieu-chuan-content {
  max-width: 1000px;
  margin: 0 auto;
}

.search-section {
  margin-bottom: 3rem;
}

.faculty-section {
  margin-bottom: 4rem;
}

.card {
  padding: 2rem;
}

.card-title {
  color: #333;
  margin-bottom: 1rem;
}

.card-text {
  color: #666;
  margin-bottom: 0.5rem;
}

.major-details {
  margin-top: 1rem;
}

.admission-criteria {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.criteria-title {
  color: #333;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.criteria-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.criteria-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.8rem;
}

.year-badge {
  background: #007bff;
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.9rem;
}

.criteria-content {
  color: #666;
}

.criteria-content p {
  margin-bottom: 0.5rem;
}

.criteria-content p:last-child {
  margin-bottom: 0;
}

.no-criteria {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.form-control {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #e9ecef;
  border-radius: 4px;
  transition: border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
}

@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }

  .criteria-header {
    flex-direction: column;
    gap: 0.5rem;
  }
}

.loading, .error, .no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
}

.no-data {
  color: #666;
  font-style: italic;
}

.search-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.form-group {
  width: 100%;
}

.form-input {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #e9ecef;
  border-radius: 4px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
}

.criteria-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: #fff;
}
.criteria-table th, .criteria-table td {
  border: 1px solid #e9ecef;
  padding: 0.7rem 0.5rem;
  text-align: center;
}
.criteria-table th {
  background: #f1f3f5;
  color: #333;
  font-weight: 600;
}
.criteria-table td {
  color: #444;
}
.criteria-table tr:nth-child(even) {
  background: #f8f9fa;
}
</style> 
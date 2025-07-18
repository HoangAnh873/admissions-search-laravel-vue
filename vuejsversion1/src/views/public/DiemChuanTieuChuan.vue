<template>
  <public-layout>
    <div class="page-container">
      <h1 class="page-title">Tra cứu điểm chuẩn & tiêu chuẩn xét tuyển</h1>
      <div class="diemchuan-tieuchuan-content">
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
                <select v-model="selectedMethod" class="form-input">
                  <option value="">Tất cả phương thức</option>
                  <option v-for="method in phuongThuc" :key="method.id" :value="method.id">
                    {{ method.tenPhuongThuc }}
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
        <div v-else>
          <section v-if="faculties.length > 0" class="faculty-section" v-for="faculty in filteredFaculties" :key="faculty.id">
            <h2 class="section-title">{{ faculty.name }}</h2>
            <div class="grid-container">
              <div class="card" v-for="major in faculty.nganh" :key="major.id">
                <h3 class="card-title">{{ major.tenNganh }}</h3>
                <div class="major-details">
                  <p class="card-text"><strong>Mã ngành:</strong> {{ major.maNganh }}</p>
                  <div class="dual-tables">
                    <!-- Bảng điểm chuẩn -->
                    <div class="table-block">
                      <h4 class="scores-title">Bảng điểm chuẩn các năm</h4>
                      <div v-if="major.diemChuan && major.diemChuan.length > 0">
                        <table class="scores-table">
                          <thead>
                            <tr>
                              <th>Năm</th>
                              <th>Phương thức</th>
                              <th>Điểm chuẩn</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(score, index) in sortedDiemChuan(major.diemChuan)" :key="index">
                              <td>{{ score.nam.nam }}</td>
                              <td>{{ score.phuongThuc.tenPhuongThuc }}</td>
                              <td><strong>{{ score.diem }}</strong></td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else class="no-scores">
                        Chưa có thông tin điểm chuẩn
                      </div>
                    </div>
                    <!-- Bảng tiêu chuẩn -->
                    <div class="table-block">
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
            </div>
          </section>
          <div v-else class="no-data">Không có dữ liệu ngành học</div>
        </div>
      </div>
    </div>
  </public-layout>
</template>

<script>
import PublicLayout from '@/components/public/layout.vue'
import '@/assets/public/css/common.css'
import axios from '@/config/axios'

export default {
  name: 'DiemChuanTieuChuanPage',
  components: { PublicLayout },
  data() {
    return {
      activeTab: 'diemchuan',
      searchQuery: '',
      selectedYear: '',
      selectedMethod: '',
      selectedFaculty: '',
      faculties: [],
      years: [],
      phuongThuc: [],
      diemChuan: [],
      tieuChuan: [],
      loading: false,
      error: null
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
  watch: {
    selectedYear() {
      this.fetchDiemChuan();
      this.fetchTieuChuan();
    },
    selectedMethod() {
      this.fetchDiemChuan();
    },
    // Không fetch lại toàn bộ khi đổi tab, chỉ fetch lại tieuChuan nếu cần
  },
  methods: {
    async fetchFaculties() {
      this.loading = true
      try {
        const response = await axios.get('/api/public/nganh')
        if (response && response.success && response.data) {
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
              diemChuan: [],
              tieuChuan: []
            })
            return acc
          }, {})
          this.faculties = Object.values(groupedByKhoa)
        } else {
          this.error = 'Dữ liệu ngành học không hợp lệ'
        }
      } catch (error) {
        this.error = 'Không thể tải dữ liệu ngành học'
      } finally {
        this.loading = false
      }
    },
    async fetchYears() {
      this.loading = true
      try {
        const response = await axios.get('/api/public/nam')
        if (response && response.success && response.data) {
          this.years = response.data.sort((a, b) => b.nam - a.nam)
        } else {
          this.error = 'Dữ liệu năm không hợp lệ'
        }
      } catch (error) {
        this.error = 'Không thể tải dữ liệu năm'
      } finally {
        this.loading = false
      }
    },
    async fetchPhuongThuc() {
      this.loading = true
      try {
        const response = await axios.get('/api/public/phuong-thuc')
        if (response && response.success && response.data) {
          this.phuongThuc = response.data
        } else {
          this.error = 'Dữ liệu phương thức không hợp lệ'
        }
      } catch (error) {
        this.error = 'Không thể tải dữ liệu phương thức'
      } finally {
        this.loading = false
      }
    },
    async fetchDiemChuan() {
      this.loading = true
      try {
        const params = {}
        if (this.selectedYear) params.nam_id = this.selectedYear
        if (this.selectedMethod) params.phuong_thuc_id = this.selectedMethod
        const response = await axios.get('/api/public/diem-chuan', { params })
        if (response && response.success && Array.isArray(response.data)) {
          this.diemChuan = response.data
          if (this.faculties.length > 0) {
            this.faculties.forEach(faculty => {
              faculty.nganh.forEach(major => {
                major.diemChuan = this.diemChuan
                  .filter(dc => String(dc.nganh_id) === String(major.id))
                  .map(score => ({
                    nam: score.nam,
                    phuongThuc: score.phuong_thuc,
                    diem: score.diemChuan,
                    ghiChu: score.ghiChu
                  }))
              })
            })
          }
        } else {
          this.error = 'Dữ liệu điểm chuẩn không hợp lệ'
        }
      } catch (error) {
        this.error = 'Không thể tải dữ liệu điểm chuẩn'
      } finally {
        this.loading = false
      }
    },
    async fetchTieuChuan() {
      this.loading = true
      try {
        const params = {}
        if (this.selectedYear) params.nam_id = this.selectedYear
        const response = await axios.get('/api/public/tieu-chuan', { params })
        if (response && response.success && Array.isArray(response.data)) {
          this.tieuChuan = response.data
          if (this.faculties.length > 0) {
            this.faculties.forEach(faculty => {
              faculty.nganh.forEach(major => {
                major.tieuChuan = this.tieuChuan
                  .filter(c => String(c.nganh_id) === String(major.id))
                  .map(c => ({
                    nam: c.nam,
                    toHop: c.toHop,
                    diemToiThieu: c.diemToiThieu,
                    ghiChu: c.ghiChu
                  }))
              })
            })
          }
        } else {
          this.error = 'Dữ liệu tiêu chuẩn xét tuyển không hợp lệ'
        }
      } catch (error) {
        this.error = 'Không thể tải dữ liệu tiêu chuẩn xét tuyển'
      } finally {
        this.loading = false
      }
    },
    async fetchAllData() {
      this.error = null
      this.loading = true
      if (this.activeTab === 'diemchuan') {
        await this.fetchFaculties()
        await this.fetchYears()
        await this.fetchPhuongThuc()
        await this.fetchDiemChuan()
      } else {
        await this.fetchFaculties()
        await this.fetchYears()
        await this.fetchTieuChuan()
      }
      this.loading = false
    },
    sortedDiemChuan(diemChuanArr) {
      if (!Array.isArray(diemChuanArr)) return [];
      return [...diemChuanArr].sort((a, b) => b.nam.nam - a.nam.nam);
    },
    sortedTieuChuan(tieuChuanArr) {
      if (!Array.isArray(tieuChuanArr)) return [];
      return [...tieuChuanArr].sort((a, b) => b.nam.nam - a.nam.nam);
    }
  },
  async created() {
    await this.fetchFaculties();
    await this.fetchYears();
    await this.fetchDiemChuan();
    await this.fetchTieuChuan();
    this.selectedYear = '';
    this.selectedMethod = '';
    this.selectedFaculty = '';
    this.searchQuery = '';
  }
}
</script>

<style scoped>
.diemchuan-tieuchuan-content {
  max-width: 1000px;
  margin: 0 auto;
}
.search-section {
  margin-bottom: 3rem;
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
.dual-tables {
  display: flex;
  gap: 2rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}
.table-block {
  flex: 1 1 320px;
  min-width: 0;
}
@media (max-width: 900px) {
  .dual-tables {
    flex-direction: column;
    gap: 1.5rem;
  }
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
.admission-scores, .admission-criteria {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}
.scores-title, .criteria-title {
  color: #333;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}
.no-scores, .no-criteria {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
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
@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
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
.scores-table, .criteria-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: #fff;
}
.scores-table th, .scores-table td, .criteria-table th, .criteria-table td {
  border: 1px solid #e9ecef;
  padding: 0.7rem 0.5rem;
  text-align: center;
}
.scores-table th, .criteria-table th {
  background: #f1f3f5;
  color: #333;
  font-weight: 600;
}
.scores-table td, .criteria-table td {
  color: #444;
}
.scores-table tr:nth-child(even), .criteria-table tr:nth-child(even) {
  background: #f8f9fa;
}
</style> 
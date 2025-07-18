<template>
  <public-layout>
    <div class="page-container">
      <h1 class="page-title">Thông tin ngành học</h1>
      
      <div class="nganh-hoc-content">
        <section class="search-section">
          <div class="card">
            <div class="search-filters" style="display: flex; gap: 1rem; flex-wrap: wrap;">
              <select v-model="selectedFaculty" class="form-control" style="max-width: 250px;">
                <option value="">Tất cả các khoa</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
              <input type="text" v-model="searchQuery" class="form-control" placeholder="Tìm kiếm ngành học..." style="flex: 1; min-width: 200px;">
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
  name: 'NganhHocPage',
  components: {
    PublicLayout
  },
  data() {
    return {
      searchQuery: '',
      selectedFaculty: '',
      faculties: [],
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
  async created() {
    await this.fetchFaculties()
  },
  methods: {
    async fetchFaculties() {
      this.loading = true
      try {
        const response = await axios.get('/api/public/nganh')
        console.log('API Response:', response) // Debug log
        
        if (response && response.success && response.data) {
          // Nhóm ngành theo khoa
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
              maNganh: nganh.maNganh
            })
            return acc
          }, {})
          
          this.faculties = Object.values(groupedByKhoa)
          console.log('Processed faculties:', this.faculties) // Debug log
        } else {
          this.error = 'Dữ liệu không hợp lệ'
        }
      } catch (error) {
        console.error('Error details:', error) // Debug log
        this.error = 'Không thể tải dữ liệu ngành học'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.nganh-hoc-content {
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
  padding-top: 1rem;
  border-top: 1px solid #eee;
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
</style> 
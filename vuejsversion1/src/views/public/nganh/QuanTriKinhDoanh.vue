<template>
  <public-layout>
    <div class="page-container">
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <router-link to="/nganh-hoc" class="breadcrumb-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          Danh sách ngành học
        </router-link>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-current">{{ nganhInfo.tenNganh }}</span>
      </div>

      <!-- Header Section -->
      <div class="nganh-header">
        <div class="nganh-header-content">
          <div class="nganh-basic-info">
            <h1 class="nganh-title">{{ nganhInfo.tenNganh }}</h1>
            <div class="nganh-meta">
              <span class="nganh-code">Mã ngành: {{ nganhInfo.maNganh }}</span>
              <span class="nganh-faculty">Thuộc trường: {{ nganhInfo.khoa?.tenKhoa }}</span>
            </div>
          </div>
          <div class="nganh-badge">
            <span class="badge-primary">{{ nganhInfo.thoiGianDaoTao }}</span>
            <span class="badge-secondary">{{ nganhInfo.bangCap }}</span>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="nganh-content">
        <div class="content-grid">
          <!-- Left Column -->
          <div class="content-main">
            <!-- Thông tin chung -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                Thông tin chung
              </h2>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Tên ngành:</span>
                  <span class="info-value">{{ nganhInfo.tenNganh }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Thời gian đào tạo:</span>
                  <span class="info-value">{{ nganhInfo.thoiGianDaoTao }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Danh hiệu cấp bằng:</span>
                  <span class="info-value">{{ nganhInfo.bangCap }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Mã ngành tuyển sinh:</span>
                  <span class="info-value">{{ nganhInfo.maNganh }}</span>
                </div>
              </div>
            </section>

            <!-- Phương thức xét tuyển -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4"/>
                  <path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z"/>
                </svg>
                Phương thức xét tuyển
              </h2>
              <div class="phuong-thuc-list">
                <div class="phuong-thuc-item" v-for="(phuongThuc, index) in nganhInfo.phuongThucXetTuyen" :key="index">
                  <h3 class="phuong-thuc-title">{{ phuongThuc.ten }}</h3>
                  <div v-if="phuongThuc.toHop && phuongThuc.toHop.length > 0" class="to-hop-list">
                    <h4>Tổ hợp xét tuyển:</h4>
                    <ul>
                      <li v-for="toHop in phuongThuc.toHop" :key="toHop">{{ toHop }}</li>
                    </ul>
                  </div>
                  <div v-if="phuongThuc.ghiChu" class="phuong-thuc-note">
                    {{ phuongThuc.ghiChu }}
                  </div>
                </div>
              </div>
            </section>

            <!-- Mục tiêu đào tạo -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                </svg>
                Mục tiêu đào tạo
              </h2>
              <div class="intro-content">
                <p>{{ nganhInfo.mucTieuDaoTao }}</p>
              </div>
            </section>

            <!-- Vị trí việc làm -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                Vị trí việc làm
              </h2>
              <div class="career-list">
                <ul>
                  <li v-for="(viTri, index) in nganhInfo.viTriViecLam" :key="index">{{ viTri }}</li>
                </ul>
              </div>
            </section>

            <!-- Khả năng học tập, nâng cao trình độ -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9,22 9,12 15,12 15,22"/>
                </svg>
                Khả năng học tập, nâng cao trình độ sau khi ra trường
              </h2>
              <div class="workplace-list">
                <ul>
                  <li v-for="(noiLamViec, index) in nganhInfo.noiLamViec" :key="index">{{ noiLamViec }}</li>
                </ul>
              </div>
            </section>
          </div>

          <!-- Right Sidebar -->
          <div class="content-sidebar">
            <div class="sidebar-card">
              <h3 class="sidebar-title">Thông tin nhanh</h3>
              <div class="quick-info">
                <div class="quick-info-item">
                  <span class="quick-label">Mã ngành</span>
                  <span class="quick-value">{{ nganhInfo.maNganh }}</span>
                </div>
                <div class="quick-info-item">
                  <span class="quick-label">Thời gian đào tạo</span>
                  <span class="quick-value">{{ nganhInfo.thoiGianDaoTao }}</span>
                </div>
                <div class="quick-info-item">
                  <span class="quick-label">Bằng cấp</span>
                  <span class="quick-value">{{ nganhInfo.bangCap }}</span>
                </div>
                <div class="quick-info-item">
                  <span class="quick-label">Số phương thức xét tuyển</span>
                  <span class="quick-value">{{ nganhInfo.phuongThucXetTuyen?.length || 0 }}</span>
                </div>
              </div>
            </div>

            <div class="sidebar-card">
              <h3 class="sidebar-title">Liên quan</h3>
              <div class="related-links">
                <router-link to="/diem-chuan-tieu-chuan" class="related-link">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12l2 2 4-4"/>
                    <path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z"/>
                  </svg>
                  Điểm chuẩn & Tiêu chuẩn
                </router-link>
                <router-link to="/nganh-hoc" class="related-link">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                    <path d="M2 17L12 22L22 17"/>
                    <path d="M2 12L12 17L22 12"/>
                  </svg>
                  Danh sách môn học
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </public-layout>
</template>

<script>
import PublicLayout from '@/components/public/layout.vue'
import '@/assets/public/css/common.css'
import '@/assets/public/css/nganh-detail.css'
import axios from '@/config/axios'

export default {
  name: 'QuanTriKinhDoanhPage',
  components: {
    PublicLayout
  },
  data() {
    return {
      nganhId: null,
      nganhInfo: {
        tenNganh: 'Quản trị kinh doanh',
        maNganh: '7340101',
        thoiGianDaoTao: '4 năm',
        bangCap: 'Cử nhân',
        khoa: { tenKhoa: 'Kinh tế' },
        phuongThucXetTuyen: [
          {
            ten: 'Tuyển thẳng (Phương thức 1)',
            toHop: []
          },
          {
            ten: 'Xét điểm Kỳ thi tốt nghiệp THPT (Phương thức 2)',
            toHop: [
              'Toán, Lý, Hóa (A00)',
              'Toán, Lý, Tiếng Anh (A01)',
              'Văn, Toán, Hóa (C02)',
              'Văn, Toán, Tiếng Anh (D01)'
            ],
            ghiChu: ''
          },
          {
            ten: 'Xét điểm học bạ THPT (Phương thức 3)',
            toHop: [
              'Toán, Lý, Hóa (A00)',
              'Toán, Lý, Tiếng Anh (A01)',
              'Văn, Toán, Hóa (C02)',
              'Văn, Toán, Tiếng Anh (D01)'
            ],
            ghiChu: ''
          },
          {
            ten: 'Xét điểm thi V-SAT (Phương thức 4)',
            toHop: [
              'Toán, Lý, Hóa (A00)',
              'Toán, Lý, Tiếng Anh (A01)',
              'Văn, Toán, Hóa (C02)',
              'Văn, Toán, Tiếng Anh (D01)'
            ],
            ghiChu: 'Riêng phương thức xét điểm V-SAT, không sử dụng những tổ hợp có các môn: Tiếng Pháp, Giáo dục kinh tế và pháp luật/Giáo dục công dân, Tin học, Công nghệ.'
          }
        ],
        mucTieuDaoTao: 'Với mục tiêu đào tạo sinh viên trở thành các nhà quản lý, nhà lãnh đạo tương lai của các công ty/doanh nghiệp/tập đoàn kinh tế, chương trình đào tạo ngành Quản trị kinh doanh trang bị cho sinh viên các kiến thức về quản trị kinh doanh hiện đại và các kỹ năng cần thiết để quản lý toàn diện và phát triển công ty/doanh nghiệp/tập đoàn kinh tế. Sự gia tăng của số lượng doanh nghiệp theo sự phát triển của nền kinh tế thúc đẩy sự gia tăng nhu cầu sử dụng lao động có trình độ cử nhân Quản trị kinh doanh. Về chương trình học, ngành Quản trị kinh doanh tại Trường Đại học Cần Thơ cung cấp các kiến thức nền tảng về quản trị như quản trị nhân lực, quản trị tài chính, quản trị sản xuất, quản trị marketing, quản trị chiến lược, tâm lý quản lý và các kỹ năng nghề nghiệp như giao tiếp, tư duy, giải quyết vấn đề, quản trị sự thay đổi, phân tích môi trường kinh doanh. Đặc biệt, sinh viên theo học ngành Quản trị kinh doanh còn được tạo điều kiện tiếp cận thực tiễn thông qua các hoạt động kiến tập và thực tập thực tế tại các doanh nghiệp cũng như được hướng dẫn sử dụng phần mềm mô phỏng tình huống trong kinh doanh để thực hành việc ra các quyết định kinh doanh ngay tại Phòng mô phỏng của Trường.',
        viTriViecLam: [
          'Chuyên viên tại các phòng bộ phận chức năng như kinh doanh, kế hoạch, sản xuất, marketing, phát triển thị trường, hỗ trợ và giao dịch khách hàng, … trong các công ty/doanh nghiệp/tập đoàn kinh tế;',
          'Tự tạo việc làm (tự lập doanh nghiệp, khởi nghiệp sáng tạo hoặc tự tìm kiếm cơ hội kinh doanh riêng cho bản thân như phân tích, dự báo và tư vấn kinh doanh,…);',
          'Nghiên cứu viên tại các viện, trung tâm nghiên cứu, các cơ sở đào tạo hoặc cơ quan hoạch định chính sách kinh doanh;',
          'Thăng tiến đảm nhận vị trí quản lý, giám đốc (hội đồng quản trị, giám đốc, giám đốc điều hành, …) hoặc chuyên gia cao cấp trong kinh doanh.'
        ],
        noiLamViec: [
          'Công ty, doanh nghiệp, tập đoàn kinh tế tư nhân;',
          'Công ty, doanh nghiệp, tập đoàn kinh tế nhà nước;',
          'Công ty, doanh nghiệp, tập đoàn kinh tế nước ngoài;',
          'Cơ quan nhà nước, cơ sở đào tạo và nghiên cứu (viện, trường, trung tâm) có liên quan đến kinh tế.'
        ]
      },
      loading: false,
      error: null
    }
  },
  async created() {
    this.nganhId = this.$route.params.id
    await this.fetchNganhDetail()
  },
  methods: {
    async fetchNganhDetail() {
      this.loading = true
      try {
        const response = await axios.get(`/api/public/nganh/${this.nganhId}`)
        console.log('Nganh detail response:', response)
        
        if (response && response.data && response.data.success && response.data.data) {
          // Merge với dữ liệu mặc định
          this.nganhInfo = { ...this.nganhInfo, ...response.data.data }
        }
      } catch (error) {
        console.error('Error fetching nganh detail:', error)
        this.error = 'Không thể tải thông tin ngành học'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Styles are now imported from nganh-detail.css */
</style> 
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

            <!-- Giới thiệu -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                </svg>
                Giới thiệu
              </h2>
              <div class="intro-content">
                <p>{{ nganhInfo.gioiThieu }}</p>
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

            <!-- Nơi làm việc -->
            <section class="info-section">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9,22 9,12 15,12 15,22"/>
                </svg>
                Nơi làm việc
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
  name: 'ChanNuoiPage',
  components: {
    PublicLayout
  },
  data() {
    return {
      nganhId: null,
      nganhInfo: {
        tenNganh: 'Chăn nuôi',
        maNganh: '7620105',
        thoiGianDaoTao: '4,5 năm',
        bangCap: 'Kỹ sư',
        khoa: { tenKhoa: 'Nông nghiệp' },
        phuongThucXetTuyen: [
          {
            ten: 'Tuyển thẳng, ưu tiên xét tuyển (Phương thức 1)',
            toHop: []
          },
          {
            ten: 'Xét điểm Kỳ thi tốt nghiệp THPT (Phương thức 2)',
            toHop: [
              'Toán, Lý, Hóa (A00)',
              'Toán, Lý, Sinh (A02)',
              'Toán, Hóa, Sinh (B00)',
              'Toán, Sinh, Tiếng Anh (B08)'
            ],
            ghiChu: ''
          },
          {
            ten: 'Xét điểm học bạ THPT (Phương thức 3)',
            toHop: [
              'Toán, Lý, Hóa (A00)',
              'Toán, Lý, Sinh (A02)',
              'Toán, Hóa, Sinh (B00)',
              'Toán, Sinh, Tiếng Anh (B08)'
            ],
            ghiChu: ''
          },
          {
            ten: 'Xét điểm thi V-SAT (Phương thức 4)',
            toHop: [
              'Toán, Lý, Hóa (A00)',
              'Toán, Lý, Sinh (A02)',
              'Toán, Hóa, Sinh (B00)',
              'Toán, Sinh, Tiếng Anh (B08)'
            ],
            ghiChu: ''
          }
        ],
        gioiThieu: 'Ngành Chăn nuôi đào tạo kỹ sư có phẩm chất chính trị, đạo đức và sức khoẻ tốt; có trình độ năng lực đáp ứng nhu cầu nguồn nhân lực và phát triển kinh tế đất nước; có kiến thức và kỹ năng về Chăn nuôi và Thú y. Sinh viên nắm vững và hiểu rõ các nguyên lý của quá trình sinh học liên quan đến nuôi dưỡng và bảo vệ vật nuôi; có đủ kiến thức chuyên ngành Chăn nuôi-Thú y và kỹ năng nghề nghiệp tốt dựa trên nền tảng của khối kiến cơ bản-cơ sở-chuyên ngành, kiến thức thực tế và công nghệ sản xuất hiện đại; có khả năng tự nghiên cứu, quản lý cơ sở sản xuất, làm dịch vụ và quản lý ngành nghề trong lĩnh vực chăn nuôi và thú y; có đạo đức và tư duy tốt, tiếp cận nhanh với khoa học kỹ thuật, làm việc độc lập và chuyên nghiệp ở các ngành nghề và vị trí khác nhau, tự hội nhập và tự phát triển nghề nghiệp, hội đủ yêu cầu chuẩn đầu ra ngày càng cao của nhà tuyển dụng trong và ngoài nước.',
        viTriViecLam: [
          'Kỹ sư tư vấn, vận hành, quản lí trang trại chăn nuôi;',
          'Kỹ sư tư vấn, vận hành, quản lí nhà máy ấp trứng/quản lý trang trại giống gia súc - gia cầm;',
          'Kỹ sư quản lý các cơ sở giết mổ gia súc-gia cầm và chế biến thực phẩm chăn nuôi;',
          'Kỹ sư phụ trách thu mua, quản lí chất lượng nguyên liệu thức ăn chăn nuôi;',
          'Giám đốc phụ trách kỹ thuật, kinh doanh, sản xuất về chăn nuôi, thú y;',
          'Chủ cơ sở, trang trại chăn nuôi, thú y;',
          'Giảng viên các viện, trường đại học, cao đẳng, trung cấp đào tạo về lĩnh vực chăn nuôi, thú y.',
          'Phụ trách các công ty sản xuất và kinh doanh nông nghiệp; Tư vấn lĩnh vực bảo hiểm vật nuôi, Nhân viên thẩm định dự án chăn nuôi tại các ngân hàng thương mại.'
        ],
        noiLamViec: [
          'Các công ty, xí nghiệp nông nghiệp; trạm, trại; nhà máy chế biến thức ăn chăn nuôi và sản xuất thuốc thú y trong và ngoài nước;',
          'Các cơ quan nông nghiệp và các ngành có liên quan như Chi cục Chăn nuôi và Thú y, Trung tâm giống vật nuôi, Trung tâm khuyến nông,…;',
          'Các viện nghiên cứu, trường đại học, cao đẳng;',
          'Các công ty tư vấn, chuyển giao công nghệ, thiết kế và xây lắp nông nghiệp,…;',
          'Nữ giới cũng đang có cơ hội lớn để làm việc trong ngành Chăn nuôi - Thú y.'
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
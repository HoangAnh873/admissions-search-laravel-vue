<template>
  <div v-if="loading" class="loading">
    <p>Đang tải...</p>
  </div>
  <component v-else :is="componentToShow" />
</template>
<script>
import HeThongThongTin from '@/views/public/nganh/HeThongThongTin.vue'
import KhoaHocMayTinh from '@/views/public/nganh/KhoaHocMayTinh.vue'
import MangMayTinhTruyenThong from '@/views/public/nganh/MangMayTinhTruyenThong.vue'
import KyThuatPhanMem from '@/views/public/nganh/KyThuatPhanMem.vue'
import CongNgheThongTin from '@/views/public/nganh/CongNgheThongTin.vue'
import AnToanThongTin from '@/views/public/nganh/AnToanThongTin.vue'
import TruyenThongDaPhuongTien from '@/views/public/nganh/TruyenThongDaPhuongTien.vue'
import QuanTriKinhDoanh from '@/views/public/nganh/QuanTriKinhDoanh.vue'
import Marketing from '@/views/public/nganh/Marketing.vue'
import KinhDoanhQuocTe from '@/views/public/nganh/KinhDoanhQuocTe.vue'
import KinhTe from '@/views/public/nganh/KinhTe.vue'
import TaiChinhNganHang from '@/views/public/nganh/TaiChinhNganHang.vue'
import KeToan from '@/views/public/nganh/KeToan.vue'
import NongHoc from '@/views/public/nganh/NongHoc.vue'
import BaoVeThucVat from '@/views/public/nganh/BaoVeThucVat.vue'
import KhoaHocCayTrong from '@/views/public/nganh/KhoaHocCayTrong.vue'
import ChanNuoi from '@/views/public/nganh/ChanNuoi.vue'
import CongNgheRauHoaQuaCanhQuan from '@/views/public/nganh/CongNgheRauHoaQuaCanhQuan.vue'
import GiaoDucTieuHoc from '@/views/public/nganh/GiaoDucTieuHoc.vue'
import SuPhamToanHoc from '@/views/public/nganh/SuPhamToanHoc.vue'
import SuPhamTinHoc from '@/views/public/nganh/SuPhamTinHoc.vue'
import SuPhamNguVan from '@/views/public/nganh/SuPhamNguVan.vue'
import SuPhamTiengAnh from '@/views/public/nganh/SuPhamTiengAnh.vue'
import NuoiTrongThuySan from '@/views/public/nganh/NuoiTrongThuySan.vue'
import BenhHocThuySan from '@/views/public/nganh/BenhHocThuySan.vue'
import QuanLyThuySan from '@/views/public/nganh/QuanLyThuySan.vue'
import KyThuatMoiTruong from '@/views/public/nganh/KyThuatMoiTruong.vue'
import QuanLyTaiNguyenMoiTruong from '@/views/public/nganh/QuanLyTaiNguyenMoiTruong.vue'
import NganhChuaCoThongTin from '@/views/public/NganhChuaCoThongTin.vue'

export default {
  name: 'NganhHocDetailRouter',
  components: { HeThongThongTin, KhoaHocMayTinh, MangMayTinhTruyenThong, KyThuatPhanMem, CongNgheThongTin, AnToanThongTin, TruyenThongDaPhuongTien, QuanTriKinhDoanh, Marketing, KinhDoanhQuocTe, KinhTe, TaiChinhNganHang, KeToan, NongHoc, BaoVeThucVat, KhoaHocCayTrong, ChanNuoi, CongNgheRauHoaQuaCanhQuan, GiaoDucTieuHoc, SuPhamToanHoc, SuPhamTinHoc, SuPhamNguVan, SuPhamTiengAnh, NuoiTrongThuySan, BenhHocThuySan, QuanLyThuySan, KyThuatMoiTruong, QuanLyTaiNguyenMoiTruong, NganhChuaCoThongTin },
  data() {
    return {
      componentToShow: null,
      loading: true
    }
  },
  created() {
    const id = this.$route.params.id
    console.log('NganhHocDetailRouter - ID:', id)
    
    // Kiểm tra id để render component tương ứng
    if (id === '168') {
      console.log('Loading HeThongThongTin component')
      this.componentToShow = 'HeThongThongTin'
    } else if (id === '165') {
      console.log('Loading KhoaHocMayTinh component')
      this.componentToShow = 'KhoaHocMayTinh'
    } else if (id === '166') {
      console.log('Loading MangMayTinhTruyenThong component')
      this.componentToShow = 'MangMayTinhTruyenThong'
    } else if (id === '167') {
      console.log('Loading KyThuatPhanMem component')
      this.componentToShow = 'KyThuatPhanMem'
    } else if (id === '170') {
      console.log('Loading CongNgheThongTin component')
      this.componentToShow = 'CongNgheThongTin'
    } else if (id === '171') {
      console.log('Loading AnToanThongTin component')
      this.componentToShow = 'AnToanThongTin'
    } else if (id === '194') {
      console.log('Loading TruyenThongDaPhuongTien component')
      this.componentToShow = 'TruyenThongDaPhuongTien'
    } else if (id === '182') {
      console.log('Loading QuanTriKinhDoanh component')
      this.componentToShow = 'QuanTriKinhDoanh'
    } else if (id === '183') {
      console.log('Loading Marketing component')
      this.componentToShow = 'Marketing'
    } else if (id === '184') {
      console.log('Loading KinhDoanhQuocTe component')
      this.componentToShow = 'KinhDoanhQuocTe'
    } else if (id === '185') {
      console.log('Loading KinhTe component')
      this.componentToShow = 'KinhTe'
    } else if (id === '186') {
      console.log('Loading TaiChinhNganHang component')
      this.componentToShow = 'TaiChinhNganHang'
    } else if (id === '187') {
      console.log('Loading KeToan component')
      this.componentToShow = 'KeToan'
    } else if (id === '172') {
      console.log('Loading NongHoc component')
      this.componentToShow = 'NongHoc'
    } else if (id === '173') {
      console.log('Loading BaoVeThucVat component')
      this.componentToShow = 'BaoVeThucVat'
    } else if (id === '174') {
      console.log('Loading KhoaHocCayTrong component')
      this.componentToShow = 'KhoaHocCayTrong'
    } else if (id === '175') {
      console.log('Loading ChanNuoi component')
      this.componentToShow = 'ChanNuoi'
    } else if (id === '176') {
      console.log('Loading CongNgheRauHoaQuaCanhQuan component')
      this.componentToShow = 'CongNgheRauHoaQuaCanhQuan'
    } else if (id === '177') {
      console.log('Loading NuoiTrongThuySan component')
      this.componentToShow = 'NuoiTrongThuySan'
    } else if (id === '178') {
      console.log('Loading BenhHocThuySan component')
      this.componentToShow = 'BenhHocThuySan'
    } else if (id === '179') {
      console.log('Loading QuanLyThuySan component')
      this.componentToShow = 'QuanLyThuySan'
    } else if (id === '180') {
      console.log('Loading KyThuatMoiTruong component')
      this.componentToShow = 'KyThuatMoiTruong'
    } else if (id === '181') {
      console.log('Loading QuanLyTaiNguyenMoiTruong component')
      this.componentToShow = 'QuanLyTaiNguyenMoiTruong'
    } else if (id === '189') {
      console.log('Loading GiaoDucTieuHoc component')
      this.componentToShow = 'GiaoDucTieuHoc'
    } else if (id === '190') {
      console.log('Loading SuPhamToanHoc component')
      this.componentToShow = 'SuPhamToanHoc'
    } else if (id === '191') {
      console.log('Loading SuPhamTinHoc component')
      this.componentToShow = 'SuPhamTinHoc'
    } else if (id === '192') {
      console.log('Loading SuPhamNguVan component')
      this.componentToShow = 'SuPhamNguVan'
    } else if (id === '193') {
      console.log('Loading SuPhamTiengAnh component')
      this.componentToShow = 'SuPhamTiengAnh'
    } else {
      console.log('Loading NganhChuaCoThongTin component')
      this.componentToShow = 'NganhChuaCoThongTin'
    }
    
    this.loading = false
  }
}
</script>
<style scoped>
.loading {
  text-align: center;
  padding: 2rem;
}
</style> 
import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/backend/Login.vue'
import Dashboard from '@/views/backend/Dashboard.vue'
// import UserIndexVue from '@/views/backend/User/UserIndex.vue'
import UserCatalogueIndex from '@/views/backend/User/Catalogue/View.vue'
import UserCatalogueStore from '@/views/backend/User/Catalogue/Store.vue'
import AdmissionScore from '@/views/backend/Admission/AdmissionScore.vue'
import AdmissionStatus from '@/views/backend/Admission/AdmissionStatus.vue'
import AdmissionCriteria from '@/views/backend/Admission/AdmissionCriteria.vue'
import MajorIndex from '@/views/backend/System/Major.vue'
import FacultyIndex from '@/views/backend/System/Faculty.vue'
import AdmissionYear from '@/views/backend/System/AdmissionYear.vue'
import AdmissionMethod from '@/views/backend/System/AdmissionMethod.vue'
import AdmissionPhase from '@/views/backend/System/AdmissionPhase.vue'

// Import public views
import Home from '@/views/public/Home.vue'
import TuyenSinh from '@/views/public/TuyenSinh.vue'
import NganhHoc from '@/views/public/NganhHoc.vue'
import TieuChuan from '@/views/public/TieuChuan.vue'
import LienHe from '@/views/public/LienHe.vue'
import DiemChuan from '@/views/public/DiemChuan.vue'
import DiemChuanTieuChuan from '@/views/public/DiemChuanTieuChuan.vue'

import { authMiddleware } from '@/middleware/auth' // Import middleware

import store from '@/store'

const routes = [
  // Public routes
  { path: '/', name: 'home', component: Home },
  { path: '/tuyen-sinh', name: 'tuyen-sinh', component: TuyenSinh },
  { path: '/nganh-hoc', name: 'nganh-hoc', component: NganhHoc },
  { path: '/tieu-chuan', name: 'tieu-chuan', component: TieuChuan },
  { path: '/diem-chuan', name: 'diem-chuan', component: DiemChuan },
  { path: '/diem-chuan-tieu-chuan', name: 'diem-chuan-tieu-chuan', component: DiemChuanTieuChuan },
  { path: '/lien-he', name: 'lien-he', component: LienHe },

  //giao diện admin
  { path: '/admin', name: 'login', component: Login },
  { path: '/dashboard', name: 'dashboard.index', component: Dashboard, meta: { requiresAuth: true }},
  { path: '/user/catalogue/index', name: 'user.catalogue.index', component: UserCatalogueIndex, meta: { requiresAuth: true }},
  { path: '/user/catalogue/store', name: 'user.catalogue.create', component: UserCatalogueStore, meta: { requiresAuth: true }},
  { path: '/lich-su-diem', name: 'admission.score', component: AdmissionScore, meta: { requiresAuth: true }},
  { path: '/trang-thai-nganh', name: 'admission.status', component: AdmissionStatus, meta: { requiresAuth: true }},
  { path: '/tieu-chuan-xet-tuyen', name: 'admission.criteria', component: AdmissionCriteria, meta: { requiresAuth: true }},
  { path: '/nganh', name: 'major.index', component: MajorIndex, meta: { requiresAuth: true }},
  { path: '/khoa', name: 'faculty.index', component: FacultyIndex, meta: { requiresAuth: true }},
  { path: '/nam-xet-tuyen', name: 'admission.year', component: AdmissionYear, meta: { requiresAuth: true }},
  { path: '/phuong-thuc-xet-tuyen', name: 'admission.method', component: AdmissionMethod, meta: { requiresAuth: true }},
  { path: '/giai-doan-tuyen-sinh', name: 'admission.phase', component: AdmissionPhase, meta: { requiresAuth: true }},
  // { path: '/user/store', name: 'user.store', component: UserStoreVue, meta: { requiresAuth: true } },
  // { path: '/user/delete', name: 'user.delete', component: UserDeleteVue, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Middleware: kiểm tra đăng nhập trước khi vào route, đã tách ra ở src/middleware/auth.js
router.beforeEach(authMiddleware) 

export default router
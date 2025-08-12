// src/lang/vn/sidebar.js

export default [
  {
    name: 'Dashboard',
    icon: 'home',
    link: '/dashboard'
  },
  {
    name: 'Tuyển sinh',
    icon: 'users',
    link: '/tuyen-sinh',
    children: [
      {
        name: 'Quản lý điểm chuẩn',
        link: '/lich-su-diem'
      },
      {
        name: 'Trạng thái ngành',
        link: '/trang-thai-nganh'
      },
      {
        name: 'Tiêu chuẩn xét tuyển',
        link: '/tieu-chuan-xet-tuyen'
      }
    ]
  },
  {
    name: 'Hệ thống',
    icon: 'settings',
    link: '/danh-muc',
    children: [
      {
        name: 'Khoa',
        link: '/khoa'
      },
      {
        name: 'Ngành đào tạo',
        link: '/nganh'
      },
      {
        name: 'Năm xét tuyển',
        link: '/nam-xet-tuyen'
      },
      {
        name: 'Phương thức xét tuyển',
        link: '/phuong-thuc-xet-tuyen'
      },
      {
        name: 'Giai đoạn tuyển sinh',
        link: '/giai-doan-tuyen-sinh'
      }
    ]
  }
]

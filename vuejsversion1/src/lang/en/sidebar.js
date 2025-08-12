// src/lang/vn/sidebar.js

export default [
  {
    name: 'Dashboard',
    icon: 'home',
    link: '/dashboard'
  },
  {
    name: 'Admissions',
    icon: 'users',
    link: '/tuyen-sinh',
    children: [
      {
        name: 'Admission Scores',
        link: '/lich-su-diem'
      },
      {
        name: 'Major Status',
        link: '/trang-thai-nganh'
      },
      {
        name: 'Admission Criteria',
        link: '/tieu-chuan-xet-tuyen'
      }
    ]
  },
  {
    name: 'System',
    icon: 'settings',
    link: '/danh-muc',
    children: [
      {
        name: 'Faculties',
        link: '/khoa'
      },
      {
        name: 'Majors',
        link: '/nganh'
      },
      {
        name: 'Admission Years',
        link: '/nam-xet-tuyen'
      },
      {
        name: 'Admission Methods',
        link: '/phuong-thuc-xet-tuyen'
      },
      {
        name: 'Admission Phases',
        link: '/giai-doan-tuyen-sinh'
      }
    ]
  }
]

<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
class DemoSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run()
    {
        // 1. Insert khoa trước
        $khoaId = DB::table('khoas')->insertGetId([
            'tenKhoa' => 'Khoa Công nghệ Thông tin'
        ]);
    
        // 2. Insert ngành dùng chính ID đó
        DB::table('nganhs')->insert([
            'tenNganh' => 'Khoa học máy tính',
            'maNganh' => '7480101',
            'moTa' => 'Ngành về lập trình',
            'khoa_id' => $khoaId
        ]);
    
        // 3. Insert năm
        DB::table('nam_xet_tuyens')->insert([
            'nam' => 2024
        ]);
    
        // 4. Insert phương thức
        DB::table('phuong_thuc_xet_tuyens')->insert([
            'tenPhuongThuc' => 'Xét học bạ',
            'ghiChu' => 'Dựa trên điểm trung bình 3 năm'
        ]);
    }
}

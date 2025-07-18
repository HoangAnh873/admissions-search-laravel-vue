<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
class KhoaSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('khoas')->insert([
            ['tenKhoa' => 'Khoa Công nghệ Thông tin'],
            ['tenKhoa' => 'Khoa Kinh tế'],
            ['tenKhoa' => 'Khoa Nông nghiệp'],
        ]);
        
    }
}

<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class GiaiDoanTuyenSinhSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('giai_doan_tuyen_sinhs')->insert([
            ['tenGiaiDoan' => 'Nhận hồ sơ', 'thuTu' => 1],
            ['tenGiaiDoan' => 'Xét tuyển', 'thuTu' => 2],
            ['tenGiaiDoan' => 'Công bố kết quả', 'thuTu' => 3],
            ['tenGiaiDoan' => 'Nhập học', 'thuTu' => 4],
            ['tenGiaiDoan' => 'Đã kết thúc', 'thuTu' => 5],
        ]);
    }
}

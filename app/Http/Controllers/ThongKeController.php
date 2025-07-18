<?php

namespace App\Http\Controllers;

use App\Models\LichSuDiem;
use Illuminate\Support\Facades\DB;

class ThongKeController extends Controller
{
    // Tổng ngành, chỉ tiêu, điểm TB theo năm
    public function theoNam($nam_id)
    {
        $data = LichSuDiem::where('nam_id', $nam_id)
            ->selectRaw('
                COUNT(DISTINCT nganh_id) as tong_nganh,
                SUM(chiTieu) as tong_chi_tieu,
                AVG(diemChuan) as diem_tb
            ')
            ->first();

        return response()->json($data);
    }

    // Thống kê theo phương thức
    public function theoPhuongThuc($nam_id)
    {
        $data = LichSuDiem::where('nam_id', $nam_id)
            ->select('phuong_thuc_id')
            ->selectRaw('COUNT(*) as so_nganh, SUM(chiTieu) as tong_chi_tieu, AVG(diemChuan) as diem_tb')
            ->groupBy('phuong_thuc_id')
            ->with('phuongThuc')
            ->get();

        return response()->json($data);
    }

    // Thống kê nhiều năm cho dashboard biểu đồ
    public function nhieuNam()
    {
        // Tạm thời trả về dữ liệu mẫu để test frontend
        return response()->json([
            ['nam' => 2021, 'diem_tb' => 18.5, 'chi_tieu' => 1200],
            ['nam' => 2022, 'diem_tb' => 19.2, 'chi_tieu' => 1300],
            ['nam' => 2023, 'diem_tb' => 20.1, 'chi_tieu' => 1400],
        ]);
    }
}


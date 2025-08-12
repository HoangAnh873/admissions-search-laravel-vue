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
            ->with('phuongThuc')
            ->get()
            ->groupBy('phuong_thuc_id')
            ->map(function ($group) {
                return [
                    'phuong_thuc_id' => $group->first()->phuong_thuc_id,
                    'so_nganh' => $group->count(),
                    'tong_chi_tieu' => $group->sum('chiTieu'),
                    'diem_tb' => $group->avg('diemChuan'),
                    'phuongThuc' => $group->first()->phuongThuc
                ];
            })->values();
    
        return response()->json($data);
    }    



    // Lấy năm gần nhất có dữ liệu
    public function namGanNhat()
    {
        try {
            $namGanNhat = LichSuDiem::join('nam_xet_tuyens', 'lich_su_diems.nam_id', '=', 'nam_xet_tuyens.id')
                ->select('nam_xet_tuyens.id', 'nam_xet_tuyens.nam')
                ->orderBy('nam_xet_tuyens.nam', 'desc')
                ->first();

            return response()->json([
                'success' => true,
                'data' => $namGanNhat
            ]);
        } catch (\Exception $e) {
            \Log::error('Lỗi khi lấy năm gần nhất: ' . $e->getMessage());
            return response()->json([
                'error' => 'Không thể lấy năm gần nhất',
                'message' => $e->getMessage()
            ], 500);
        }
    }
}


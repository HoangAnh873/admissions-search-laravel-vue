<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\LichSuDiem;
use Illuminate\Support\Facades\DB;

class ThongKeController extends Controller
{
    /**
     * Thống kê theo năm
     */
    public function theoNam($namId)
    {
        $data = LichSuDiem::where('nam_id', $namId)
            ->selectRaw('
                COUNT(DISTINCT nganh_id) as tong_nganh,
                SUM(chiTieu) as tong_chi_tieu,
                AVG(diemChuan) as diem_tb
            ')
            ->first();

        return response()->json([
            'success' => true,
            'data' => $data
        ]);
    }

    /**
     * Thống kê theo phương thức
     */
    public function theoPhuongThuc($namId)
    {
        $data = LichSuDiem::where('nam_id', $namId)
            ->select('phuong_thuc_id')
            ->selectRaw('COUNT(*) as so_nganh, SUM(chiTieu) as tong_chi_tieu, AVG(diemChuan) as diem_tb')
            ->groupBy('phuong_thuc_id')
            ->with('phuongThuc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $data
        ]);
    }

    /**
     * Thống kê theo khoa
     */
    public function theoKhoa($namId)
    {
        $data = LichSuDiem::join('nganhs', 'lich_su_diems.nganh_id', '=', 'nganhs.id')
            ->join('khoas', 'nganhs.khoa_id', '=', 'khoas.id')
            ->where('lich_su_diems.nam_id', $namId)
            ->select('khoas.id', 'khoas.tenKhoa')
            ->selectRaw('COUNT(DISTINCT nganhs.id) as so_nganh, SUM(lich_su_diems.chiTieu) as tong_chi_tieu, AVG(lich_su_diems.diemChuan) as diem_tb')
            ->groupBy('khoas.id', 'khoas.tenKhoa')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $data
        ]);
    }
} 
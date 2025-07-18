<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\LichSuDiem;
use Illuminate\Http\Request;

class DiemChuanController extends Controller
{
    /**
     * Lấy danh sách điểm chuẩn theo năm
     */
    public function index(Request $request)
    {
        $namId = $request->get('nam_id');
        $phuongThucId = $request->get('phuong_thuc_id');
        $query = LichSuDiem::with(['nganh', 'nam', 'phuongThuc']);

        if ($namId) {
            $query->where('nam_id', $namId);
        }

        if ($phuongThucId) {
            $query->where('phuong_thuc_id', $phuongThucId);
        }

        $diemChuans = $query->orderBy('nam_id', 'desc')->get();
        
        return response()->json([
            'success' => true,
            'data' => $diemChuans
        ]);
    }

    /**
     * Lấy thông tin chi tiết điểm chuẩn
     */
    public function show($id)
    {
        $diemChuan = LichSuDiem::with(['nganh', 'nam', 'phuongThuc'])->findOrFail($id);
        return response()->json([
            'success' => true,
            'data' => $diemChuan
        ]);
    }

    /**
     * Lấy điểm chuẩn theo ngành
     */
    public function getByNganh($nganhId)
    {
        $diemChuans = LichSuDiem::with(['nam', 'phuongThuc'])
            ->where('nganh_id', $nganhId)
            ->orderBy('nam_id', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $diemChuans
        ]);
    }
} 
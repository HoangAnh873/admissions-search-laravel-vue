<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\TieuChuanXetTuyen;
use Illuminate\Http\Request;

class TieuChuanController extends Controller
{
    /**
     * Lấy danh sách tiêu chuẩn xét tuyển
     */
    public function index(Request $request)
    {
        $namId = $request->get('nam_id');
        $query = TieuChuanXetTuyen::with(['nganh', 'nam']);

        if ($namId) {
            $query->where('nam_id', $namId);
        }

        $tieuChuans = $query->orderBy('nam_id', 'desc')->get();
        
        return response()->json([
            'success' => true,
            'data' => $tieuChuans
        ]);
    }

    /**
     * Lấy thông tin chi tiết tiêu chuẩn xét tuyển
     */
    public function show($id)
    {
        $tieuChuan = TieuChuanXetTuyen::with(['nganh', 'nam'])->findOrFail($id);
        return response()->json([
            'success' => true,
            'data' => $tieuChuan
        ]);
    }

    /**
     * Lấy tiêu chuẩn xét tuyển theo ngành
     */
    public function getByNganh($nganhId)
    {
        $tieuChuans = TieuChuanXetTuyen::with(['nganh.khoa', 'nam'])
            ->where('nganh_id', $nganhId)
            ->orderBy('nam_id', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $tieuChuans
        ]);
    }
} 
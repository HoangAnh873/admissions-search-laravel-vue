<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\NamXetTuyen;
use App\Models\PhuongThucXetTuyen;
use App\Models\GiaiDoanTuyenSinh;
use Illuminate\Http\Request;

class TuyenSinhController extends Controller
{
    /**
     * Lấy thông tin tuyển sinh
     */
    public function index()
    {
        $data = [
            'namTuyenSinh' => NamXetTuyen::orderBy('nam', 'desc')->get(),
            'phuongThuc' => PhuongThucXetTuyen::all(),
            'giaiDoan' => GiaiDoanTuyenSinh::orderBy('thuTu', 'asc')->get()
        ];

        return response()->json([
            'success' => true,
            'data' => $data
        ]);
    }

    /**
     * Lấy thông tin năm tuyển sinh
     */
    public function getNamTuyenSinh()
    {
        $namTuyenSinh = NamXetTuyen::orderBy('nam', 'desc')->get();
        return response()->json([
            'success' => true,
            'data' => $namTuyenSinh
        ]);
    }

    /**
     * Lấy thông tin phương thức xét tuyển
     */
    public function getPhuongThuc()
    {
        $phuongThuc = PhuongThucXetTuyen::all();
        return response()->json([
            'success' => true,
            'data' => $phuongThuc
        ]);
    }

    /**
     * Lấy thông tin giai đoạn tuyển sinh
     */
    public function getGiaiDoan()
    {
        $giaiDoan = GiaiDoanTuyenSinh::orderBy('thuTu', 'asc')->get();
        return response()->json([
            'success' => true,
            'data' => $giaiDoan
        ]);
    }
} 
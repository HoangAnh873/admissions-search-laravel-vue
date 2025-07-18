<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\TrangThaiNganh;
use Illuminate\Http\Request;

class TrangThaiController extends Controller
{
    /**
     * Lấy danh sách trạng thái ngành
     */
    public function index(Request $request)
    {
        $namId = $request->get('nam_id');
        $query = TrangThaiNganh::with(['nganh', 'nam', 'phuongThuc', 'giaiDoan']);

        if ($namId) {
            $query->where('nam_id', $namId);
        }

        $trangThais = $query->get();
        return response()->json([
            'success' => true,
            'data' => $trangThais
        ]);
    }

    /**
     * Lấy thông tin chi tiết trạng thái ngành
     */
    public function show($id)
    {
        $trangThai = TrangThaiNganh::with(['nganh', 'nam', 'phuongThuc', 'giaiDoan'])->findOrFail($id);
        return response()->json([
            'success' => true,
            'data' => $trangThai
        ]);
    }

    /**
     * Lấy trạng thái theo ngành
     */
    public function getByNganh($nganhId)
    {
        $trangThais = TrangThaiNganh::with(['nam', 'phuongThuc', 'giaiDoan'])
            ->where('nganh_id', $nganhId)
            ->orderBy('nam_id', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $trangThais
        ]);
    }
} 
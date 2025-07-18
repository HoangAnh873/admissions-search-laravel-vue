<?php

namespace App\Http\Controllers;

use App\Models\NamXetTuyen;
use Illuminate\Http\Request;

class NamXetTuyenController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $namXetTuyens = NamXetTuyen::all();
        return response()->json($namXetTuyens);
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'nam' => 'required|integer|unique:nam_xet_tuyens,nam'
        ]);

        $namXetTuyen = NamXetTuyen::create([
            'nam' => $request->nam
        ]);

        return response()->json($namXetTuyen, 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(NamXetTuyen $namXetTuyen)
    {
        return response()->json($namXetTuyen);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(NamXetTuyen $namXetTuyen)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, NamXetTuyen $namXetTuyen)
    {
        $request->validate([
            'nam' => 'required|integer|unique:nam_xet_tuyens,nam,' . $namXetTuyen->id
        ]);

        $namXetTuyen->update([
            'nam' => $request->nam
        ]);

        return response()->json($namXetTuyen);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(NamXetTuyen $namXetTuyen)
    {
        try {
            // Kiểm tra các ràng buộc
            $hasTieuChuan = $namXetTuyen->tieuChuanXetTuyens()->exists();
            $hasTrangThai = $namXetTuyen->trangThaiNganhs()->exists();
            $hasLichSuDiem = $namXetTuyen->lichSuDiems()->exists();
            
            if ($hasTieuChuan || $hasTrangThai || $hasLichSuDiem) {
                $constraints = [];
                if ($hasTieuChuan) $constraints[] = 'tiêu chuẩn xét tuyển';
                if ($hasTrangThai) $constraints[] = 'trạng thái ngành';
                if ($hasLichSuDiem) $constraints[] = 'lịch sử điểm';
                
                return response()->json([
                    'message' => 'Không thể xóa năm tuyển sinh này vì đã có dữ liệu liên quan đến: ' . implode(', ', $constraints)
                ], 422);
            }

            $namXetTuyen->delete();
            return response()->json(['message' => 'Đã xoá']);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Lỗi khi xóa năm tuyển sinh: ' . $e->getMessage()
            ], 500);
        }
    }
}

<?php

namespace App\Http\Controllers;

use App\Models\PhuongThucXetTuyen;
use Illuminate\Http\Request;

class PhuongThucXetTuyenController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return PhuongThucXetTuyen::all();
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
            'tenPhuongThuc' => 'required|string|max:255',
            'ghiChu' => 'nullable|string',
        ]);

        $phuongThuc = PhuongThucXetTuyen::create($request->all());
        return response()->json($phuongThuc, 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(PhuongThucXetTuyen $phuongThucXetTuyen)
    {
        return $phuongThucXetTuyen;
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(PhuongThucXetTuyen $phuongThucXetTuyen)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, PhuongThucXetTuyen $phuongThucXetTuyen)
    {
        $request->validate([
            'tenPhuongThuc' => 'required|string|max:255',
            'ghiChu' => 'nullable|string',
        ]);

        $phuongThucXetTuyen->update($request->all());
        return response()->json($phuongThucXetTuyen);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(PhuongThucXetTuyen $phuongThucXetTuyen)
    {
        try {
            // Kiểm tra các ràng buộc
            $hasTieuChuan = $phuongThucXetTuyen->tieuChuanXetTuyens()->exists();
            $hasTrangThai = $phuongThucXetTuyen->trangThaiNganhs()->exists();
            $hasLichSuDiem = $phuongThucXetTuyen->lichSuDiems()->exists();
            
            if ($hasTieuChuan || $hasTrangThai || $hasLichSuDiem) {
                $constraints = [];
                if ($hasTieuChuan) $constraints[] = 'tiêu chuẩn xét tuyển';
                if ($hasTrangThai) $constraints[] = 'trạng thái ngành';
                if ($hasLichSuDiem) $constraints[] = 'lịch sử điểm';
                
                return response()->json([
                    'message' => 'Không thể xóa phương thức xét tuyển này vì đã có dữ liệu liên quan đến: ' . implode(', ', $constraints)
                ], 422);
            }

            $phuongThucXetTuyen->delete();
            return response()->json(['message' => 'Xóa phương thức xét tuyển thành công']);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Có lỗi xảy ra khi xóa phương thức xét tuyển: ' . $e->getMessage()
            ], 500);
        }
    }
}

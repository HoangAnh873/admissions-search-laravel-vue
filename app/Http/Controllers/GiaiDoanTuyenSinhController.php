<?php

namespace App\Http\Controllers;

use App\Models\GiaiDoanTuyenSinh;
use Illuminate\Http\Request;

class GiaiDoanTuyenSinhController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return GiaiDoanTuyenSinh::orderBy('thuTu', 'asc')->get();
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'tenGiaiDoan' => 'required|string|max:255',
            'thuTu' => 'required|integer|min:1',
            'ghiChu' => 'nullable|string'
        ]);

        // Kiểm tra thứ tự đã tồn tại chưa
        $existingOrder = GiaiDoanTuyenSinh::where('thuTu', $request->thuTu)->exists();
        if ($existingOrder) {
            return response()->json([
                'message' => 'The given data was invalid.',
                'errors' => [
                    'thuTu' => ['Thứ tự này đã tồn tại, vui lòng chọn thứ tự khác']
                ]
            ], 422);
        }

        $giaiDoan = GiaiDoanTuyenSinh::create([
            'tenGiaiDoan' => $request->tenGiaiDoan,
            'thuTu' => $request->thuTu,
            'ghiChu' => $request->ghiChu
        ]);

        return response()->json($giaiDoan, 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        return GiaiDoanTuyenSinh::findOrFail($id);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $giaiDoan = GiaiDoanTuyenSinh::findOrFail($id);

        $request->validate([
            'tenGiaiDoan' => 'required|string|max:255',
            'thuTu' => 'required|integer|min:1',
            'ghiChu' => 'nullable|string'
        ]);

        // Kiểm tra thứ tự đã tồn tại chưa (trừ bản ghi hiện tại)
        $existingOrder = GiaiDoanTuyenSinh::where('thuTu', $request->thuTu)
            ->where('id', '!=', $id)
            ->exists();
        if ($existingOrder) {
            return response()->json([
                'message' => 'The given data was invalid.',
                'errors' => [
                    'thuTu' => ['Thứ tự này đã tồn tại, vui lòng chọn thứ tự khác']
                ]
            ], 422);
        }

        $giaiDoan->update([
            'tenGiaiDoan' => $request->tenGiaiDoan,
            'thuTu' => $request->thuTu,
            'ghiChu' => $request->ghiChu
        ]);

        return response()->json($giaiDoan);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        try {
            $giaiDoan = GiaiDoanTuyenSinh::findOrFail($id);
            
            // Kiểm tra xem giai đoạn này có đang được sử dụng trong trạng thái ngành không
            $hasTrangThai = $giaiDoan->trangThaiNganhs()->exists();
            
            if ($hasTrangThai) {
                return response()->json([
                    'message' => 'Không thể xóa giai đoạn tuyển sinh này vì đã có dữ liệu trạng thái ngành liên quan'
                ], 422);
            }

            $giaiDoan->delete();
            return response()->json(['message' => 'Xóa giai đoạn tuyển sinh thành công']);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Có lỗi xảy ra khi xóa giai đoạn tuyển sinh: ' . $e->getMessage()
            ], 500);
        }
    }
} 
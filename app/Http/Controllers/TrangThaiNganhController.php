<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\TrangThaiNganh;

class TrangThaiNganhController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return TrangThaiNganh::with(['nganh.khoa', 'nam', 'phuongThuc', 'giaiDoan'])->get();
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'nganh_id' => 'required|exists:nganhs,id',
            'nam_id' => 'required|exists:nam_xet_tuyens,id',
            'phuong_thuc_id' => 'required|exists:phuong_thuc_xet_tuyens,id',
            'giai_doan_id' => 'required|exists:giai_doan_tuyen_sinhs,id',
            'ghiChu' => 'nullable|string',
        ]);

        $trangThai = TrangThaiNganh::create([
            'nganh_id' => $request->nganh_id,
            'nam_id' => $request->nam_id,
            'phuong_thuc_id' => $request->phuong_thuc_id,
            'giai_doan_id' => $request->giai_doan_id,
            'ghiChu' => $request->ghiChu,
            'ngayCapNhat' => now(),
        ]);

        return response()->json($trangThai->load(['nganh', 'nam', 'phuongThuc', 'giaiDoan']), 201);
    }

    /**
     * Hiển thị chi tiết một trạng thái ngành
     */
    public function show(string $id)
    {
        return TrangThaiNganh::with(['nganh.khoa', 'nam', 'phuongThuc', 'giaiDoan'])->findOrFail($id);
    }       


    /**
     * Cập nhật một trạng thái ngành
     */
    public function update(Request $request, string $id)
    {
        $trangThai = TrangThaiNganh::findOrFail($id);

        $request->validate([
            'nganh_id' => 'required|exists:nganhs,id',
            'nam_id' => 'required|exists:nam_xet_tuyens,id',
            'phuong_thuc_id' => 'required|exists:phuong_thuc_xet_tuyens,id',
            'giai_doan_id' => 'required|exists:giai_doan_tuyen_sinhs,id',
            'ghiChu' => 'nullable|string',
        ]);

        $trangThai->update([
            'nganh_id' => $request->nganh_id,
            'nam_id' => $request->nam_id,
            'phuong_thuc_id' => $request->phuong_thuc_id,
            'giai_doan_id' => $request->giai_doan_id,
            'ghiChu' => $request->ghiChu,
            'ngayCapNhat' => now(),
        ]);

        return response()->json($trangThai->load(['nganh', 'nam', 'phuongThuc', 'giaiDoan']));
    }

    /**
     * Xóa trạng thái ngành
     */
    public function destroy(string $id)
    {
        $trangThai = TrangThaiNganh::findOrFail($id);
        $trangThai->delete();

        return response()->json(['message' => 'Đã xóa trạng thái ngành']);
    }

    /**
     * Kiểm tra trùng lặp dữ liệu
     */
    public function checkDuplicate(Request $request)
    {
        try {
            $request->validate([
                'nganh_id' => 'required|exists:nganhs,id',
                'nam_id' => 'required|exists:nam_xet_tuyens,id',
                'phuong_thuc_id' => 'required|exists:phuong_thuc_xet_tuyens,id',
                'id' => 'nullable|exists:trang_thai_nganhs,id'
            ]);

            $query = TrangThaiNganh::where('nganh_id', $request->nganh_id)
                ->where('nam_id', $request->nam_id)
                ->where('phuong_thuc_id', $request->phuong_thuc_id);

            // Nếu có id được truyền lên (trường hợp edit), loại trừ bản ghi đó
            if ($request->has('id')) {
                $query->where('id', '!=', $request->id);
            }

            $exists = $query->exists();

            return response()->json(['exists' => $exists]);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Lỗi khi kiểm tra trùng lặp: ' . $e->getMessage()
            ], 422);
        }
    }
}

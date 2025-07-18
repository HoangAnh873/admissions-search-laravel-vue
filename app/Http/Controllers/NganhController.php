<?php

namespace App\Http\Controllers;

use App\Models\Nganh;
use App\Models\Khoa;
use Illuminate\Http\Request;

class NganhController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return Nganh::with('khoa')->get();
    }

    /**
     * Lấy danh sách ngành theo khoa
     */
    public function getByKhoa($khoaId)
    {
        return Nganh::with('khoa')
            ->where('khoa_id', $khoaId)
            ->get();
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
            'tenNganh' => 'required',
            'maNganh' => 'required|unique:nganhs',
            'khoa_id' => 'required|exists:khoas,id',
        ]);

        return Nganh::create($request->all());
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        return Nganh::with('khoa')->findOrFail($id);
    }


    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Nganh $nganh)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $nganh = Nganh::findOrFail($id);
        $nganh->update($request->all());
        return $nganh;
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        try {
            $nganh = Nganh::findOrFail($id);
            
            // Kiểm tra các ràng buộc
            $hasTieuChuan = $nganh->tieuChuanXetTuyens()->exists();
            $hasTrangThai = $nganh->trangThaiNganhs()->exists();
            $hasLichSuDiem = $nganh->lichSuDiems()->exists();
            
            if ($hasTieuChuan || $hasTrangThai || $hasLichSuDiem) {
                $constraints = [];
                if ($hasTieuChuan) $constraints[] = 'tiêu chuẩn xét tuyển';
                if ($hasTrangThai) $constraints[] = 'trạng thái ngành';
                if ($hasLichSuDiem) $constraints[] = 'lịch sử điểm';
                
                return response()->json([
                    'message' => 'Không thể xóa ngành này vì đã có dữ liệu liên quan đến: ' . implode(', ', $constraints)
                ], 422);
            }

            $nganh->delete();
            return response()->json(['message' => 'Đã xoá']);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Lỗi khi xóa ngành: ' . $e->getMessage()
            ], 500);
        }
    }
}

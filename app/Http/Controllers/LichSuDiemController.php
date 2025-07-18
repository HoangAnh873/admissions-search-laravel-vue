<?php

namespace App\Http\Controllers;

use App\Models\LichSuDiem;
use Illuminate\Http\Request;

class LichSuDiemController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return LichSuDiem::with(['nganh.khoa', 'nam', 'phuongThuc'])->get();
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
            'nganh_id' => 'required|exists:nganhs,id',
            'nam_id' => 'required|exists:nam_xet_tuyens,id',
            'phuong_thuc_id' => 'required|exists:phuong_thuc_xet_tuyens,id',
            'chiTieu' => 'required|integer|min:0',
            'diemChuan' => 'required|numeric|min:0|max:30',
            'ghiChu' => 'nullable|string',
        ]);
    
        $diem = LichSuDiem::create([
            'nganh_id' => $request->nganh_id,
            'nam_id' => $request->nam_id,
            'phuong_thuc_id' => $request->phuong_thuc_id,
            'chiTieu' => $request->chiTieu,
            'diemChuan' => $request->diemChuan,
            'ghiChu' => $request->ghiChu,
        ]);
    
        return response()->json($diem->load(['nganh', 'nam', 'phuongThuc']), 201);
    }
    

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        $lichSuDiem = LichSuDiem::with([
            'nganh' => function($query) {
                $query->with('khoa');
            },
            'nam',
            'phuongThuc'
        ])->findOrFail($id);

        // Debug log
        \Log::info('LichSuDiem data:', [
            'id' => $lichSuDiem->id,
            'nganh' => $lichSuDiem->nganh,
            'khoa' => $lichSuDiem->nganh->khoa ?? null
        ]);

        return $lichSuDiem;
    }


    /**
     * Show the form for editing the specified resource.
     */
    public function edit(lich_su_diem $lich_su_diem)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $lichSu = LichSuDiem::findOrFail($id);
        $lichSu->update($request->all());

        return $lichSu;
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        $lichSu = LichSuDiem::findOrFail($id);
        $lichSu->delete();

        return response()->json(['message' => 'Đã xoá']);
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
                'id' => 'nullable|exists:lich_su_diems,id'
            ]);

            $query = LichSuDiem::where('nganh_id', $request->nganh_id)
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

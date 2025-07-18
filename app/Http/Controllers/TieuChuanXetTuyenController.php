<?php

namespace App\Http\Controllers;

use App\Models\TieuChuanXetTuyen;
use Illuminate\Http\Request;

class TieuChuanXetTuyenController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return TieuChuanXetTuyen::with(['nganh.khoa', 'nam'])->get();
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
    // Lưu dữ liệu mới vào database
    public function store(Request $request)
    {
        $validated = $request->validate([
            'nganh_id' => 'required|exists:nganhs,id',
            'nam_id' => 'required|exists:nam_xet_tuyens,id',
            'toHop' => 'required|string|max:255',
            'diemToiThieu' => 'required|numeric|min:0',
            'ghiChu' => 'nullable|string',
        ]);

        $tieuChuan = TieuChuanXetTuyen::create($validated);

        return response()->json($tieuChuan->load(['nganh', 'nam']), 201);
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        $tieuChuan = TieuChuanXetTuyen::with(['nganh', 'nam'])->findOrFail($id);
        return response()->json($tieuChuan);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(tieu_chuan_xet_tuyens $tieu_chuan_xet_tuyens)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $tieuChuan = TieuChuanXetTuyen::findOrFail($id);

        $validated = $request->validate([
            'nganh_id' => 'sometimes|required|exists:nganhs,id',
            'nam_id' => 'sometimes|required|exists:nam_xet_tuyens,id',
            'toHop' => 'sometimes|required|string|max:255',
            'diemToiThieu' => 'sometimes|required|numeric|min:0',
            'ghiChu' => 'nullable|string',
        ]);

        $tieuChuan->update($validated);

        return response()->json($tieuChuan->load(['nganh', 'nam']));
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        $tieuChuan = TieuChuanXetTuyen::findOrFail($id);
        $tieuChuan->delete();

        return response()->json(['message' => 'Xoá thành công']);
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
                'id' => 'nullable|exists:tieu_chuan_xet_tuyens,id'
            ]);

            $query = TieuChuanXetTuyen::where('nganh_id', $request->nganh_id)
                ->where('nam_id', $request->nam_id);

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

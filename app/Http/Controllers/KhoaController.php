<?php

namespace App\Http\Controllers;

use App\Models\Khoa;
use Illuminate\Http\Request;

class KhoaController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return Khoa::all();
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
            'tenKhoa' => 'required|string|max:255',
        ]);

        return Khoa::create($request->all());
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        return Khoa::findOrFail($id);
    }


    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Khoa $khoa)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $request->validate([
            'tenKhoa' => 'required|string|max:255',
        ]);
    
        $khoa = Khoa::findOrFail($id);
        $khoa->update([
            'tenKhoa' => $request->tenKhoa,
        ]);
    
        return response()->json($khoa);
    }
    

    public function destroy($id)
    {
        try {
            $khoa = Khoa::findOrFail($id);
            
            // Kiểm tra các ràng buộc
            $hasNganh = $khoa->nganhs()->exists();
            
            if ($hasNganh) {
                return response()->json([
                    'message' => 'Không thể xóa khoa này vì đã có ngành thuộc khoa này'
                ], 422);
            }

            $khoa->delete();
            return response()->json(['message' => 'Đã xoá']);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Lỗi khi xóa khoa: ' . $e->getMessage()
            ], 500);
        }
    }
}

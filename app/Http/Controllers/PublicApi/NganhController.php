<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\Nganh;
use Illuminate\Http\Request;

class NganhController extends Controller
{
    /**
     * Lấy danh sách ngành học
     */
    public function index()
    {
        $nganhs = Nganh::with('khoa')->get();
        return response()->json([
            'success' => true,
            'data' => $nganhs
        ]);
    }

    /**
     * Lấy thông tin chi tiết ngành học
     */
    public function show($id)
    {
        $nganh = Nganh::with('khoa')->findOrFail($id);
        return response()->json([
            'success' => true,
            'data' => $nganh
        ]);
    }

    /**
     * Tìm kiếm ngành học
     */
    public function search(Request $request)
    {
        $query = $request->get('query');
        $nganhs = Nganh::with('khoa')
            ->where('tenNganh', 'like', "%{$query}%")
            ->orWhere('maNganh', 'like', "%{$query}%")
            ->get();

        return response()->json([
            'success' => true,
            'data' => $nganhs
        ]);
    }
} 
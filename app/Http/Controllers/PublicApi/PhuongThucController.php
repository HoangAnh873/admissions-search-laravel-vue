<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\PhuongThucXetTuyen;
use Illuminate\Http\Request;

class PhuongThucController extends Controller
{
    public function index()
    {
        $methods = PhuongThucXetTuyen::all();
        return response()->json([
            'success' => true,
            'data' => $methods
        ]);
    }
} 
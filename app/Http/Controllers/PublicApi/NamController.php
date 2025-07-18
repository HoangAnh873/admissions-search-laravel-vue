<?php

namespace App\Http\Controllers\PublicApi;

use App\Http\Controllers\Controller;
use App\Models\NamXetTuyen;
use Illuminate\Http\Request;

class NamController extends Controller
{
    public function index()
    {
        $years = NamXetTuyen::orderBy('nam', 'desc')->get();
        return response()->json([
            'success' => true,
            'data' => $years
        ]);
    }
} 
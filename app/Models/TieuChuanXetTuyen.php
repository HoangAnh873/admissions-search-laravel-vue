<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\Nganh;
use App\Models\NamXetTuyen;

class TieuChuanXetTuyen extends Model
{
    use HasFactory;

    protected $fillable = [
        'nganh_id', 
        'nam_id',
        'toHop', 
        'diemToiThieu',
        'ghiChu'
    ];

    public function nganh()
    {
        return $this->belongsTo(Nganh::class);
    }

    public function nam()
    {
        return $this->belongsTo(NamXetTuyen::class, 'nam_id');
    }
}

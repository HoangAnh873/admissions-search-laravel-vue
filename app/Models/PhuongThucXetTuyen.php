<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\LichSuDiem;
use App\Models\TrangThaiNganh;

class PhuongThucXetTuyen extends Model
{
    use HasFactory;

    protected $fillable = [
        'tenPhuongThuc', 'ghiChu'
    ];

    public function lichSuDiems()
    {
        return $this->hasMany(LichSuDiem::class, 'phuong_thuc_id');
    }


    public function trangThaiNganhs()
    {
        return $this->hasMany(TrangThaiNganh::class, 'phuong_thuc_id');
    }
}

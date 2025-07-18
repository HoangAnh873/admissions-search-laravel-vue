<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\TrangThaiNganh;
class GiaiDoanTuyenSinh extends Model
{
    use HasFactory;

    protected $fillable = [
        'tenGiaiDoan',
        'thuTu',
        'ghiChu'
    ];

    public function trangThaiNganhs()
    {
        return $this->hasMany(TrangThaiNganh::class, 'giai_doan_id');
    }
}

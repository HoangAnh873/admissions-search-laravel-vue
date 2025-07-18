<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\LichSuDiem;
use App\Models\TieuChuanXetTuyen;
use App\Models\TrangThaiNganh;

class NamXetTuyen extends Model
{
    use HasFactory;

    protected $fillable = [
        'nam'
    ];

    public function lichSuDiems()
    {
        return $this->hasMany(LichSuDiem::class, 'nam_id');
    }

    public function tieuChuanXetTuyens()
    {
        return $this->hasMany(TieuChuanXetTuyen::class, 'nam_id');
    }

    public function trangThaiNganhs()
    {
        return $this->hasMany(TrangThaiNganh::class, 'nam_id');
    }
}

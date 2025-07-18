<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\Khoa;
use App\Models\LichSuDiem;
use App\Models\TieuChuanXetTuyen;
use App\Models\TrangThaiNganh;

class Nganh extends Model
{
    use HasFactory;

    protected $fillable = ['tenNganh', 'maNganh', 'moTa', 'khoa_id'];

    public function khoa()
    {
        return $this->belongsTo(Khoa::class);
    }

    public function lichSuDiems()
    {
        return $this->hasMany(LichSuDiem::class);
    }

    public function tieuChuanXetTuyens()
    {
        return $this->hasMany(TieuChuanXetTuyen::class);
    }

    public function trangThaiNganhs()
    {
        return $this->hasMany(TrangThaiNganh::class, 'nganh_id');
    }
}

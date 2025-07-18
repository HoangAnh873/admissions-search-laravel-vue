<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\GiaiDoanTuyenSinh;
use App\Models\Nganh;
use App\Models\NamXetTuyen;
use App\Models\PhuongThucXetTuyen;

class TrangThaiNganh extends Model
{
    use HasFactory;

    protected $fillable = [
        'nganh_id',
        'nam_id',
        'phuong_thuc_id',
        'giai_doan_id',
        'ghiChu',
        'ngayCapNhat',
    ];

    public function nganh()
    {
        return $this->belongsTo(Nganh::class, 'nganh_id');
    }

    public function nam()
    {
        return $this->belongsTo(NamXetTuyen::class, 'nam_id');
    }

    public function phuongThuc()
    {
        return $this->belongsTo(PhuongThucXetTuyen::class, 'phuong_thuc_id');
    }

    public function giaiDoan()
    {
        return $this->belongsTo(GiaiDoanTuyenSinh::class, 'giai_doan_id');
    }

}

<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\Nganh;

class Khoa extends Model
{
    use HasFactory;

    protected $fillable = ['tenKhoa'];

    public function nganhs()
    {
        return $this->hasMany(Nganh::class);
    }
}

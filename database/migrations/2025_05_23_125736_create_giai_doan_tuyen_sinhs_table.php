<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('giai_doan_tuyen_sinhs', function (Blueprint $table) {
            $table->id();
            $table->string('tenGiaiDoan');
            $table->integer('thuTu')->default(0); // VD: 1 = Nhận hồ sơ, 2 = Xét tuyển...
            $table->timestamps();
        });
        
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('giai_doan_tuyen_sinhs');
    }
};

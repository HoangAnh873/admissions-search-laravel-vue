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
        Schema::create('trang_thai_nganhs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('nganh_id')->constrained('nganhs')->onDelete('cascade');
            $table->foreignId('nam_id')->constrained('nam_xet_tuyens')->onDelete('cascade');
            $table->foreignId('phuong_thuc_id')->constrained('phuong_thuc_xet_tuyens')->onDelete('cascade');
            $table->foreignId('giai_doan_id')->constrained('giai_doan_tuyen_sinhs')->onDelete('cascade');
            $table->text('ghiChu')->nullable();
            $table->timestamp('ngayCapNhat')->useCurrent();
            $table->timestamps();
        });
        
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('trang_thai_nganhs');
    }
};

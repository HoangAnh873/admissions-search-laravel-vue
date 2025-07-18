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
        Schema::create('lich_su_diems', function (Blueprint $table) {
            $table->id();
            $table->foreignId('nganh_id')->constrained('nganhs')->onDelete('cascade');
            $table->foreignId('nam_id')->constrained('nam_xet_tuyens')->onDelete('cascade');
            $table->foreignId('phuong_thuc_id')->constrained('phuong_thuc_xet_tuyens')->onDelete('cascade');
            $table->integer('chiTieu');
            $table->float('diemChuan', 4, 2);
            $table->text('ghiChu')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('lich_su_diems');
    }
};

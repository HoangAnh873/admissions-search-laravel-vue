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
        Schema::create('tieu_chuan_xet_tuyens', function (Blueprint $table) {
            $table->id();
            $table->foreignId('nganh_id')->constrained('nganhs')->onDelete('cascade');
            $table->foreignId('phuong_thuc_id')->constrained('phuong_thuc_xet_tuyens')->onDelete('cascade');
            $table->string('toHop'); // VD: A00, D01
            $table->text('ghiChu')->nullable();
            $table->timestamps();
        });
        
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('tieu_chuan_xet_tuyens');
    }
};

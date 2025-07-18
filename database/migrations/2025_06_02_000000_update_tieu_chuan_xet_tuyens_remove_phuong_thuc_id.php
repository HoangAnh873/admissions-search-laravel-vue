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
        Schema::table('tieu_chuan_xet_tuyens', function (Blueprint $table) {
            $table->dropForeign(['phuong_thuc_id']);
            $table->dropColumn('phuong_thuc_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('tieu_chuan_xet_tuyens', function (Blueprint $table) {
            $table->foreignId('phuong_thuc_id')->constrained('phuong_thuc_xet_tuyens')->onDelete('cascade');
        });
    }
}; 
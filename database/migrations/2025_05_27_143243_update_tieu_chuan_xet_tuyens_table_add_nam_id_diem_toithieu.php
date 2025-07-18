<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('tieu_chuan_xet_tuyens', function (Blueprint $table) {
            // Thêm cột nam_id và liên kết foreign key
            $table->foreignId('nam_id')
                  ->after('nganh_id')
                  ->constrained('nam_xet_tuyens')
                  ->onDelete('cascade');

            // Thêm cột diemToiThieu
            $table->float('diemToiThieu')
                  ->after('toHop')
                  ->default(0);
        });
    }

    public function down(): void
    {
        Schema::table('tieu_chuan_xet_tuyens', function (Blueprint $table) {
            $table->dropForeign(['nam_id']);
            $table->dropColumn('nam_id');
            $table->dropColumn('diemToiThieu');
        });
    }
};

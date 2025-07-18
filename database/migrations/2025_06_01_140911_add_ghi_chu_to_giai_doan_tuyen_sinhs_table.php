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
        Schema::table('giai_doan_tuyen_sinhs', function (Blueprint $table) {
            $table->text('ghiChu')->nullable()->after('thuTu');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('giai_doan_tuyen_sinhs', function (Blueprint $table) {
            $table->dropColumn('ghiChu');
        });
    }
};

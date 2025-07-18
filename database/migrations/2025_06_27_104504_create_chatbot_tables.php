<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('tai_lieu', function (Blueprint $table) {
            $table->id('IDTaiLieu');
            $table->string('tieuDe')->nullable();
            $table->longText('noiDung');
            $table->string('nguon')->nullable();
            $table->timestamps();
        });

        Schema::create('vector_embeddings', function (Blueprint $table) {
            $table->id('IDVector');
            $table->longText('vectorEmbedding'); // JSON dạng text
            $table->longText('chunk'); // đoạn văn bản
            $table->timestamps();
        });

        // 3. Bảng TAI_LIEU_VECTOR (thực thể yếu)
        Schema::create('tai_lieu_vector', function (Blueprint $table) {
            $table->unsignedBigInteger('IDTaiLieu');
            $table->unsignedBigInteger('IDVector');

            $table->primary(['IDTaiLieu', 'IDVector']);

            $table->foreign('IDTaiLieu')->references('IDTaiLieu')->on('tai_lieu')->onDelete('cascade');
            $table->foreign('IDVector')->references('IDVector')->on('vector_embeddings')->onDelete('cascade');
        });

        Schema::create('lich_su_chat', function (Blueprint $table) {
            $table->id('ID_LSChat');
            $table->text('cauHoi');
            $table->text('traLoi');
            $table->timestamps();
        });

        Schema::create('phan_hoi', function (Blueprint $table) {
            $table->id('IDPhanHoi');
            $table->unsignedBigInteger('ID_LSChat');
            $table->integer('diem')->nullable(); // 1–5
            $table->text('binhLuan')->nullable();
            $table->timestamps();

            $table->foreign('ID_LSChat')->references('ID_LSChat')->on('lich_su_chat')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('phan_hoi');
        Schema::dropIfExists('lich_su_chat');
        Schema::dropIfExists('tai_lieu_vector');
        Schema::dropIfExists('vector_embeddings');
        Schema::dropIfExists('tai_lieu');
    }
};

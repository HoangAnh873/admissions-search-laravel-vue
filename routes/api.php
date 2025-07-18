<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\V1\AuthController;
use App\Http\Controllers\Api\V1\DashboardController;
use App\Http\Controllers\Api\V1\User\UserCatalogueController;
use App\Http\Controllers\KhoaController;
use App\Http\Controllers\NganhController;
use App\Http\Controllers\LichSuDiemController;
use App\Http\Controllers\TieuChuanXetTuyenController;
use App\Http\Controllers\TrangThaiNganhController;
use App\Http\Controllers\ThongKeController;
use App\Http\Controllers\PhuongThucXetTuyenController;
use App\Http\Controllers\NamXetTuyenController;
use App\Http\Controllers\GiaiDoanTuyenSinhController;
// use Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful;

// Phần giao diện người dùng tra cứu
use App\Http\Controllers\PublicApi\NganhController as PublicNganhController;
use App\Http\Controllers\PublicApi\DiemChuanController;
use App\Http\Controllers\PublicApi\TieuChuanController;
use App\Http\Controllers\PublicApi\TrangThaiController;
use App\Http\Controllers\PublicApi\TuyenSinhController;
use App\Http\Controllers\PublicApi\ThongKeController as PublicThongKeController;
use App\Http\Controllers\PublicApi\NamController;
use App\Http\Controllers\PublicApi\PhuongThucController;


Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

Route::prefix('auth')->group(function () {
    Route::post('/login', [AuthController::class, 'login'])->name('login');
});

// Giao diện Admin
Route::middleware(['auth:sanctum'])->group(function () {
    // Route logout
    Route::post('/auth/logout', [AuthController::class, 'logout'])->name('auth.logout');

    // User Catalogue
    Route::post('/user/catalogue/store', [UserCatalogueController::class, 'store'])->name('user.catalogue.store');

    // Khoa
    Route::apiResource('khoas', KhoaController::class);

    // Nganh
    Route::apiResource('nganhs', NganhController::class);
    Route::get('/nganhs/khoa/{khoaId}', [NganhController::class, 'getByKhoa']);

    // LichSuDiem
    Route::get('/lich-su-diems/check-duplicate', [LichSuDiemController::class, 'checkDuplicate']);
    Route::apiResource('lich-su-diems', LichSuDiemController::class);

    Route::get('/tieu-chuan-xet-tuyens/check-duplicate', [TieuChuanXetTuyenController::class, 'checkDuplicate']);
    Route::apiResource('tieu-chuan-xet-tuyens', TieuChuanXetTuyenController::class);

    // TrangThaiNganh
    Route::get('/trang-thai-nganhs/check-duplicate', [TrangThaiNganhController::class, 'checkDuplicate']);
    Route::apiResource('trang-thai-nganhs', TrangThaiNganhController::class);

    Route::get('/thong-ke/nam/{nam_id}', [ThongKeController::class, 'theoNam']);
    Route::get('/thong-ke/phuong-thuc/{nam_id}', [ThongKeController::class, 'theoPhuongThuc']);
    Route::get('/thong-ke/nhieu-nam', [ThongKeController::class, 'nhieuNam']);

    // PhuongThucXetTuyen
    Route::apiResource('phuong-thuc-xet-tuyens', PhuongThucXetTuyenController::class);

    Route::apiResource('giai-doan-tuyen-sinhs', GiaiDoanTuyenSinhController::class);

    // NamXetTuyen
    Route::apiResource('nam-xet-tuyens', NamXetTuyenController::class);
});

// Giao diện người dùng tra cứu
Route::prefix('public')->group(function () {
    // Ngành học
    Route::get('/nganh', [PublicNganhController::class, 'index']);
    Route::get('/nganh/{id}', [PublicNganhController::class, 'show']);
    
    // Điểm chuẩn
    Route::get('/diem-chuan', [DiemChuanController::class, 'index']);
    Route::get('/diem-chuan/{id}', [DiemChuanController::class, 'show']);
    Route::get('/diem-chuan/nganh/{nganhId}', [DiemChuanController::class, 'getByNganh']);
    
    // Tiêu chuẩn
    Route::get('/tieu-chuan', [TieuChuanController::class, 'index']);
    Route::get('/tieu-chuan/{id}', [TieuChuanController::class, 'show']);
    
    // Trạng thái
    Route::get('/trang-thai', [TrangThaiController::class, 'index']);
    
    // Tuyển sinh
    Route::get('/tuyen-sinh', [TuyenSinhController::class, 'index']);
    Route::get('/tuyen-sinh/{id}', [TuyenSinhController::class, 'show']);
    
    // Thống kê
    Route::get('/thong-ke/nam/{namId}', [PublicThongKeController::class, 'theoNam']);
    Route::get('/thong-ke/phuong-thuc/{namId}', [PublicThongKeController::class, 'theoPhuongThuc']);
    Route::get('/thong-ke/khoa/{namId}', [PublicThongKeController::class, 'theoKhoa']);

    // Năm xét tuyển
    Route::get('/nam', [NamController::class, 'index']);
    
    // Phương thức xét tuyển
    Route::get('/phuong-thuc', [PhuongThucController::class, 'index']);
});

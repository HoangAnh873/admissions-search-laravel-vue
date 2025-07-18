<?php

namespace App\Http\Controllers;

use Illuminate\Http\Response;
use Illuminate\Support\Facades\DB;
use App\Models\Nganh;
use App\Models\Khoa;
use App\Models\LichSuDiem;
use App\Models\TieuChuanXetTuyen;
use App\Models\TrangThaiNganh;
use App\Models\PhuongThucXetTuyen;
use App\Models\GiaiDoanTuyenSinh;
use App\Models\NamXetTuyen;

class ExportChatbotController extends Controller
{
    public function export()
    {
        $nganhs = Nganh::with([
            'khoa',
            'lichSuDiems.nam',
            'lichSuDiems.phuongThuc',
            'tieuChuanXetTuyens.nam',
            'trangThaiNganhs.nam',
            'trangThaiNganhs.phuongThuc',
            'trangThaiNganhs.giaiDoan',
        ])->get();

        $data = [];
        foreach ($nganhs as $nganh) {
            $item = [
                'nganh' => $nganh->tenNganh,
                'ma_nganh' => $nganh->maNganh,
                'khoa' => $nganh->khoa->tenKhoa ?? '',
                'mo_ta' => $nganh->moTa ?? '',
                'tieu_chi_xet_tuyen' => [],
                'diem_chuan' => [],
                'trang_thai_nganh' => [],
            ];
            foreach ($nganh->tieuChuanXetTuyens as $tc) {
                $item['tieu_chi_xet_tuyen'][] = [
                    'nam' => $tc->nam->nam ?? '',
                    'to_hop' => $tc->toHop,
                    'diem_toi_thieu' => $tc->diemToiThieu,
                    'ghi_chu' => $tc->ghiChu ?? '',
                ];
            }
            foreach ($nganh->lichSuDiems as $lsd) {
                $item['diem_chuan'][] = [
                    'nam' => $lsd->nam->nam ?? '',
                    'phuong_thuc' => $lsd->phuongThuc->tenPhuongThuc ?? '',
                    'diem' => $lsd->diemChuan,
                    'chi_tieu' => $lsd->chiTieu,
                    'ghi_chu' => $lsd->ghiChu ?? '',
                ];
            }
            foreach ($nganh->trangThaiNganhs as $tt) {
                $item['trang_thai_nganh'][] = [
                    'nam' => $tt->nam->nam ?? '',
                    'giai_doan' => $tt->giaiDoan->tenGiaiDoan ?? '',
                    'phuong_thuc' => $tt->phuongThuc->tenPhuongThuc ?? '',
                    'ghi_chu' => $tt->ghiChu ?? '',
                    'ngay_cap_nhat' => $tt->ngayCapNhat ?? '',
                ];
            }
            $data[] = $item;
        }

        $phuong_thuc_xet_tuyen = [];
        foreach (PhuongThucXetTuyen::all() as $pt) {
            $phuong_thuc_xet_tuyen[] = [
                'ten' => $pt->tenPhuongThuc,
                'ghi_chu' => $pt->ghiChu ?? '',
            ];
        }

        $giai_doan_tuyen_sinh = [];
        foreach (GiaiDoanTuyenSinh::all() as $gd) {
            $giai_doan_tuyen_sinh[] = [
                'ten' => $gd->tenGiaiDoan,
                'thu_tu' => $gd->thuTu,
                'ghi_chu' => $gd->ghiChu ?? '',
            ];
        }

        $output = [
            'nganhs' => $data,
            'phuong_thuc_xet_tuyen' => $phuong_thuc_xet_tuyen,
            'giai_doan_tuyen_sinh' => $giai_doan_tuyen_sinh,
        ];

        return response(json_encode($output, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))
            ->header('Content-Type', 'application/json')
            ->header('Content-Disposition', 'attachment; filename="data_chatbot.json"');
    }
} 
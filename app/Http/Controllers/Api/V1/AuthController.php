<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Http\Requests\AuthRequest;
use Illuminate\Support\Facades\Auth;
use App\Enums\ResponseEnum;

class AuthController extends Controller
{
   public function __construct(

   ){

   }

   public function login(AuthRequest $request)
   {
       $credentials = $request->only('email', 'password');
   
       // Kiểm tra thông tin đăng nhập
       if (Auth::attempt($credentials)) {
           $user = Auth::user();
   
           // Nếu sử dụng Sanctum, gửi cookie xác thực
           $token = $user->createToken('Login')->plainTextToken; // Tạo Sanctum token
           $cookie = cookie('XSRF-TOKEN', csrf_token(), 60); // CSRF cookie
           
           // Trả về phản hồi với token và cookie
           return response()->json([
               'success' => true,
               'user' => $user->only(['id', 'name', 'email']),
               'message' => 'Đăng nhập thành công',
               'token' => $token
           ], ResponseEnum::OK)
           ->withCookie($cookie) // Trả về CSRF token cookie
           ->withCookie(cookie('auth_token', $token, 60, null, null, false, true)); // Lưu token vào cookie (HttpOnly)
       }
   
       // Trả về lỗi nếu đăng nhập không thành công
       return response()->json([
           'success' => false,
           'message' => 'Email hoặc mật khẩu không đúng'
       ], ResponseEnum::UNAUTHORIZED);
   }

   public function logout(Request $request)
   {
       // Nếu dùng Sanctum: xóa token hiện tại
       $request->user()->currentAccessToken()->delete();

       return response()->json(['message' => 'Đăng xuất thành công']);
   }
   
}

<?php

namespace App\Http\Controllers\Api\V1\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Http\Requests\V1\UserCatalogue\UserCatalogueStoreRequest;
use App\Services\Interfaces\User\UserCatalogueServiceInterface as UserCatalogueService;
use App\Enums\ResponseEnum;

class UserCatalogueController extends Controller
{
    protected $userCatalogueService;

    public function __construct(
        UserCatalogueService $userCatalogueService  
    ){
        $this->userCatalogueService = $userCatalogueService;
    }

    public function store(UserCatalogueStoreRequest $request)
    {
        $created = $this->userCatalogueService->create($request);
    
        if ($created) {
            return response()->json([
                'message' => 'Thêm nhóm người dùng thành công.',
                'data' => $created
            ], 200); // 201: Created
        }
    
        return response()->json([
            'message' => 'Thêm nhóm người dùng thất bại.'
        ], 422);
    }
    
    
  
}

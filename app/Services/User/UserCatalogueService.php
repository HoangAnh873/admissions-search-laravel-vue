<?php

namespace App\Services\User;

use App\Services\Interfaces\User\UserCatalogueServiceInterface;
use App\Repositories\Interfaces\User\UserCatalogueRepositoryInterface as UserCatalogueRepository;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use App\Models\UserCatalogue;

class UserCatalogueService implements UserCatalogueServiceInterface
{
    protected $userCatalogueRepository;
    protected $payload = ['name' , 'description'];

    public function __construct(
        UserCatalogueRepository $userCatalogueRepository
    ){
        $this->userCatalogueRepository = $userCatalogueRepository;
    }

    public function create($request)
    {
        DB::beginTransaction();
        try {
            $payload = $request->only($this->payload);
            $userCatalogue = $this->userCatalogueRepository->create($payload);
            DB::commit();
            return true;
        } catch (\Exception $e) {
            DB::rollBack();
            // Log::error('Error creating user catalogue: ' . $e->getMessage());
            echo $e->getMessage(); die();   
            return false;
        }
    }


}


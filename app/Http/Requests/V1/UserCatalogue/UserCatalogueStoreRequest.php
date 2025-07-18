<?php

namespace App\Http\Requests\V1\UserCatalogue;

use Illuminate\Foundation\Http\FormRequest;

class UserCatalogueStoreRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'name'        => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string', 'max:1000'],
        ];
    }
    
    public function messages(): array
    {
        return [
            'name.required'  => 'Vui lòng nhập tên.',
            'name.max'       => 'Tên không được vượt quá 255 ký tự.',
            
            'description.max'=> 'Mô tả không được vượt quá 1000 ký tự.',
        ];
    }
    
}

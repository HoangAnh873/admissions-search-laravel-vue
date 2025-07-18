// src/config/csrf.js
import axios from './axios';

const getCookie = async () => {
    try {
        await axios.get('/sanctum/csrf-cookie');
        // Lấy token từ cookie sau khi đã request
        const token = document.cookie
            .split('; ')
            .find(row => row.startsWith('XSRF-TOKEN='))
            ?.split('=')[1];
        
        if (token) {
            // Cập nhật header cho tất cả request sau này
            axios.defaults.headers.common['X-XSRF-TOKEN'] = decodeURIComponent(token);
        }
        return true;
    } catch (error) {
        console.error('Lỗi khi lấy CSRF Cookie:', error);
        throw error;
    }
};

export default { getCookie };
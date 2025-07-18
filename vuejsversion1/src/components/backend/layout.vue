<!-- src/components/layout.vue -->
<script setup>
    import { ref } from 'vue'
    import Sidebar from './Sidebar.vue'
    import Navbar from './Navbar.vue'
    import { useRouter } from 'vue-router'
    import { useStore } from 'vuex'
    import { useI18n } from 'vue-i18n'

    const { locale } = useI18n()
    const router = useRouter()
    const store = useStore()

    // Thêm biến title để truyền cho Navbar
    const currentTitle = ref('Dashboard')

    // Nhận title từ Sidebar
    const handleTitleUpdate = (title) => {
        currentTitle.value = title
    }

    // Xử lý chuyển ngôn ngữ
    const toggleLanguage = () => {
        locale.value = locale.value === 'vn' ? 'en' : 'vn'
    }

    const handleLogout = () => {
        store.dispatch('auth/logout')
        router.push({ name: 'login' })
    }
</script>

<template>
    <div id="wrapper" class="dashboard">
        <Sidebar @update-title="handleTitleUpdate" />
        
        <div class="page-wrapper">
            <Navbar
                :title="currentTitle"
                @toggle-language="toggleLanguage"
                @logout="handleLogout"
            />
            
            <div class="content-wrapper">
                <slot name="template"></slot>
            </div>
        </div>
    </div>
</template>

<style scoped>
.dashboard {
    display: flex;
    min-height: 100vh;
    background-color: #f8fafc;
}

.page-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.content-wrapper {
    flex: 1;
    padding: 20px;
}
</style>
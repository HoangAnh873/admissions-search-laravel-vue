<template>
  <public-layout>
    <div class="page-container" style="text-align:center; padding: 4rem 1rem;">
      <h1>Chưa có thông tin về ngành này</h1>
      <p>Chúng tôi sẽ cập nhật thông tin trong thời gian tới.</p>
      <router-link to="/nganh-hoc" class="btn btn-primary">Quay lại danh sách ngành học</router-link>
    </div>
  </public-layout>
</template>
<script>
import PublicLayout from '@/components/public/layout.vue'
export default { components: { PublicLayout } }
</script>
<style scoped>
.btn {
  display: inline-block;
  margin-top: 2rem;
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.3s;
}
.btn:hover {
  background: #0056b3;
}
</style> 
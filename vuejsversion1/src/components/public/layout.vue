<script>
import PublicHeader from './header.vue'
import PublicFooter from './footer.vue'

export default {
  name: 'PublicLayout',
  components: {
    PublicHeader,
    PublicFooter
  }
}
</script>

<template>
  <div class="public-layout">
    <public-header />
    
    <!-- Main Content -->
    <main class="public-main">
      <div class="container">
        <slot></slot>
      </div>
    </main>

    <public-footer />
  </div>
</template>

<style scoped>
.public-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.public-main {
  flex: 1;
  margin-top: 80px; /* Adjust based on header height */
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style> 
<script setup>
import { computed } from 'vue'

// Nhận props từ parent
const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['update:page'])

// Tính tổng số trang
const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize))

// Điều hướng đến trang mới
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    emit('update:page', page)
  }
}
</script>

<template>
  <ul class="uk-pagination uk-flex-center uk-margin" uk-margin>
    <li :class="{ 'uk-disabled': props.currentPage === 1 }">
      <a href="#" @click.prevent="goToPage(props.currentPage - 1)">
        <span uk-pagination-previous></span>
      </a>
    </li>
    <li v-for="page in totalPages" :key="page" :class="{ 'uk-active': props.currentPage === page }">
      <a href="#" @click.prevent="goToPage(page)">{{ page }}</a>
    </li>
    <li :class="{ 'uk-disabled': props.currentPage === totalPages }">
      <a href="#" @click.prevent="goToPage(props.currentPage + 1)">
        <span uk-pagination-next></span>
      </a>
    </li>
  </ul>
</template>

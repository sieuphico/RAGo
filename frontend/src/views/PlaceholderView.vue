<script setup lang="ts">
// Trang tạm cho route chưa có màn hình thật (T-502); các task màn hình thay thế.
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <main id="main" class="page">
    <h1>{{ route.meta.title }}</h1>
  </main>
</template>

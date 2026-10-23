<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
import BannerHost from "@/components/BannerHost.vue";
import ToastHost from "@/components/ToastHost.vue";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const auth = useAuthStore();

// Thanh trên cùng chỉ hiện khi đã được cấp quyền và không ở S-01/S-02.
const showHeader = computed(
  () => auth.status === "allowed" && route.path !== "/login" && route.path !== "/denied",
);
</script>

<template>
  <AppHeader v-if="showHeader" :role="auth.me?.role ?? null" :user-name="auth.me?.email ?? ''" @logout="auth.logout()" />
  <BannerHost />
  <RouterView />
  <ToastHost />
</template>

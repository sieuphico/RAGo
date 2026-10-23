<script setup lang="ts">
// S-02 Không có quyền (denied.html). Không gọi API danh sách tài liệu và không hiện tên tài liệu nào (US-002).
import { computed } from "vue";
import { t } from "@/content/messages";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const title = computed(() => (auth.status === "revoked" ? t("denied.revoked") : t("denied.title")));
</script>

<template>
  <div>
    <a class="skip-link" href="#main">{{ t("app.skipToMain") }}</a>
    <main id="main" class="center-page">
      <div class="card">
        <span class="icon-large" aria-hidden="true">⛔</span>
        <h1 data-testid="denied-title">{{ title }}</h1>
        <button type="button" class="btn btn-primary" data-testid="logout" @click="auth.logout()">
          {{ t("auth.logout") }}
        </button>
        <p class="caption muted">{{ t("denied.note") }}</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.icon-large {
  font-size: 32px;
}
</style>

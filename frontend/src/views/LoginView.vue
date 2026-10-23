<script setup lang="ts">
// S-01 Đăng nhập (login.html). Không có ô mật khẩu: SSO của công ty (DEC-011).
import { ref } from "vue";
import { useRoute } from "vue-router";
import { t } from "@/content/messages";
import { useAuthStore } from "@/stores/auth";
import { KEY_RETURN_TO, storageGet } from "@/utils/storage";

const route = useRoute();
const auth = useAuthStore();
const redirecting = ref(false);
const expired = route.query.expired === "1" || route.query.expired === "true";

function onLogin() {
  redirecting.value = true;
  auth.login(storageGet(KEY_RETURN_TO) ?? "/");
}
</script>

<template>
  <div>
    <a class="skip-link" href="#main">{{ t("app.skipToMain") }}</a>
    <div v-if="expired" class="banner" role="alert" data-testid="expired-banner">{{ t("login.expired") }}</div>
    <main id="main" class="center-page">
      <div class="card">
        <span class="brand-mark" aria-hidden="true">◆</span>
        <h1>{{ t("app.name") }}</h1>
        <p class="muted">{{ t("login.intro") }}</p>
        <button type="button" class="btn btn-primary btn-block" data-testid="login-button" :disabled="redirecting" @click="onLogin">
          {{ t("login.button") }}
        </button>
        <p class="caption muted" role="status">{{ redirecting ? t("login.redirecting") : "" }}</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.brand-mark {
  font-size: 32px;
}
.btn-block {
  width: 100%;
}
</style>

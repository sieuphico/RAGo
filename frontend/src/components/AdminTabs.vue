<script setup lang="ts">
// Hai tab trong mục "Quản trị": Người dùng (S-07) và Nhật ký (S-08).
import { RouterLink, useRoute } from "vue-router";
import { t } from "@/content/messages";

const route = useRoute();
</script>

<template>
  <nav class="nav admin-tabs" :aria-label="t('admin.tabsAria')">
    <RouterLink to="/admin/users" custom v-slot="{ href, navigate }">
      <a :href="href" :aria-current="route.path === '/admin/users' ? 'page' : undefined" @click="navigate">{{
        t("admin.tabUsers")
      }}</a>
    </RouterLink>
    <RouterLink to="/admin/audit" custom v-slot="{ href, navigate }">
      <a :href="href" :aria-current="route.path === '/admin/audit' ? 'page' : undefined" @click="navigate">{{
        t("admin.tabAudit")
      }}</a>
    </RouterLink>
  </nav>
</template>

<style scoped>
.admin-tabs {
  margin-bottom: var(--space-4);
  flex: none;
}
</style>

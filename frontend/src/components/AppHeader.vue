<script setup lang="ts">
// Thanh trên cùng (CMP-01..03). Nhận vai trò và tên từ ngoài; App.vue nối với useAuthStore (T-505).
import { computed } from "vue";
import { RouterLink, useRoute } from "vue-router";
import type { Role } from "@/api/types";
import { t, M } from "@/content/messages";
import { isCurrent, navItems } from "@/router/nav";

const props = defineProps<{ role: Role | null; userName: string }>();
const emit = defineEmits<{ logout: [] }>();

const route = useRoute();
const items = computed(() => navItems(props.role));
const roleLabel = computed(() => (props.role ? M[`role.${props.role}`] : ""));
</script>

<template>
  <header class="app-header" data-testid="app-header">
    <a class="skip-link" href="#main" data-testid="skip-link">{{ t("app.skipToMain") }}</a>
    <span class="brand"><span class="brand-mark" aria-hidden="true">◆</span> {{ t("app.name") }}</span>
    <nav class="nav" :aria-label="t('nav.aria')">
      <RouterLink v-for="item in items" :key="item.to" :to="item.to" custom v-slot="{ href, navigate }">
        <a :href="href" :aria-current="isCurrent(item, route.path) ? 'page' : undefined" @click="navigate">{{
          item.label
        }}</a>
      </RouterLink>
    </nav>
    <div class="header-user">
      <span class="caption" data-testid="user-name">{{ userName }}</span>
      <span v-if="roleLabel" class="caption muted">({{ roleLabel }})</span>
      <button type="button" class="btn btn-ghost btn-sm" data-testid="logout" @click="emit('logout')">
        {{ t("auth.logout") }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.header-user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
</style>

<script setup lang="ts">
// Thanh bên của S-03: Phiên mới, Lịch sử (slot cho T-516), tóm tắt kho tài liệu.
import { RouterLink } from "vue-router";
import { t } from "@/content/messages";
import { useDocumentsStore } from "@/stores/documents";

defineProps<{ collapsed?: boolean }>();
const emit = defineEmits<{ newSession: [] }>();
const docs = useDocumentsStore();
</script>

<template>
  <aside class="sidebar" :class="{ collapsed }" :aria-label="t('chat.sidebarAria')" data-testid="sidebar">
    <button
      type="button"
      class="btn btn-primary"
      :aria-label="t('chat.newSession')"
      data-testid="new-session"
      @click="emit('newSession')"
    >
      <span aria-hidden="true">＋</span><span class="side-text">{{ t("chat.newSession") }}</span>
    </button>
    <div class="side-text">
      <slot name="history" />
    </div>
    <div class="lib-link side-text">
      <p class="caption muted" data-testid="sidebar-doc-count">{{ t("chat.docCount", { N: docs.items.length }) }}</p>
      <RouterLink to="/library">{{ t("chat.openLibrary") }}</RouterLink>
    </div>
  </aside>
</template>

<style scoped>
.sidebar.collapsed {
  padding: var(--space-2);
  align-items: center;
}
.sidebar.collapsed .side-text {
  display: none;
}
</style>

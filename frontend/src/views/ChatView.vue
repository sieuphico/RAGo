<script setup lang="ts">
// S-03 Hỏi đáp: thanh bên, hội thoại, khung xem nguồn (S-05). Bố cục theo độ rộng (Blueprint 3.8.3).
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ChatSidebar from "@/components/ChatSidebar.vue";
import Composer from "@/components/Composer.vue";
import { layoutFor, useViewport } from "@/composables/useViewport";
import { t } from "@/content/messages";
import { useChatStore } from "@/stores/chat";
import { useDocumentsStore } from "@/stores/documents";

const route = useRoute();
const router = useRouter();
const chat = useChatStore();
const docs = useDocumentsStore();
const { width } = useViewport();

const layout = computed(() => layoutFor(width.value));
const viewerDoc = computed(() => (typeof route.query.doc === "string" ? route.query.doc : null));
const menuOpen = ref(false);

onMounted(() => {
  if (docs.items.length === 0 && !docs.loading) void docs.fetch({ silent: true });
});

// Đổi sessionId trên URL → mở phiên (T-516/T-524 cài đặt `open`).
watch(
  () => route.params.sessionId,
  (id) => {
    if (typeof id === "string" && id && id !== chat.sessionId) void chat.open(id);
  },
  { immediate: true },
);

function onNewSession() {
  chat.newSession();
  menuOpen.value = false;
  void router.push("/");
}
</script>

<template>
  <div
    class="chat-shell"
    :class="[`layout-${layout}`, { 'has-viewer': viewerDoc }]"
    data-testid="chat-shell"
  >
    <button
      v-if="layout === 'narrow'"
      type="button"
      class="btn btn-sm menu-button"
      :aria-expanded="menuOpen"
      data-testid="menu-button"
      @click="menuOpen = !menuOpen"
    >
      ☰ {{ t("chat.menu") }}
    </button>
    <ChatSidebar
      v-show="layout !== 'narrow' || menuOpen"
      :collapsed="layout === 'medium'"
      :class="{ drawer: layout === 'narrow' }"
      @new-session="onNewSession"
    >
      <template #history><!-- Danh sách lịch sử (T-516) --></template>
    </ChatSidebar>
    <main id="main" class="chat-main" :aria-label="t('chat.conversationAria')" data-testid="conversation">
      <div class="chat-scroll">
        <div class="chat-inner"><!-- Danh sách tin nhắn (T-512) --></div>
      </div>
      <div class="composer-wrap">
        <Composer @submit="chat.send($event)" @stop="chat.stop()" />
      </div>
    </main>
    <section v-if="viewerDoc" class="viewer-slot" :class="{ overlay: layout !== 'wide' }" data-testid="viewer-slot">
      <!-- Khung xem nguồn (T-513) -->
    </section>
  </div>
</template>

<style scoped>
.chat-shell {
  display: grid;
  height: calc(100vh - var(--header-height));
  position: relative;
}
.layout-wide {
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
}
.layout-wide.has-viewer {
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr) var(--viewer-width);
}
.layout-medium {
  grid-template-columns: 56px minmax(0, 1fr);
}
.layout-narrow {
  grid-template-columns: minmax(0, 1fr);
}
.menu-button {
  position: absolute;
  top: var(--space-2);
  left: var(--space-2);
  z-index: 20;
}
.drawer {
  position: absolute;
  inset: 0 auto 0 0;
  width: var(--sidebar-width);
  z-index: 25;
}
.layout-narrow .chat-scroll {
  padding-top: calc(var(--space-5) + 32px);
}
.chat-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  background: var(--color-white);
}
.viewer-slot {
  background: var(--color-surface);
  border-left: 1px solid var(--color-divider);
  min-width: 0;
  overflow: hidden;
}
.viewer-slot.overlay {
  position: fixed;
  inset: var(--header-height) 0 0 0;
  z-index: 30;
  border-left: 0;
}
</style>

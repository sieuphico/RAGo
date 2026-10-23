<script setup lang="ts">
// Màn hình chào và gợi ý câu hỏi (CMP-10, CMP-23; US-030, US-031; EC-01, EC-02). Hiện khi phiên chưa có tin nhắn.
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { request } from "@/api/client";
import { track } from "@/api/telemetry";
import type { SuggestionOut } from "@/api/types";
import { t } from "@/content/messages";
import { useAuthStore } from "@/stores/auth";
import { useChatStore } from "@/stores/chat";
import { useDocumentsStore } from "@/stores/documents";
import { useFeaturesStore } from "@/stores/features";
import { KEY_ONBOARDED, storageGet, storageSet } from "@/utils/storage";

defineProps<{ userName: string }>();

const docs = useDocumentsStore();
const chat = useChatStore();
const auth = useAuthStore();
const features = useFeaturesStore();

const suggestions = ref<SuggestionOut[]>([]);
const readyCount = computed(() => docs.readyItems.length);
const emptyLibrary = computed(() => docs.loaded && docs.items.length === 0);
const canUpload = computed(() => auth.me?.role === "TEAM_LEAD");

// EC-01: kho trống → vô hiệu ô nhập.
watch(emptyLibrary, (v) => (chat.libraryEmpty = v), { immediate: true });
onBeforeUnmount(() => (chat.libraryEmpty = false));

// Gợi ý chỉ khi cờ bật và có tài liệu sẵn sàng (API-17).
watch(
  [() => docs.loaded, readyCount, () => features.flags.suggestions],
  async ([loaded, n, flag]) => {
    if (!loaded || !flag || n === 0) {
      suggestions.value = [];
      return;
    }
    try {
      suggestions.value = (await request<{ items: SuggestionOut[] }>("/api/v1/suggestions")).items.slice(0, 3);
    } catch {
      suggestions.value = [];
    }
  },
  { immediate: true },
);

// `onboarding_viewed` một lần mỗi trình duyệt, sau khi biết số tài liệu.
const onboarded = ref(false);
watch(
  () => docs.loaded,
  (loaded) => {
    if (!loaded || onboarded.value) return;
    onboarded.value = true;
    if (storageGet(KEY_ONBOARDED, "local") === "1") return;
    storageSet(KEY_ONBOARDED, "1", "local");
    track("onboarding_viewed", { doc_count: readyCount.value });
  },
  { immediate: true },
);

function pick(i: number) {
  const s = suggestions.value[i];
  if (!s) return;
  track("suggestion_clicked", { suggestion_index: i });
  void chat.send(s.text);
}
</script>

<template>
  <section class="welcome" data-testid="welcome" aria-labelledby="welcome-title">
    <template v-if="!docs.loaded">
      <div class="skeleton welcome-skeleton" aria-busy="true"></div>
    </template>
    <template v-else-if="emptyLibrary">
      <div class="state-box" data-testid="welcome-empty">
        <span aria-hidden="true" class="empty-icon">📄</span>
        <h2 id="welcome-title">{{ t("chat.emptyLibrary") }}</h2>
        <RouterLink v-if="canUpload" class="btn btn-primary" to="/library" data-testid="upload-cta">{{
          t("welcome.uploadCta")
        }}</RouterLink>
      </div>
    </template>
    <template v-else>
      <h2 id="welcome-title" data-testid="welcome-title">{{ t("welcome.greeting", { tên: userName, N: readyCount }) }}</h2>
      <p v-if="docs.processingCount > 0" class="muted" data-testid="processing-note">
        {{ t("library.processingCount", { N: docs.processingCount }) }}
      </p>
      <template v-if="suggestions.length">
        <p class="suggest-title">{{ t("suggest.title") }}</p>
        <div class="suggest-list">
          <button
            v-for="(s, i) in suggestions"
            :key="s.docId + i"
            type="button"
            class="suggest"
            data-testid="suggestion"
            @click="pick(i)"
          >
            {{ s.text }}
          </button>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.welcome-skeleton {
  width: 320px;
  height: 28px;
}
.empty-icon {
  font-size: 32px;
}
</style>

<script setup lang="ts">
// Danh sách lịch sử (S-06, CMP-13, US-041): nhóm Hôm nay, 7 ngày qua, Cũ hơn; bấm để mở lại phiên. P1 (cờ `history`).
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { request } from "@/api/client";
import type { SessionSummaryOut } from "@/api/types";
import SkeletonRows from "@/components/SkeletonRows.vue";
import { t } from "@/content/messages";
import { useChatStore } from "@/stores/chat";
import { useFeaturesStore } from "@/stores/features";
import { groupSessions } from "@/utils/history";


const features = useFeaturesStore();
const chat = useChatStore();
const route = useRoute();

const items = ref<SessionSummaryOut[]>([]);
const loading = ref(false);
const failed = ref(false);

const groups = computed(() => groupSessions(items.value, new Date()));
const sections = computed(
  () =>
    [
      { key: "today", label: t("history.today"), rows: groups.value.today },
      { key: "last7", label: t("history.last7"), rows: groups.value.last7 },
      { key: "older", label: t("history.older"), rows: groups.value.older },
    ].filter((s) => s.rows.length > 0),
);
const currentId = computed(() => (typeof route.params.sessionId === "string" ? route.params.sessionId : chat.sessionId));

async function load() {
  if (!features.flags.history) return;
  loading.value = true;
  failed.value = false;
  try {
    items.value = (await request<{ items: SessionSummaryOut[] }>("/api/v1/chat/sessions")).items;
  } catch {
    failed.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
// Sau mỗi lượt hỏi xong (nhất là câu đầu của phiên mới) lấy lại danh sách để có tiêu đề.
watch(
  () => chat.busy,
  (now, before) => {
    if (before && !now) void load();
  },
);
</script>


<template>
  <div v-if="features.flags.history" class="history" data-testid="history">
    <h2>{{ t("chat.history") }}</h2>
    <SkeletonRows v-if="loading" :rows="3" :label="t('history.loading')" />
    <div v-else-if="failed" class="history-state" role="alert" data-testid="history-error">
      <p class="caption">{{ t("history.error") }}</p>
      <button type="button" class="btn btn-sm" data-testid="history-retry" @click="load">{{ t("action.retry") }}</button>
    </div>
    <p v-else-if="items.length === 0" class="caption muted" data-testid="history-empty">{{ t("history.empty") }}</p>
    <template v-else>
      <div v-for="g in sections" :key="g.key" class="history-group" :data-testid="`group-${g.key}`">
        <h3>{{ g.label }}</h3>
        <RouterLink
          v-for="s in g.rows"
          :key="s.sessionId"
          v-slot="{ href, navigate }"
          :to="`/chat/${s.sessionId}`"
          custom
        >
          <a
            class="history-item"
            :href="href"
            :aria-current="currentId === s.sessionId ? 'page' : undefined"
            :title="s.title ?? ''"
            data-testid="history-item"
            @click="navigate"
          >{{ s.title ?? t("history.untitled") }}</a>
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.history-item {
  text-decoration: none;
}
.history-item[aria-current="page"] {
  background: var(--color-white);
  font-weight: 600;
}
.history-state {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  align-items: flex-start;
}
</style>

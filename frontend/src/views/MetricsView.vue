<script setup lang="ts">
// S-09 Số liệu thí điểm (US-051, BR-024): chỉ số tuần, biểu đồ SVG thuần và bảng thay thế. Không có nội dung câu hỏi/trả lời.
import { computed, onMounted, ref } from "vue";
import { request } from "@/api/client";
import type { WeeklyMetricsOut } from "@/api/types";
import IconGlyph from "@/components/IconGlyph.vue";
import SkeletonRows from "@/components/SkeletonRows.vue";
import WeeklyChart from "@/components/WeeklyChart.vue";
import { t } from "@/content/messages";
import { formatDateTime } from "@/utils/format";
import {
  DASH, integer, latencyStatus, notFoundStatus, percent, seconds, thumbsStatus, wauStatus, weekLabel, type KpiStatus,
} from "@/utils/metrics";

const data = ref<WeeklyMetricsOut | null>(null);
const loading = ref(true);
const failed = ref(false);
const selectedWeek = ref("");

async function load(week?: string) {
  loading.value = true;
  failed.value = false;
  try {
    const qs = week ? `?week=${encodeURIComponent(week)}` : "";
    data.value = await request<WeeklyMetricsOut>(`/api/v1/metrics/weekly${qs}`);
    selectedWeek.value = data.value.week;
  } catch {
    failed.value = true;
  } finally {
    loading.value = false;
  }
}

const empty = computed(() => data.value !== null && data.value.weeks.length === 0);

interface Kpi {
  key: string;
  label: string;
  value: string;
  goal: string;
  status: KpiStatus;
}

const kpis = computed<Kpi[]>(() => {
  const m = data.value?.metrics;
  if (!m) return [];
  const wau =
    m.wauPercent === null ? DASH : `${percent(m.wauPercent)} (${integer(m.wauCount)}/${integer(m.allowedCount)})`;
  const latency =
    m.latencyP90Ms === null && m.latencyP50Ms === null ? DASH : `${seconds(m.latencyP50Ms)} / ${seconds(m.latencyP90Ms)}`;
  return [
    { key: "wau", label: t("metrics.kpiWau"), value: wau, goal: t("metrics.goalWau"), status: wauStatus(m.wauPercent) },
    { key: "questions", label: t("metrics.kpiQuestions"), value: integer(m.questions), goal: "", status: null },
    { key: "latency", label: t("metrics.kpiLatency"), value: latency, goal: t("metrics.goalLatency"), status: latencyStatus(m.latencyP90Ms) },
    { key: "thumbs", label: t("metrics.kpiThumbs"), value: percent(m.thumbsUpPercent), goal: t("metrics.goalThumbs"), status: thumbsStatus(m.thumbsUpPercent) },
    { key: "notFound", label: t("metrics.kpiNotFound"), value: percent(m.notFoundPercent), goal: t("metrics.goalNotFound"), status: notFoundStatus(m.notFoundPercent) },
  ];
});

const STATUS_VIEW: Record<Exclude<KpiStatus, null>, { cls: string; icon: "check" | "warn"; text: string }> = {
  ok: { cls: "badge-success", icon: "check", text: t("metrics.ok") },
  inRange: { cls: "badge-neutral", icon: "check", text: t("metrics.inRange") },
  warn: { cls: "badge-warning", icon: "warn", text: t("metrics.warn") },
};

onMounted(() => load());
</script>

<template>
  <main id="main" class="page" data-testid="metrics">
    <div class="page-head">
      <h1>{{ t("metrics.title") }}</h1>
      <div v-if="data && !empty" class="head-tools">
        <div class="field week-field">
          <label for="week">{{ t("metrics.week") }}</label>
          <select id="week" v-model="selectedWeek" class="select week-select" data-testid="week-select" @change="load(selectedWeek)">
            <option v-for="w in data.weeks" :key="w" :value="w">{{ weekLabel(w) }}</option>
          </select>
        </div>
        <span class="caption muted" data-testid="updated">{{ t("metrics.updated", { "thời điểm": formatDateTime(data.updatedAt) }) }}</span>
      </div>
    </div>

    <SkeletonRows v-if="loading" :rows="4" />
    <div v-else-if="failed" class="state-box is-error" role="alert" data-testid="load-error">
      <strong>{{ t("metrics.loadError") }}</strong>
      <button type="button" class="btn" data-testid="retry" @click="load(selectedWeek || undefined)">{{ t("action.retry") }}</button>
    </div>
    <div v-else-if="empty" class="state-box" data-testid="empty">
      <strong>{{ t("metrics.empty") }}</strong>
    </div>
    <template v-else-if="data">
      <div class="kpi-grid" data-testid="kpis">
        <div v-for="k in kpis" :key="k.key" class="kpi" :data-testid="`kpi-${k.key}`">
          <span class="kpi-label">{{ k.label }}</span>
          <span class="kpi-value" data-testid="kpi-value">{{ k.value }}</span>
          <span v-if="k.goal" class="kpi-goal">{{ k.goal }}</span>
          <span v-if="k.status" class="badge" :class="STATUS_VIEW[k.status].cls" data-testid="kpi-status">
            <IconGlyph :name="STATUS_VIEW[k.status].icon" />{{ STATUS_VIEW[k.status].text }}
          </span>
        </div>
      </div>
      <section class="chart-card" :aria-label="t('metrics.chartTitle')">
        <h2>{{ t("metrics.chartTitle") }}</h2>
        <WeeklyChart :series="data.series" />
      </section>
    </template>
  </main>
</template>

<style scoped>
.head-tools {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  flex-wrap: wrap;
}
.week-field {
  flex-direction: row;
  align-items: center;
  gap: var(--space-2);
}
.week-select {
  width: auto;
}
.chart-card h2 {
  margin-bottom: var(--space-2);
}
</style>

<script setup lang="ts">
// Biểu đồ theo tuần bằng SVG thuần (không thư viện): cột = số câu hỏi, đường + chấm = WAU %. Có bảng thay thế.
import { computed, ref } from "vue";
import { t } from "@/content/messages";
import { integer, percent, weekLabel, weekShort } from "@/utils/metrics";

const props = defineProps<{ series: { week: string; questions: number; wauPercent: number | null }[] }>();

const W = 640;
const H = 260;
const L = 44;
const R = 44;
const T = 16;
const B = 44;
const iw = W - L - R;
const ih = H - T - B;

const asTable = ref(false);
const data = computed(() => [...props.series].sort((a, b) => a.week.localeCompare(b.week)));
const maxQ = computed(() => Math.max(50, Math.ceil(Math.max(0, ...data.value.map((d) => d.questions)) / 50) * 50));
const band = computed(() => iw / Math.max(1, data.value.length));

const bars = computed(() =>
  data.value.map((d, i) => {
    const x = L + band.value * i + band.value * 0.2;
    const w = band.value * 0.6;
    const h = (d.questions / maxQ.value) * ih;
    return { ...d, x, w, h, y: T + ih - h, cx: x + w / 2, cy: d.wauPercent === null ? null : T + ih - (d.wauPercent / 100) * ih };
  }),
);
const linePoints = computed(() =>
  bars.value.filter((b) => b.cy !== null).map((b) => `${b.cx},${b.cy}`).join(" "),
);
const qTicks = computed(() => [0, 0.5, 1].map((f) => ({ v: Math.round(maxQ.value * f), y: T + ih - f * ih })));
const pTicks = [0, 50, 100].map((v) => ({ v, y: T + ih - (v / 100) * ih }));

const summary = computed(() =>
  data.value
    .map((d) => `${weekShort(d.week)}: ${d.questions} ${t("metrics.questionsUnit")}, WAU ${percent(d.wauPercent)}`)
    .join("; "),
);
</script>

<template>
  <div class="weekly-chart" data-testid="weekly-chart">
    <div class="chart-legend">
      <span><span class="legend-swatch swatch-bar"></span>{{ t("metrics.legendBars") }}</span>
      <span><span class="legend-swatch swatch-line"></span>{{ t("metrics.legendLine") }}</span>
    </div>

    <svg
      v-if="!asTable"
      :viewBox="`0 0 ${W} ${H}`"
      width="100%"
      role="img"
      :aria-label="t('metrics.chartAria', { 'tóm tắt': summary })"
      class="chart-svg"
      data-testid="chart-svg"
    >
      <g v-for="tk in qTicks" :key="`q${tk.v}`">
        <line :x1="L" :x2="W - R" :y1="tk.y" :y2="tk.y" class="grid" />
        <text :x="L - 6" :y="tk.y + 4" text-anchor="end" class="axis">{{ tk.v }}</text>
      </g>
      <text v-for="tk in pTicks" :key="`p${tk.v}`" :x="W - R + 6" :y="tk.y + 4" class="axis axis-pct">{{ tk.v }}%</text>
      <g v-for="b in bars" :key="b.week">
        <rect :x="b.x" :y="b.y" :width="b.w" :height="b.h" rx="3" class="bar" />
        <text :x="b.cx" :y="H - 26" text-anchor="middle" class="axis">{{ weekShort(b.week) }}</text>
        <text :x="b.cx" :y="H - 10" text-anchor="middle" class="value">{{ b.questions }} {{ t("metrics.questionsUnit") }}</text>
      </g>
      <polyline v-if="linePoints" :points="linePoints" fill="none" class="line" />
      <g v-for="b in bars.filter((x) => x.cy !== null)" :key="`pt${b.week}`">
        <circle :cx="b.cx" :cy="b.cy!" r="4" class="dot" />
        <text :x="b.cx" :y="b.cy! - 8" text-anchor="middle" class="point-label">{{ percent(b.wauPercent) }}</text>
      </g>
    </svg>

    <div v-else class="table-wrap">
      <table class="table" data-testid="chart-table">
        <caption class="sr-only">{{ t("metrics.tableCaption") }}</caption>
        <thead>
          <tr>
            <th scope="col">{{ t("metrics.colWeek") }}</th>
            <th scope="col" class="num">{{ t("metrics.colQuestions") }}</th>
            <th scope="col" class="num">{{ t("metrics.colWau") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in data" :key="d.week" data-testid="chart-table-row">
            <th scope="row" class="row-head">{{ weekLabel(d.week) }}</th>
            <td class="num">{{ integer(d.questions) }}</td>
            <td class="num">{{ percent(d.wauPercent).replace("%", "") }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <button type="button" class="btn btn-sm toggle" data-testid="toggle-table" :aria-pressed="asTable" @click="asTable = !asTable">
      {{ asTable ? t("metrics.showChart") : t("metrics.showTable") }}
    </button>
  </div>
</template>

<style scoped>
.chart-svg {
  max-width: 720px;
}
.grid {
  stroke: var(--color-divider);
}
.axis {
  font-size: 13px;
  fill: var(--color-text-muted);
}
.axis-pct {
  fill: var(--color-warning-text);
}
.bar {
  fill: var(--color-primary);
}
.value {
  font-size: 13px;
  font-weight: 600;
  fill: var(--color-text);
}
.line {
  stroke: var(--color-warning-text);
  stroke-width: 2;
}
.dot {
  fill: var(--color-white);
  stroke: var(--color-warning-text);
  stroke-width: 2;
}
.point-label {
  font-size: 13px;
  font-weight: 600;
  fill: var(--color-warning-text);
  stroke: var(--color-white);
  stroke-width: 4px;
  paint-order: stroke;
}
.swatch-bar {
  background: var(--color-primary);
}
.swatch-line {
  background: var(--color-warning-text);
  border-radius: 50%;
}
.row-head {
  background: none;
  text-align: left;
  font-weight: 600;
}
.toggle {
  margin-top: var(--space-3);
}
</style>

import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import { installGuards } from "@/router/guards";
import MetricsView from "@/views/MetricsView.vue";
import type { WeeklyMetricsOut } from "@/api/types";
import { weekLabel, percent, seconds, wauStatus, notFoundStatus, thumbsStatus, latencyStatus } from "@/utils/metrics";
import { calls, installFetch, jsonRes } from "./helpers/api";

const SAMPLE: WeeklyMetricsOut = {
  week: "2026-12-21",
  weeks: ["2026-12-21", "2026-12-14"],
  updatedAt: "2026-12-28T06:00:00Z",
  metrics: {
    wauPercent: 72.2, wauCount: 13, allowedCount: 18, questions: 241,
    latencyP50Ms: 6200, latencyP90Ms: 13800, thumbsUpPercent: 76.0, notFoundPercent: 18.0,
  },
  series: [{ week: "2026-12-14", questions: 198, wauPercent: 66.7 }],
};

async function mountMetrics(body: unknown, status = 200) {
  setActivePinia(createPinia());
  const fetchMock = installFetch({ "GET /api/v1/metrics/weekly": () => jsonRes(status, body) });
  const w = mount(MetricsView);
  await flushPromises();
  return { w, fetchMock };
}

const kpi = (w: ReturnType<typeof mount>, key: string) => w.get(`[data-testid=kpi-${key}]`);

describe("MetricsView", () => {
  beforeEach(() => {
    process.env.TZ = "Asia/Ho_Chi_Minh";
  });
  afterEach(() => vi.unstubAllGlobals());

  it("renders_all_kpis", async () => {
    const { w } = await mountMetrics(SAMPLE);
    expect(kpi(w, "wau").get("[data-testid=kpi-value]").text()).toBe("72,2% (13/18)");
    expect(kpi(w, "questions").get("[data-testid=kpi-value]").text()).toBe("241");
    expect(kpi(w, "latency").get("[data-testid=kpi-value]").text()).toBe("6,2 s / 13,8 s");
    expect(kpi(w, "thumbs").get("[data-testid=kpi-value]").text()).toBe("76%");
    expect(kpi(w, "notFound").get("[data-testid=kpi-value]").text()).toBe("18%");
    expect(w.get("h1").text()).toBe("Số liệu thí điểm");
    expect(w.get("[data-testid=updated]").text()).toBe("Cập nhật: 28/12/2026 13:00");
    const options = w.findAll("option").map((o) => o.text());
    expect(options).toEqual(["21/12 – 27/12/2026", "14/12 – 20/12/2026"]);
  });

  it("kpi_status_labels", async () => {
    const good = await mountMetrics(SAMPLE);
    expect(kpi(good.w, "wau").get("[data-testid=kpi-status]").text()).toBe("Đạt mục tiêu");
    expect(kpi(good.w, "latency").get("[data-testid=kpi-status]").text()).toBe("Đạt mục tiêu");
    expect(kpi(good.w, "thumbs").get("[data-testid=kpi-status]").text()).toBe("Đạt mục tiêu");
    expect(kpi(good.w, "notFound").get("[data-testid=kpi-status]").text()).toBe("Trong ngưỡng");
    expect(kpi(good.w, "questions").find("[data-testid=kpi-status]").exists()).toBe(false);
    expect(good.w.get("[data-testid=kpi-wau] svg").attributes("aria-hidden")).toBe("true");

    const bad = await mountMetrics({
      ...SAMPLE,
      metrics: { ...SAMPLE.metrics, wauPercent: 50, notFoundPercent: 35, latencyP90Ms: 16000, thumbsUpPercent: 69 },
    });
    for (const k of ["wau", "notFound", "latency", "thumbs"]) {
      expect(kpi(bad.w, k).get("[data-testid=kpi-status]").text(), k).toBe("Cảnh báo");
    }
  });

  it("threshold_boundaries", () => {
    expect(wauStatus(60)).toBe("ok");
    expect(wauStatus(59.9)).toBe("warn");
    expect(latencyStatus(15000)).toBe("ok");
    expect(latencyStatus(15001)).toBe("warn");
    expect(thumbsStatus(70)).toBe("ok");
    expect(notFoundStatus(30)).toBe("inRange");
    expect(notFoundStatus(30.1)).toBe("warn");
    expect(wauStatus(null)).toBeNull();
  });

  it("chart_has_table_fallback", async () => {
    const series = [
      { week: "2026-12-07", questions: 143, wauPercent: 58 },
      { week: "2026-12-14", questions: 198, wauPercent: 66.7 },
      { week: "2026-12-21", questions: 241, wauPercent: null },
    ];
    const { w } = await mountMetrics({ ...SAMPLE, series });
    const svg = w.get("[data-testid=chart-svg]");
    expect(svg.attributes("role")).toBe("img");
    expect(svg.attributes("aria-label")).toContain("14/12: 198 câu hỏi, WAU 66,7%");
    expect(svg.findAll("rect.bar")).toHaveLength(3);
    expect(svg.findAll("circle")).toHaveLength(2); // tuần không có WAU không có chấm
    expect(w.find("table").exists()).toBe(false);
    await w.get("[data-testid=toggle-table]").trigger("click");
    expect(w.findAll("[data-testid=chart-table-row]")).toHaveLength(series.length);
    expect(w.find("[data-testid=chart-svg]").exists()).toBe(false);
  });

  it("null_values", async () => {
    const { w } = await mountMetrics({
      ...SAMPLE,
      metrics: { ...SAMPLE.metrics, thumbsUpPercent: null, latencyP50Ms: null, latencyP90Ms: null },
    });
    expect(kpi(w, "thumbs").get("[data-testid=kpi-value]").text()).toBe("—");
    expect(kpi(w, "thumbs").find("[data-testid=kpi-status]").exists()).toBe(false);
    expect(kpi(w, "latency").get("[data-testid=kpi-value]").text()).toBe("—");
    expect(kpi(w, "latency").find("[data-testid=kpi-status]").exists()).toBe(false);
  });

  it("empty_state", async () => {
    const { w } = await mountMetrics({ ...SAMPLE, weeks: [], series: [] });
    expect(w.get("[data-testid=empty]").text()).toBe("Chưa có dữ liệu. Số liệu xuất hiện sau tuần sử dụng đầu tiên.");
  });

  it("error_state_and_retry", async () => {
    setActivePinia(createPinia());
    let fail = true;
    const fetchMock = installFetch({
      "GET /api/v1/metrics/weekly": () => (fail ? jsonRes(500, { code: "INTERNAL", retryable: false }) : jsonRes(200, SAMPLE)),
    });
    const w = mount(MetricsView);
    await flushPromises();
    expect(w.get("[data-testid=load-error]").text()).toContain("Không tải được số liệu.");
    fail = false;
    await w.get("[data-testid=retry]").trigger("click");
    await flushPromises();
    expect(calls(fetchMock)).toHaveLength(2);
    expect(w.find("[data-testid=kpis]").exists()).toBe(true);
  });

  it("changing_week_refetches_with_param", async () => {
    const { w, fetchMock } = await mountMetrics(SAMPLE);
    await w.get("[data-testid=week-select]").setValue("2026-12-14");
    await flushPromises();
    expect(String(fetchMock.mock.calls[1]![0])).toBe("/api/v1/metrics/weekly?week=2026-12-14");
  });

  it("no_question_or_answer_text_is_rendered", async () => {
    const { w } = await mountMetrics(SAMPLE);
    expect(w.text()).not.toMatch(/\[\[|Hợp đồng|HD_/);
  });

  it("formatters", () => {
    expect(weekLabel("2026-12-28")).toBe("28/12 – 03/01/2027");
    expect(percent(18)).toBe("18%");
    expect(percent(null)).toBe("—");
    expect(seconds(13800)).toBe("13,8 s");
  });

  it("metrics_roles_guard", async () => {
    setActivePinia(createPinia());
    installFetch({ "GET /api/v1/me": () => jsonRes(200, { email: "lan@congty.vn", role: "BD_USER", allowed: true }) });
    const router = createRouter({ history: createMemoryHistory(), routes });
    installGuards(router);
    await router.push("/metrics");
    expect(router.currentRoute.value.path).toBe("/denied");
  });

  it("sponsor_and_admin_can_enter", async () => {
    for (const role of ["SPONSOR", "ADMIN"]) {
      setActivePinia(createPinia());
      installFetch({ "GET /api/v1/me": () => jsonRes(200, { email: "x@congty.vn", role, allowed: true }) });
      const router = createRouter({ history: createMemoryHistory(), routes });
      installGuards(router);
      await router.push("/metrics");
      expect(router.currentRoute.value.path, role).toBe("/metrics");
    }
  });
});

import { formatDecimal, formatInt } from "./format";

export type KpiStatus = "ok" | "warn" | "inRange" | null;

export const DASH = "—";

/** Phần trăm: tối đa 1 chữ số thập phân, dấu phẩy (72,2%; 76%). `null` → "—". */
export function percent(v: number | null | undefined): string {
  if (v === null || v === undefined) return DASH;
  return `${new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 1 }).format(v)}%`;
}

export function seconds(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return DASH;
  return `${formatDecimal(ms / 1000, 1)} s`;
}

export function integer(v: number | null | undefined): string {
  return v === null || v === undefined ? DASH : formatInt(v);
}

// Ngưỡng theo mục tiêu OKR (task T-520 bước 3). `null` → không có nhãn.
export const wauStatus = (v: number | null): KpiStatus => (v === null ? null : v >= 60 ? "ok" : "warn");
export const latencyStatus = (p90Ms: number | null): KpiStatus => (p90Ms === null ? null : p90Ms <= 15_000 ? "ok" : "warn");
export const thumbsStatus = (v: number | null): KpiStatus => (v === null ? null : v >= 70 ? "ok" : "warn");
export const notFoundStatus = (v: number | null): KpiStatus => (v === null ? null : v <= 30 ? "inRange" : "warn");

const pad = (n: number): string => String(n).padStart(2, "0");

/** `"2026-12-21"` (thứ Hai) → `"21/12 – 27/12/2026"`. Tính theo lịch, không phụ thuộc múi giờ. */
export function weekLabel(monday: string): string {
  const [y, m, d] = monday.split("-").map(Number) as [number, number, number];
  const start = new Date(Date.UTC(y, m - 1, d));
  const end = new Date(Date.UTC(y, m - 1, d + 6));
  const fmt = (dt: Date) => `${pad(dt.getUTCDate())}/${pad(dt.getUTCMonth() + 1)}`;
  return `${fmt(start)} – ${fmt(end)}/${end.getUTCFullYear()}`;
}

/** `"2026-12-21"` → `"21/12"`. */
export function weekShort(monday: string): string {
  const [, m, d] = monday.split("-").map(Number) as [number, number, number];
  return `${pad(d)}/${pad(m)}`;
}

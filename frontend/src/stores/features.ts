import { ref } from "vue";
import { defineStore } from "pinia";
import { request } from "@/api/client";
import type { Features } from "@/api/types";

/** Mặc định mọi cờ P1 tắt: tính năng P1 chỉ hiện khi `GET /api/v1/features` bật (DD-08). */
export const NO_FEATURES: Features = {
  suggestions: false,
  summary: false,
  history: false,
  rating: false,
  copy: false,
  scope: false,
  followup: false,
  duplicateCheck: false,
};

export const useFeaturesStore = defineStore("features", () => {
  const flags = ref<Features>({ ...NO_FEATURES });

  async function load(): Promise<void> {
    try {
      const data = await request<Features>("/api/v1/features");
      flags.value = { ...NO_FEATURES, ...data };
    } catch {
      flags.value = { ...NO_FEATURES }; // không lấy được cờ: ẩn mọi tính năng P1
    }
  }

  return { flags, load };
});

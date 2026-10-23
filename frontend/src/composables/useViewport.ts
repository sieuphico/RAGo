import { onBeforeUnmount, onMounted, ref } from "vue";

/** Độ rộng cửa sổ theo dõi được (NFR-007, Blueprint 3.8.3). */
export function useViewport() {
  const width = ref(typeof window === "undefined" ? 1280 : window.innerWidth);
  const update = () => {
    width.value = window.innerWidth;
  };
  onMounted(() => {
    update();
    window.addEventListener("resize", update);
  });
  onBeforeUnmount(() => window.removeEventListener("resize", update));
  return { width };
}

export type Layout = "wide" | "medium" | "narrow";

/** ≥ 1280: ba vùng; 1024–1279: thanh bên thu gọn, khung nguồn là lớp phủ; < 1024: một cột. */
export function layoutFor(width: number): Layout {
  if (width >= 1280) return "wide";
  if (width >= 1024) return "medium";
  return "narrow";
}

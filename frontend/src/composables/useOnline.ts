import { onBeforeUnmount, onMounted, ref } from "vue";

/** Theo dõi trạng thái mạng của trình duyệt (EC-05). */
export function useOnline() {
  const online = ref(typeof navigator === "undefined" ? true : navigator.onLine);
  const on = () => (online.value = true);
  const off = () => (online.value = false);
  onMounted(() => {
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
  });
  onBeforeUnmount(() => {
    window.removeEventListener("online", on);
    window.removeEventListener("offline", off);
  });
  return { online };
}

import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { ApiError, request } from "@/api/client";
import type { DocumentListOut, DocumentOut, DocumentSort, DocumentStatusData } from "@/api/types";
import { normalizeText } from "@/utils/format";

const collator = new Intl.Collator("vi");

export const useDocumentsStore = defineStore("documents", () => {
  const items = ref<DocumentOut[]>([]);
  const loading = ref(false);
  /** Đã tải danh sách thành công ít nhất một lần (để phân biệt "kho trống" với "chưa tải"). */
  const loaded = ref(false);
  const error = ref<string | null>(null);
  /** Mã tài liệu OCR đang xử lý quá 15 phút (T-509, EC-20). */
  const slowIds = ref<Set<string>>(new Set());

  const readyItems = computed(() => items.value.filter((d) => d.status === "READY"));
  const processingCount = computed(
    () => items.value.filter((d) => d.status === "PROCESSING" || d.status === "OCR_PROCESSING").length,
  );

  /** Tải toàn bộ danh sách (API-03); tìm và sắp xếp làm ở trình duyệt (Q-C12). `silent`: không bật trạng thái đang tải. */
  async function fetch(opts: { silent?: boolean } = {}): Promise<void> {
    if (!opts.silent) loading.value = true;
    error.value = null;
    try {
      const data = await request<DocumentListOut>("/api/v1/documents");
      items.value = data.items;
      loaded.value = true;
    } catch (e) {
      if (!opts.silent) error.value = e instanceof ApiError ? e.code : "INTERNAL";
    } finally {
      loading.value = false;
    }
  }

  function upsert(d: DocumentOut): void {
    const i = items.value.findIndex((x) => x.docId === d.docId);
    if (i === -1) items.value.unshift(d);
    else items.value[i] = d;
  }

  function remove(docId: string): void {
    items.value = items.value.filter((d) => d.docId !== docId);
    slowIds.value.delete(docId);
  }

  /** Áp dụng khung `status` của API-04 (CONTRACTS mục 5.1). */
  function applyEvent(e: DocumentStatusData): void {
    if (e.status === "DELETED") {
      remove(e.docId);
      return;
    }
    const doc = items.value.find((d) => d.docId === e.docId);
    if (!doc) {
      void fetch({ silent: true }); // tài liệu do người khác tải: lấy lại danh sách
      return;
    }
    doc.status = e.status;
    doc.failureReason = e.failureReason;
    if (e.pageCount !== null) doc.pageCount = e.pageCount;
    if (e.status !== "OCR_PROCESSING") slowIds.value.delete(e.docId);
  }

  function filtered(search: string, sort: DocumentSort): DocumentOut[] {
    const q = normalizeText(search.trim());
    const rows = q ? items.value.filter((d) => normalizeText(d.name).includes(q)) : [...items.value];
    const dir = sort.endsWith("_asc") ? 1 : -1;
    if (sort.startsWith("name")) rows.sort((a, b) => dir * collator.compare(a.name, b.name));
    else rows.sort((a, b) => dir * (Date.parse(a.uploadedAt) - Date.parse(b.uploadedAt)));
    return rows;
  }

  return { items, loading, loaded, error, slowIds, readyItems, processingCount, fetch, upsert, remove, applyEvent, filtered };
});

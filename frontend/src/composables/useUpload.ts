// Hàng đợi tải lên (T-523): mỗi tệp một yêu cầu XMLHttpRequest riêng (Q-C11) để có tiến độ và thử lại từng tệp (EC-03).
import { ref, type Ref } from "vue";
import { ApiError, CSRF_HEADER, CSRF_VALUE, notifyAuthError } from "@/api/client";
import { track } from "@/api/telemetry";
import type { DocumentOut, ErrorBody, UploadResultOut } from "@/api/types";
import { useAuthStore } from "@/stores/auth";
import { useDocumentsStore } from "@/stores/documents";

export interface UploadItem {
  id: string;
  file: File;
  state: "UPLOADING" | "INTERRUPTED" | "DONE" | "REJECTED";
  progress: number;
  errorCode?: string;
}

export const MAX_PARALLEL = 2;
const UPLOAD_URL = "/api/v1/documents";

// Trạng thái dùng chung toàn trang (hàng đợi sống qua các lần đổi route trong cùng phiên).
const items = ref<UploadItem[]>([]);
const xhrs = new Map<string, XMLHttpRequest>();
const waiting: string[] = []; // mã tệp chờ lượt gửi
let active = 0;
let seq = 0;

function find(id: string): UploadItem | undefined {
  return items.value.find((i) => i.id === id);
}

function pump(): void {
  while (active < MAX_PARALLEL && waiting.length > 0) {
    const id = waiting.shift()!;
    const item = find(id);
    if (item && item.state === "UPLOADING") start(item);
  }
}

function settle(item: UploadItem, state: UploadItem["state"], errorCode?: string): void {
  item.state = state;
  item.errorCode = errorCode;
  if (state !== "UPLOADING") item.progress = state === "DONE" ? 100 : item.progress;
  xhrs.delete(item.id);
  active = Math.max(0, active - 1);
  pump();
}

function parseError(text: string): ErrorBody | null {
  try {
    const b = JSON.parse(text) as Partial<ErrorBody>;
    return typeof b.code === "string" ? { code: b.code, retryable: b.retryable === true } : null;
  } catch {
    return null;
  }
}

function start(item: UploadItem): void {
  active += 1;
  item.state = "UPLOADING";
  item.progress = 0;
  item.errorCode = undefined;

  const xhr = new XMLHttpRequest();
  xhrs.set(item.id, xhr);
  xhr.open("POST", UPLOAD_URL);
  xhr.setRequestHeader(CSRF_HEADER, CSRF_VALUE);
  xhr.withCredentials = true;

  xhr.upload.onprogress = (e: ProgressEvent) => {
    if (e.lengthComputable && e.total > 0) item.progress = Math.min(100, Math.round((e.loaded / e.total) * 100));
  };
  xhr.onerror = () => settle(item, "INTERRUPTED", "NETWORK");
  xhr.onabort = () => settle(item, "INTERRUPTED", "NETWORK");
  xhr.ontimeout = () => settle(item, "INTERRUPTED", "NETWORK");
  xhr.onload = () => {
    if (xhr.status === 202) {
      let result: UploadResultOut | undefined;
      try {
        result = (JSON.parse(xhr.responseText) as { results: UploadResultOut[] }).results[0];
      } catch {
        result = undefined;
      }
      if (!result) return settle(item, "INTERRUPTED", "INTERNAL");
      if (result.error) return settle(item, "REJECTED", result.error);
      const me = useAuthStore().me;
      const doc: DocumentOut = {
        docId: result.docId ?? item.id,
        name: result.name,
        pageCount: null,
        uploadedBy: me?.email ?? "",
        uploadedAt: new Date().toISOString(),
        sizeBytes: item.file.size,
        status: result.status ?? "PROCESSING",
        failureReason: null,
        usedOcr: false,
        canDelete: true,
      };
      useDocumentsStore().upsert(doc);
      return settle(item, "DONE");
    }
    const body = parseError(xhr.responseText);
    const code = body?.code ?? "INTERNAL";
    if (code === "AUTH_EXPIRED" || code === "AUTH_FORBIDDEN") notifyAuthError(new ApiError(code, false, xhr.status));
    // Lỗi máy chủ hoặc có thể thử lại: cho thử lại từng tệp; còn lại là bị từ chối.
    if (xhr.status >= 500 || body?.retryable || code === "AUTH_EXPIRED") settle(item, "INTERRUPTED", code);
    else settle(item, "REJECTED", code);
  };

  const form = new FormData();
  form.append("files", item.file);
  xhr.send(form);
}

export function useUpload(): {
  items: Ref<UploadItem[]>;
  enqueue(files: File[]): void;
  retry(id: string): void;
  dismiss(id: string): void;
} {
  function enqueue(files: File[]): void {
    if (files.length === 0) return;
    const totalMb = files.reduce((n, f) => n + f.size, 0) / 1024 / 1024;
    track("document_upload_started", { file_count: files.length, total_size_mb: Math.round(totalMb * 100) / 100 });
    for (const file of files) {
      const item: UploadItem = { id: `up-${++seq}`, file, state: "UPLOADING", progress: 0 };
      items.value.push(item);
      waiting.push(item.id);
    }
    pump();
  }

  function retry(id: string): void {
    const item = find(id);
    if (!item || item.state !== "INTERRUPTED") return;
    item.state = "UPLOADING";
    item.progress = 0;
    item.errorCode = undefined;
    waiting.push(id);
    pump();
  }

  function dismiss(id: string): void {
    items.value = items.value.filter((i) => i.id !== id);
  }

  return { items, enqueue, retry, dismiss };
}

/** Chỉ dùng trong test: xóa hàng đợi và bộ đếm. */
export function resetUploadsForTest(): void {
  items.value = [];
  xhrs.clear();
  waiting.length = 0;
  active = 0;
}

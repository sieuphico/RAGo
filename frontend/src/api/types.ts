// Kiểu dữ liệu dùng chung với backend. Chép từ CONTRACTS mục 2, 4.2, 5 và 10.1; khóa camelCase đúng như JSON.

export type Role = "BD_USER" | "TEAM_LEAD" | "ADMIN" | "SPONSOR";

/** Trạng thái phía máy chủ (CONTRACTS mục 2). */
export type DocumentStatus =
  | "PROCESSING"
  | "OCR_PROCESSING"
  | "READY"
  | "FAILED"
  | "DELETED";

export type FailureReason =
  | "FILE_CORRUPTED"
  | "FILE_ENCRYPTED"
  | "OCR_UNREADABLE"
  | "PROCESSING_ERROR";

export type MessageStatus =
  | "SEARCHING"
  | "STREAMING"
  | "COMPLETED"
  | "NOT_FOUND"
  | "STOPPED"
  | "INTERRUPTED"
  | "FAILED";

/** Trạng thái chỉ có ở trình duyệt (CONTRACTS mục 10.1). */
export type ClientUploadState = "UPLOADING" | "INTERRUPTED";

// ---- Dạng trả về của API (CONTRACTS mục 4.2)

export interface MeOut {
  email: string;
  role: Role | null; // ngoài allow-list: null
  allowed: boolean;
}

export interface UploadResultOut {
  name: string;
  docId: string | null;
  status: DocumentStatus | null;
  error: string | null;
}

export interface DocumentOut {
  docId: string;
  name: string;
  pageCount: number | null;
  uploadedBy: string;
  uploadedAt: string; // ISO 8601 UTC
  sizeBytes: number;
  status: DocumentStatus;
  failureReason: FailureReason | null;
  usedOcr: boolean;
  canDelete: boolean;
}

export interface CitationOut {
  index: number;
  docId: string;
  docName: string;
  page: number;
  snippet: string;
  deleted: boolean;
}

export interface SessionSummaryOut {
  sessionId: string;
  title: string | null;
  createdAt: string;
  lastMessageAt: string;
}

export interface MessageOut {
  messageId: string;
  role: "user" | "assistant";
  text: string;
  status: MessageStatus;
  createdAt: string;
  isNotFound: boolean;
  citations: CitationOut[];
  rating: "UP" | "DOWN" | null;
}

export interface SessionDetailOut {
  sessionId: string;
  title: string | null;
  createdAt: string;
  scopeDocIds: string[];
  messages: MessageOut[];
}

export interface WeeklyMetricsOut {
  week: string;
  weeks: string[];
  updatedAt: string;
  metrics: {
    wauPercent: number | null;
    wauCount: number | null;
    allowedCount: number | null;
    questions: number | null;
    latencyP50Ms: number | null;
    latencyP90Ms: number | null;
    thumbsUpPercent: number | null;
    notFoundPercent: number | null;
  };
  series: { week: string; questions: number; wauPercent: number | null }[];
}

export interface UserOut {
  email: string;
  role: Role;
  addedBy: string;
  addedAt: string;
}

export type AuditAction = "UPLOAD" | "DELETE" | "PURGE";

export interface AuditOut {
  actor: string;
  action: AuditAction;
  docId: string;
  docName: string;
  at: string;
}

export interface SuggestionOut {
  docId: string;
  text: string;
}

export interface Features {
  suggestions: boolean;
  summary: boolean;
  history: boolean;
  rating: boolean;
  copy: boolean;
  scope: boolean;
  followup: boolean;
  duplicateCheck: boolean;
}

export interface SummaryOut {
  docId: string;
  docName: string;
  text: string;
  citations: CitationOut[];
}

// ---- Sự kiện SSE API-08 (CONTRACTS mục 5.2)

export interface StatusData {
  stage: "searching";
  docCount: number;
  messageId: string;
  scopeRemoved: string[];
}

export interface TokenData {
  text: string;
}

/** Khung `citation` không có `deleted` (CONTRACTS mục 5.2). */
export interface CitationData {
  index: number;
  docId: string;
  docName: string;
  page: number;
  snippet: string;
}

export interface DoneData {
  messageId: string;
  citationCount: number;
  isNotFound: boolean;
  notFoundReason: "NO_READY_DOCS" | "NO_EVIDENCE" | null;
  notice: "LANG_UNSUPPORTED" | null;
  stopped: boolean;
}

export interface ErrorData {
  code: string;
  retryable: boolean;
}

// ---- Sự kiện SSE API-04 (CONTRACTS mục 5.1)

export interface DocumentStatusData {
  docId: string;
  status: DocumentStatus;
  failureReason: FailureReason | null;
  pageCount: number | null;
}

/** Tin nhắn trong giao diện (CONTRACTS mục 10.5, Blueprint 3.5.2). */
export type UiMessageState =
  | "SUBMITTING"
  | "SEARCHING"
  | "STREAMING"
  | "COMPLETED"
  | "NOT_FOUND"
  | "STOPPED"
  | "INTERRUPTED"
  | "FAILED";

export interface UiMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  state: UiMessageState;
  citations: CitationOut[];
  messageId?: string;
  docCount?: number;
  errorCode?: string;
  notFoundReason?: "NO_READY_DOCS" | "NO_EVIDENCE" | null;
  notice?: "LANG_UNSUPPORTED" | null;
  sentAt: number;
  /** Đánh giá hiện tại (T-517). */
  rating?: "UP" | "DOWN" | null;
}

/** Giá trị `sort` của API-03 (CONTRACTS mục 4.1). */
export type DocumentSort = "uploadedAt_desc" | "uploadedAt_asc" | "name_asc" | "name_desc";

export interface DocumentListOut {
  items: DocumentOut[];
  total: number;
}

/** Lỗi trả về của mọi API (CONTRACTS mục 3). */
export interface ErrorBody {
  code: string;
  retryable: boolean;
}

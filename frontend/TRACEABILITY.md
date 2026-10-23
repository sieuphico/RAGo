# Truy vết frontend (Pha 5)

Bảng task → file → test → trạng thái, kèm US/BR. Sẽ được gộp vào `docs/traceability.md` ở nhánh chính.

| Task | US | BR | File chính | Test | Trạng thái |
|---|---|---|---|---|---|
| T-501 | — | — | `frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `eslint.config.js`, `src/main.ts`, `src/App.vue`, `scripts/check-dist.mjs` | `src/__tests__/app.spec.ts`; kiểm tra gói qua `npm run build` | Xong |
| T-503 | — | — | `src/api/types.ts`, `src/api/client.ts`, `src/api/errors.ts`, `src/content/messages.ts` | `src/__tests__/errors.spec.ts`, `src/__tests__/client.spec.ts` | Xong |
| T-502 | US-001 | BR-033 | `src/styles/tokens.css`, `src/styles/base.css`, `src/router/nav.ts`, `src/router/index.ts`, `src/components/AppHeader.vue`, `src/views/PlaceholderView.vue` | `src/__tests__/header.spec.ts` | Xong (AppHeader nhận `role`/`userName` qua props; App.vue nối kho đăng nhập ở T-505) |
| T-504 | US-027 | BR-013 | `src/api/sse.ts` | `src/__tests__/sse.spec.ts` | Xong |
| T-505 | US-001, US-002 | BR-016 | `src/stores/auth.ts`, `src/stores/features.ts`, `src/router/guards.ts`, `src/router/navigation.ts`, `src/views/LoginView.vue`, `src/views/DeniedView.vue`, `src/utils/storage.ts`, `src/App.vue` | `src/__tests__/auth.spec.ts` | Xong (thêm `setForbiddenHandler`, xem FQ-05) |
| T-506 | US-012 | — | `src/components/{ToastHost,BannerHost,ConfirmDialog,SkeletonRows,StatusBadge,IconGlyph}.vue`, `src/composables/{useToast,useBanner}.ts` | `src/__tests__/components.spec.ts` | Xong (thêm trạng thái DELETED "Đã xóa", prop `slow`; xem FQ-06) |
| T-507 | US-015 | BR-006 | `src/views/LibraryView.vue`, `src/stores/documents.ts`, `src/components/DocumentTable.vue`, `src/utils/format.ts` | `src/__tests__/library.spec.ts`, `src/__tests__/format.spec.ts` | Xong (store không giữ `uploads`: hàng đợi ở `useUpload`, T-523) |
| T-521 | US-051 | — | `src/api/telemetry.ts` | `src/__tests__/telemetry.spec.ts` | Xong (id sự kiện kiểm là UUID; lược đồ chỉ gồm 6 sự kiện giao diện) |
| T-511 | US-020 | BR-008, BR-013 | `src/views/ChatView.vue`, `src/components/ChatSidebar.vue`, `src/composables/useViewport.ts`, `src/stores/chat.ts` (khung) | `src/__tests__/chat_layout.spec.ts` | Xong (kho chat ban đầu chỉ có khung; hoàn thiện ở T-524) |
| T-524 | US-020, US-027 | BR-008, BR-013 | `src/stores/chat.ts`, `src/components/Composer.vue`, `src/composables/useOnline.ts` | `src/__tests__/composer.spec.ts`, `src/__tests__/chat_store.spec.ts` | Xong (URL không đổi khi tạo phiên mới; thêm tự động FAILED/TIMEOUT sau 65 giây ở store) |
| T-508 | US-010, US-011, US-014 | BR-001..BR-004 | `src/components/DropZone.vue`, `src/utils/validateFiles.ts`, `src/views/LibraryView.vue` | `src/__tests__/upload.spec.ts` | Xong (nối `enqueue` ở T-523) |
| T-512 | US-020, US-022, US-023, US-027 | BR-010, BR-011, BR-013 | `src/components/{MessageList,AnswerBlock,CitationChip}.vue`, `src/utils/answerText.ts` | `src/__tests__/answer.spec.ts` | Xong |
| T-523 | US-010, US-014 | BR-001, BR-003, BR-004 | `src/composables/useUpload.ts`, `src/components/UploadQueue.vue`, `src/views/LibraryView.vue` | `src/__tests__/use_upload.spec.ts` | Xong (hàng đợi dùng chung cấp module; thêm `dismiss`) |
| T-509 | US-012 | BR-005 | `src/composables/useDocumentEvents.ts`, `src/views/LibraryView.vue` | `src/__tests__/document_events.spec.ts` | Xong (composable trả thêm `announcement`) |
| T-525 | US-023, US-027, US-020 | BR-011, BR-013 | `src/components/AnswerState.vue`, `src/stores/chat.ts` (retry), `src/components/MessageList.vue` | `src/__tests__/answer_state.spec.ts` | Xong |
| T-513 | US-022 | BR-010 | `src/components/SourceViewer.vue`, `src/views/ChatView.vue` | `src/__tests__/source_viewer.spec.ts` | Xong |
| T-519 | US-061, US-063 | BR-016, BR-018 | `src/views/AdminUsersView.vue`, `src/views/AdminAuditView.vue`, `src/components/AdminTabs.vue` | `src/__tests__/admin.spec.ts` | Xong |
| T-520 | US-051 | BR-024 | `src/views/MetricsView.vue`, `src/components/WeeklyChart.vue`, `src/utils/metrics.ts` | `src/__tests__/metrics.spec.ts` | Xong |
| T-522 | — | BR-033 | `e2e/a11y.spec.ts` (khung, chưa chạy), `A11Y_REPORT.md`, h1 ẩn ở `ChatView.vue` | `src/__tests__/a11y_static.spec.ts` | Một phần: kiểm tĩnh xong; quét axe, cuộn ngang, 200% zoom, trình đọc màn hình chưa chạy (FQ-07, FQ-08) |
| T-514 | US-026 | BR-015 | `src/components/ScopePicker.vue`, `src/views/ChatView.vue` | `src/__tests__/scope_picker.spec.ts` | Xong (P1, ẩn khi cờ `scope` tắt; xử lý `scopeRemoved` ở `stores/chat.ts`) |
| T-516 | US-041 | BR-021 | `src/components/HistoryList.vue`, `src/utils/history.ts`, `src/stores/chat.ts` (open) | `src/__tests__/history.spec.ts` | Xong (P1, ẩn khi cờ `history` tắt; `groupSessions` đặt ở `utils/history.ts`) |
| T-515 | US-030, US-031 | BR-020, BR-035 | `src/components/WelcomePanel.vue`, `src/stores/documents.ts` (cờ `loaded`), `src/views/ChatView.vue` | `src/__tests__/welcome.spec.ts` | Xong (P1; thêm `docs.loaded` để không báo "kho trống" trước khi tải xong) |
| T-517 | US-042, US-050 | BR-022, BR-023 | `src/components/AnswerActions.vue`, `src/components/RatingDialog.vue`, `src/utils/answerText.ts` (copyText), `src/components/ConfirmDialog.vue` (prop `cancelLabel`) | `src/__tests__/answer_actions.spec.ts` | Xong (P1, ẩn theo cờ `copy`/`rating`) |
| T-510 | US-016, US-017, US-062 | BR-007, BR-001 | `src/components/RowMenu.vue`, `src/components/DuplicateDialog.vue`, `src/views/LibraryView.vue` | `src/__tests__/row_actions.spec.ts` | Xong (P1; kiểm tra trùng chỉ khi cờ `duplicateCheck` bật; dòng không có thao tác thì không hiện nút ⋯) |

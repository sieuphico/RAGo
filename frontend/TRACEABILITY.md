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

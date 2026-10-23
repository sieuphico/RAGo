# Truy vết frontend (Pha 5)

Bảng task → file → test → trạng thái, kèm US/BR. Sẽ được gộp vào `docs/traceability.md` ở nhánh chính.

| Task | US | BR | File chính | Test | Trạng thái |
|---|---|---|---|---|---|
| T-501 | — | — | `frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `eslint.config.js`, `src/main.ts`, `src/App.vue`, `scripts/check-dist.mjs` | `src/__tests__/app.spec.ts`; kiểm tra gói qua `npm run build` | Xong |
| T-503 | — | — | `src/api/types.ts`, `src/api/client.ts`, `src/api/errors.ts`, `src/content/messages.ts` | `src/__tests__/errors.spec.ts`, `src/__tests__/client.spec.ts` | Xong |
| T-502 | US-001 | BR-033 | `src/styles/tokens.css`, `src/styles/base.css`, `src/router/nav.ts`, `src/router/index.ts`, `src/components/AppHeader.vue`, `src/views/PlaceholderView.vue` | `src/__tests__/header.spec.ts` | Xong (AppHeader nhận `role`/`userName` qua props; App.vue nối kho đăng nhập ở T-505) |
| T-504 | US-027 | BR-013 | `src/api/sse.ts` | `src/__tests__/sse.spec.ts` | Xong |
| T-505 | US-001, US-002 | BR-016 | `src/stores/auth.ts`, `src/stores/features.ts`, `src/router/guards.ts`, `src/router/navigation.ts`, `src/views/LoginView.vue`, `src/views/DeniedView.vue`, `src/utils/storage.ts`, `src/App.vue` | `src/__tests__/auth.spec.ts` | Xong (thêm `setForbiddenHandler`, xem FQ-05) |

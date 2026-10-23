import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import type { Role } from "@/api/types";
import PlaceholderView from "@/views/PlaceholderView.vue";
import LoginView from "@/views/LoginView.vue";
import DeniedView from "@/views/DeniedView.vue";

declare module "vue-router" {
  interface RouteMeta {
    /** Vai trò được vào; vắng mặt = không giới hạn theo vai trò. */
    roles?: Role[];
    /** Trang không cần đăng nhập. */
    public?: boolean;
    title?: string;
  }
}

const CHAT_ROLES: Role[] = ["BD_USER", "TEAM_LEAD", "ADMIN"];

// CONTRACTS mục 10.2. Component tạm là trang rỗng có tiêu đề; task màn hình thay sau.
export const routes: RouteRecordRaw[] = [
  { path: "/login", name: "login", component: LoginView, meta: { public: true, title: "Đăng nhập" } },
  { path: "/denied", name: "denied", component: DeniedView, meta: { title: "Không có quyền" } },
  { path: "/", name: "chat", component: PlaceholderView, meta: { roles: CHAT_ROLES, title: "Hỏi đáp" } },
  {
    path: "/chat/:sessionId",
    name: "chat-session",
    component: PlaceholderView,
    meta: { roles: CHAT_ROLES, title: "Hỏi đáp" },
  },
  { path: "/library", name: "library", component: PlaceholderView, meta: { roles: CHAT_ROLES, title: "Kho tài liệu" } },
  {
    path: "/admin/users",
    name: "admin-users",
    component: PlaceholderView,
    meta: { roles: ["ADMIN"], title: "Người dùng được cấp quyền" },
  },
  {
    path: "/admin/audit",
    name: "admin-audit",
    component: PlaceholderView,
    meta: { roles: ["ADMIN"], title: "Nhật ký" },
  },
  { path: "/metrics", name: "metrics", component: PlaceholderView, meta: { roles: ["ADMIN", "SPONSOR"], title: "Số liệu" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

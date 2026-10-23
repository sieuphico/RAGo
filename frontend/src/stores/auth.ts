import { ref } from "vue";
import { defineStore } from "pinia";
import { ApiError, request } from "@/api/client";
import type { MeOut } from "@/api/types";
import { getRouter } from "@/router/navigation";
import { redirect } from "@/utils/navigate";

export type AuthStatus = "loading" | "unauthenticated" | "denied" | "revoked" | "allowed";

export const useAuthStore = defineStore("auth", () => {
  const status = ref<AuthStatus>("loading");
  const me = ref<MeOut | null>(null);

  /** Tải `/me` (API-01). 401 → chưa đăng nhập; `allowed=false` → không có quyền. */
  async function load(): Promise<void> {
    try {
      const data = await request<MeOut>("/api/v1/me");
      me.value = data;
      status.value = data.allowed ? "allowed" : "denied";
    } catch (e) {
      me.value = null;
      // Mọi lỗi khác (kể cả mạng) coi như chưa có phiên hợp lệ: trang đăng nhập không cần API.
      status.value = e instanceof ApiError || e instanceof Error ? "unauthenticated" : "unauthenticated";
    }
  }

  function login(next: string): void {
    redirect(`/auth/login?next=${encodeURIComponent(next)}`);
  }

  async function logout(): Promise<void> {
    try {
      await request<void>("/auth/logout", { method: "POST" });
    } catch {
      /* dù lỗi vẫn đưa người dùng về trang đăng nhập */
    }
    me.value = null;
    status.value = "unauthenticated";
    await getRouter().push("/login");
  }

  /** Dùng bởi bộ xử lý lỗi toàn cục (guards.ts). */
  function setStatus(s: AuthStatus): void {
    status.value = s;
  }

  return { status, me, load, login, logout, setStatus };
});

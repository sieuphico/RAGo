import type { Router } from "vue-router";
import { setAuthExpiredHandler, setForbiddenHandler } from "@/api/client";
import { useAuthStore, type AuthStatus } from "@/stores/auth";
import { useFeaturesStore } from "@/stores/features";
import { setRouter } from "./navigation";
import { KEY_RETURN_TO, storageRemove, storageSet } from "@/utils/storage";

function homeFor(role: string | null | undefined): string {
  return role === "SPONSOR" ? "/metrics" : "/";
}

/** Bảo vệ route theo trạng thái đăng nhập và `meta.roles`; đăng ký xử lý hết phiên và thu hồi quyền. */
export function installGuards(router: Router): void {
  setRouter(router);

  // Hết phiên giữa chừng: giữ đường dẫn hiện tại và bản nháp (sessionStorage), chuyển tới đăng nhập (EC-16).
  setAuthExpiredHandler(() => {
    const auth = useAuthStore();
    if (auth.status === "loading") return; // lần tải /me đầu tiên: guard tự điều hướng
    storageSet(KEY_RETURN_TO, router.currentRoute.value.fullPath);
    auth.setStatus("unauthenticated");
    void router.push({ path: "/login", query: { expired: "1" } });
  });

  // Quyền bị thu hồi khi đang dùng (EC-17).
  setForbiddenHandler(() => {
    const auth = useAuthStore();
    if (auth.status !== "allowed") return;
    auth.setStatus("revoked");
    void router.push("/denied");
  });

  router.beforeEach(async (to) => {
    const auth = useAuthStore();
    if (auth.status === "loading") {
      await auth.load();
      if ((auth.status as AuthStatus) === "allowed") {
        storageRemove(KEY_RETURN_TO);
        await useFeaturesStore().load();
      }
    }

    if (auth.status === "unauthenticated") {
      if (to.path === "/login") return true;
      if (to.path !== "/") storageSet(KEY_RETURN_TO, to.fullPath);
      return { path: "/login" };
    }

    if (auth.status === "denied" || auth.status === "revoked") {
      return to.path === "/denied" ? true : { path: "/denied" };
    }

    // allowed
    const role = auth.me?.role ?? null;
    if (to.path === "/login") return { path: homeFor(role) };
    if (to.path === "/" && role === "SPONSOR") return { path: "/metrics" };
    const roles = to.meta.roles;
    if (roles && (!role || !roles.includes(role))) return { path: "/denied" };
    return true;
  });
}

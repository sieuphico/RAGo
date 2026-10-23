import type { Role } from "@/api/types";
import { t } from "@/content/messages";

export interface NavItem {
  label: string;
  to: string;
}

/** Mục điều hướng theo vai trò (CONTRACTS mục 10.2). */
export function navItems(role: Role | null): NavItem[] {
  const chat = { label: t("nav.chat"), to: "/" };
  const library = { label: t("nav.library"), to: "/library" };
  const metrics = { label: t("nav.metrics"), to: "/metrics" };
  const admin = { label: t("nav.admin"), to: "/admin/users" };
  switch (role) {
    case "BD_USER":
    case "TEAM_LEAD":
      return [chat, library];
    case "ADMIN":
      return [chat, library, metrics, admin];
    case "SPONSOR":
      return [metrics];
    default:
      return [];
  }
}

/** Mục điều hướng có đang mở không (để đặt `aria-current="page"`). */
export function isCurrent(item: NavItem, path: string): boolean {
  if (item.to === "/") return path === "/" || path.startsWith("/chat/");
  if (item.to.startsWith("/admin")) return path.startsWith("/admin");
  return path === item.to || path.startsWith(item.to + "/");
}

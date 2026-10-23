import type { SessionSummaryOut } from "@/api/types";

export interface SessionGroups {
  today: SessionSummaryOut[];
  last7: SessionSummaryOut[];
  older: SessionSummaryOut[];
}

const DAY = 86_400_000;
const startOfDay = (d: Date): number => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();

/** Nhóm phiên theo `lastMessageAt` và giờ máy: hôm nay; 1–7 ngày trước; cũ hơn. */
export function groupSessions(items: SessionSummaryOut[], now: Date): SessionGroups {
  const today = startOfDay(now);
  const out: SessionGroups = { today: [], last7: [], older: [] };
  for (const s of items) {
    const days = Math.round((today - startOfDay(new Date(s.lastMessageAt))) / DAY);
    if (days <= 0) out.today.push(s);
    else if (days <= 7) out.last7.push(s);
    else out.older.push(s);
  }
  return out;
}

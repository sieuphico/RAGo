import type { UiMessage } from "@/api/types";
import { t } from "@/content/messages";

export type AnswerPart = { kind: "text"; value: string } | { kind: "cite"; index: number };

/** Tách văn bản trả lời theo dấu trích dẫn `[[n]]` (CONTRACTS mục 4.3). Đoạn chữ rỗng bị bỏ. */
export function splitAnswer(text: string): AnswerPart[] {
  const parts: AnswerPart[] = [];
  const re = /\[\[(\d+)\]\]/g;
  let last = 0;
  for (let m = re.exec(text); m !== null; m = re.exec(text)) {
    if (m.index > last) parts.push({ kind: "text", value: text.slice(last, m.index) });
    parts.push({ kind: "cite", index: Number(m[1]) });
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push({ kind: "text", value: text.slice(last) });
  return parts;
}

/** Văn bản sao chép: `[[n]]` → `[n]`, thêm khối "Nguồn:" mỗi dòng `[n] Tên tài liệu, tr. N` theo thứ tự `index` (CONTRACTS 4.3). */
export function copyText(m: Pick<UiMessage, "text" | "citations">): string {
  const body = m.text.replace(/\[\[(\d+)\]\]/g, "[$1]");
  if (m.citations.length === 0) return body;
  const lines = [...m.citations]
    .sort((a, b) => a.index - b.index)
    .map((c) => `[${c.index}] ${c.docName}, tr. ${c.page}`);
  return `${body}\n\n${t("actions.sources")}\n${lines.join("\n")}`;
}

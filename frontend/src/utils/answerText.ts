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

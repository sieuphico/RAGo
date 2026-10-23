/** Rút gọn ở giữa, giữ phần đầu và phần đuôi (đuôi `.pdf`); đầy đủ nên đặt ở `title`. */
export function truncateMiddle(s: string, max: number): string {
  if (s.length <= max) return s;
  const keep = Math.max(max - 1, 2);
  const head = Math.ceil(keep / 2);
  const tail = keep - head;
  return s.slice(0, head) + "…" + s.slice(s.length - tail);
}

const pad = (n: number): string => String(n).padStart(2, "0");

/** `dd/MM/yyyy HH:mm` theo giờ máy người dùng (CONTRACTS mục 0, UX-11). */
export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** `dd/MM/yyyy` theo giờ máy. */
export function formatDate(iso: string): string {
  return formatDateTime(iso).slice(0, 10);
}

/** So khớp không dấu: bỏ dấu, `đ → d`, chữ thường. */
export function normalizeText(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/đ/g, "d");
}

/** Số có dấu chấm ngăn nghìn kiểu Việt Nam: 2001 → "2.001". */
export function formatInt(n: number): string {
  return new Intl.NumberFormat("vi-VN").format(n);
}

/** Số thập phân dấu phẩy, `digits` chữ số: 6.2 → "6,2". */
export function formatDecimal(n: number, digits: number): string {
  return new Intl.NumberFormat("vi-VN", { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

/** Dung lượng theo MB, 1 chữ số thập phân. */
export function formatMegabytes(bytes: number): string {
  return formatDecimal(bytes / 1024 / 1024, 1);
}

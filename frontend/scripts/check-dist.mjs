// Kiểm tra gói (T-501): dist/ không chứa URL http(s) tới tên miền ngoài.
// Cho phép chuỗi không gây tải tài nguyên: URL không gian tên XML (w3.org) do Vue dùng để tạo phần tử SVG/MathML,
// và chú thích giấy phép.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, extname } from "node:path";

// và liên kết tài liệu nằm trong chuỗi thông báo lỗi của Vue (không bao giờ được gọi tải).
const ALLOWED = [/^https?:\/\/www\.w3\.org\//, /^https:\/\/vuejs\.org\/error-reference\//];
const dist = new URL("../dist", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

const bad = [];
for (const file of walk(dist)) {
  if (![".js", ".css", ".html"].includes(extname(file))) continue;
  const text = readFileSync(file, "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  for (const m of text.matchAll(/https?:\/\/[^\s"'`)<>\\]+/g)) {
    if (!ALLOWED.some((re) => re.test(m[0]))) bad.push(`${file}: ${m[0]}`);
  }
}
if (bad.length) {
  console.error("dist/ chứa URL ngoài:\n" + bad.join("\n"));
  process.exit(1);
}
console.log("dist/ không chứa URL ngoài.");

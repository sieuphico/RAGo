// Kiểm thử đầu cuối bằng trình duyệt thật: giao diện Vue + API FastAPI + worker + Ollama.
// Cách chạy: scripts/e2e/README.md (Playwright cài riêng, chưa nằm trong phụ thuộc của dự án).
import { chromium } from "playwright";
import path from "node:path";

const BASE = process.env.BASE ?? "http://localhost:5173";
const OUT = process.env.SHOTS ?? ".";
const PDF = process.env.PDF ?? "var/sample/text_12p.pdf";
const log = (...a) => console.log(...a);

async function login(browser, email, next = "/") {
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 }, ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  page.on("pageerror", (e) => log("  [pageerror]", email, e.message));
  page.on("console", (m) => m.type() === "error" && log("  [console.error]", email, m.text().slice(0, 200)));
  await page.goto(`${BASE}/auth/login?login_hint=${encodeURIComponent(email)}&next=${encodeURIComponent(next)}`);
  await page.waitForLoadState("networkidle");
  return { ctx, page };
}

const browser = await chromium.launch();
try {
  // 1. Minh (Trưởng nhóm BD) tải PDF lên kho
  const minh = await login(browser, "minh@congty.vn", "/library");
  await minh.page.waitForSelector('[data-testid="library"]', { timeout: 15000 });
  log("1. Kho tài liệu mở:", await minh.page.title());
  await minh.page.setInputFiles('[data-testid="file-input"]', PDF);
  await minh.page.waitForSelector('[data-testid="doc-row"]', { timeout: 20000 });
  const started = Date.now();
  await minh.page.waitForFunction(
    () => document.querySelector('[data-testid="doc-row"] [data-testid="status-badge"]')?.textContent?.includes("Sẵn sàng"),
    null, { timeout: 90000 });
  log(`   Tệp thành "Sẵn sàng" sau ${((Date.now() - started) / 1000).toFixed(1)}s (cập nhật SSE, không tải lại trang)`);
  log("   Hàng:", (await minh.page.locator('[data-testid="doc-row"]').first().innerText()).replace(/\s+/g, " "));
  await minh.page.screenshot({ path: path.join(OUT, "1-library.png") });

  // 2. Lan hỏi đáp có trích dẫn
  const lan = await login(browser, "lan@congty.vn", "/");
  await lan.page.waitForSelector('[data-testid="composer-input"]', { timeout: 15000 });
  await lan.page.screenshot({ path: path.join(OUT, "2-chat-empty.png") });
  const question = "Hợp đồng số HD-2026-012 có thời hạn bao lâu?";
  await lan.page.fill('[data-testid="composer-input"]', question);
  await lan.page.click('[data-testid="send"]');
  const t0 = Date.now();
  await lan.page.waitForSelector('[data-testid="searching"], [data-testid="answer-block"]', { timeout: 10000 });
  log(`2. Đã gửi câu hỏi; trạng thái tìm kiếm hiện sau ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await lan.page.waitForSelector('[data-testid="citation"]', { timeout: 120000 });
  await lan.page.waitForSelector('[data-testid="answer-actions"]', { timeout: 60000 });
  log(`   Câu trả lời xong sau ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  log("   Trả lời:", (await lan.page.locator('[data-testid="answer-text"]').last().innerText()).replace(/\s+/g, " "));
  log("   Thẻ trích dẫn:", (await lan.page.locator('[data-testid="citation"]').first().innerText()).replace(/\s+/g, " "));
  await lan.page.screenshot({ path: path.join(OUT, "3-answer.png") });

  // 3. Bấm thẻ trích dẫn để mở đúng trang PDF
  await lan.page.click('[data-testid="citation"]');
  await lan.page.waitForSelector('[data-testid="source-viewer"]', { timeout: 10000 });
  await lan.page.waitForTimeout(1500);
  log("3. Khung xem nguồn:", (await lan.page.locator('[data-testid="viewer-name"]').innerText()).trim(),
      "| trang:", (await lan.page.locator('[data-testid="viewer-page"]').innerText()).trim());
  const src = await lan.page.locator('[data-testid="viewer-iframe"]').getAttribute("src");
  log("   iframe src:", src);
  await lan.page.screenshot({ path: path.join(OUT, "4-source-viewer.png") });

  // 4. Đánh giá 👍
  await lan.page.click('[data-testid="rate-up"]');
  await lan.page.waitForTimeout(800);
  log("4. Đã bấm 👍");

  // 5. Câu hỏi ngoài phạm vi
  await lan.page.click('[data-testid="viewer-close"]').catch(() => {});
  await lan.page.fill('[data-testid="composer-input"]', "Giá vàng hôm nay là bao nhiêu?");
  await lan.page.click('[data-testid="send"]');
  await lan.page.waitForSelector('[data-testid="not-found"]', { timeout: 120000 });
  log("5. Câu ngoài phạm vi hiện khối 'không tìm thấy':", (await lan.page.locator('[data-testid="not-found"]').innerText()).replace(/\s+/g, " "));
  await lan.page.screenshot({ path: path.join(OUT, "5-not-found.png") });

  // 6. Lan không thấy vùng tải lên; quản trị viên xem số liệu và nhật ký
  await lan.page.goto(`${BASE}/library`);
  await lan.page.waitForSelector('[data-testid="library"]');
  log("6. Lan thấy dropzone?", await lan.page.locator('[data-testid="dropzone"]').count() > 0);

  const admin = await login(browser, "quantri@congty.vn", "/admin/audit");
  await admin.page.waitForSelector('[data-testid="admin-audit"]', { timeout: 15000 });
  log("   Nhật ký:", (await admin.page.locator('[data-testid="audit-row"]').first().innerText()).replace(/\s+/g, " "));
  await admin.page.screenshot({ path: path.join(OUT, "6-audit.png") });
  await admin.page.goto(`${BASE}/metrics`);
  await admin.page.waitForSelector('[data-testid="metrics"]', { timeout: 15000 });
  await admin.page.waitForTimeout(1500);
  log("   KPI:", (await admin.page.locator('[data-testid="kpis"]').innerText()).replace(/\s+/g, " ").slice(0, 300));
  await admin.page.screenshot({ path: path.join(OUT, "7-metrics.png") });
  log("HOÀN TẤT");
} catch (e) {
  log("LỖI:", e.message.split("\n")[0]);
  process.exitCode = 1;
} finally {
  await browser.close();
}

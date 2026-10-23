// KHUNG (T-522): quét khả năng tiếp cận trên trình duyệt thật bằng axe. CHƯA CHẠY ĐƯỢC trong nhánh này:
//  - cần thêm devDependencies `@playwright/test` và `@axe-core/playwright` (T-522 ghi [Đề xuất]; xem frontend/OPEN_QUESTIONS.md, FQ-07);
//  - cần môi trường E2E của T-606 (playwright.config.ts, backend + IdpFake). File này bị loại khỏi tsconfig và eslint.
// Khi môi trường có: `npx playwright test e2e/a11y.spec.ts`.
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const WIDTHS = [1024, 1280, 1440, 1920];

// IdpFake: `login_hint` là email đăng nhập (CONTRACTS 4.0).
async function loginAs(page: Page, email: string, next = "/") {
  await page.goto(`/auth/login?next=${encodeURIComponent(next)}&login_hint=${encodeURIComponent(email)}`);
}

const PAGES: { name: string; email: string; path: string }[] = [
  { name: "S-03 Hỏi đáp", email: "lan@congty.vn", path: "/" },
  { name: "S-04 Kho tài liệu", email: "minh@congty.vn", path: "/library" },
  { name: "S-07 Người dùng", email: "quantri@congty.vn", path: "/admin/users" },
  { name: "S-08 Nhật ký", email: "quantri@congty.vn", path: "/admin/audit" },
  { name: "S-09 Số liệu", email: "quantri@congty.vn", path: "/metrics" },
];

for (const p of PAGES) {
  test(`axe: ${p.name} không có lỗi serious/critical`, async ({ page }) => {
    await loginAs(page, p.email, p.path);
    await page.waitForSelector("#main");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
    const bad = results.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
    expect(bad, JSON.stringify(bad.map((v) => v.id))).toEqual([]);
  });

  for (const width of WIDTHS) {
    test(`không cuộn ngang: ${p.name} ở ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 800 });
      await loginAs(page, p.email, p.path);
      await page.waitForSelector("#main");
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      expect(overflow).toBe(false);
    });
  }
}

test("axe: S-01 Đăng nhập và S-02 Không có quyền", async ({ page }) => {
  await page.goto("/login");
  expect((await new AxeBuilder({ page }).analyze()).violations.filter((v) => v.impact === "serious" || v.impact === "critical")).toEqual([]);
  await loginAs(page, "khong-co-quyen@congty.vn");
  await page.waitForURL("**/denied");
  expect((await new AxeBuilder({ page }).analyze()).violations.filter((v) => v.impact === "serious" || v.impact === "critical")).toEqual([]);
});

test("giảm chuyển động: không có hoạt ảnh kéo dài", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await loginAs(page, "lan@congty.vn");
  await page.waitForSelector("#main");
  const dur = await page.evaluate(() => getComputedStyle(document.body).transitionDuration);
  expect(dur === "0s" || dur === "0.001s" || dur === "1e-06s").toBe(true);
});

test("phím tắt: / focus ô nhập", async ({ page }) => {
  await loginAs(page, "lan@congty.vn");
  await page.waitForSelector("#composer-input");
  await page.keyboard.press("/");
  await expect(page.locator("#composer-input")).toBeFocused();
});

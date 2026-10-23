# T-520 · Trang Số liệu (S-09)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 7 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-051 |
| BR | BR-024 |
| NFR, EC, cổng | UX-03 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md), [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) |
| Mở khóa | — |

## Mục tiêu

Các ô chỉ số, biểu đồ theo tuần bằng SVG thuần và bảng thay thế.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-13, 4.2 `WeeklyMetricsOut`
- `docs/04-design/UI_UX_design/metrics.html`
- Mục tiêu OKR (PRD mục 1.2, chép ở bước 3)
- API thật do T-312 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu: `useToast`, `useBanner`, `ConfirmDialog.vue`, `StatusBadge.vue`
- [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02: `useAuthStore`, `installGuards`

## File cần tạo hoặc sửa

- `frontend/src/views/MetricsView.vue`
- `frontend/src/components/WeeklyChart.vue`
- `frontend/src/__tests__/metrics.spec.ts`

## Chữ ký và giao diện

```typescript
// WeeklyChart.vue
defineProps<{ series: { week: string; questions: number; wauPercent: number | null }[] }>()
```

## Các bước

1. Dựng `MetricsView` theo `docs/04-design/UI_UX_design/metrics.html`: tiêu đề "Số liệu thí điểm", chọn tuần (từ `weeks`, nhãn `dd/MM – dd/MM/yyyy`), "Cập nhật: {updatedAt}".
2. 5 ô: WAU (`{wauPercent}% ({wauCount}/{allowedCount})`), Câu hỏi, Phản hồi p50/p90 (giây, 1 chữ số thập phân, dấu phẩy), 👍 hữu ích, Không tìm thấy. Giá trị `null` → `—`.
3. Mỗi ô có nhãn trạng thái chữ + biểu tượng: WAU ≥ 60% "Đạt mục tiêu" ngược lại "Cảnh báo"; p90 ≤ 15 s "Đạt mục tiêu"; 👍 ≥ 70% "Đạt mục tiêu"; Không tìm thấy ≤ 30% "Trong ngưỡng" ngược lại "Cảnh báo"; Câu hỏi không có nhãn.
4. `WeeklyChart` bằng SVG thuần (không thư viện): cột = số câu hỏi, đường = WAU %, trục có nhãn, mỗi điểm có hình tròn và nhãn giá trị; `role="img"` + `aria-label` tóm tắt. Nút "Xem dạng bảng" bật bảng `<table>` cùng dữ liệu `series`.
5. Không có `weeks` → `metrics.empty`. Lỗi → thông báo + [Thử lại]. Route `meta.roles = ["ADMIN", "SPONSOR"]`.

## Tiêu chí hoàn thành

- [ ] Hiển thị đủ chỉ số của AC-024.
- [ ] Không có văn bản câu hỏi hay câu trả lời nào.
- [ ] Biểu đồ có bảng thay thế truy cập được.
- [ ] Nhãn trạng thái đúng ngưỡng ở bước 3, có chữ và biểu tượng.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `renders_all_kpis` | API-13 giả trả mẫu `WeeklyMetricsOut` ở CONTRACTS mục 4.2 | "72,2% (13/18)", "241", "6,2 s / 13,8 s", "76%", "18%" |
| `kpi_status_labels` | Mẫu trên; rồi `wauPercent=50`, `notFoundPercent=35` | WAU "Đạt mục tiêu", Không tìm thấy "Trong ngưỡng"; sau đó WAU "Cảnh báo", Không tìm thấy "Cảnh báo" |
| `chart_has_table_fallback` | Bấm "Xem dạng bảng" | Có `<table>` với số dòng = `series.length` |
| `null_values` | `thumbsUpPercent = null` | Ô 👍 hiện "—", không có nhãn trạng thái |
| `metrics_roles_guard` | `me.role = BD_USER`; điều hướng `/metrics` | Kết thúc ở `/denied` |
| `empty_state` | `weeks = []` | "Chưa có dữ liệu. Số liệu xuất hiện sau tuần sử dụng đầu tiên." |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/metrics.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Tính số liệu (T-312).
- Xuất báo cáo (ngoài MVP).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.

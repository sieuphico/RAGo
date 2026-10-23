# T-519 · Trang quản trị: người dùng (S-07) và nhật ký (S-08)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-061, US-063 |
| BR | BR-016, BR-018 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md), [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) |
| Mở khóa | — |

## Mục tiêu

Bảng allow-list với thêm và gỡ; bảng nhật ký 4 trường; cả hai đủ 5 trạng thái.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-14, API-15, 4.2 `UserOut`, `AuditOut`
- CONTRACTS mục 3 (`EMAIL_INVALID`, `USER_EXISTS`, `USER_LIMIT_REACHED`, `LAST_ADMIN`)
- `docs/04-design/UI_UX_design/users.html`, `docs/04-design/UI_UX_design/audit.html`
- Blueprint 3.2.4 dòng S-07, S-08
- API thật do T-110, T-111 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu: `useToast`, `useBanner`, `ConfirmDialog.vue`, `StatusBadge.vue`
- [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02: `useAuthStore`, `installGuards`

## File cần tạo hoặc sửa

- `frontend/src/views/AdminUsersView.vue`
- `frontend/src/views/AdminAuditView.vue`
- `frontend/src/__tests__/admin.spec.ts`

## Chữ ký và giao diện

```typescript
// AdminUsersView.vue, AdminAuditView.vue: không nhận props; đọc dữ liệu qua `request` khi mount
```

## Các bước

1. `AdminUsersView` theo `docs/04-design/UI_UX_design/users.html`: tiêu đề "Người dùng được cấp quyền ({count}/20)", bảng Email, Vai trò (tên hiển thị CONTRACTS mục 1), Thêm lúc, nút gỡ.
2. [+ Thêm người dùng] mở form: ô email (kiểm tra cùng biểu thức với T-110 trước khi gửi), chọn vai trò (4 vai trò), [Thêm]. Lỗi `EMAIL_INVALID`, `USER_EXISTS` hiện ngay dưới ô email (`aria-describedby`); `USER_LIMIT_REACHED` hiện ở đầu form.
3. Gỡ: `ConfirmDialog destructive` "Gỡ quyền của {email}?"; `LAST_ADMIN` → toast thông báo của mã.
4. `AdminAuditView` theo `docs/04-design/UI_UX_design/audit.html`: bảng Người thực hiện, Thao tác (UPLOAD → "Tải lên", DELETE → "Xóa", PURGE → "Xóa dữ liệu (hệ thống)"), Tài liệu, Thời điểm; mặc định 100 dòng mới nhất.
5. Hai trang là hai tab trong mục "Quản trị"; route có `meta.roles = ["ADMIN"]`.
6. Trạng thái mỗi trang: khung xương; `users.empty` / `audit.empty`; lỗi + [Thử lại].

## Tiêu chí hoàn thành

- [ ] Thêm email X thì X xuất hiện ngay trong bảng và đăng nhập được (US-061).
- [ ] Bảng nhật ký có đủ 4 cột (AC-018).
- [ ] Email sai báo lỗi tại ô nhập, không gọi API.
- [ ] Vai trò khác ADMIN không vào được (T-505 chuyển `/denied`).

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `add_user_validation` | Nhập "lan@" và bấm [Thêm] | Thông báo "Email không hợp lệ." dưới ô; `request` không được gọi |
| `add_user_success` | Nhập "lan@congty.vn", vai trò BD; API giả trả 201 | Bảng thêm 1 dòng; tiêu đề tăng số đếm |
| `duplicate_user_error` | API giả ném `ApiError("USER_EXISTS")` | "Người dùng này đã có trong danh sách." dưới ô email |
| `audit_table_columns` | API-15 giả trả 2 mục UPLOAD, PURGE | 4 cột; ô thao tác "Tải lên" và "Xóa dữ liệu (hệ thống)" |
| `admin_only_route` | `me.role = TEAM_LEAD`; điều hướng `/admin/users` | Kết thúc ở `/denied` |
| `empty_states` | API-14a trả `items: []` | "Chưa có người dùng nào được cấp quyền" |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/admin.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sửa vai trò của người đã có (gỡ rồi thêm lại; ngoài MVP).
- Lọc, xuất nhật ký (ngoài MVP).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.

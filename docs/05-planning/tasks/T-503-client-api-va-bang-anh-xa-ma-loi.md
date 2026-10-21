# T-503 · Client API và bảng ánh xạ mã lỗi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | UX-06 |
| Quyết định kiến trúc | DD-06 |
| Phụ thuộc | [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md) |
| Mở khóa | [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md), [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-521](T-521-telemetry-phia-giao-dien.md) |

## Mục tiêu

Một client gọi API; mã lỗi `{code}` ánh xạ sang thông báo tiếng Việt ở một nơi duy nhất.

## File cần tạo hoặc sửa

- `frontend/src/api/client.ts`
- `frontend/src/api/errors.ts`
- `frontend/src/__tests__/errors.spec.ts`

## Chữ ký và giao diện

```typescript
export class ApiError extends Error { code: string; retryable: boolean }
```

## Các bước

1. `request<T>(path, options)` thêm tiêu đề `X-Requested-With` cho phương thức ghi; lỗi trả `ApiError(code, retryable)`.
2. `errors.ts`: bảng `code → thông báo tiếng Việt` theo Blueprint 3.8.4 và 5.2; không bao giờ hiển thị chuỗi lỗi của máy chủ.
3. Mã `AUTH_EXPIRED` kích hoạt luồng đăng nhập lại (T-505).

## Tiêu chí hoàn thành

- [ ] Mọi mã lỗi của T-107 có thông báo tiếng Việt, kiểm bằng test.
- [ ] Thêm một mã lỗi chỉ cần sửa `errors.ts` (QA-04).
- [ ] Thông báo không có mã hay thuật ngữ kỹ thuật.

## Kiểm thử cần viết

- `every_error_code_has_message`
- `unknown_code_gets_generic_message`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.

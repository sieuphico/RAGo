# ADR 0004: AI chạy nội bộ bằng Ollama (Qwen3 1.7B) cho nhúng và sinh câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận (theo yêu cầu người dùng 2026-10-23) |
| Ngày | 2026-10-23 |
| Task / Story | T-302, T-315 · US-020, US-022, US-060 |
| Liên quan | AD-06, AD-04, CON-005, RA-01, CONTRACTS mục 7 |

## Bối cảnh
AD-06 (nhà cung cấp AI) chưa chốt; DEP-001 chưa duyệt nên chưa được gửi dữ liệu thật ra dịch vụ ngoài. Người dùng yêu cầu dùng Ollama với Qwen3 1.7B để chạy AI cục bộ (phương án nội bộ, SAD RA-01).

## Quyết định
- Bộ nối `OllamaAi` (`app/adapters/ai_ollama.py`) cài `AiPort`: `embed` qua `/api/embed`, `generate` qua `/api/chat` dạng luồng NDJSON, `think=false`, `temperature=0.1`, `num_predict=800`. Không thêm thư viện (dùng `httpx`).
- Mô hình sinh: `qwen3:1.7b` (theo yêu cầu). Mô hình nhúng: `qwen3-embedding:0.6b` (1024 chiều, đa ngôn ngữ), vì `qwen3:1.7b` là mô hình sinh, không phải mô hình nhúng. **Đây là lựa chọn của tôi, chưa được người dùng xác nhận**; đổi bằng `CWD_OLLAMA_EMBED_MODEL` và `CWD_EMBEDDING_DIM`.
- Thêm 3 khóa cấu hình ngoài CONTRACTS mục 7: `ollama_base_url`, `ollama_chat_model`, `ollama_embed_model`.
- Chạy bằng Docker (`deploy/compose.dev.yml`, profile `ai`): `make ai-up`, `make ai-pull`.
- Khởi động API và worker gọi `self_check()` (nhúng thử, so số chiều với `embedding_dim`).
- Đặt `ai_provider=ollama` và `embedding_dim=1024`.

## Lựa chọn đã xét
- Nhúng bằng chính `qwen3:1.7b`: chất lượng truy xuất kém, chiều 2048.
- Cài Ollama trực tiếp trên máy: sửa hệ thống người dùng, khó tái lập; chọn container.
- Dịch vụ AI đám mây: bị chặn bởi DEP-001.

## Hệ quả
- Đổi mô hình nhúng đổi số chiều: phải tạo lại CSDL (`make db-reset`) và nhúng lại mọi tài liệu (migration 001 đọc `embedding_dim` lúc chạy).
- Qwen3 1.7B nhỏ: chất lượng trả lời, trích dẫn nhãn `[cK]` và tiếng Việt cần đo bằng bộ câu hỏi chuẩn (T-607); chạy CPU có thể chậm hơn NFR-001 (p90 ≤ 15 giây).
- CONTRACTS mục 7 thiếu 3 khóa; người duyệt cần cập nhật tài liệu baseline.

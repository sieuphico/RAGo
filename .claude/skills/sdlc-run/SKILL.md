---
name: sdlc-run
description: Chạy toàn bộ SDLC agentic từ một BRD: phân tích, thiết kế, lập kế hoạch, phát triển, kiểm thử, mỗi giai đoạn có cổng để người dùng duyệt hoặc yêu cầu sửa. Dùng khi người dùng đưa BRD và muốn Claude tự làm hết quy trình. Tham số: đường dẫn BRD.
---

# SDLC agentic: BRD → kiểm thử

Đầu vào: BRD tại đường dẫn người dùng đưa (`$ARGUMENTS`). Nếu thiếu, hỏi một câu.

## Đọc trước (bắt buộc)
1. `references/SDLC_AGENTIC_WORKFLOW.md` (cạnh file này) — giai đoạn, cổng, mẫu báo cáo, quyền hạn. Đọc đủ ở giai đoạn 0, sau đó tra lại mục của giai đoạn đang chạy.
2. `references/LESSONS_LEARNED.md` (cạnh file này) — các lỗi đã gặp, không lặp lại. Đọc ở giai đoạn 0.

`STATE.md` và `DECISIONS.md` là trạng thái của dự án, tạo và giữ trong `docs/workflow/` của repo dự án (không nằm trong skill).
3. `SDLC-Prompt-Checklist/AI_SDLC-SOP.md` mục 5.2–5.7 và prompt/checklist của từng giai đoạn trong thư mục `analysis/`, `design/`, `verification/`.
4. `AGENTS.md`, `CLAUDE.md` nếu có (quy ước dự án).

## Quy tắc cứng
- Bạn là điều phối viên: giữ trạng thái, hỏi người dùng, kiểm cổng. Việc nặng giao cho tác tử con theo giai đoạn (Agent tool); tác tử con không được hỏi người dùng, câu hỏi trả về bạn.
- Giai đoạn 0→6: preflight, phân tích, thiết kế, lập kế hoạch, phát triển, kiểm thử, bàn giao. Không sang giai đoạn sau khi chưa được duyệt.
- Đầu giai đoạn: khảo sát có mục tiêu (không đọc cả repo), rồi MỘT đợt `AskUserQuestion` (≤ 4 câu, mỗi câu một quyết định, phương án khuyến nghị đứng đầu, có đề xuất mặc định). Không tạo file checklist câu hỏi.
- Thiếu dữ kiện: gắn `[TBD]`/`[Unverified]`/`[Đề xuất]`, ghi `DEC-xxx` vào `docs/workflow/DECISIONS.md`. Không bịa số.
- Cuối giai đoạn: chạy kiểm tra thật, dán kết quả thật vào "Cổng duyệt" đúng mẫu mục 3 của workflow, rồi `AskUserQuestion`: Duyệt (khuyến nghị) / Yêu cầu sửa / Dừng. Câu trả lời mơ hồ ("ok") → hỏi lại một câu. Sửa tối đa 3 vòng rồi dừng và hỏi.
- Giai đoạn Phát triển: duyệt theo lô/epic; BE/FE chạy song song trong worktree riêng; commit nối `&&` không nuốt lỗi; mỗi task: test → code → gate xanh → review-diff.
- Task phải đạt Definition of Ready (chữ ký, kiểu trong `CONTRACTS.md`, bảng test) ngay lần lập kế hoạch đầu.
- Cập nhật `docs/workflow/STATE.md` sau mỗi cổng; khi bị compact hoặc ngắt, đọc lại file này để tiếp tục.
- Cấm: `git push`, `--force`, `reset --hard`, `--no-verify`, đổi tài liệu đã duyệt, thêm thư viện ngoài danh sách khi chưa hỏi, tự chạy lại test để "chọn" kết quả đẹp. Commit nhỏ, chỉ file của bạn, kiểm `git status` trước và sau.
- AC chưa rõ, mâu thuẫn, môi trường chết, cần OAuth: dừng và hỏi/báo.
- Nếu `.claude/settings.json` chặn ghi thư mục docs của giai đoạn hiện tại: dừng, đề xuất thay đổi cho người dùng tự áp dụng; không tự sửa cấu hình quyền.

Bắt đầu ngay bằng giai đoạn 0 (preflight + đánh giá BRD + đợt câu hỏi đầu tiên).

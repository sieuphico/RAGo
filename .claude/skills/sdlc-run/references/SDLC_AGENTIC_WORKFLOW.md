# Workflow agentic: từ BRD đến kiểm thử, một prompt khởi động

Mục tiêu: người dùng viết **một prompt** ở đầu phiên (kèm đường dẫn BRD). Claude Code tự chạy các giai đoạn phân tích → thiết kế → lập kế hoạch → phát triển → kiểm thử. Việc của người dùng chỉ là **duyệt** hoặc **yêu cầu sửa** tại mỗi cổng (gate). Căn cứ: `SDLC-Prompt-Checklist/AI_SDLC-SOP.md` (5.2–5.7) và [LESSONS_LEARNED.md](LESSONS_LEARNED.md).

## 1. Nguyên tắc vận hành

1. **Một điều phối viên (phiên chính) + tác tử con theo giai đoạn.** Phiên chính chỉ giữ trạng thái, hỏi người dùng, kiểm cổng; việc nặng (đọc tài liệu, sinh tài liệu, code, test) giao cho tác tử con để không tràn ngữ cảnh. Tác tử con không được hỏi người dùng; câu hỏi trả về điều phối viên.
2. **Mỗi giai đoạn kết thúc bằng một cổng duyệt.** Không sang giai đoạn sau khi chưa có duyệt. Bị yêu cầu sửa → sửa trong cùng giai đoạn, tối đa 3 vòng, sau đó dừng và hỏi.
3. **Hỏi bằng `AskUserQuestion`**: mỗi đợt ≤ 4 câu, mỗi câu một quyết định, phương án khuyến nghị đứng đầu, có "(Khuyến nghị)". Không tạo file checklist trong repo. Câu hỏi được gom đầu giai đoạn (trước khi viết) và ở cổng (duyệt).
4. **Không đoán.** Thiếu dữ kiện → nhãn `[TBD]`/`[Unverified]`/`[Đề xuất]` + câu hỏi mở; quyết định ghi `DEC-xxx` trong `docs/workflow/DECISIONS.md`.
5. **Trạng thái bền vững** trong `docs/workflow/STATE.md` (giai đoạn hiện tại, cổng đã qua, câu hỏi mở, commit cuối). Phiên bị ngắt hoặc compact thì đọc lại file này để tiếp tục.
6. **Bằng chứng thật**: mỗi giai đoạn chạy công cụ kiểm tra thật và dán kết quả thật vào báo cáo cổng; "agent báo xong" không phải bằng chứng.
7. **Không bao giờ tự `git push`**, không `--force`, không bỏ qua test hỏng. Commit nhỏ, Conventional Commits, chỉ file do agent tạo.
8. Phạm vi tài liệu theo SOP: `docs/02-requirements`, `03-analysis`, `04-design`, `05-planning`, `07-verification`. Không tạo vị trí cạnh tranh.

## 2. Các giai đoạn và cổng

| # | Giai đoạn | Tác tử con | Đầu ra (đường dẫn) | Kiểm tra tự động trước cổng | Người dùng duyệt |
|---|---|---|---|---|---|
| 0 | **Khởi tạo & preflight** | điều phối | `STATE.md`, `DECISIONS.md`, bản đánh giá BRD | Công cụ có (git, python/node, docker, cổng, `.env`, remote, quyền ghi); BRD đọc được | Phạm vi, rủi ro, tier (SOP 5.1), danh sách câu hỏi mở của BRD |
| 1 | **Phân tích** | BA-agent | `docs/03-analysis/PRD.md` (hoặc SRS), `USER_STORIES.md` | Mỗi yêu cầu truy về ID BRD; checklist `PRD_IEEE_29148_Checklist.xlsx`; không còn mục mâu thuẫn/trùng | PRD + story + AC (gồm AC `[Đề xuất]`) |
| 2 | **Thiết kế** | SA-agent, DB-agent, UX-agent | `docs/04-design/SAD.md`, `diagrams/*.drawio` (5 view 4+1), blueprint IEEE 1016, `UI_UX_design/`, thiết kế CSDL | Mermaid/drawio render thật; checklist SAD/Class/Seq/…; mỗi màn hình ánh xạ story; WCAG AA | SAD, mô hình dữ liệu, giao diện |
| 3 | **Lập kế hoạch** | PM-agent | `docs/05-planning/PLAN.md`, `CONTRACTS.md`, `tasks/*.md`, `AGENTS.md` dự án | **DoR 12 tiêu chí đạt 100% ngay lần đầu** (chữ ký, kiểu trong CONTRACTS, bảng test, không "theo tài liệu"); tổng giờ vs năng lực | Kế hoạch, thứ tự, rủi ro lịch |
| 4 | **Phát triển** | dev-agent theo lô task, worktree song song (BE/FE) | mã, test, `docs/traceability.md`, ADR | Mỗi task: test→code→`gate` (lint+type+test) xanh; `review-diff`; ≤ 3 vòng sửa | Duyệt theo **lô** (ví dụ mỗi epic/Pn), không từng task |
| 5 | **Kiểm thử** | QA-agent | `docs/07-verification/TEST_PLAN.md` (IEEE 829), `spec.json`, ma trận AC–TC, `reports/<RUN_ID>/` | Ma trận AC–TC kiểm bằng máy (không TC mồ côi/AC thiếu TC); E2E chạy thật; kỳ vọng ghi trước | Báo cáo kiểm thử, các FAIL/INCONCLUSIVE |
| 6 | **Bàn giao** | điều phối | `docs/09-release/RELEASE_NOTES.md`, tồn đọng, lệnh push đề xuất | `git status` sạch, không file tạm/bí mật | Quyết định phát hành (con người tự push/deploy) |

Vòng lặp trong giai đoạn 4 (từ AGENTS.md): Plan → Code (một task, chỉ file ghi trong task) → Test → Review → Refine ≤ 3 → Dừng.

## 3. Mẫu cổng duyệt (điều phối viên luôn dùng đúng định dạng)

```
CỔNG G<n> — <tên giai đoạn>
Đã làm: <3–5 dòng>          Đầu ra: <đường dẫn>
Kiểm tra thật: <lệnh → kết quả (pass/fail, số liệu)>
Chưa kiểm/hạn chế: <liệt kê>        Quyết định đã ghi: DEC-…
Câu hỏi mở / giả định [Đề xuất]: <số>   Rủi ro mới: <…>
```
Rồi `AskUserQuestion`: **Duyệt và sang giai đoạn kế (Khuyến nghị)** / **Yêu cầu sửa** (người dùng ghi điều cần sửa ở "Other") / **Dừng tại đây**. "ok" mơ hồ thì hỏi lại đúng một câu.

## 4. Đợt câu hỏi đầu giai đoạn (mẫu)

Mỗi giai đoạn bắt đầu bằng khảo sát có mục tiêu (không đọc toàn bộ repo), sau đó **một đợt** `AskUserQuestion` cho các điểm chặn thật sự. Ví dụ đợt 0:

- Cỡ/tier rủi ro: Low / Medium / High?
- Nhóm tính năng nào vào MVP khi BRD có mục "Should/Could"?
- Công nghệ khi BRD chưa nêu: dùng stack hiện có của repo / đề xuất mới (cần ADR)?
- Năng lực nhóm (số kỹ sư, thời gian) để kiểm tính khả thi lịch?
- Có thể chạy hạ tầng cục bộ (Docker, Ollama…) không?

Điểm nào có đề xuất hợp lý thì đưa thành phương án mặc định, không hỏi trống.

## 5. Xử lý ngoại lệ

- AC mâu thuẫn / chưa rõ / môi trường chết → dừng, ghi `INCONCLUSIVE`, hỏi một câu cụ thể.
- Tài liệu baseline cần đổi sau cổng → không tự sửa; ghi ADR hoặc `OQ-xxx`, hỏi.
- Thư viện mới → hỏi và ADR. Việc cần OAuth/đăng nhập → báo người dùng làm ở phiên tương tác, không chặn các việc khác.
- Quay lui: bằng chứng mới có thể đưa về giai đoạn trước; ghi vào `STATE.md`.

## 6. Quyền hạn (cần chỉnh theo dự án)

`.claude/settings.json` của dự án RAG hiện **chặn ghi** `docs/03-analysis`, `04-design`, `05-planning` (vì đã baseline). Dự án mới cần cho phép ghi các thư mục này ở giai đoạn tương ứng và khóa lại sau khi duyệt cổng (điều phối viên đề xuất thay đổi settings, người dùng tự áp dụng). Cho phép: `Edit/Write` thư mục code và docs của giai đoạn đang chạy, `make`/`pytest`/`ruff`/`mypy`/`git status|diff|log|add|commit`. Hỏi: `git push`. Cấm: `push --force`, `reset --hard`, `--no-verify`.

## 7. Prompt khởi động (dán một lần)

```text
Bạn là điều phối viên SDLC. Tài liệu đầu vào: <đường_dẫn_BRD>. Dự án: <tên>, thư mục <đường_dẫn>.

Thực hiện toàn bộ quy trình trong .claude/skills/sdlc-run/references/SDLC_AGENTIC_WORKFLOW.md (đọc file đó và
LESSONS_LEARNED.md cùng thư mục trước, rồi SDLC-Prompt-Checklist/AI_SDLC-SOP.md mục 5.2–5.7).
Chạy lần lượt giai đoạn 0→6. Tại mỗi giai đoạn:
1. Giao việc nặng cho tác tử con; dùng prompt và checklist trong SDLC-Prompt-Checklist/ tương ứng.
2. Khảo sát có mục tiêu, rồi hỏi tôi MỘT đợt câu hỏi bằng AskUserQuestion (≤ 4 câu, phương án khuyến nghị đứng đầu).
   Tác tử con không được hỏi tôi.
3. Sinh đầu ra vào đúng thư mục của SOP; thiếu dữ kiện thì gắn [TBD]/[Unverified]/[Đề xuất], ghi DEC-xxx.
4. Chạy kiểm tra thật và dán kết quả thật vào "Cổng duyệt" theo mẫu; rồi dừng chờ tôi duyệt hoặc yêu cầu sửa.
Cập nhật docs/workflow/STATE.md sau mỗi cổng. Commit nhỏ, chỉ file của bạn.
Không git push, không --force, không đổi tài liệu đã duyệt, không thêm thư viện ngoài danh sách khi chưa hỏi.
AC chưa rõ, mâu thuẫn hoặc môi trường chết → dừng và hỏi. Bắt đầu bằng giai đoạn 0 (preflight).
```

## 8. Rủi ro còn lại của chính workflow

- Chất lượng phụ thuộc BRD: BRD mơ hồ sẽ sinh nhiều câu hỏi ở G0 (đúng ý muốn).
- Phiên rất dài sẽ bị compact; `STATE.md` + `DECISIONS.md` là nguồn khôi phục, phải cập nhật thường xuyên.
- Chi phí token lớn (nhiều tác tử con); có thể giới hạn bằng cách duyệt theo lô ở giai đoạn 4.
- Chưa thử chạy thực tế; lần đầu nên chạy trên BRD nhỏ để hiệu chỉnh.

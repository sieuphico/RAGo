# T-112 · Bộ nối kho tệp (StoragePort)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-010, US-022 |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-11 |
| Phụ thuộc | [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) |
| Mở khóa | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md) |

## Mục tiêu

Lưu, đọc theo khoảng byte và xóa tệp PDF trên đĩa; an toàn với đường dẫn.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Chữ ký `StoragePort` ở T-008

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) Cổng (ports) và bộ nối giả (fake adapters): `ProviderError`, `ProviderTimeout`, `AiPort`, `OcrPort`, `StoragePort`, `IdpPort`

## File cần tạo hoặc sửa

- `app/adapters/storage_fs.py`
- `tests/unit/test_storage_fs.py`

## Chữ ký và giao diện

```python
class FsStorage:
    def __init__(self, root: Path) -> None: ...
    def save(self, key: str, data: bytes) -> None: ...
    def read(self, key: str, start: int | None = None, end: int | None = None) -> bytes: ...
    def size(self, key: str) -> int: ...
    def delete(self, key: str) -> None: ...

def new_file_key() -> str: ...
```

## Các bước

1. `FsStorage(root: Path)` triển khai `StoragePort`; tạo `root` nếu chưa có.
2. Khóa tệp do người gọi tạo bằng `uuid4().hex + ".pdf"`; chỉ nhận khóa khớp `^[0-9a-f]{32}\.pdf$`, sai → `ValueError`. Đường dẫn thật = `root / key[:2] / key`.
3. `save` ghi vào tệp tạm cùng thư mục rồi `os.replace` (nguyên tử); quyền tệp 0o600.
4. `read(key, start, end)` đọc byte `[start, end)` (end không bao gồm); `None` nghĩa là từ đầu hoặc tới cuối.
5. `delete` không lỗi khi tệp không tồn tại; `size` trả số byte.
6. Thêm `FsStorage` vào `core/wiring.py` (`build_storage(settings)`).

## Tiêu chí hoàn thành

- [ ] Khóa chứa `..`, `/` hay đường dẫn tuyệt đối bị từ chối.
- [ ] `read(key, 10, 20)` trả đúng 10 byte từ vị trí 10.
- [ ] Xóa tệp không tồn tại không ném lỗi.
- [ ] Ghi lỗi giữa chừng không để lại tệp dở.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_path_traversal_rejected` | `save("../x.pdf", b"..")` và `save("/etc/passwd", ...)` | `ValueError`, không có tệp nào được tạo |
| `test_range_read` | Lưu 100 byte `bytes(range(100))`; `read(k, 10, 20)` | `bytes(range(10, 20))` |
| `test_read_to_end` | `read(k, 95, None)` | 5 byte cuối |
| `test_delete_missing_ok` | `delete(<khóa hợp lệ chưa lưu>)` | Không ngoại lệ |
| `test_atomic_write` | Giả lập lỗi khi ghi (monkeypatch `write`) | Không có tệp đích; không còn tệp tạm |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_storage_fs.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Mã hóa ổ đĩa và chọn đĩa hay NAS (T-602, Q-A8).
- Sao lưu kho tệp (T-603).

## Lưu ý

Kho tệp là đĩa mã hóa hay NAS vẫn là câu hỏi Q-A8; bộ nối chỉ cần thư mục gắn sẵn.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.

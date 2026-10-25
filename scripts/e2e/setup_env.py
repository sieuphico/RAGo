"""SETUP-1 cho kiểm thử E2E: người dùng, tệp mẫu đã Sẵn sàng. Chạy lại nhiều lần không hỏng.

    python scripts/e2e/setup_env.py            # bảo đảm dữ liệu nền
    python scripts/e2e/setup_env.py --reset    # XÓA tài liệu, hội thoại, tác vụ, nhật ký, số liệu (CSDL dev) rồi dựng lại

Điều kiện: API (:8000) và worker đang chạy, `CWD_ALLOW_FAKE_IDP=true`, tệp var/sample/text_12p.pdf
(`python scripts/make_sample_data.py --out var/sample`). Thoát 0 khi tệp mẫu đã Sẵn sàng, khác 0 nếu không.
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.cli import main as cli_main
from app.core.config import get_settings

ROOT = Path(__file__).resolve().parents[2]
API = "http://localhost:8000"
PDF = ROOT / "var" / "sample" / "text_12p.pdf"
NAME = "text_12p.pdf"
H = {"X-Requested-With": "cwd"}
USERS = {"minh@congty.vn": "TEAM_LEAD", "lan@congty.vn": "BD_USER"}
ADMIN = "quantri@congty.vn"
READY_TIMEOUT_S = 180


def reset() -> None:
    settings = get_settings()
    engine = create_engine(make_url(settings.database_url).set(drivername="postgresql+psycopg"))
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE document, chat_session, job, audit_log, telemetry_event, ai_usage CASCADE"
        ))  # fmt: skip
    engine.dispose()
    shutil.rmtree(settings.storage_root, ignore_errors=True)
    print("Đã xóa dữ liệu dev")


def login(email: str) -> httpx.Client:
    """Gắn cookie thủ công: cờ Secure khiến httpx không gửi lại cookie qua http thường."""
    client = httpx.Client(base_url=API, timeout=120, follow_redirects=False)
    start = client.get("/auth/login", params={"login_hint": email})
    state = next(h for h in start.headers.get_list("set-cookie") if h.startswith("cwd_state="))
    callback = client.get(
        start.headers["location"].removeprefix(API), headers={"Cookie": state.split(";", 1)[0]}
    )
    session = next(h for h in callback.headers.get_list("set-cookie") if h.startswith("cwd_session="))
    client.cookies.clear()
    client.headers["Cookie"] = session.split(";", 1)[0]
    return client


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    if not PDF.is_file():
        print(f"Thiếu {PDF}; chạy: python scripts/make_sample_data.py --out var/sample")
        return 2
    if args.reset:
        reset()
    if cli_main(["add-admin", ADMIN]) != 0:
        return 3
    admin = login(ADMIN)
    for email, role in USERS.items():
        code = admin.post(
            "/api/v1/admin/users", json={"email": email, "role": role}, headers=H
        ).status_code
        if code not in (201, 409):  # 409: đã tồn tại
            print(f"Không thêm được {email}: HTTP {code}")
            return 4
    minh = login("minh@congty.vn")
    items = minh.get("/api/v1/documents").json()["items"]
    doc = next((d for d in items if d["name"] == NAME), None)
    if doc is None:
        with PDF.open("rb") as handle:
            files = {"files": (NAME, handle, "application/pdf")}
            result = minh.post("/api/v1/documents", files=files, headers=H).json()["results"][0]
        if result["error"]:
            print(f"Tải lên lỗi: {result['error']}")
            return 5
    deadline = time.monotonic() + READY_TIMEOUT_S
    while time.monotonic() < deadline:
        items = minh.get("/api/v1/documents").json()["items"]
        doc = next(d for d in items if d["name"] == NAME)
        if doc["status"] == "READY":
            print(f"SETUP-1 xong: {NAME} READY, {doc['pageCount']} trang")
            return 0
        if doc["status"] in ("FAILED", "DELETED"):
            print(f"{NAME} ở trạng thái {doc['status']} ({doc['failureReason']})")
            return 6
        time.sleep(2)
    print(f"{NAME} chưa READY sau {READY_TIMEOUT_S}s")
    return 7


if __name__ == "__main__":
    sys.exit(main())

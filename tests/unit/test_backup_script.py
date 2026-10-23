import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "deploy" / "backup" / "backup.sh"
FAKE = ROOT / "tests" / "fixtures" / "fake_compose.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="cần bash")


def _run(tmp_path: Path, stamp: str, **extra: str) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "BACKUP_DIR": str(tmp_path / "bk"),
        "BACKUP_STAMP": stamp,
        "COMPOSE": f"bash {FAKE.as_posix()}",
        "TEXTFILE_DIR": str(tmp_path),
        **extra,
    }
    return subprocess.run(
        [BASH or "bash", str(SCRIPT)], env=env, capture_output=True, text=True, check=False, timeout=60
    )


def test_backup_creates_files_and_clears_failure(tmp_path: Path) -> None:
    result = _run(tmp_path, "20261201-010000")
    assert result.returncode == 0, result.stdout + result.stderr
    target = tmp_path / "bk" / "20261201-010000"
    assert (target / "db.dump").read_bytes() == b"PGDMP-fake-dump"
    assert (target / "storage.tar").stat().st_size > 0
    assert not (tmp_path / "bk" / "last_failure").exists()
    assert (tmp_path / "cwd_backup.prom").read_text().strip().endswith(" 0")


def test_backup_failure_exit_code_and_marker(tmp_path: Path) -> None:
    result = _run(tmp_path, "20261201-010000", FAKE_FAIL_DB="1")
    assert result.returncode != 0
    assert (tmp_path / "bk" / "last_failure").is_file()
    assert int((tmp_path / "cwd_backup.prom").read_text().split()[-1]) > 0  # có dấu thời gian lỗi


@pytest.mark.skipif(os.name == "nt", reason="quyền chỉ-đọc kiểu POSIX")
def test_backup_unwritable_destination(tmp_path: Path) -> None:
    (tmp_path / "bk").mkdir()
    (tmp_path / "bk").chmod(0o500)
    try:
        result = _run(tmp_path, "20261201-010000")
    finally:
        (tmp_path / "bk").chmod(0o700)
    assert result.returncode != 0


def test_backup_keeps_seven(tmp_path: Path) -> None:
    for day in range(1, 10):
        assert _run(tmp_path, f"2026120{day}-010000").returncode == 0
    kept = sorted(p.name for p in (tmp_path / "bk").iterdir() if p.is_dir())
    assert len(kept) == 7 and kept[0] == "20261203-010000" and kept[-1] == "20261209-010000"

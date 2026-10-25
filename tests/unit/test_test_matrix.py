import copy
import subprocess
import sys
from pathlib import Path

from scripts.check_test_matrix import MATRIX, load, render, validate

ROOT = Path(__file__).resolve().parents[2]


def test_spec_is_consistent_and_matrix_in_sync() -> None:
    spec = load()
    assert validate(spec) == []
    assert MATRIX.read_text(encoding="utf-8") == render(spec)


def test_every_scope_ac_has_a_row() -> None:
    spec = load()
    stories = {a["story"] for a in spec["acs"]}
    assert stories == set(spec["scope"])
    assert len(spec["acs"]) == 13  # US-010: 3, US-020: 6, US-022: 4


def test_orphan_tc_is_rejected() -> None:
    spec = copy.deepcopy(load())
    spec["tcs"].append({**spec["tcs"][0], "id": "TC-ORPHAN", "ac": "US-999/AC1"})
    assert any("mồ côi" in e for e in validate(spec))


def test_measurable_ac_without_full_tc_is_rejected() -> None:
    spec = copy.deepcopy(load())
    spec["tcs"] = [t for t in spec["tcs"] if t["ac"] != "US-020/AC3"]
    assert any("US-020/AC3" in e and "chưa có TC full" in e for e in validate(spec))


def test_unmeasurable_ac_cannot_have_full_tc() -> None:
    spec = copy.deepcopy(load())
    spec["tcs"][-1]["covers"] = "full"  # TC-CITE-03 trỏ AC chưa đo được
    assert any("chưa đo được" in e for e in validate(spec))


def test_tc_needs_prewritten_expectations() -> None:
    spec = copy.deepcopy(load())
    spec["tcs"][0]["expected"] = []
    assert any("thiếu kỳ vọng" in e for e in validate(spec))
    spec = copy.deepcopy(load())
    spec["tcs"][0]["expected"][0]["kind"] = "ngoai_tu_vung"
    assert any("ngoài từ vựng" in e for e in validate(spec))


def test_out_of_scope_ac_cannot_have_tc() -> None:
    spec = copy.deepcopy(load())
    spec["tcs"].append({**spec["tcs"][0], "id": "TC-X", "ac": "US-010/AC3"})
    assert any("ngoài phạm vi" in e for e in validate(spec))


def test_cli_exit_code() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_test_matrix.py")],
        capture_output=True, text=True, check=False, timeout=60,
    )  # fmt: skip
    assert result.returncode == 0, result.stdout
    assert result.stdout.startswith("OK: 13 AC, 7 TC")

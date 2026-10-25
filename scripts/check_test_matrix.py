"""Kiểm tra ma trận AC ↔ TC của kiểm thử E2E (tests/e2e/spec.json) và sinh tests/e2e/AC_TC_MATRIX.md.

    python scripts/check_test_matrix.py          # kiểm tra, và báo nếu ma trận md lệch spec
    python scripts/check_test_matrix.py --write  # ghi lại ma trận md

Quy tắc:
  - mọi AC phạm vi có đúng một dòng; AC MEASURABLE phải có ≥ 1 TC `full`;
  - AC NOT_MEASURABLE / OUT_OF_SCOPE có lý do và không có TC `full`; OUT_OF_SCOPE không có TC nào;
  - mọi TC trỏ về một AC có thật (TC mồ côi bị từ chối: loại TC hoặc mở thêm AC);
  - mọi TC có kỳ vọng ghi trước, mỗi kỳ vọng có id/kind/target/op/value và kind nằm trong từ vựng.
"""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "tests" / "e2e" / "spec.json"
MATRIX = ROOT / "tests" / "e2e" / "AC_TC_MATRIX.md"
STATUSES = {"MEASURABLE", "NOT_MEASURABLE", "OUT_OF_SCOPE"}


def load(path: Path = SPEC) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def validate(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    acs = {a["id"]: a for a in spec["acs"]}
    if len(acs) != len(spec["acs"]):
        errors.append("AC trùng id")
    tc_ids = [t["id"] for t in spec["tcs"]]
    if len(set(tc_ids)) != len(tc_ids):
        errors.append("TC trùng id")
    kinds = set(spec["assertion_kinds"])
    for ac in spec["acs"]:
        if ac["story"] not in spec["scope"]:
            errors.append(f"{ac['id']}: story ngoài phạm vi")
        if ac["status"] not in STATUSES:
            errors.append(f"{ac['id']}: trạng thái lạ {ac['status']}")
        if ac["status"] != "MEASURABLE" and not ac.get("reason"):
            errors.append(f"{ac['id']}: thiếu lý do cho trạng thái {ac['status']}")
        if ac["status"] == "MEASURABLE" and not ac.get("testable", "").strip("— "):
            errors.append(f"{ac['id']}: thiếu phát biểu đo được")
    for tc in spec["tcs"]:
        ac = acs.get(tc["ac"])
        if ac is None:
            errors.append(f"{tc['id']}: mồ côi, không có AC {tc['ac']} (loại TC hoặc mở thêm AC)")
            continue
        if tc["covers"] not in {"full", "partial"}:
            errors.append(f"{tc['id']}: covers phải là full hoặc partial")
        if ac["status"] == "OUT_OF_SCOPE":
            errors.append(f"{tc['id']}: AC {ac['id']} ngoài phạm vi, không được có TC")
        if ac["status"] == "NOT_MEASURABLE" and tc["covers"] == "full":
            errors.append(f"{tc['id']}: AC {ac['id']} chưa đo được, TC chỉ được là partial")
        if not tc.get("steps"):
            errors.append(f"{tc['id']}: thiếu bước")
        if not tc.get("expected"):
            errors.append(f"{tc['id']}: thiếu kỳ vọng ghi trước")
        ids: set[str] = set()
        for e in tc.get("expected", []):
            missing = {"id", "kind", "target", "op", "value"} - set(e)
            if missing:
                errors.append(f"{tc['id']}/{e.get('id', '?')}: thiếu {sorted(missing)}")
            if e.get("kind") not in kinds:
                errors.append(f"{tc['id']}/{e.get('id', '?')}: kind ngoài từ vựng")
            if e.get("id") in ids:
                errors.append(f"{tc['id']}: kỳ vọng trùng id {e.get('id')}")
            ids.add(e.get("id", ""))
    for ac in spec["acs"]:
        if ac["status"] == "MEASURABLE":
            full = [t for t in spec["tcs"] if t["ac"] == ac["id"] and t["covers"] == "full"]
            if not full:
                errors.append(f"{ac['id']}: AC đo được nhưng chưa có TC full")
    return errors


def render(spec: dict[str, Any]) -> str:
    rows = ["# Ma trận AC ↔ test case (sinh tự động, không sửa tay)", "",
            "Nguồn: `tests/e2e/spec.json`. Sinh bằng `python scripts/check_test_matrix.py --write`.", "",
            "| AC | Story | Trạng thái | Phát biểu đo được (tạm, chờ PM/PO duyệt) | TC (full) | TC (một phần) |",
            "|---|---|---|---|---|---|"]  # fmt: skip
    for ac in spec["acs"]:
        full = ", ".join(t["id"] for t in spec["tcs"] if t["ac"] == ac["id"] and t["covers"] == "full")
        part = ", ".join(t["id"] for t in spec["tcs"] if t["ac"] == ac["id"] and t["covers"] == "partial")
        text = ac["testable"] if ac["status"] == "MEASURABLE" else f"**{ac['status']}**: {ac.get('reason', '')}"
        rows.append(f"| {ac['id']} | {ac['story']} | {ac['status']} | {text} | {full or '—'} | {part or '—'} |")
    rows += ["", "## Test case và kỳ vọng ghi trước", "",
             "| TC | AC | Hồ sơ | Lặp | Kỳ vọng (PASS khi mọi kỳ vọng đúng) |", "|---|---|---|---|---|"]  # fmt: skip
    for tc in spec["tcs"]:
        rep = tc.get("repeat")
        repeat = f"{rep['times']} phiên, {rep['pass_when']}" if rep else "1"
        expected = "<br>".join(f"{e['id']}: `{e['kind']}` {e['target']} {e['op']} `{e['value']}`" for e in tc["expected"])
        rows.append(f"| {tc['id']} | {tc['ac']} ({tc['covers']}) | {tc['profile']} | {repeat} | {expected} |")
    return "\n".join(rows).replace("|", "|") + "\n"


def main(argv: list[str]) -> int:
    spec = load()
    errors = validate(spec)
    if errors:
        print("\n".join(f"LỖI: {e}" for e in errors))
        return 1
    text = render(spec)
    if "--write" in argv:
        MATRIX.write_text(text, encoding="utf-8", newline="\n")
        print(f"Đã ghi {MATRIX.relative_to(ROOT)}")
        return 0
    if not MATRIX.exists() or MATRIX.read_text(encoding="utf-8") != text:
        print("LỖI: AC_TC_MATRIX.md lệch spec.json; chạy với --write")
        return 1
    print(f"OK: {len(spec['acs'])} AC, {len(spec['tcs'])} TC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""Chạy các TC trong tests/e2e/spec.json bằng agent-browser; ghi reports/<RUN_ID>/. Không sửa code hay spec.

    python scripts/e2e/run_e2e.py <RUN_ID> [TC-ID ...]

Cần stack dev đang chạy và đã SETUP-1 (xem CLAUDE.md). Mỗi TC (và mỗi lượt lặp) dùng một phiên agent-browser riêng.
Thời gian của US-010/AC1 và US-022/AC2 đo trong trang vì mỗi lệnh CLI tốn ≈ 0,5 s.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "tests/e2e/spec.json"
SPEC = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
RUN = sys.argv[1]
ONLY = set(sys.argv[2:])
OUT = ROOT / "reports" / RUN
BASE = SPEC["env"]["base_url"]
PDF = str(ROOT / SPEC["data"]["pdf"]["file"])
QUESTION = SPEC["data"]["question"]
WAIT_ANSWER_S = 120
TCS = {t["id"]: t for t in SPEC["tcs"]}
Rec = dict[str, Any]
LOG: dict[str, list[str]] = {}
EXE = os.path.join(subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, shell=True, check=False).stdout.strip(), "agent-browser", "bin", "agent-browser-win32-x64.exe")


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class Session:
    def __init__(self, tc: str, suffix: str = "") -> None:
        self.tc = tc
        self.name = f"qa-{tc}-{RUN}{suffix}"
        self.env = {**os.environ, "AGENT_BROWSER_SESSION": self.name}
        (OUT / tc).mkdir(parents=True, exist_ok=True)

    def run(self, *args: str, timeout: int = 150) -> tuple[str, float]:
        """Chạy một lệnh; ghi ra file để daemon không giữ ống đầu ra. Trả (đầu ra, ms)."""
        tmp = OUT / self.tc / ".out"
        t = time.perf_counter()
        with tmp.open("wb") as fh:
            subprocess.run([EXE, *args], env=self.env, stdout=fh, stderr=subprocess.STDOUT,
                           timeout=timeout, check=False)
        ms = (time.perf_counter() - t) * 1000
        text = tmp.read_text(encoding="utf-8", errors="replace").strip()
        LOG.setdefault(self.tc, []).append(f"{' '.join(args)[:140]}  -> {ms:.0f} ms | {text[:100]!r}")
        return text, ms

    def snapshot(self, name: str) -> str:
        text, _ = self.run("snapshot", "-i")
        (OUT / self.tc / f"{name}.txt").write_text(text, encoding="utf-8")
        return text

    def login(self, email: str, nxt: str, ready: str) -> None:
        self.run("set", "viewport", "1400", "900")
        self.run("open", f"{BASE}/auth/login?login_hint={email}&next={nxt}")
        self.wait_for(ready, 30)

    def count(self, sel: str) -> int:
        text, _ = self.run("get", "count", sel)
        return int(text) if text.strip().isdigit() else -1

    def wait_for(self, sel: str, timeout_s: float) -> float | None:
        """Chờ tới khi có phần tử; trả ms từ lúc bắt đầu chờ, hoặc None nếu hết giờ."""
        start = time.perf_counter()
        while time.perf_counter() - start < timeout_s:
            if self.count(sel) >= 1:
                return (time.perf_counter() - start) * 1000
            time.sleep(0.2)
        return None

    def texts(self, sel: str) -> list[str]:
        js = f"JSON.stringify([...document.querySelectorAll('{sel}')].map(e=>e.innerText.trim()))"
        text, _ = self.run("eval", js)
        try:
            val = json.loads(text)
            return json.loads(val) if isinstance(val, str) else list(val)
        except ValueError:
            return [f"<không đọc được: {text[:80]}>"]

    def evidence(self) -> list[str]:
        shot = OUT / self.tc / "screenshot.png"
        self.run("screenshot", str(shot).replace("\\", "/"))
        console, _ = self.run("console")
        errors, _ = self.run("errors")
        (OUT / self.tc / "console.txt").write_text(f"{console}\n--- errors\n{errors}\n", encoding="utf-8")
        return [f"{self.tc}/screenshot.png", f"{self.tc}/console.txt"]

    def close(self) -> None:
        self.run("close")


def exp(tc: str) -> dict[str, Rec]:
    return {e["id"]: e for e in TCS[tc]["expected"]}


def asserted(rec: Rec, eid: str, actual: Any, ok: bool) -> None:
    rec["assertions"].append({"id": eid, "actual": actual, "pass": bool(ok)})


def finalize(rec: Rec) -> Rec:
    a = rec["assertions"]
    rec["verdict"] = rec.get("verdict") or ("PASS" if a and all(x["pass"] for x in a) else "FAIL")
    return rec


# ---------------------------------------------------------------------------- các TC
def tc_up_01() -> Rec:
    s = Session("TC-UP-01"); E = exp("TC-UP-01"); rec: Rec = {"assertions": []}
    s.login("minh@congty.vn", "/library", "[data-testid=library]")
    s.snapshot("snapshot-before")
    # Đo trong trang: từ lúc POST /documents trả lời (tải lên xong) tới lúc hàng xuất hiện trong danh sách
    s.run("eval", """window.__m={post:null,row:null};
      const oo=XMLHttpRequest.prototype.open; XMLHttpRequest.prototype.open=function(m,u,...r){
        if(m==='POST'&&String(u).includes('/api/v1/documents')) this.addEventListener('loadend',()=>{ if(window.__m.post===null) window.__m.post=performance.now(); });
        return oo.call(this,m,u,...r); };
      new MutationObserver(()=>{ if(window.__m.row===null&&document.querySelector('[data-testid=doc-row]')) window.__m.row=performance.now(); })
        .observe(document.body,{childList:true,subtree:true}); 'ok'""")
    s.run("upload", "[data-testid=file-input]", PDF)
    t_up = time.perf_counter()
    waited = s.wait_for("[data-testid=doc-row]", 30)
    marks, _ = s.run("eval", "JSON.stringify(window.__m)")
    try:
        m = json.loads(json.loads(marks)) if marks.startswith('"') else json.loads(marks)
    except ValueError:
        m = {}
    elapsed = (m["row"] - m["post"]) if m.get("row") is not None and m.get("post") is not None else None
    rec["cli_elapsed_ms"] = round((time.perf_counter() - t_up) * 1000) if waited is not None else None
    name = s.texts("[data-testid=doc-row] [data-testid=doc-name]")
    badge = s.texts("[data-testid=doc-row] [data-testid=status-badge]")
    s.snapshot("snapshot-after")
    asserted(rec, "E1", None if elapsed is None else round(elapsed), elapsed is not None and elapsed <= E["E1"]["value"])
    asserted(rec, "E2", name[:1], bool(name) and re.search(E["E2"]["value"], name[0]) is not None)
    asserted(rec, "E3", badge[:1], bool(badge) and re.search(E["E3"]["value"], badge[0]) is not None)
    rec["evidence"] = s.evidence(); s.close()
    rec["notes"] = f"Đo trong trang: XHR POST /documents kết thúc → hàng xuất hiện. Tham khảo: theo CLI (gồm ~0,5 s khởi chạy mỗi lệnh) = {rec["cli_elapsed_ms"]} ms."
    return finalize(rec)


def ensure_ready(s: Session) -> bool:
    deadline = time.time() + 180
    while time.time() < deadline:
        s.run("open", f"{BASE}/library"); s.wait_for("[data-testid=library]", 20)
        badges = s.texts("[data-testid=doc-row] [data-testid=status-badge]")
        if any("Sẵn sàng" in b for b in badges):
            return True
        time.sleep(4)
    return False


def ask(s: Session, question: str, new_session: bool = False) -> float | None:
    if new_session:
        s.run("click", "[data-testid=new-session]")
    s.run("fill", "[data-testid=composer-input]", question)
    s.run("click", "[data-testid=send]")
    return s.wait_for("[data-testid=answer-actions]", WAIT_ANSWER_S)


def tc_up_02() -> Rec:
    s = Session("TC-UP-02"); E = exp("TC-UP-02"); rec: Rec = {"assertions": []}
    s.login("lan@congty.vn", "/", "[data-testid=composer-input]")
    if not ensure_ready(s):
        rec["verdict"] = "INCONCLUSIVE"; rec["notes"] = "text_12p.pdf không Sẵn sàng sau 180 s"
        rec["evidence"] = s.evidence(); s.close(); return rec
    s.run("open", f"{BASE}/"); s.wait_for("[data-testid=composer-input]", 20)
    s.snapshot("snapshot-before")
    done = ask(s, QUESTION)
    chips = s.texts("[data-testid=citation]")
    s.snapshot("snapshot-after")
    if done is None:
        rec["verdict"] = "INCONCLUSIVE"; rec["notes"] = f"Không có câu trả lời sau {WAIT_ANSWER_S} s"
    asserted(rec, "E1", len(chips), len(chips) >= E["E1"]["value"])
    asserted(rec, "E2", chips, any(re.search(E["E2"]["value"], c) for c in chips))
    rec["evidence"] = s.evidence(); s.close()
    return finalize(rec)


def tc_qa_01() -> Rec:
    E = exp("TC-QA-01"); rec: Rec = {"assertions": [], "runs": []}
    for i in range(1, TCS["TC-QA-01"]["repeat"]["times"] + 1):
        s = Session("TC-QA-01", f"-r{i}"); run: Rec = {"assertions": []}
        s.login("lan@congty.vn", "/", "[data-testid=composer-input]")
        s.snapshot(f"snapshot-before-r{i}")
        done = ask(s, QUESTION, new_session=True)
        answer = s.texts("[data-testid=answer-text]")
        chips = s.count("[data-testid=citation]")
        s.snapshot(f"snapshot-after-r{i}")
        text = answer[-1] if answer else ""
        asserted(run, "E1", text[:200], done is not None and re.search(E["E1"]["value"], text) is not None)
        asserted(run, "E2", chips, chips >= E["E2"]["value"])
        run["evidence"] = s.evidence(); s.close()
        rec["runs"].append(run)
        rec["assertions"] += [{**a, "id": f"r{i}-{a['id']}"} for a in run["assertions"]]
    return finalize(rec)


def tc_qa_02() -> Rec:
    s = Session("TC-QA-02"); E = exp("TC-QA-02"); rec: Rec = {"assertions": []}
    s.login("lan@congty.vn", "/", "[data-testid=composer-input]")
    s.snapshot("snapshot-before")
    s.run("network", "requests", "--clear")
    s.run("fill", "[data-testid=composer-input]", "   ")
    enabled, _ = s.run("is", "enabled", "[data-testid=send]")
    s.run("press", "Enter")
    time.sleep(1.5)
    users = s.count("[data-testid=user-message]")
    reqs, _ = s.run("network", "requests", "--filter", "/messages")
    posts = [l for l in reqs.splitlines() if "POST" in l and "/messages" in l]
    s.snapshot("snapshot-after")
    asserted(rec, "E1", "enabled" if enabled.strip() == "true" else "disabled", enabled.strip() == "false")
    asserted(rec, "E2", users, users == E["E2"]["value"])
    asserted(rec, "E3", len(posts), len(posts) == E["E3"]["value"])
    rec["evidence"] = s.evidence(); s.close()
    return finalize(rec)


def answer_session(tc: str) -> tuple[Session, float | None, Rec]:
    s = Session(tc); s.login("lan@congty.vn", "/", "[data-testid=composer-input]")
    s.snapshot("snapshot-before")
    return s, ask(s, QUESTION), {"assertions": []}


def tc_cite_01() -> Rec:
    s, done, rec = answer_session("TC-CITE-01"); E = exp("TC-CITE-01")
    chips = s.texts("[data-testid=citation]"); answer = s.texts("[data-testid=answer-text]")
    s.snapshot("snapshot-after")
    text = answer[-1] if answer else ""
    if done is None:
        rec["verdict"] = "INCONCLUSIVE"; rec["notes"] = f"Không có câu trả lời sau {WAIT_ANSWER_S} s"
    asserted(rec, "E1", len(chips), len(chips) >= E["E1"]["value"])
    asserted(rec, "E2", chips, bool(chips) and all(re.search(E["E2"]["value"], c) for c in chips))
    asserted(rec, "E3", text[:200], re.search(E["E3"]["value"], text) is None)
    rec["evidence"] = s.evidence(); s.close()
    return finalize(rec)


def tc_cite_02() -> Rec:
    s, done, rec = answer_session("TC-CITE-02"); E = exp("TC-CITE-02")
    chips = s.texts("[data-testid=citation]")
    m = re.search(r"tr\. (\d+)\]", chips[0]) if chips else None
    if done is None or not m:
        rec["verdict"] = "INCONCLUSIVE"; rec["notes"] = f"Không lấy được thẻ trích dẫn (chips={chips})"
        rec["evidence"] = s.evidence(); s.close(); return rec
    n = m.group(1)
    # Đo trong trang: từ lúc bấm thẻ tới lúc khung xem xuất hiện
    res, _ = s.run("eval", """new Promise(r=>{const t=performance.now();
      document.querySelector('[data-testid=citation]').click();
      const f=()=>{ if(document.querySelector('[data-testid=source-viewer]')) r(JSON.stringify({ms:performance.now()-t}));
        else if(performance.now()-t>10000) r(JSON.stringify({ms:null})); else requestAnimationFrame(f); }; f(); })""")
    try:
        val = json.loads(res); ms = (json.loads(val) if isinstance(val, str) else val)["ms"]
    except (ValueError, KeyError, TypeError):
        ms = None
    got = s.wait_for("[data-testid=source-viewer]", 10) if ms is not None else None
    elapsed = ms if ms is not None else 1e9
    name = s.texts("[data-testid=viewer-name]"); page = s.texts("[data-testid=viewer-page]")
    src, _ = s.run("eval", "document.querySelector('[data-testid=viewer-iframe]')?.getAttribute('src') ?? ''")
    src = src.strip().strip('"')
    s.snapshot("snapshot-after")
    asserted(rec, "E1", round(elapsed), got is not None and elapsed <= E["E1"]["value"])
    asserted(rec, "E2", name[:1], bool(name) and re.search(E["E2"]["value"], name[0]) is not None)
    want_page = E["E3"]["value"].replace("{N}", n)
    asserted(rec, "E3", page[:1], bool(page) and page[0] == want_page)
    asserted(rec, "E4", src, re.search(E["E4"]["value"].replace("{N}", n), src) is not None)
    rec["notes"] = f"N (từ thẻ) = {n}. Thời gian đo trong trang (JS click → khung xem xuất hiện); không đọc được nội dung trong iframe."
    rec["evidence"] = s.evidence(); s.close()
    return finalize(rec)


def tc_cite_03() -> Rec:
    s, done, rec = answer_session("TC-CITE-03"); E = exp("TC-CITE-03")
    chips = s.texts("[data-testid=citation]")
    s.snapshot("snapshot-after")
    if done is None:
        rec["verdict"] = "INCONCLUSIVE"; rec["notes"] = f"Không có câu trả lời sau {WAIT_ANSWER_S} s"
    asserted(rec, "E1", chips, any(re.search(E["E1"]["value"], c) for c in chips))
    rec["notes"] = "Mẫu n=1, không đóng US-022/AC3."
    rec["evidence"] = s.evidence(); s.close()
    return finalize(rec)


ORDER = [("TC-UP-01", tc_up_01), ("TC-UP-02", tc_up_02), ("TC-QA-01", tc_qa_01), ("TC-QA-02", tc_qa_02),
         ("TC-CITE-01", tc_cite_01), ("TC-CITE-02", tc_cite_02), ("TC-CITE-03", tc_cite_03)]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    started = now()
    results = []
    for tc_id, fn in ORDER:
        if ONLY and tc_id not in ONLY:
            continue
        t = time.time()
        try:
            rec = fn()
        except Exception as exc:  # noqa: BLE001 - lỗi bộ chạy là INCONCLUSIVE, không phải FAIL của sản phẩm
            rec = {"verdict": "INCONCLUSIVE", "assertions": [], "notes": f"Lỗi bộ chạy: {type(exc).__name__}: {exc}"}
        rec.update({"id": tc_id, "ac": TCS[tc_id]["ac"], "covers": TCS[tc_id]["covers"], "seconds": round(time.time() - t, 1)})
        results.append(rec)
        print(f"{tc_id}: {rec['verdict']} ({rec['seconds']}s) {[ (a['id'], a['pass']) for a in rec['assertions']]}", flush=True)
    sha = hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    (OUT / "results.json").write_text(json.dumps(
        {"run_id": RUN, "commit": commit, "profile": "ollama", "spec_sha256": sha, "started": started,
         "finished": now(), "tcs": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "commands.log").write_text("\n".join(f"## {k}\n" + "\n".join(v) for k, v in LOG.items()), encoding="utf-8")

/*
 * S-03 Hỏi đáp (CMP-04..CMP-13, CMP-23), S-05 Khung xem nguồn (CMP-09), S-06 Lịch sử.
 * Nội dung câu trả lời là DỮ LIỆU MINH HỌA, không có AI thật phía sau.
 */
(function () {
  "use strict";
  var $ = CWD.$, $$ = CWD.$$, esc = CWD.esc, ICON = CWD.ICON;
  var MAX_CHARS = 2000;
  var HD = "HD_ABC_2026.pdf", PL = "PL2_ABC.pdf", BG = "BangGia_2026.pdf";

  /* ---------- Dữ liệu minh họa ---------- */
  function cite(doc, page, snippet) { return { cite: { doc: doc, page: page, snippet: snippet } }; }
  var ANSWERS = [
    { match: /thời hạn|bao lâu|gia hạn/i, q: "Thời hạn hợp đồng với công ty X là bao lâu?", segs: [
      "Hợp đồng với công ty X có thời hạn 24 tháng, bắt đầu từ 01/03/2026. ", cite(HD, 12, "…thời hạn hợp đồng là 24 tháng kể từ ngày 01/03/2026…"), " ",
      "¶", "Phụ lục 2 cho phép gia hạn thêm 12 tháng nếu thông báo trước 60 ngày. ", cite(PL, 3, "…các bên có thể gia hạn thêm 12 tháng nếu thông báo trước 60 ngày…")
    ] },
    { match: /thanh toán|giá trị|giá\b|chi phí/i, q: "Điều khoản thanh toán trong hợp đồng X là gì?", segs: [
      "Theo hợp đồng, thanh toán chia làm hai đợt: 50% khi ký và 50% khi nghiệm thu. ", cite(HD, 20, "…50% giá trị hợp đồng được thanh toán khi ký…"), " ",
      "¶", "Bảng giá 2026 áp dụng đơn giá đã bao gồm thuế. ", cite(BG, 2, "…đơn giá đã bao gồm thuế giá trị gia tăng…")
    ] },
    { match: /rủi ro/i, q: "Rủi ro nào được nêu trong hợp đồng?", segs: [
      "Các rủi ro được nêu gồm chậm tiến độ bàn giao và thay đổi phạm vi công việc. ", cite(HD, 31, "…chậm tiến độ quá 15 ngày bị phạt 0,1% mỗi ngày…")
    ] }
  ];
  var FALLBACK = { segs: ["Nội dung liên quan được nêu trong phần phạm vi công việc của hợp đồng. ", cite(HD, 5, "…phạm vi công việc gồm thiết kế, triển khai và bàn giao…")] };
  var NOT_FOUND_RE = /giá vàng|thời tiết|bóng đá|ngoài phạm vi|bitcoin/i;
  var SUGGESTIONS = [
    "Điều khoản thanh toán trong hợp đồng X là gì?", "Thời hạn hợp đồng với công ty X là bao lâu?",
    "Rủi ro nào được nêu trong hợp đồng?", "Phạm vi công việc của hợp đồng X gồm những gì?", "Bảng giá 2026 áp dụng cho những hạng mục nào?"
  ];
  var HISTORY = [
    { group: "Hôm nay", q: "Thời hạn hợp đồng với công ty X là bao lâu?" },
    { group: "7 ngày qua", q: "Điều khoản thanh toán trong hợp đồng X là gì?" },
    { group: "7 ngày qua", q: "Rủi ro nào được nêu trong hợp đồng?" },
    { group: "Cũ hơn", q: "Phạm vi công việc của hợp đồng X gồm những gì?" }
  ];

  /* ---------- Trạng thái ---------- */
  var messages = [];          // {q, spec}
  var scope = [];             // rỗng = tất cả tài liệu
  var busy = null;            // điều khiển câu trả lời đang tạo
  var viewerDoc = null, viewerPage = 1, viewerOpener = null, viewerFail = false;
  var deletedDocs = {};
  var skipSeed = false;        // không nạp hội thoại mẫu khi chuyển sang "data" do người dùng gửi câu hỏi

  function readyDocs() { return CWD.DOCS.filter(function (d) { return d.status === "ready"; }); }
  function pendingCount() { return CWD.DOCS.filter(function (d) { return ["processing", "ocr", "uploading"].indexOf(d.status) !== -1; }).length; }
  function nfmt(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
  function srSay(t) { $("#sr-status").textContent = t; }
  function scopeCount() { return scope.length ? scope.length : readyDocs().length; }
  function pickAnswer(q) { for (var i = 0; i < ANSWERS.length; i++) { if (ANSWERS[i].match.test(q)) { return ANSWERS[i]; } } return FALLBACK; }
  function titleOf(q) { return q.length > 60 ? q.slice(0, 60) + "…" : q; } // tiêu đề phiên = 60 ký tự đầu (DEC-002)
  function scrollDown() { var s = $("#scroll"); s.scrollTop = s.scrollHeight; }

  /* ---------- Thẻ trích dẫn (CMP-08) ---------- */
  function citeEl(c) {
    var b = document.createElement("button");
    b.className = "citation";
    var gone = !!deletedDocs[c.doc];
    b.setAttribute("aria-label", "Trích dẫn: " + c.doc + ", trang " + c.page + (gone ? ", tài liệu đã bị xóa" : ", mở trang nguồn"));
    b.dataset.doc = c.doc;
    b.innerHTML = '<span class="cit-label">' + esc(CWD.shortName(c.doc)) + " – tr. " + c.page + '</span><span class="tip" aria-hidden="true">' +
      (gone ? "Tài liệu đã bị xóa" : esc(c.snippet.slice(0, 200))) + "</span>";
    if (gone) { b.classList.add("is-deleted"); b.setAttribute("aria-disabled", "true"); }
    b.onclick = function () { if (!deletedDocs[c.doc]) { openViewer(c.doc, c.page, b); } };
    return b;
  }

  /* ---------- Dựng khối câu trả lời ---------- */
  function newAnswerShell() {
    var wrap = document.createElement("div");
    wrap.className = "msg-ai";
    return wrap;
  }
  function addUser(q) {
    var d = document.createElement("div");
    d.className = "msg-user";
    d.textContent = q;
    $("#log").appendChild(d);
    scrollDown();
    return d;
  }
  function actionsEl(q, notFound) {
    var a = document.createElement("div");
    a.className = "answer-actions";
    var html = "";
    if (!notFound) { html += '<button class="btn btn-sm" data-copy>' + ICON.copy + " Sao chép</button>"; }
    html += '<button class="btn btn-sm" data-rate="up" aria-pressed="false" aria-label="Hữu ích">' + ICON.up2 + '</button>' +
      '<button class="btn btn-sm" data-rate="down" aria-pressed="false" aria-label="Chưa tốt">' + ICON.down2 + "</button>";
    if (notFound) { html += '<button class="btn btn-sm" data-retry>Hỏi lại</button>'; }
    a.innerHTML = html;
    var copy = $("[data-copy]", a);
    if (copy) { copy.onclick = function () { copyAnswer(a.closest(".msg-ai")); }; }
    $$("[data-rate]", a).forEach(function (b) {
      b.onclick = function () {
        if (b.dataset.rate === "up") { setRating(a, "up"); CWD.toast("Đã ghi nhận đánh giá"); }
        else { reasonDialog(a); }
      };
    });
    var r = $("[data-retry]", a);
    if (r) { r.onclick = function () { rerun(a.closest(".msg-ai"), q); }; }
    return a;
  }
  function setRating(a, v) {
    $$("[data-rate]", a).forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.rate === v)); b.style.background = b.dataset.rate === v ? "var(--color-info-bg)" : ""; });
  }
  function reasonDialog(a) {
    CWD.openDialog(
      '<h2 id="rate-title">Câu trả lời chưa tốt ở điểm nào? (tùy chọn)</h2>' +
      '<fieldset style="border:0;padding:0;margin:0"><legend class="sr-only">Lý do</legend><div class="radio-row">' +
      ["Sai thông tin", "Trích dẫn sai", "Thiếu ý", "Khác"].map(function (t, i) { return '<label><input type="radio" name="reason" value="' + i + '"> ' + t + "</label>"; }).join("") +
      '</div></fieldset><div class="dlg-actions"><button class="btn" data-skip>Bỏ qua</button><button class="btn btn-primary" data-send>Gửi</button></div>',
      function (dlg) {
        dlg.setAttribute("aria-labelledby", "rate-title");
        function done() { setRating(a, "down"); dlg.close(); CWD.toast("Đã ghi nhận đánh giá"); }
        $("[data-skip]", dlg).onclick = done;
        $("[data-send]", dlg).onclick = done;
      });
  }
  function copyAnswer(wrap) {
    var body = $(".answer-body", wrap);
    var cites = [];
    $$(".citation", body).forEach(function (c) { var t = c.getAttribute("aria-label").replace(/^Trích dẫn: /, "").replace(/, mở trang nguồn$/, ""); if (cites.indexOf(t) === -1) { cites.push(t); } });
    var text = body.innerText.replace(/\s+\n/g, "\n").trim() + (cites.length ? "\n\nNguồn:\n- " + cites.join("\n- ") : "");
    function ok() { CWD.toast("Đã sao chép"); }
    function fallback() {
      var t = document.createElement("textarea"); t.value = text; document.body.appendChild(t); t.select();
      try { document.execCommand("copy"); ok(); } catch (e) { CWD.toast("Không sao chép được", { error: true }); }
      t.remove();
    }
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(ok, fallback); } else { fallback(); }
  }
  function notice(kind, text, btnLabel, onClick) {
    var n = document.createElement("div");
    n.className = "msg-notice is-" + kind;
    n.setAttribute("role", kind === "danger" ? "alert" : "status");
    n.innerHTML = "<span>" + (kind === "neutral" ? "" : ICON.warn + " ") + esc(text) + "</span>";
    if (btnLabel) {
      var b = document.createElement("button");
      b.className = "btn btn-sm";
      b.textContent = btnLabel;
      b.onclick = onClick;
      n.appendChild(b);
    }
    return n;
  }
  function notFoundEl() {
    var n = document.createElement("div");
    n.className = "msg-not-found";
    n.innerHTML = "<strong>" + ICON.search + " Không tìm thấy thông tin này trong các tài liệu hiện có.</strong>" +
      '<span class="caption">Thử diễn đạt khác, hoặc kiểm tra tài liệu đã được tải lên chưa.</span>';
    return n;
  }

  /* ---------- Render câu trả lời hoàn chỉnh (lịch sử) ---------- */
  function renderComplete(q, spec) {
    addUser(q);
    var wrap = newAnswerShell();
    var body = document.createElement("div");
    body.className = "answer-body";
    fillBody(body, spec.segs);
    wrap.appendChild(body);
    wrap.appendChild(actionsEl(q, false));
    $("#log").appendChild(wrap);
  }
  function fillBody(body, segs) {
    var p = document.createElement("p");
    body.appendChild(p);
    segs.forEach(function (s) {
      if (s === "¶") { p = document.createElement("p"); body.appendChild(p); }
      else if (typeof s === "string") { p.appendChild(document.createTextNode(s)); }
      else { p.appendChild(citeEl(s.cite)); }
    });
  }

  /* ---------- Gửi câu hỏi, tạo câu trả lời dần (SSE giả lập) ---------- */
  function wait(ms, ctl) { return new Promise(function (res) { setTimeout(res, ctl && ctl.fast ? 0 : ms); }); }

  async function ask(q, mode, reuseUserEl) {
    if (busy) { return; }
    if (!reuseUserEl) { addUser(q); }
    var wrap = newAnswerShell();
    $("#log").appendChild(wrap);
    var ctl = { stopped: false, fast: CWD.reduceMotion };
    busy = ctl;
    updateComposer();

    // Searching: phản hồi cục bộ ≤ 300 ms (UX-08)
    var search = document.createElement("div");
    search.className = "msg-searching";
    search.innerHTML = ICON.spin + "<span>Đang tìm trong " + scopeCount() + " tài liệu…</span>";
    wrap.appendChild(search);
    scrollDown();
    srSay("Đang tìm trong " + scopeCount() + " tài liệu");

    if (mode === "slow") { // EC-06: mô phỏng 15 s và 60 s bằng 1,5 s và 4 s
      await wait(1500, ctl);
      $("span", search).textContent = "Câu hỏi đang mất nhiều thời gian hơn bình thường…";
      await wait(2500, ctl);
      search.remove();
      wrap.appendChild(notice("danger", "Không thể trả lời lúc này.", "Thử lại", function () { rerun(wrap, q); }));
      finish(); return;
    }
    await wait(900, ctl);
    if (ctl.stopped) { search.remove(); wrap.appendChild(notice("neutral", "Đã dừng", "Hỏi lại", function () { rerun(wrap, q); })); finish(); return; }

    if (mode === "failed") { // EC-07
      search.remove();
      wrap.appendChild(notice("danger", "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút.", "Thử lại", function () { rerun(wrap, q); }));
      srSay("Dịch vụ hỏi đáp tạm thời gián đoạn");
      finish(); return;
    }
    if (mode === "notfound" || (!mode && NOT_FOUND_RE.test(q))) { // EC-13, US-023
      search.remove();
      wrap.appendChild(notFoundEl());
      wrap.appendChild(actionsEl(q, true));
      srSay("Không tìm thấy thông tin này trong các tài liệu hiện có");
      finish(); return;
    }

    search.remove();
    var spec = pickAnswer(q);
    var body = document.createElement("div");
    body.className = "answer-body";
    wrap.appendChild(body);
    var p = document.createElement("p");
    body.appendChild(p);
    var caret = document.createElement("span");
    caret.className = "caret";
    p.appendChild(caret);
    var cites = 0, interruptAt = mode === "interrupted" ? Math.ceil(spec.segs.length / 2) : -1;

    for (var i = 0; i < spec.segs.length; i++) {
      if (ctl.stopped) { break; }
      if (i === interruptAt) { break; }
      var s = spec.segs[i];
      if (s === "¶") { p.removeChild(caret); p = document.createElement("p"); body.appendChild(p); p.appendChild(caret); continue; }
      if (typeof s === "string") {
        var words = s.split(/(?<=\s)/);
        for (var w = 0; w < words.length; w++) {
          if (ctl.stopped) { break; }
          p.insertBefore(document.createTextNode(words[w]), caret);
          scrollDown();
          await wait(40, ctl);
        }
      } else {
        p.insertBefore(citeEl(s.cite), caret);
        cites++;
        scrollDown();
        await wait(120, ctl);
      }
    }
    caret.remove();
    scrollDown();
    if (ctl.stopped) { wrap.appendChild(notice("neutral", "Đã dừng", "Hỏi lại", function () { rerun(wrap, q); })); finish(); return; }
    if (interruptAt !== -1) { // EC-04
      wrap.appendChild(notice("warning", "Mất kết nối – câu trả lời chưa đầy đủ.", "Hỏi lại", function () { rerun(wrap, q); }));
      srSay("Mất kết nối, câu trả lời chưa đầy đủ");
      finish(); return;
    }
    wrap.appendChild(actionsEl(q, false));
    srSay("Câu trả lời đã hoàn tất, " + cites + " trích dẫn"); // thông báo khi xong, không đọc từng chữ
    finish();
    addHistory(q);
  }
  function finish() { busy = null; updateComposer(); scrollDown(); }
  function rerun(wrap, q) {
    if (busy) { return; }
    wrap.remove();
    ask(q, null, true);
  }

  /* ---------- Ô nhập (CMP-05) ---------- */
  var input = $("#composer-input"), sendBtn = $("#send"), counter = $("#counter");
  function updateComposer() {
    var len = input.value.length, state = CWD.getState();
    var over = len > MAX_CHARS, empty = input.value.trim() === "";
    counter.textContent = nfmt(len) + "/" + nfmt(MAX_CHARS);
    counter.classList.toggle("is-over", over);
    var blocked = state === "emptylib" || state === "loading";
    input.disabled = blocked;
    input.placeholder = state === "emptylib" ? "Kho chưa có tài liệu." : "Hỏi về nội dung tài liệu…";
    if (busy) {
      sendBtn.innerHTML = ICON.stop + " Dừng";
      sendBtn.disabled = false;
      sendBtn.dataset.mode = "stop";
    } else {
      sendBtn.textContent = "Gửi";
      sendBtn.dataset.mode = "send";
      sendBtn.disabled = blocked || over || empty || state === "error"; // vô hiệu khi không hợp lệ (UX-08)
    }
    var pend = pendingCount();
    var note = $("#processing-note");
    note.hidden = !(pend > 0 && state !== "emptylib");
    note.textContent = pend + " tài liệu đang được xử lý, chưa dùng để trả lời.";
  }
  input.addEventListener("input", function () {
    CWD.store("cwd.draft", input.value || null); // bản nháp chỉ ở bộ nhớ phiên (DD-07)
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 160) + "px";
    updateComposer();
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit(); }
  });
  sendBtn.onclick = function () {
    if (busy) { busy.stopped = true; return; }
    submit();
  };
  function submit(textOverride, mode) {
    var q = (textOverride || input.value).trim();
    if (!q || q.length > MAX_CHARS || busy) { return; }
    if (CWD.getState() !== "data") { skipSeed = true; CWD.setState("data"); skipSeed = false; }
    input.value = ""; CWD.store("cwd.draft", null); input.style.height = "auto";
    messages.push({ q: q });
    updateComposer();
    ask(q, mode);
  }

  /* ---------- Phạm vi tài liệu (CMP-11) ---------- */
  function renderScope() {
    var list = $("#scope-list");
    var docs = readyDocs();
    list.innerHTML = '<label><input type="checkbox" id="scope-all" ' + (scope.length ? "" : "checked") + "> Tất cả tài liệu</label>" +
      docs.map(function (d) { return '<label><input type="checkbox" data-doc="' + d.id + '" ' + (scope.indexOf(d.id) !== -1 ? "checked" : "") + "> " + esc(d.name) + "</label>"; }).join("");
    $("#scope-all").onchange = function () { scope = []; renderScope(); updateScopeLabel(); };
    $$("[data-doc]", list).forEach(function (c) {
      c.onchange = function () {
        var i = scope.indexOf(c.dataset.doc);
        if (c.checked && i === -1) { scope.push(c.dataset.doc); }
        if (!c.checked && i !== -1) { scope.splice(i, 1); }
        if (scope.length === docs.length) { scope = []; }
        renderScope(); updateScopeLabel();
      };
    });
  }
  function updateScopeLabel() {
    $("#scope-btn").innerHTML = (scope.length ? "Đang hỏi trong " + scope.length + " tài liệu" : "Phạm vi: Tất cả tài liệu") + ' <span aria-hidden="true">▾</span>';
  }
  $("#scope-btn").onclick = function () {
    var l = $("#scope-list");
    l.hidden = !l.hidden;
    this.setAttribute("aria-expanded", String(!l.hidden));
    if (!l.hidden) { renderScope(); }
  };

  /* ---------- Khung xem nguồn (S-05) ---------- */
  function docByName(n) { return CWD.DOCS.filter(function (d) { return d.name === n; })[0]; }
  function openViewer(name, page, opener) {
    viewerDoc = docByName(name); viewerPage = page; viewerOpener = opener || viewerOpener; viewerFail = false;
    $("#shell").classList.add("has-viewer");
    $("#viewer-title").textContent = name;
    $("#viewer-title").title = name;
    renderViewerLoading();
    setTimeout(renderViewerPage, CWD.reduceMotion ? 0 : 500); // mở trang nguồn ≤ 3 s (C-01)
    $("#viewer-close").focus();
  }
  function renderViewerLoading() {
    $("#viewer-body").innerHTML = '<span class="badge badge-info">' + ICON.spin + "Đang mở trang…</span>";
    $("#pg-label").textContent = "";
  }
  function renderViewerPage() {
    if (!$("#shell").classList.contains("has-viewer")) { return; }
    var total = viewerDoc ? viewerDoc.pages : 1;
    if (viewerFail) {
      $("#viewer-body").innerHTML = '<div class="state-box is-error" role="alert" style="width:100%"><strong>Không mở được trang.</strong><button class="btn" id="viewer-retry">Thử lại</button></div>';
      $("#viewer-retry").onclick = function () { viewerFail = false; renderViewerLoading(); setTimeout(renderViewerPage, 400); };
      return;
    }
    $("#pg-label").textContent = "Trang " + viewerPage + " / " + total;
    $("#pg-prev").disabled = viewerPage <= 1;
    $("#pg-next").disabled = viewerPage >= total;
    var lines = "";
    for (var i = 0; i < 14; i++) { lines += '<div class="pdf-line ' + ["w90", "w70", "w90", "w50", "w90", "w70"][i % 6] + (i === 6 || i === 7 ? " hl" : "") + '"></div>'; }
    $("#viewer-body").innerHTML = '<div class="pdf-page" role="img" aria-label="Trang ' + viewerPage + ' của ' + esc(viewerDoc.name) + ' (minh họa)"><div class="pdf-head">' + esc(viewerDoc.name) + " · trang " + viewerPage + "</div>" + lines + "</div>";
  }
  function closeViewer() {
    if (!$("#shell").classList.contains("has-viewer")) { return false; }
    $("#shell").classList.remove("has-viewer");
    if (viewerOpener && document.contains(viewerOpener)) { viewerOpener.focus(); }
    return true;
  }
  $("#viewer-close").onclick = closeViewer;
  $("#pg-prev").onclick = function () { if (viewerPage > 1) { viewerPage--; renderViewerPage(); } };
  $("#pg-next").onclick = function () { if (viewerDoc && viewerPage < viewerDoc.pages) { viewerPage++; renderViewerPage(); } };

  /* ---------- Lịch sử (S-06, CMP-13) ---------- */
  function addHistory(q) {
    if (!HISTORY.some(function (h) { return h.q === q; })) { HISTORY.unshift({ group: "Hôm nay", q: q }); }
    renderHistory();
  }
  function renderHistory() {
    var h = $("#history"), state = CWD.getState();
    if (state === "loading") { h.innerHTML = '<div class="skeleton" style="height:20px;margin:8px 0"></div><div class="skeleton" style="height:20px;margin:8px 0"></div><div class="skeleton" style="height:20px;margin:8px 0"></div>'; return; }
    if (state === "error") { h.innerHTML = '<p class="caption muted">Không tải được lịch sử.</p><button class="btn btn-sm" id="hist-retry">Thử lại</button>'; $("#hist-retry").onclick = function () { CWD.setState("data"); }; return; }
    if (state === "welcome" || state === "emptylib" || !HISTORY.length) { h.innerHTML = '<p class="caption muted">Chưa có phiên nào</p>'; return; }
    var groups = ["Hôm nay", "7 ngày qua", "Cũ hơn"], html = "";
    groups.forEach(function (g) {
      var items = HISTORY.filter(function (x) { return x.group === g; });
      if (!items.length) { return; }
      html += '<div class="history-group"><h3>' + g + "</h3>" + items.map(function (x) {
        return '<button class="history-item" data-q="' + esc(x.q) + '" title="' + esc(x.q) + '">' + esc(titleOf(x.q)) + "</button>";
      }).join("") + "</div>";
    });
    h.innerHTML = html;
    $$(".history-item", h).forEach(function (b) {
      b.onclick = function () { openSession(b.dataset.q); $$(".history-item").forEach(function (x) { x.removeAttribute("aria-current"); }); b.setAttribute("aria-current", "true"); };
    });
  }
  function openSession(q) {
    if (busy) { return; }
    $("#log").innerHTML = "";
    messages = [{ q: q }];
    renderComplete(q, pickAnswer(q));
    if (CWD.getState() !== "data") { CWD.setState("data"); }
    closeViewer();
  }
  $("#new-session").onclick = function () {
    if (busy) { busy.stopped = true; }
    $("#log").innerHTML = ""; messages = []; closeViewer();
    CWD.setState(readyDocs().length ? "welcome" : "emptylib");
  };

  /* ---------- Gợi ý câu hỏi mẫu (CMP-23, US-031) ---------- */
  function renderSuggestions() {
    var pool = SUGGESTIONS.slice().sort(function () { return Math.random() - 0.5; }).slice(0, 3); // 3 gợi ý ngẫu nhiên (DEC-018)
    $("#suggest-list").innerHTML = pool.map(function (s) { return '<button class="suggest">' + esc(s) + "</button>"; }).join("");
    $$(".suggest").forEach(function (b) { b.onclick = function () { submit(b.textContent); }; });
  }

  /* ---------- Khởi tạo ---------- */
  function onState(state) {
    $("#offline").hidden = state !== "error";
    var n = readyDocs().length;
    $("#lib-count").textContent = CWD.DOCS.length + " tài liệu";
    $("#welcome-sub").textContent = "Kho đang có " + n + " tài liệu sẵn sàng. Hỏi bất cứ điều gì về nội dung tài liệu, ví dụ:";
    $("#welcome-title").textContent = "Xin chào " + CWD.ROLES[CWD.getRole()].user + "!";
    if (state === "welcome") { $("#log").innerHTML = ""; messages = []; renderSuggestions(); }
    if (state === "data" && !skipSeed && !$("#log").children.length) {
      HISTORY[0] && renderComplete(HISTORY[0].q, pickAnswer(HISTORY[0].q));
    }
    renderHistory();
    updateComposer();
  }
  CWD.onState(onState);
  CWD.init({
    page: "chat",
    roles: ["bd", "tn", "qt"],
    defaultState: "data",
    states: [
      { id: "loading", label: "Đang tải" }, { id: "welcome", label: "Chưa có hội thoại" }, { id: "emptylib", label: "Kho trống (EC-01)" },
      { id: "data", label: "Có hội thoại" }, { id: "error", label: "Mất kết nối (EC-05)" }, { id: "restricted", label: "Hạn chế quyền → S-02" }
    ],
    extra: [
      { label: "Không tìm thấy", run: function () { submit("Giá vàng hôm nay là bao nhiêu?", "notfound"); } },
      { label: "Đứt giữa chừng (EC-04)", run: function () { submit("Thời hạn hợp đồng với công ty X là bao lâu?", "interrupted"); } },
      { label: "Lỗi dịch vụ (EC-07)", run: function () { submit("Điều khoản thanh toán trong hợp đồng X là gì?", "failed"); } },
      { label: "Quá chậm (EC-06)", run: function () { submit("Rủi ro nào được nêu trong hợp đồng?", "slow"); } },
      { label: "Lỗi mở trang nguồn", run: function () { if (viewerDoc) { viewerFail = true; renderViewerPage(); } else { CWD.toast("Hãy bấm một thẻ trích dẫn trước"); } } },
      { label: "Tài liệu bị xóa (EC-14)", run: function () { deletedDocs[PL] = true; $$('.citation[data-doc="' + PL + '"]').forEach(function (c) { var n = c.cloneNode(true); c.replaceWith(citeEl({ doc: PL, page: 3, snippet: "" })); }); CWD.toast("Tài liệu PL2_ABC.pdf đã bị xóa"); } }
    ],
    onRole: function () { onState(CWD.getState()); }
  });
  var draft = CWD.store("cwd.draft");
  if (draft) { input.value = draft; }
  updateComposer();
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (!$("#scope-list").hidden) { $("#scope-list").hidden = true; $("#scope-btn").setAttribute("aria-expanded", "false"); $("#scope-btn").focus(); return; }
      closeViewer();
    }
    if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !input.disabled) { e.preventDefault(); input.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".scope-wrap") && !$("#scope-list").hidden) { $("#scope-list").hidden = true; $("#scope-btn").setAttribute("aria-expanded", "false"); }
  });
})();

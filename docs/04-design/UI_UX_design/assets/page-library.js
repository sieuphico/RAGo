/* S-04 Kho tài liệu (CMP-14, CMP-15, CMP-16, CMP-17) */
(function () {
  "use strict";
  var $ = CWD.$, $$ = CWD.$$, esc = CWD.esc, fmt = CWD.fmt, ICON = CWD.ICON;
  var docs = CWD.DOCS.map(function (d) { return Object.assign({}, d); });
  var sortKey = "at", sortDir = "desc", query = "";
  var MAX_FILES = 10, MAX_BYTES = 50 * 1024 * 1024;

  function announce(text) { $("#sr-live").textContent = text; }

  function canDelete(d) { var r = CWD.getRole(); return r === "qt" || (r === "tn" && d.uploader === "Minh"); }

  /* ---------- Hiển thị bảng ---------- */
  function render() {
    var rows = docs.filter(function (d) { return d.name.toLowerCase().indexOf(query.toLowerCase()) !== -1; });
    rows.sort(function (a, b) {
      var cmp = sortKey === "name" ? a.name.localeCompare(b.name, "vi") : a.at - b.at;
      return sortDir === "asc" ? cmp : -cmp;
    });
    $("#doc-count").textContent = "(" + docs.length + ")";
    $("#no-match").hidden = rows.length > 0 || docs.length === 0;
    $("#doc-rows").innerHTML = rows.map(function (d) {
      var actions = [];
      if (d.status === "ready") { actions.push('<button class="btn btn-ghost btn-sm" role="menuitem" data-act="summary" data-id="' + d.id + '">Tóm tắt</button>'); }
      if (canDelete(d)) { actions.push('<button class="btn btn-ghost btn-sm" role="menuitem" data-act="delete" data-id="' + d.id + '" style="color:var(--color-danger-text)">Xóa</button>'); }
      var retry = d.status === "interrupted" ? ' <button class="btn btn-sm" data-act="retry" data-id="' + d.id + '">Thử lại</button>' : "";
      var menu = actions.length
        ? '<button class="btn btn-ghost btn-icon" aria-haspopup="menu" aria-expanded="false" aria-label="Thao tác với ' + esc(d.name) + '" data-menu="' + d.id + '"><span aria-hidden="true">⋯</span></button>' +
          '<div class="user-menu-list" role="menu" hidden data-menu-list="' + d.id + '">' + actions.join("") + "</div>"
        : "";
      return '<tr data-id="' + d.id + '">' +
        '<td><span class="doc-name" title="' + esc(d.name) + '">' + esc(d.name) + "</span></td>" +
        '<td class="num">' + (d.pages == null ? "—" : d.pages) + "</td>" +
        "<td>" + esc(d.uploader) + "</td>" +
        "<td>" + fmt(d.at) + "</td>" +
        "<td>" + CWD.statusBadge(d) + retry + "</td>" +
        '<td class="row-actions">' + menu + "</td></tr>";
    }).join("");
  }

  /* ---------- Giả lập xử lý tệp (không tải lại trang) ---------- */
  function simulate(d) {
    d.status = "uploading"; d.progress = 0; render();
    var t = setInterval(function () {
      d.progress += 20 + Math.floor(Math.random() * 15);
      if (d.progress >= 100) {
        clearInterval(t);
        d.status = "processing"; render();
        var scan = /scan/i.test(d.name);
        setTimeout(function () {
          if (scan) {
            d.status = "ocr"; render();
            setTimeout(function () { finish(d, scan); }, 4000);
          } else { finish(d, scan); }
        }, 1600);
      } else { render(); }
    }, 350);
  }
  function finish(d, scan) {
    d.status = "ready"; d.pages = 10 + Math.floor(Math.random() * 80);
    render();
    announce(d.name + ": Sẵn sàng");
  }

  /* ---------- Kiểm tra tệp ở trình duyệt (EC-08, DD-05; máy chủ kiểm tra lại) ---------- */
  async function handleFiles(fileList) {
    var files = Array.prototype.slice.call(fileList);
    var rej = $("#rejections");
    rej.innerHTML = "";
    var problems = [];
    if (files.length > MAX_FILES) {
      problems.push("Chỉ tải tối đa " + MAX_FILES + " tệp mỗi lần.");
      files = files.slice(0, MAX_FILES);
    }
    var valid = [];
    files.forEach(function (f) {
      if (!/\.pdf$/i.test(f.name) && f.type !== "application/pdf") { problems.push(f.name + ": Chỉ hỗ trợ tệp PDF."); }
      else if (f.size > MAX_BYTES) { problems.push(f.name + ": Tệp vượt quá 50 MB."); }
      else { valid.push(f); }
    });
    if (problems.length) {
      rej.innerHTML = '<div class="msg-notice is-danger" style="margin-bottom:16px"><span>' + problems.map(esc).join("<br>") + "</span></div>";
    }
    for (var i = 0; i < valid.length; i++) {
      var f = valid[i];
      var dup = docs.some(function (d) { return d.name.toLowerCase() === f.name.toLowerCase(); });
      if (dup) {
        var ok = await CWD.confirmDialog({
          title: "Tài liệu này có thể đã có trong kho",
          body: "“" + esc(f.name) + "” (" + (f.size / 1048576).toFixed(1).replace(".", ",") + " MB) trùng tên với một tài liệu đã có trong kho.",
          confirmLabel: "Vẫn tải lên"
        });
        if (!ok) { continue; }
      }
      var d = { id: "n" + Date.now() + i, name: f.name, pages: null, uploader: "Minh", at: new Date(), status: "uploading", progress: 0, size: "" };
      docs.push(d);
      simulate(d);
    }
    if (docs.length && CWD.getState() === "empty") { CWD.setState("data"); }
  }

  /* ---------- Sự kiện ---------- */
  CWD.init({
    page: "library",
    roles: ["bd", "tn", "qt"],
    defaultState: "data",
    states: [
      { id: "loading", label: "Đang tải" }, { id: "empty", label: "Trống" }, { id: "data", label: "Có dữ liệu" },
      { id: "error", label: "Lỗi" }, { id: "restricted", label: "Hạn chế quyền → S-02" }
    ],
    extra: [{ label: "Dải mất kết nối (EC-05)", run: function () { var b = $("#offline"); b.hidden = !b.hidden; } }],
    onRole: render
  });
  render();

  $("#search").addEventListener("input", function (e) { query = e.target.value; render(); });

  $$("[data-sort]").forEach(function (b) {
    b.onclick = function () {
      var key = b.dataset.sort;
      sortDir = sortKey === key && sortDir === "asc" ? "desc" : "asc";
      sortKey = key;
      $$("th[aria-sort]").forEach(function (th) { th.setAttribute("aria-sort", "none"); });
      b.closest("th").setAttribute("aria-sort", sortDir === "asc" ? "ascending" : "descending");
      $$("[data-sort] span").forEach(function (s) { s.textContent = "↕"; });
      b.querySelector("span").textContent = sortDir === "asc" ? "↑" : "↓";
      render();
    };
  });

  $("#retry-list").onclick = function () {
    CWD.setState("loading");
    setTimeout(function () { CWD.setState("data"); }, 700);
  };

  // Kéo thả / chọn tệp (chỉ Trưởng nhóm BD thấy vùng này)
  var dz = $("#dropzone");
  $("#pick").onclick = function () { $("#file").click(); };
  $("#file").onchange = function (e) { handleFiles(e.target.files); e.target.value = ""; };
  ["dragenter", "dragover"].forEach(function (ev) { dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.add("is-over"); }); });
  ["dragleave", "drop"].forEach(function (ev) { dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.remove("is-over"); }); });
  dz.addEventListener("drop", function (e) { handleFiles(e.dataTransfer.files); });

  // Menu "⋯", Tóm tắt, Xóa, Thử lại
  document.addEventListener("click", function (e) {
    var menuBtn = e.target.closest("[data-menu]");
    $$("[data-menu-list]").forEach(function (l) {
      var btn = $('[data-menu="' + l.dataset.menuList + '"]');
      if (menuBtn && menuBtn.dataset.menu === l.dataset.menuList) {
        l.hidden = !l.hidden; btn.setAttribute("aria-expanded", String(!l.hidden));
      } else { l.hidden = true; if (btn) { btn.setAttribute("aria-expanded", "false"); } }
    });
    var act = e.target.closest("[data-act]");
    if (!act) { return; }
    var d = docs.filter(function (x) { return x.id === act.dataset.id; })[0];
    if (!d) { return; }
    if (act.dataset.act === "retry") { simulate(d); }
    if (act.dataset.act === "delete") { del(d); }
    if (act.dataset.act === "summary") { summary(d); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { $$("[data-menu-list]").forEach(function (l) { l.hidden = true; }); }
  });

  async function del(d) {
    var ok = await CWD.confirmDialog({
      title: "Xóa tài liệu?",
      body: "Bạn sắp xóa “" + esc(d.name) + "”.<br>Cả đội sẽ không thể hỏi về tài liệu này nữa. Dữ liệu được xóa trong 24 giờ.",
      confirmLabel: "Xóa tài liệu", danger: true
    });
    if (!ok) { return; }
    docs = docs.filter(function (x) { return x.id !== d.id; });
    render();
    CWD.toast("Đã xóa tài liệu");
    announce("Đã xóa " + d.name);
    if (!docs.length) { CWD.setState("empty"); }
  }

  function summary(d) {
    CWD.openDialog(
      '<h2 id="sum-title">Tóm tắt do AI tạo cho ' + esc(d.name) + "</h2>" +
      '<div class="dlg-body" id="sum-body"><span class="badge badge-info">' + ICON.spin + "Đang tóm tắt…</span></div>" +
      '<div class="dlg-actions"><button class="btn" data-close>Đóng</button></div>',
      function (dlg) {
        dlg.setAttribute("aria-labelledby", "sum-title");
        $("[data-close]", dlg).onclick = function () { dlg.close(); };
        setTimeout(function () {
          $("#sum-body", dlg).innerHTML =
            "<p>Nội dung minh họa: tài liệu nêu phạm vi công việc, thời hạn và điều khoản thanh toán.</p>" +
            '<p style="margin-top:8px"><button class="citation" tabindex="0"><span class="cit-label">' + esc(CWD.shortName(d.name)) + " – tr. 1</span></button></p>" +
            '<p class="caption muted" style="margin-top:8px">Hãy kiểm tra trích dẫn với thông tin quan trọng.</p>';
        }, 900);
      });
  }
})();

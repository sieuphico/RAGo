/* S-07 Quản lý người dùng (CMP-19) và S-08 Nhật ký (CMP-20) – chỉ Quản trị viên */
(function () {
  "use strict";
  var $ = CWD.$, esc = CWD.esc, fmt = CWD.fmt;
  var page = document.body.dataset.page;
  var MAX_USERS = 20; // ASM-002
  var ROLE_NAMES = ["Người dùng BD", "Trưởng nhóm BD", "Quản trị viên", "Nhà tài trợ"];
  var min = 60000, now = Date.now();
  var users = [
    { email: "lan@congty.vn", role: "Người dùng BD", at: new Date(now - 4 * 864e5) },
    { email: "minh@congty.vn", role: "Trưởng nhóm BD", at: new Date(now - 4 * 864e5) },
    { email: "an@congty.vn", role: "Người dùng BD", at: new Date(now - 4 * 864e5) },
    { email: "quantri@congty.vn", role: "Quản trị viên", at: new Date(now - 5 * 864e5) },
    { email: "tai.tro@congty.vn", role: "Nhà tài trợ", at: new Date(now - 5 * 864e5) }
  ];
  var audit = [
    { who: "quantri@congty.vn", act: "Xóa", doc: "DieuKhoan_cu.pdf", at: new Date(now - 40 * min) },
    { who: "minh@congty.vn", act: "Tải lên", doc: "HD_XYZ.pdf", at: new Date(now - 8 * min) },
    { who: "minh@congty.vn", act: "Tải lên", doc: "Scan_0043.pdf", at: new Date(now - 19 * 60 * min) },
    { who: "minh@congty.vn", act: "Tải lên", doc: "Scan_0042.pdf", at: new Date(now - 19 * 60 * min - 3 * min) },
    { who: "minh@congty.vn", act: "Tải lên", doc: "HD_ABC_2026.pdf", at: new Date(now - 5 * 60 * min) }
  ].sort(function (a, b) { return b.at - a.at; });

  function announce(t) { var l = $("#sr-live"); if (l) { l.textContent = t; } }

  function renderUsers() {
    $("#user-count").textContent = "(" + users.length + "/" + MAX_USERS + ")";
    $("#user-rows").innerHTML = users.map(function (u, i) {
      return "<tr><td>" + esc(u.email) + "</td><td>" + esc(u.role) + "</td><td>" + fmt(u.at) + "</td>" +
        '<td><button class="btn btn-ghost btn-sm" data-del="' + i + '" style="color:var(--color-danger-text)" aria-label="Gỡ quyền của ' + esc(u.email) + '">🗑 Gỡ</button></td></tr>';
    }).join("");
    document.querySelectorAll("[data-del]").forEach(function (b) {
      b.onclick = function () { remove(Number(b.dataset.del)); };
    });
  }
  function renderAudit() {
    $("#audit-rows").innerHTML = audit.map(function (a) {
      var cls = a.act === "Xóa" ? "badge-warning" : "badge-neutral";
      return "<tr><td>" + esc(a.who) + '</td><td><span class="badge ' + cls + '">' + esc(a.act) + "</span></td><td>" + esc(a.doc) + "</td><td>" + fmt(a.at) + "</td></tr>";
    }).join("");
  }

  async function remove(i) {
    var u = users[i];
    var ok = await CWD.confirmDialog({
      title: "Gỡ quyền truy cập?",
      body: esc(u.email) + " sẽ không thể truy cập công cụ nữa. Thay đổi có hiệu lực trong vòng 1 phút.",
      confirmLabel: "Gỡ quyền", danger: true
    });
    if (!ok) { return; }
    users.splice(i, 1);
    renderUsers();
    CWD.toast("Đã gỡ quyền của " + u.email);
    announce("Đã gỡ quyền của " + u.email);
    if (!users.length) { CWD.setState("empty"); }
  }

  function addDialog() {
    if (users.length >= MAX_USERS) { CWD.toast("Đã đủ " + MAX_USERS + " người dùng được cấp quyền.", { error: true }); return; }
    CWD.openDialog(
      '<h2 id="add-title">Thêm người dùng</h2>' +
      '<form id="add-form" novalidate><div class="field" style="margin-bottom:12px"><label for="add-email">Email công ty</label>' +
      '<input id="add-email" class="input" type="email" autocomplete="off" aria-describedby="add-err" placeholder="ten@congty.vn"><span class="field-error" id="add-err" role="alert"></span></div>' +
      '<div class="field" style="margin-bottom:20px"><label for="add-role">Vai trò</label><select id="add-role" class="select">' +
      ROLE_NAMES.map(function (r) { return "<option>" + r + "</option>"; }).join("") + "</select></div>" +
      '<div class="dlg-actions"><button type="button" class="btn" data-cancel>Hủy</button><button type="submit" class="btn btn-primary">Thêm</button></div></form>',
      function (dlg) {
        dlg.setAttribute("aria-labelledby", "add-title");
        $("#add-email", dlg).focus();
        $("[data-cancel]", dlg).onclick = function () { dlg.close(); };
        $("#add-form", dlg).onsubmit = function (e) {
          e.preventDefault();
          var email = $("#add-email", dlg).value.trim().toLowerCase();
          var err = $("#add-err", dlg);
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { err.textContent = "Email không hợp lệ. Nhập địa chỉ dạng ten@congty.vn."; $("#add-email", dlg).focus(); return; }
          if (users.some(function (u) { return u.email === email; })) { err.textContent = "Email này đã có trong danh sách."; $("#add-email", dlg).focus(); return; }
          users.push({ email: email, role: $("#add-role", dlg).value, at: new Date() });
          dlg.close();
          renderUsers();
          if (CWD.getState() === "empty") { CWD.setState("data"); }
          CWD.toast("Đã thêm " + email);
          announce("Đã thêm " + email);
        };
      });
  }

  CWD.init({
    page: page === "users" ? "admin" : "audit",
    roles: ["qt"],
    defaultState: "data",
    states: [
      { id: "loading", label: "Đang tải" }, { id: "empty", label: "Trống" }, { id: "data", label: "Có dữ liệu" },
      { id: "error", label: "Lỗi" }, { id: "restricted", label: "Hạn chế quyền → S-02" }
    ]
  });
  var retry = $("#retry");
  if (retry) { retry.onclick = function () { CWD.setState("loading"); setTimeout(function () { CWD.setState("data"); }, 700); }; }
  if (page === "users") {
    renderUsers();
    $("#add-user").onclick = addDialog;
    var o = $("[data-open-add]"); if (o) { o.onclick = addDialog; }
  } else { renderAudit(); }
})();

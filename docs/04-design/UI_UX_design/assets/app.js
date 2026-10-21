/*
 * Prototype "Chat với tài liệu" – lõi dùng chung.
 * Chỉ HTML/CSS/JS thuần, không gọi dịch vụ bên ngoài (Blueprint 3.7: giao diện không gọi trực tiếp
 * dịch vụ ngoài, không tải font hay script bên thứ ba). Dữ liệu là dữ liệu minh họa.
 */
(function () {
  "use strict";

  /* ---------------- Dữ liệu minh họa ---------------- */
  const ROLES = {
    bd: { label: "Người dùng BD", user: "Lan" },
    tn: { label: "Trưởng nhóm BD", user: "Minh" },
    qt: { label: "Quản trị viên", user: "Quản trị viên" },
    ntt: { label: "Nhà tài trợ", user: "Nhà tài trợ" }
  };
  // Mục điều hướng theo vai trò (Blueprint 3.2.2)
  const NAV = [
    { id: "chat", href: "chat.html", label: "Hỏi đáp", roles: ["bd", "tn", "qt"] },
    { id: "library", href: "library.html", label: "Kho tài liệu", roles: ["bd", "tn", "qt"] },
    { id: "metrics", href: "metrics.html", label: "Số liệu", roles: ["qt", "ntt"] },
    { id: "admin", href: "users.html", label: "Quản trị", roles: ["qt"] }
  ];
  const HOME = { bd: "chat.html", tn: "chat.html", qt: "chat.html", ntt: "metrics.html" };

  const MIN = 60 * 1000;
  const now = Date.now();
  function ago(mins) { return new Date(now - mins * MIN); }

  const DOCS = [
    { id: "d1", name: "HD_ABC_2026.pdf", pages: 48, uploader: "Minh", at: ago(60 * 5), status: "ready", size: "4,2 MB" },
    { id: "d2", name: "PL2_ABC.pdf", pages: 6, uploader: "Minh", at: ago(60 * 5), status: "ready", size: "0,6 MB" },
    { id: "d3", name: "BangGia_2026.pdf", pages: 12, uploader: "Minh", at: ago(60 * 30), status: "ready", size: "1,1 MB" },
    { id: "d4", name: "BaoCao_Q3.pdf", pages: 120, uploader: "Minh", at: ago(60 * 18), status: "processing", size: "9,8 MB" },
    { id: "d5", name: "Scan_0042.pdf", pages: null, uploader: "Minh", at: ago(60 * 19), status: "ocr", size: "22,4 MB" },
    { id: "d6", name: "Scan_0043.pdf", pages: null, uploader: "Minh", at: ago(60 * 19), status: "failed", reason: "Không đọc được nội dung", size: "3,0 MB" },
    { id: "d7", name: "HD_XYZ.pdf", pages: null, uploader: "Minh", at: ago(8), status: "uploading", progress: 64, size: "5,3 MB" },
    { id: "d8", name: "DieuKhoan.pdf", pages: null, uploader: "Minh", at: ago(8), status: "interrupted", size: "2,7 MB" }
  ];

  const ICON = {
    check: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5"/></svg>',
    x: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>',
    up: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 13V3M4 7l4-4 4 4"/></svg>',
    warn: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2l6.5 11.5h-13zM8 6.5v3.2M8 11.6v.1"/></svg>',
    spin: '<svg class="spin" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M8 2a6 6 0 1 0 6 6"/></svg>',
    ocr: '<svg class="spin" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M8 2a6 6 0 1 0 6 6"/><path d="M5.5 8h5M8 5.5v5" stroke-width="1.4"/></svg>',
    search: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" width="16" height="16"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/></svg>',
    stop: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" width="14" height="14"><rect x="3" y="3" width="10" height="10" rx="1.5"/></svg>',
    copy: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true" width="16" height="16"><rect x="5.5" y="5.5" width="8" height="8" rx="1.5"/><path d="M10.5 3.5v-.5a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h.5"/></svg>',
    up2: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true" width="16" height="16"><path d="M5 7.5V14H3V7.5zM5 7.5l3-5.5c1.2 0 1.8 1 1.5 2l-.5 2.5h3.2a1.3 1.3 0 0 1 1.3 1.6l-.9 4A1.5 1.5 0 0 1 11.1 14H5"/></svg>',
    down2: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true" width="16" height="16"><path d="M5 8.5V2H3v6.5zM5 8.5l3 5.5c1.2 0 1.8-1 1.5-2l-.5-2.5h3.2a1.3 1.3 0 0 0 1.3-1.6l-.9-4A1.5 1.5 0 0 0 11.1 2H5"/></svg>'
  };

  /* ---------------- Tiện ích ---------------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  // dd/MM/yyyy HH:mm (UX-11)
  function fmt(d) {
    return pad(d.getDate()) + "/" + pad(d.getMonth() + 1) + "/" + d.getFullYear() + " " + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }
  function shortName(name) {
    // Rút gọn giữa, đầy đủ ở tooltip (Blueprint 3.6.3)
    return name.length > 24 ? name.slice(0, 10) + "…" + name.slice(-10) : name;
  }
  function store(key, val) {
    try { if (val === undefined) { return sessionStorage.getItem(key); } if (val === null) { sessionStorage.removeItem(key); } else { sessionStorage.setItem(key, val); } } catch (e) { /* trình duyệt chặn lưu trữ */ }
    return null;
  }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- Vai trò ---------------- */
  function getRole() {
    const q = new URLSearchParams(location.search).get("role");
    if (q && ROLES[q]) { store("cwd.role", q); return q; }
    const s = store("cwd.role");
    return ROLES[s] ? s : "bd";
  }
  let role = getRole();

  /* ---------------- Trạng thái trang ---------------- */
  let currentState = "data";
  const stateListeners = [];
  function applyState(state) {
    currentState = state;
    document.body.dataset.state = state;
    $$("[data-show]").forEach(function (el) {
      el.hidden = el.dataset.show.split(" ").indexOf(state) === -1;
    });
    $$(".proto-bar [data-state]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.state === state)); });
    stateListeners.forEach(function (fn) { fn(state); });
  }

  /* ---------------- Thông báo tạm (toast, role=status) ---------------- */
  function toast(text, opts) {
    opts = opts || {};
    let host = $(".toast-host");
    if (!host) {
      host = document.createElement("div");
      host.className = "toast-host";
      document.body.appendChild(host);
    }
    const t = document.createElement("div");
    t.className = "toast" + (opts.error ? " is-error" : "");
    t.setAttribute("role", opts.error ? "alert" : "status");
    t.innerHTML = "<span>" + esc(text) + "</span>";
    if (opts.error) {
      const b = document.createElement("button");
      b.className = "btn btn-ghost btn-sm";
      b.style.color = "#fff";
      b.setAttribute("aria-label", "Đóng thông báo");
      b.innerHTML = ICON.x;
      b.onclick = function () { t.remove(); };
      t.appendChild(b);
    } else {
      setTimeout(function () { t.remove(); }, 4000); // tự ẩn sau 4 giây; lỗi giữ đến khi đóng
    }
    host.appendChild(t);
  }

  /* ---------------- Hộp thoại (dùng <dialog>: giam focus, Esc đóng, trả focus) ---------------- */
  function openDialog(html, setup) {
    const opener = document.activeElement;
    const dlg = document.createElement("dialog");
    dlg.setAttribute("aria-modal", "true");
    dlg.innerHTML = html;
    document.body.appendChild(dlg);
    dlg.addEventListener("close", function () {
      dlg.remove();
      if (opener && opener.focus) { opener.focus(); }
    });
    dlg.showModal();
    if (setup) { setup(dlg); }
    return dlg;
  }
  // Hộp thoại xác nhận; mặc định focus vào nút Hủy khi thao tác phá hủy
  function confirmDialog(o) {
    return new Promise(function (resolve) {
      const html =
        '<h2>' + esc(o.title) + '</h2>' +
        '<div class="dlg-body">' + o.body + '</div>' +
        '<div class="dlg-actions">' +
        '<button class="btn" data-act="cancel"' + (o.danger ? " autofocus" : "") + '>' + esc(o.cancelLabel || "Hủy") + '</button>' +
        '<button class="btn ' + (o.danger ? "btn-danger" : "btn-primary") + '" data-act="ok">' + esc(o.confirmLabel) + '</button>' +
        '</div>';
      let result = false;
      const dlg = openDialog(html, function (d) {
        d.setAttribute("aria-labelledby", "dlg-title");
        $("h2", d).id = "dlg-title";
        $('[data-act="cancel"]', d).onclick = function () { d.close(); };
        $('[data-act="ok"]', d).onclick = function () { result = true; d.close(); };
        if (o.danger) { $('[data-act="cancel"]', d).focus(); }
      });
      dlg.addEventListener("close", function () { resolve(result); });
    });
  }

  /* ---------------- Huy hiệu trạng thái tài liệu (CMP-16, Blueprint 3.5.1) ---------------- */
  function statusBadge(doc) {
    switch (doc.status) {
      case "uploading": return '<span class="badge badge-info">' + ICON.up + "Đang tải lên (" + (doc.progress || 0) + "%)</span>";
      case "interrupted": return '<span class="badge badge-warning">' + ICON.warn + "Tải lên bị gián đoạn</span>";
      case "processing": return '<span class="badge badge-info">' + ICON.spin + "Đang xử lý</span>";
      case "ocr": return '<span class="badge badge-info" title="Tài liệu dạng ảnh quét cần thêm thời gian xử lý.">' + ICON.ocr + "Đang nhận dạng ký tự (OCR)</span>";
      case "ready": return '<span class="badge badge-success">' + ICON.check + "Sẵn sàng</span>";
      case "failed": return '<span class="badge badge-danger">' + ICON.x + "Thất bại – " + esc(doc.reason || "Không đọc được nội dung") + "</span>";
      default: return "";
    }
  }

  /* ---------------- Vỏ ứng dụng: thanh điều hướng + thanh demo ---------------- */
  function renderHeader(page) {
    const host = $("#app-header");
    if (!host) { return; }
    const items = NAV.filter(function (n) { return n.roles.indexOf(role) !== -1; });
    const adminPages = { admin: 1, audit: 1 };
    host.className = "app-header";
    host.setAttribute("role", "banner");
    host.innerHTML =
      '<a class="brand" href="' + HOME[role] + '"><span class="brand-mark" aria-hidden="true">◆</span> Chat với tài liệu</a>' +
      '<nav class="nav" aria-label="Điều hướng chính">' +
      items.map(function (n) {
        const cur = n.id === page || (n.id === "admin" && adminPages[page]);
        return '<a href="' + n.href + '"' + (cur ? ' aria-current="page"' : "") + ">" + n.label + "</a>";
      }).join("") +
      "</nav>" +
      '<div class="user-menu"><button class="btn btn-ghost" id="user-btn" aria-haspopup="true" aria-expanded="false">' +
      esc(ROLES[role].user) + ' <span aria-hidden="true">▾</span></button>' +
      '<div class="user-menu-list" hidden><div class="caption muted" style="padding:4px 8px">' + esc(ROLES[role].label) + '</div>' +
      '<button class="btn btn-ghost" data-logout>Đăng xuất</button></div></div>';
    const btn = $("#user-btn", host);
    const list = $(".user-menu-list", host);
    btn.onclick = function () {
      const open = list.hidden;
      list.hidden = !open;
      btn.setAttribute("aria-expanded", String(open));
    };
    $("[data-logout]", host).onclick = function () { location.href = "login.html"; };
    host.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !list.hidden) { list.hidden = true; btn.setAttribute("aria-expanded", "false"); btn.focus(); }
    });
  }

  function renderProtoBar(cfg) {
    const bar = document.createElement("div");
    bar.className = "proto-bar";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Thanh demo prototype (không thuộc sản phẩm)");
    let html = '<span class="proto-label">Demo</span>';
    html += '<label class="sr-only" for="proto-role">Vai trò</label><select id="proto-role">' +
      Object.keys(ROLES).map(function (k) { return '<option value="' + k + '"' + (k === role ? " selected" : "") + ">" + ROLES[k].label + "</option>"; }).join("") + "</select>";
    if (cfg.states && cfg.states.length) {
      html += '<span class="proto-sep">|</span>' +
        cfg.states.map(function (s) { return '<button data-state="' + s.id + '" aria-pressed="false">' + esc(s.label) + "</button>"; }).join("");
    }
    if (cfg.extra && cfg.extra.length) {
      html += '<span class="proto-sep">|</span>' +
        cfg.extra.map(function (x, i) { return '<button data-extra="' + i + '">' + esc(x.label) + "</button>"; }).join("");
    }
    bar.innerHTML = html;
    var skip = $(".skip-link");
    if (skip && skip.nextSibling) { skip.parentNode.insertBefore(bar, skip.nextSibling); } else { document.body.insertBefore(bar, document.body.firstChild); }
    function measure() { document.documentElement.style.setProperty("--proto-h", bar.offsetHeight + "px"); }
    measure();
    window.addEventListener("resize", measure);
    $("#proto-role", bar).onchange = function (e) {
      role = e.target.value;
      store("cwd.role", role);
      if (cfg.roles && cfg.roles.indexOf(role) === -1) { location.href = "denied.html"; return; }
      document.body.dataset.role = role;
      renderHeader(cfg.page);
      applyRoleVisibility();
      if (cfg.onRole) { cfg.onRole(role); }
    };
    $$("[data-state]", bar).forEach(function (b) {
      b.onclick = function () {
        if (b.dataset.state === "restricted") { location.href = "denied.html"; return; }
        applyState(b.dataset.state);
      };
    });
    $$("[data-extra]", bar).forEach(function (b) {
      b.onclick = function () { cfg.extra[Number(b.dataset.extra)].run(); };
    });
  }

  function applyRoleVisibility() {
    $$("[data-roles]").forEach(function (el) {
      el.hidden = el.dataset.roles.split(" ").indexOf(role) === -1;
    });
    $$("[data-not-roles]").forEach(function (el) {
      el.hidden = el.dataset.notRoles.split(" ").indexOf(role) !== -1;
    });
  }

  function init(cfg) {
    // Chặn vai trò không có quyền → S-02 (Hạn chế quyền)
    if (cfg.roles && cfg.roles.indexOf(role) === -1) { location.replace("denied.html"); return; }
    document.body.dataset.role = role;
    renderHeader(cfg.page);
    renderProtoBar(cfg);
    applyRoleVisibility();
    applyState(cfg.defaultState || "data");
  }

  window.CWD = {
    ROLES: ROLES, DOCS: DOCS, ICON: ICON, esc: esc, fmt: fmt, shortName: shortName, store: store,
    $: $, $$: $$, reduceMotion: reduceMotion,
    getRole: function () { return role; },
    home: function (r) { return HOME[r || role]; },
    getState: function () { return currentState; },
    onState: function (fn) { stateListeners.push(fn); },
    setState: applyState, init: init, toast: toast, openDialog: openDialog, confirmDialog: confirmDialog,
    statusBadge: statusBadge, applyRoleVisibility: applyRoleVisibility
  };
})();

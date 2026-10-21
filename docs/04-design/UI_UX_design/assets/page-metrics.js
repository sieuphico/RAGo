/* S-09 Số liệu (CMP-21): Quản trị viên và Nhà tài trợ. DỮ LIỆU MINH HỌA. */
(function () {
  "use strict";
  var $ = CWD.$, ICON = CWD.ICON;
  var WEEKS = [
    { label: "30/11 – 06/12/2026", wau: 45, wauN: "8/18", q: 98, p50: 7.1, p90: 14.9, up: 68, nf: 21 },
    { label: "07/12 – 13/12/2026", wau: 58, wauN: "10/18", q: 143, p50: 6.8, p90: 14.2, up: 71, nf: 19 },
    { label: "14/12 – 20/12/2026", wau: 66, wauN: "12/18", q: 198, p50: 6.4, p90: 13.9, up: 74, nf: 18 },
    { label: "21/12 – 27/12/2026", wau: 72, wauN: "13/18", q: 241, p50: 6.2, p90: 13.8, up: 76, nf: 18 }
  ];
  var sel = WEEKS.length - 1;
  function n1(v) { return String(v).replace(".", ","); }

  function status(ok, warn) {
    if (warn) { return '<span class="badge badge-warning">' + ICON.warn + "Cảnh báo</span>"; }
    return ok ? '<span class="badge badge-success">' + ICON.check + "Đạt mục tiêu</span>" : '<span class="badge badge-neutral">Chưa đạt mục tiêu</span>';
  }
  function render() {
    var w = WEEKS[sel];
    $("#updated").textContent = "Cập nhật: 28/12/2026 06:00";
    $("#kpis").innerHTML = [
      ["WAU", w.wau + "% (" + w.wauN + ")", "mục tiêu ≥ 60%", status(w.wau >= 60)],
      ["Câu hỏi", String(w.q), "", ""],
      ["Phản hồi p50 / p90", n1(w.p50) + " s / " + n1(w.p90) + " s", "mục tiêu p90 ≤ 15 s", status(w.p90 <= 15)],
      ["👍 hữu ích", w.up + "%", "mục tiêu ≥ 70%", status(w.up >= 70)],
      ["Không tìm thấy", w.nf + "%", "cảnh báo khi > 30%", w.nf > 30 ? status(false, true) : '<span class="badge badge-neutral">Trong ngưỡng</span>']
    ].map(function (k) {
      return '<div class="kpi"><span class="kpi-label">' + k[0] + '</span><span class="kpi-value">' + k[1] + "</span>" +
        (k[2] ? '<span class="kpi-goal">' + k[2] + "</span>" : "") + (k[3] ? "<span>" + k[3] + "</span>" : "") + "</div>";
    }).join("");
    $("#metric-rows").innerHTML = WEEKS.map(function (x) {
      return '<tr><th scope="row" style="background:none">' + x.label + '</th><td class="num">' + x.wau + '</td><td class="num">' + x.q +
        '</td><td class="num">' + n1(x.p50) + '</td><td class="num">' + n1(x.p90) + '</td><td class="num">' + x.up + '</td><td class="num">' + x.nf + "</td></tr>";
    }).join("");
    chart();
  }

  // Biểu đồ SVG thuần (không thư viện ngoài): cột = số câu hỏi, đường + chấm = WAU %
  function chart() {
    var W = 640, H = 260, L = 44, R = 44, T = 16, B = 44;
    var iw = W - L - R, ih = H - T - B, n = WEEKS.length, band = iw / n;
    var maxQ = 300;
    var s = '<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="Biểu đồ theo tuần: số câu hỏi (cột) và WAU phần trăm (đường). Dữ liệu minh họa; xem bảng bên dưới." style="max-width:720px">';
    [0, 100, 200, 300].forEach(function (v) {
      var y = T + ih - (v / maxQ) * ih;
      s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y + '" y2="' + y + '" stroke="#D1D5DB"/><text x="' + (L - 6) + '" y="' + (y + 4) + '" font-size="13" text-anchor="end" fill="#4B5563">' + v + "</text>";
    });
    [0, 50, 100].forEach(function (v) {
      var y = T + ih - (v / 100) * ih;
      s += '<text x="' + (W - R + 6) + '" y="' + (y + 4) + '" font-size="13" fill="#92400E">' + v + "%</text>";
    });
    var pts = [];
    WEEKS.forEach(function (w, i) {
      var x = L + band * i + band * 0.2, bw = band * 0.6, h = (w.q / maxQ) * ih, y = T + ih - h;
      s += '<rect x="' + x + '" y="' + y + '" width="' + bw + '" height="' + h + '" fill="#1D4ED8"' + (i === sel ? ' stroke="#1F2937" stroke-width="3"' : "") + ' rx="3"/>';
      s += '<text x="' + (x + bw / 2) + '" y="' + (H - 26) + '" font-size="13" text-anchor="middle" fill="#4B5563">' + w.label.slice(0, 5) + "</text>";
      s += '<text x="' + (x + bw / 2) + '" y="' + (H - 10) + '" font-size="13" font-weight="600" text-anchor="middle" fill="#1F2937">' + w.q + " câu hỏi</text>";
      pts.push([x + bw / 2, T + ih - (w.wau / 100) * ih, w.wau]);
    });
    s += '<polyline fill="none" stroke="#92400E" stroke-width="2" points="' + pts.map(function (p) { return p[0] + "," + p[1]; }).join(" ") + '"/>';
    pts.forEach(function (p) { s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4" fill="#fff" stroke="#92400E" stroke-width="2"/><text x="' + p[0] + '" y="' + (p[1] - 8) + '" font-size="13" font-weight="600" text-anchor="middle" fill="#92400E" stroke="#fff" stroke-width="4" paint-order="stroke">' + p[2] + "%</text>"; });
    s += "</svg>";
    $("#chart").innerHTML = s;
  }

  CWD.init({
    page: "metrics",
    roles: ["qt", "ntt"],
    defaultState: "data",
    states: [
      { id: "loading", label: "Đang tải" }, { id: "empty", label: "Trống" }, { id: "data", label: "Có dữ liệu" },
      { id: "error", label: "Lỗi" }, { id: "restricted", label: "Hạn chế quyền → S-02" }
    ]
  });
  $("#week").innerHTML = WEEKS.map(function (w, i) { return '<option value="' + i + '"' + (i === sel ? " selected" : "") + ">" + w.label + "</option>"; }).join("");
  $("#week").onchange = function (e) { sel = Number(e.target.value); render(); };
  $("#retry").onclick = function () { CWD.setState("loading"); setTimeout(function () { CWD.setState("data"); }, 700); };
  render();
})();

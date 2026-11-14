// 架構圖產生器：一份定義，產出每一版的 SVG。
//
// 每個元件記著 since（第幾版出現）、until（最後出現在第幾版，可省略）、
// changed（哪幾版改過）。畫第 N 版的時候：
//   since 在 N 之後的不畫；since 等於 N 的畫成綠色（新增）；
//   N 在 changed 裡的畫成橘色（改了）；其他畫成灰色。
//
// 用法：node gen.js 1.1 > v1.1.svg
//       node gen.js all          （在這個資料夾產出全部版本）

const VERS = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.10",
  "0.11", "0.12", "0.13", "0.14", "0.15", "0.16", "0.17", "1.0", "1.1"];

const TITLES = {
  "0.1": ["收得到事件", "快速上手"],
  "0.2": ["查得到事件", "HTTP Request 的三層結構"],
  "0.3": ["通知值班的人", "非同步"],
  "0.4": ["事件格式是一份合約", "Pydantic"],
  "0.5": ["內容也要合理", "Validation"],
  "0.6": ["第一個 MVP：事件變成告警", "Workshop 1"],
  "0.7": ["先把程式整理好", "專案結構"],
  "0.8": ["設計資料表", "PostgreSQL + ORM（一）"],
  "0.9": ["API 接上資料庫", "PostgreSQL + ORM（二）"],
  "0.10": ["錯誤有固定的格式", "錯誤處理"],
  "0.11": ["不是誰都能打這個 API", "API Key"],
  "0.12": ["看信心值決定要不要吵醒人", "防呆"],
  "0.13": ["每次改動都有人把關", "API 自動測試"],
  "0.14": ["統計報表", "Pandas"],
  "0.15": ["斷線後整批補傳", "檔案上傳"],
  "0.16": ["交班摘要", "LLM Pipeline"],
  "0.17": ["摘要一段一段出現", "串流回應"],
  "1.0": ["告警沒人理的時候", "Workshop 2"],
  "1.1": ["一台 server 服務兩家客戶", "Homework"],
};

const vi = (v) => VERS.indexOf(v);

const W = 1440, H = 880;
const SANS = "'PingFang TC','Noto Sans TC','Noto Sans CJK TC','Microsoft JhengHei',sans-serif";
const MONO = "'SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace";

const PALETTE = {
  old: { fill: "#f4f5f7", stroke: "#a3a8b0", text: "#3a3f47", line: "#8a9099" },
  new: { fill: "#e3f7e8", stroke: "#1f9d4c", text: "#0f5132", line: "#1f9d4c" },
  changed: { fill: "#fff4dc", stroke: "#d9901a", text: "#7a4b00", line: "#d9901a" },
  error: { fill: "#fdecec", stroke: "#d33a3a", text: "#9b1c1c", line: "#d33a3a" },
};

// --------------------------------------------------
// 元件
// kind：actor / port / service / store / chip / group / frame / external / note / error
// lines：一個字串陣列；或 [[since, [第一行, 第二行]], ...]，依版本換文字
// --------------------------------------------------
const E = [];

function el(id, kind, x, y, w, h, lines, since, opts = {}) {
  if (typeof lines[0] === "string") lines = [[since, lines]];
  E.push({ id, kind, x, y, w, h, lines, since, until: null, changed: [], badge: true, lock: null, ...opts });
}

const ED = [];

function edge(pts, since, opts = {}) {
  let label = opts.label || null;
  if (typeof label === "string") label = [[since, label]];
  ED.push({ pts, since, until: null, changed: [], dashed: false, error: false, arrow: true,
    lpos: null, lanchor: "middle", ...opts, label });
}

// ---------- 外框 ----------
el("pytest", "frame", 258, 82, 924, 762, ["pytest：自動測試把整個平台包起來"], "0.13", { dashed: true });
el("platform", "frame", 280, 100, 880, 720, ["告警平台"], "0.1", { badge: false });

// ---------- 平台最上面一列 ----------
el("c_factory", "chip", 400, 112, 118, 26, ["工廠 factory"], "1.1");
el("c_care", "chip", 526, 112, 100, 26, ["健康 care"], "1.1");
el("c_profiles", "chip", 640, 112, 200, 26,
  [["0.6", ["profiles/<一家>.json"]], ["1.0", ["profiles/<一家>.json ＋ 升級策略"]], ["1.1", ["profiles/*.json 全部讀進來"]]],
  "0.6", { changed: ["1.0", "1.1"] });
el("c_keys", "chip", 852, 112, 150, 26,
  [["0.11", ["2 把 key：設備／值班"]], ["1.1", ["4 把 key：客戶 × 角色"]]], "0.11", { changed: ["1.1"] });
el("p_health", "port", 1016, 112, 130, 26, ["GET /health"], "0.1");

// ---------- 欄位標題（v0.7 分層） ----------
el("h_left", "note", 385, 172, 0, 0, ["routers（門口）"], "0.7", { badge: false });
el("h_mid", "note", 726, 172, 0, 0, ["services（裡面）"], "0.7", { badge: false });
el("h_right", "note", 1059, 172, 0, 0, ["routers（門口）"], "0.7", { badge: false });

// ---------- 左邊：送資料進來的 ----------
el("a_dev", "actor", 30, 180, 190, 160, ["設備", "攝影機／手環"], "0.1");
el("a_sched", "actor", 30, 420, 190, 60, ["排程器", "每分鐘一次"], "1.0");

el("p_events", "port", 292, 190, 186, 32, ["POST /events"], "0.1", { lock: "0.11" });
el("p_upload", "port", 292, 234, 186, 32, ["POST /events/upload"], "0.15", { lock: "0.15" });
el("p_image", "port", 292, 278, 186, 32, ["POST /events/{id}/image"], "1.1", { lock: "1.1" });
el("e_err", "error", 292, 320, 186, 24, ["錯誤：{status, reason, code}"], "0.10");
el("p_escalate", "port", 292, 430, 186, 40, ["POST /alerts/", "escalate-overdue"], "1.0", { lock: "1.0" });

// ---------- services：事件進來 ----------
el("g_ingest", "group", 506, 184, 440, 92, ["ingest：單筆、補傳走同一條路"], "0.15");
el("s_contract", "service", 516, 206, 128, 56,
  [["0.4", ["合約", "Pydantic"]], ["0.5", ["合約＋範圍", "Pydantic"]]], "0.4", { changed: ["0.5"] });
el("s_type", "service", 660, 206, 128, 56,
  [["0.6", ["事件類型", "對照設定檔"]], ["1.1", ["事件類型", "對照該客戶設定檔"]]], "0.6", { changed: ["1.1"] });
el("s_guard", "service", 804, 206, 132, 56, ["防呆分流", "看信心值"], "0.12");
el("n_log", "note", 806, 298, 0, 0, ["< 0.5 只記錄，不開告警"], "0.12", { badge: false, anchor: "start", size: 10 });
el("s_image", "service", 516, 288, 128, 44, ["存影像"], "1.1");
el("f_uploads", "store", 660, 288, 128, 44, ["uploads/<客戶>/", "影像檔"], "1.1");

// ---------- services：通知（v0.3 到 v0.5，還沒有告警） ----------
el("s_notify", "service", 700, 410, 200, 56, ["通知值班人員", "await asyncio.sleep(2)"], "0.3", { until: "0.5" });

// ---------- services：告警 ----------
el("s_escalate", "service", 506, 420, 136, 60, ["升級策略", "by_minutes｜high_first"], "1.0");
el("sm", "group", 650, 356, 300, 164, ["告警狀態機"], "0.6", { solid: true, changed: ["0.12", "1.0"] });
el("st_pending", "chip", 658, 392, 84, 24, ["pending_review"], "0.12", { badge: false });
el("st_open", "chip", 758, 392, 84, 24, ["open"], "0.6", { badge: false });
el("st_ack", "chip", 858, 392, 84, 24, ["acknowledged"], "0.6", { badge: false });
el("st_esc", "chip", 758, 438, 84, 24, ["escalated"], "1.0", { badge: false });
el("st_dis", "chip", 658, 482, 84, 24, ["dismissed"], "0.6", { badge: false });
el("st_res", "chip", 858, 482, 84, 24, ["resolved"], "0.6", { badge: false });
el("n_dis", "note", 750, 512, 0, 0, ["← 沒結案的都能 dismiss"], "0.6", { badge: false, anchor: "start", size: 10 });

// ---------- services：報表 ----------
el("s_stats", "service", 506, 556, 128, 56, ["Pandas 統計"], "0.14");
el("s_prompt", "service", 652, 556, 128, 56, ["交班摘要", "組 prompt"], "0.16");
el("s_sse", "service", 798, 556, 148, 56, ["串流 SSE", "一段一段送"], "0.17");

// ---------- 資料 ----------
el("list", "store", 506, 724, 300, 86,
  [["0.1", ["Python list", "events = []，server 重開就清空"]], ["0.6", ["Python list", "events、alerts，server 重開就清空"]]],
  "0.1", { until: "0.7", changed: ["0.6"] });
el("n_layer", "note", 516, 716, 0, 0,
  [["0.6", ["▲▼ 每個 service 都存取這裡"]], ["0.9", ["▲▼ 每個 service 都透過 ORM 存取這裡"]]],
  "0.6", { badge: false, anchor: "start", size: 10, changed: ["0.9"] });
el("db", "store", 506, 724, 300, 86, ["PostgreSQL"], "0.8", { labelTop: true, changed: ["0.9", "1.1"] });
el("t_events", "chip", 516, 754, 120, 24, ["detection_events"], "0.8", { badge: false });
el("t_alerts", "chip", 642, 754, 60, 24, ["alerts"], "0.8", { badge: false });
el("t_history", "chip", 708, 754, 92, 24, ["alert_history"], "1.0", { badge: false });
el("n_seed", "note", 516, 800, 0, 0, ["先用 seed.py 驗證；API 還在用 list，下一版才接上"], "0.8",
  { until: "0.8", badge: false, anchor: "start", size: 10 });
el("n_customer", "note", 516, 800, 0, 0, ["每一列都多了 customer 欄位"], "1.1", { badge: false, anchor: "start", size: 10 });
el("db_test", "store", 826, 744, 120, 46, ["events_test", "測試用"], "0.13");

// ---------- 右邊：門口 ----------
el("r_events", "port", 966, 190, 186, 40, ["GET /events/{id}", "GET /locations/…"], "0.2", { lock: "0.11" });
el("r_alerts", "port", 966, 380, 186, 40, ["GET・POST /alerts/…", "查、ack、resolve…"], "0.6", { lock: "0.11" });
el("r_history", "port", 966, 430, 186, 32, ["GET /alerts/{id}/history"], "1.0", { lock: "1.0" });
el("r_summary", "port", 966, 556, 186, 30, ["GET /reports/summary"], "0.14", { lock: "0.14" });
el("r_handover", "port", 966, 596, 186, 36,
  [["0.16", ["GET /reports/handover"]], ["0.17", ["GET /reports/handover", "（/stream）"]]], "0.16",
  { lock: "0.16", changed: ["0.17"] });

// ---------- 右邊：用結果的 ----------
el("a_handler", "actor", 1222, 180, 196, 340,
  [["0.2", ["查詢的人", "curl／瀏覽器"]], ["0.3", ["值班人員", "主管／護理師", "（App）"]]], "0.2", { changed: ["0.3"] });
el("a_manager", "actor", 1222, 548, 196, 90, ["主管、交班的人"], "0.14");
el("a_llm", "external", 1222, 652, 196, 66, ["LLM", "外部服務"], "0.16");

// --------------------------------------------------
// 箭頭（箭頭 = 資料往哪裡走）
// --------------------------------------------------
edge([[220, 206], [292, 206]], "0.1", { label: [["0.1", "送事件"], ["0.15", "即時"]], lpos: [256, 200] });
edge([[220, 250], [292, 250]], "0.15", { label: "補傳 CSV", lpos: [256, 244] });
edge([[220, 294], [292, 294]], "1.1", { label: "截圖", lpos: [256, 288] });
edge([[292, 332], [222, 332]], "0.10", { error: true });
edge([[220, 450], [292, 450]], "1.0");

// v0.1 到 v0.3：事件直接存進 list
edge([[478, 206], [494, 206], [494, 767], [506, 767]], "0.1", { until: "0.3" });
// v0.3：存完就通知
edge([[494, 438], [700, 438]], "0.3", { until: "0.3" });
// v0.4、v0.5：先過合約，再存、再通知
edge([[478, 206], [494, 206], [494, 234], [516, 234]], "0.4");
edge([[580, 262], [580, 724]], "0.4", { until: "0.5" });
edge([[644, 248], [672, 248], [672, 438], [700, 438]], "0.4", { until: "0.5" });
edge([[900, 438], [1222, 438]], "0.3", { until: "0.5", dashed: true, label: "通知（等 2 秒）", lpos: [1060, 432] });

edge([[478, 250], [494, 250], [494, 238]], "0.15", { arrow: false });
edge([[478, 294], [496, 294], [496, 310], [516, 310]], "1.1");
edge([[644, 310], [660, 310]], "1.1");
edge([[644, 234], [660, 234]], "0.6");
edge([[724, 262], [724, 356]], "0.6", { until: "0.11", label: "開告警", lpos: [730, 322], lanchor: "start" });
edge([[788, 234], [804, 234]], "0.12");
edge([[900, 262], [900, 340], [800, 340], [800, 356]], "0.12", { label: "開告警／待確認", lpos: [906, 322], lanchor: "start" });

edge([[478, 450], [506, 450]], "1.0");
edge([[642, 450], [758, 450]], "1.0", { label: "系統升級", lpos: [700, 444] });

// 狀態機內部
edge([[742, 404], [758, 404]], "0.12");
edge([[842, 404], [858, 404]], "0.6");
edge([[900, 416], [900, 482]], "0.6");
edge([[800, 416], [800, 438]], "1.0");
edge([[842, 450], [872, 416]], "1.0");

edge([[950, 500], [1222, 500]], "0.6", {
  dashed: true, changed: ["0.9"], lpos: [1086, 494],
  label: [["0.6", "通知（await，等 2 秒）"], ["0.9", "通知（背景執行）"]],
});
edge([[1222, 400], [1152, 400]], "0.6");
edge([[966, 400], [950, 400]], "0.6");
edge([[1152, 446], [1222, 446]], "1.0");
edge([[1152, 210], [1222, 210]], "0.2");

edge([[570, 556], [570, 538], [956, 538], [956, 571], [966, 571]], "0.14");
edge([[634, 584], [652, 584]], "0.16");
edge([[716, 612], [716, 668], [1222, 668]], "0.16", { label: "只給統計，不給事件細節", lpos: [740, 662], lanchor: "start" });
edge([[1222, 704], [760, 704], [760, 612]], "0.16", { until: "0.16", label: "生成的文字", lpos: [1100, 698] });
edge([[780, 604], [966, 604]], "0.16", { until: "0.16" });
edge([[1222, 704], [872, 704], [872, 612]], "0.17", { label: "生成的文字", lpos: [1100, 698] });
edge([[946, 604], [966, 604]], "0.17");
edge([[1152, 571], [1222, 571]], "0.14");
edge([[1152, 614], [1222, 614]], "0.16");

// --------------------------------------------------
// 繪製
// --------------------------------------------------
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const isAscii = (s) => [...s].every((c) => c.charCodeAt(0) < 128);

function stateOf(item, t) {
  if (item.since === t) return "new";
  if (item.changed.includes(t)) return "changed";
  return "old";
}

function visible(item, t) {
  if (vi(item.since) > vi(t)) return false;
  if (item.until && vi(t) > vi(item.until)) return false;
  return true;
}

function atVersion(variants, t) {
  let cur = variants[0][1];
  for (const [since, value] of variants) if (vi(since) <= vi(t)) cur = value;
  return cur;
}

function text(x, y, s, o = {}) {
  const size = o.size || 13, fill = o.fill || "#333", weight = o.weight || "normal", anchor = o.anchor || "middle";
  const mono = o.mono === undefined ? isAscii(s) : o.mono;
  return `<text x="${x}" y="${y}" font-family="${mono ? MONO : SANS}" font-size="${size}" fill="${fill}" ` +
    `font-weight="${weight}" text-anchor="${anchor}">${esc(s)}</text>`;
}

function lockIcon(x, y, color) {
  return `<g transform="translate(${x},${y})" fill="none" stroke="${color}" stroke-width="1.4">` +
    `<rect x="-5" y="-1" width="10" height="8" rx="1.5" fill="${color}" stroke="none"/>` +
    `<path d="M-3,-1 v-3 a3,3 0 0 1 6,0 v3"/></g>`;
}

function badge(x2, y, v, st) {
  const label = `v${v}`;
  const w = label.length * 6.4 + 10;
  const [bg, fg] = st === "new" ? ["#1f9d4c", "#fff"] : ["#e9ebee", "#5b616b"];
  return `<rect x="${x2 - w}" y="${y - 8}" width="${w}" height="15" rx="7.5" fill="${bg}"/>` +
    text(x2 - w / 2, y + 3.5, label, { size: 10, fill: fg, mono: true });
}

function render(t) {
  if (!VERS.includes(t)) throw new Error(`沒有這個版本：${t}`);
  const out = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">`, "<defs>"];
  for (const [name, p] of Object.entries(PALETTE)) {
    out.push(`<marker id="arr-${name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" ` +
      `orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="${p.line}"/></marker>`);
  }
  out.push("</defs>");
  out.push(`<rect width="${W}" height="${H}" fill="#ffffff"/>`);

  // 標題和圖例
  const [title, chapter] = TITLES[t];
  out.push(text(24, 40, `v${t}　${title}`, { size: 22, fill: "#1f2328", weight: "bold", anchor: "start", mono: false }));
  out.push(text(24, 64, `這一章：${chapter}　｜　箭頭 = 資料往哪裡走　｜　小標籤 = 第幾版出現`,
    { size: 13, fill: "#6b7280", anchor: "start", mono: false }));
  let lx = 760;
  for (const [st, label] of [["old", "之前就有"], ["new", "這一章新增"], ["changed", "這一章改了"]]) {
    const p = PALETTE[st];
    out.push(`<rect x="${lx}" y="27" width="16" height="16" rx="3" fill="${p.fill}" stroke="${p.stroke}" stroke-width="1.5"/>`);
    out.push(text(lx + 22, 40, label, { size: 12, fill: "#444", anchor: "start", mono: false }));
    lx += 112;
  }
  out.push(`<line x1="${lx}" y1="35" x2="${lx + 30}" y2="35" stroke="#8a9099" stroke-width="1.6" stroke-dasharray="5 4"/>`);
  out.push(text(lx + 36, 40, "背景執行", { size: 12, fill: "#444", anchor: "start", mono: false }));
  lx += 104;
  out.push(`<line x1="${lx}" y1="35" x2="${lx + 30}" y2="35" stroke="#d33a3a" stroke-width="1.6" stroke-dasharray="5 4"/>`);
  out.push(text(lx + 36, 40, "錯誤回應", { size: 12, fill: "#444", anchor: "start", mono: false }));

  const badges = [];
  const order = { frame: 0, group: 1 };
  const shown = E.filter((e) => visible(e, t)).sort((a, b) => (order[a.kind] ?? 2) - (order[b.kind] ?? 2));
  for (const e of shown) {
    const st = stateOf(e, t);
    const p = PALETTE[e.kind === "error" ? "error" : st];
    const ls = atVersion(e.lines, t);
    const { x, y, w, h, kind: k } = e;
    const sw = st !== "old" ? 2 : 1.3;

    if (k === "frame") {
      const dash = e.dashed ? ' stroke-dasharray="7 5"' : "";
      const fill = e.dashed ? "none" : "#fbfbfc";
      const stroke = st !== "old" ? p.stroke : "#9aa0a8";
      out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="16" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"${dash}/>`);
      if (e.dashed) {
        out.push(text(x + 14, y + h - 7, ls[0], { size: 12, fill: p.text, anchor: "start", mono: false }));
        badges.push([x + 14 + ls[0].length * 12.5 + 46, y + h - 11, e.since, st]);
      } else {
        out.push(text(x + 16, y + 28, ls[0], { size: 16, fill: "#1f2328", weight: "bold", anchor: "start", mono: false }));
      }
      continue;
    }

    if (k === "group") {
      if (e.solid) {
        out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${p.fill}" stroke="${p.stroke}" stroke-width="${sw}"/>`);
        out.push(text(x + 12, y + 22, ls[0], { size: 13, fill: p.text, weight: "bold", anchor: "start" }));
      } else {
        out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="none" stroke="${p.stroke}" stroke-width="${sw}" stroke-dasharray="5 4"/>`);
        out.push(text(x + 10, y + 14, ls[0], { size: 10.5, fill: p.text, anchor: "start" }));
      }
      if (e.badge) badges.push([x + w - 4, y, e.since, st]);
      continue;
    }

    if (k === "note") {
      const fill = st !== "old" ? PALETTE[st].text : "#6b7280";
      out.push(text(x, y, ls[0], { size: e.size || 12, fill, anchor: e.anchor || "middle", mono: false }));
      continue;
    }

    const rx = { port: h / 2, chip: h / 2, error: h / 2, actor: 12, external: 12 }[k] ?? 8;
    const fill = (["port", "actor", "external"].includes(k) && st === "old") ? "#ffffff" : p.fill;
    const dash = k === "external" ? ' stroke-dasharray="6 4"' : "";
    if (k === "store" && !e.labelTop) {
      out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${fill}" stroke="${p.stroke}" stroke-width="${sw}"/>` +
        `<path d="M${x},${y + 8} h${w}" stroke="${p.stroke}" stroke-width="1"/>`);
    } else {
      out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${p.stroke}" stroke-width="${sw}"${dash}/>`);
    }

    let cx = x + w / 2;
    if (e.lock && visible({ since: e.lock }, t)) {
      const lk = e.lock === t ? "new" : (t === "1.1" ? "changed" : "old");
      out.push(lockIcon(x + 15, y + h / 2 - 1, PALETTE[lk].line));
      cx += 7;
    }

    if (e.labelTop) {
      out.push(text(x + 10, y + 20, ls[0], { size: 13, fill: p.text, weight: "bold", anchor: "start" }));
    } else {
      const big = { actor: 15, external: 15, service: 13.5 }[k] ?? 10.5;
      const small = 10.5;
      if (ls.length === 1) {
        const size = k !== "chip" ? big : (e.id.startsWith("st_") ? 9.5 : 10.5);
        const bold = ["actor", "external", "service"].includes(k);
        out.push(text(cx, y + h / 2 + big * 0.36, ls[0], { size, fill: p.text, weight: bold ? "bold" : "normal" }));
      } else {
        const gap = ["actor", "external"].includes(k) ? 16 : 14;
        const top = y + h / 2 - (ls.length - 1) * gap / 2 + 4;
        ls.forEach((s, i) => {
          const first = i === 0 && ["actor", "external", "service", "store"].includes(k);
          out.push(text(cx, top + i * gap, s, { size: first ? big : small, fill: p.text, weight: first ? "bold" : "normal" }));
        });
      }
    }
    if (e.badge) badges.push([x + w + 4, y, e.since, st]);
  }

  for (const d of ED) {
    if (!visible(d, t)) continue;
    const st = d.error ? "error" : stateOf(d, t);
    const p = PALETTE[st];
    const pts = d.pts.map(([a, b]) => `${a},${b}`).join(" ");
    const dash = (d.dashed || d.error) ? ' stroke-dasharray="5 4"' : "";
    const marker = d.arrow ? ` marker-end="url(#arr-${st})"` : "";
    const sw = (st === "new" || st === "changed") ? 1.8 : 1.4;
    out.push(`<polyline points="${pts}" fill="none" stroke="${p.line}" stroke-width="${sw}"${dash}${marker}/>`);
    if (d.label) {
      const [lx2, ly2] = d.lpos;
      out.push(`<text x="${lx2}" y="${ly2}" font-family="${SANS}" font-size="10.5" fill="${p.text}" ` +
        `text-anchor="${d.lanchor}" stroke="#fff" stroke-width="4" paint-order="stroke">${esc(atVersion(d.label, t))}</text>`);
    }
  }

  for (const [bx, by, v, st] of badges) out.push(badge(bx, by, v, st));
  out.push("</svg>");
  return out.join("\n") + "\n";
}

if (typeof process !== "undefined" && process.argv && process.argv[1] && process.argv[1].endsWith("gen.js")) {
  const arg = process.argv[2] || "1.1";
  if (arg === "all") {
    const fs = require("fs");
    const path = require("path");
    for (const v of VERS) fs.writeFileSync(path.join(__dirname, `v${v}.svg`), render(v));
  } else {
    process.stdout.write(render(arg));
  }
}

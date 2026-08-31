const pptxgen = require("pptxgenjs");

// ---------- Palette ----------
const NAVY = "1B2A4A";
const NAVY_DARK = "121D33";
const STEEL = "3F5C82";
const ICE = "CADCFC";
const GOLD = "C9A227";
const WHITE = "FFFFFF";
const LIGHT_BG = "F4F6FA";
const CARD_BG = "FFFFFF";
const MUTED = "6B7A99";
const TEXT = "1B2A4A";
const RED = "A23B2E";
const GREEN = "2E6B4F";

const FONT_HEAD = "Cambria";
const FONT_BODY = "Calibri";

const W = 13.33, H = 7.5;

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "SIH26190 Team";
pres.company = "SIH26190";
pres.title = "Secure Digital Document Management System — Architecture";

// ---------- Helpers ----------
function bgSlide(color) {
  const s = pres.addSlide();
  s.background = { color };
  return s;
}

function pageNum(s, n) {
  s.addText(String(n), {
    x: W - 0.7, y: H - 0.5, w: 0.4, h: 0.3, fontFace: FONT_BODY, fontSize: 10,
    color: MUTED, align: "right", isTextBox: true, margin: 0,
  });
}

function kicker(s, text, opts) {
  opts = opts || {};
  s.addText(text.toUpperCase(), {
    x: opts.x != null ? opts.x : 0.6, y: opts.y != null ? opts.y : 0.45, w: 8, h: 0.35,
    fontFace: FONT_BODY, fontSize: 13, color: opts.color || GOLD, bold: true,
    charSpacing: 2, isTextBox: true, margin: 0,
  });
}

function title(s, text, opts) {
  opts = opts || {};
  s.addText(text, {
    x: opts.x != null ? opts.x : 0.6, y: opts.y != null ? opts.y : 0.78, w: opts.w || 11.8, h: opts.h || 0.9,
    fontFace: FONT_HEAD, fontSize: opts.size || 30, color: opts.color || NAVY, bold: true,
    isTextBox: true, margin: 0,
  });
}

function subtitle(s, text, opts) {
  opts = opts || {};
  s.addText(text, {
    x: opts.x != null ? opts.x : 0.6, y: opts.y != null ? opts.y : 1.5, w: opts.w || 11.8, h: opts.h || 0.5,
    fontFace: FONT_BODY, fontSize: opts.size || 14, color: opts.color || MUTED, italic: true,
    isTextBox: true, margin: 0,
  });
}

function card(s, x, y, w, h, opts) {
  opts = opts || {};
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill || CARD_BG },
    line: { color: opts.line || "E3E8F0", width: 1 },
    shadow: opts.noShadow ? undefined : { type: "outer", color: "1B2A4A", opacity: 0.12, blur: 8, offset: 2, angle: 90 },
  });
}

function bulletBox(s, x, y, w, h, items, opts) {
  opts = opts || {};
  const size = opts.size || 14;
  const color = opts.color || TEXT;
  const arr = items.map((it, i) => ({
    text: it,
    options: {
      bullet: { code: "25CF", color: opts.bulletColor || GOLD, indent: 18 },
      breakLine: i !== items.length - 1,
      color, fontSize: size, fontFace: FONT_BODY,
      paraSpaceAfter: opts.gap != null ? opts.gap : 10,
    },
  }));
  s.addText(arr, { x, y, w, h, isTextBox: true, margin: 0, valign: "top" });
}

function numberBadge(s, x, y, d, n, color) {
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color: color || GOLD }, line: { type: "none" } });
  s.addText(String(n), {
    x, y, w: d, h: d, align: "center", valign: "middle",
    fontFace: FONT_HEAD, fontSize: d > 0.4 ? 16 : 12, bold: true, color: NAVY_DARK,
    isTextBox: true, margin: 0,
  });
}

function box(s, x, y, w, h, label, sub, opts) {
  opts = opts || {};
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.07,
    fill: { color: opts.fill || STEEL },
    line: { color: opts.line || "FFFFFF", width: opts.lineW || 0 },
  });
  s.addText(label, {
    x: x + 0.08, y: y + (sub ? 0.08 : 0), w: w - 0.16, h: sub ? h - 0.34 : h,
    align: "center", valign: sub ? "top" : "middle",
    fontFace: FONT_BODY, fontSize: opts.size || 12, bold: true, color: opts.color || WHITE,
    isTextBox: true, margin: 0,
  });
  if (sub) {
    s.addText(sub, {
      x: x + 0.08, y: y + h - 0.30, w: w - 0.16, h: 0.28,
      align: "center", valign: "top",
      fontFace: FONT_BODY, fontSize: 8.5, color: opts.subColor || ICE,
      isTextBox: true, margin: 0,
    });
  }
}

function arrowH(s, x1, y, x2, opts) {
  opts = opts || {};
  s.addShape("line", {
    x: x1, y, w: x2 - x1, h: 0,
    line: { color: opts.color || STEEL, width: opts.width || 1.75, endArrowType: "triangle" },
  });
}
function arrowV(s, x, y1, y2, opts) {
  opts = opts || {};
  s.addShape("line", {
    x, y: y1, w: 0, h: y2 - y1,
    line: { color: opts.color || STEEL, width: opts.width || 1.75, endArrowType: "triangle" },
  });
}
function arrowDiag(s, x1, y1, x2, y2, opts) {
  opts = opts || {};
  s.addShape("line", {
    x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color: opts.color || STEEL, width: opts.width || 1.5, endArrowType: "triangle" },
  });
}

function tinyLabel(s, x, y, w, text, color) {
  s.addText(text, {
    x, y, w, h: 0.25, align: "center",
    fontFace: FONT_BODY, fontSize: 8.5, italic: true, color: color || MUTED,
    isTextBox: true, margin: 0,
  });
}

function makeTable(s, rows, opts) {
  opts = opts || {};
  const colW = opts.colW;
  const header = rows[0].map((c) => ({
    text: c,
    options: { bold: true, color: WHITE, fill: { color: opts.headFill || NAVY }, fontFace: FONT_BODY, fontSize: opts.headSize || 11.5, align: "left", valign: "middle" },
  }));
  const body = rows.slice(1).map((r, ri) =>
    r.map((c) => ({
      text: c,
      options: {
        color: TEXT, fontFace: FONT_BODY, fontSize: opts.bodySize || 10.5, align: "left", valign: "top",
        fill: { color: ri % 2 === 0 ? "FFFFFF" : "EEF2F8" },
      },
    }))
  );
  s.addTable([header, ...body], {
    x: opts.x, y: opts.y, w: opts.w, colW,
    border: { type: "solid", color: "D8DFEA", pt: 0.5 },
    autoPage: false,
    rowH: opts.rowH,
  });
}

function statPill(s, x, y, w, h, num, label) {
  card(s, x, y, w, h, { fill: NAVY, line: NAVY, noShadow: true });
  s.addText(num, {
    x, y: y + 0.12, w, h: h - 0.55, align: "center", valign: "bottom",
    fontFace: FONT_HEAD, fontSize: 30, bold: true, color: GOLD, isTextBox: true, margin: 0,
  });
  s.addText(label, {
    x: x + 0.1, y: y + h - 0.42, w: w - 0.2, h: 0.36, align: "center", valign: "top",
    fontFace: FONT_BODY, fontSize: 10, color: ICE, isTextBox: true, margin: 0,
  });
}

// ============================================================
// SLIDE 1 — TITLE
// ============================================================
{
  const s = bgSlide(NAVY);
  s.addShape("ellipse", { x: 9.7, y: -2.3, w: 6, h: 6, fill: { color: NAVY_DARK }, line: { type: "none" } });
  s.addShape("ellipse", { x: -2.2, y: 5.0, w: 4.5, h: 4.5, fill: { color: STEEL }, line: { type: "none" }, });
  s.addShape("ellipse", { x: -2.2, y: 5.0, w: 4.5, h: 4.5, fill: { color: STEEL, transparency: 55 }, line: { type: "none" } });

  s.addText("SIH26190", {
    x: 0.9, y: 2.15, w: 8, h: 0.5, fontFace: FONT_BODY, fontSize: 15, color: GOLD, bold: true, charSpacing: 3,
    isTextBox: true, margin: 0,
  });
  s.addText("Secure Digital Document\nManagement System", {
    x: 0.9, y: 2.6, w: 10.8, h: 2.0, fontFace: FONT_HEAD, fontSize: 44, color: WHITE, bold: true,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.05,
  });
  s.addText("Architecture Design — v2  ·  Multi-Org Case, Evidence, Bail & Audit Platform", {
    x: 0.9, y: 4.55, w: 10.5, h: 0.5, fontFace: FONT_BODY, fontSize: 16, color: ICE, italic: true,
    isTextBox: true, margin: 0,
  });
  s.addText("Team Build Review  ·  Blockchain-anchored tamper evidence  ·  AI-assisted redaction  ·  Zero external SaaS", {
    x: 0.9, y: 6.55, w: 11, h: 0.4, fontFace: FONT_BODY, fontSize: 11.5, color: MUTED,
    isTextBox: true, margin: 0,
  });
}

// ============================================================
// SLIDE 2 — PROBLEM & SCOPE
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Problem & Scope");
  title(s, "One system, five kinds of institution, one criminal case");
  subtitle(s, "Police · Forensic labs · Hospitals · Courts · External verifiers (Bank / Telecom / RTO) all touch the same case record");

  const stages = [
    ["FIR", "Registration"], ["Investigation", "+ Evidence"], ["Bail Track", "(independent)"],
    ["Charge Sheet", "Filing"], ["Court", "Disposition"],
  ];
  const gap = 0.28, bw = (11.2 - gap * 4) / 5, by = 2.6;
  stages.forEach((st, i) => {
    const x = 0.9 + i * (bw + gap);
    box(s, x, by, bw, 1.15, st[0], st[1], { fill: i === 2 ? GOLD : STEEL, color: i === 2 ? NAVY_DARK : WHITE, subColor: i === 2 ? NAVY_DARK : ICE, size: 13 });
    if (i < stages.length - 1) arrowH(s, x + bw, by + 0.575, x + bw + gap, { color: MUTED });
  });
  tinyLabel(s, 0.9, by + 1.25, 11.2, "Investigation and Bail run on two independent timelines — neither blocks the other (see slide on concurrent tracks)", MUTED);

  bulletBox(s, 0.9, 4.55, 11.3, 2.3, [
    "Every document carries a field-level sensitivity schema — role-based redaction, decided by config, not by a model guessing at runtime",
    "Every state-changing action (upload, evidence submission, bail order, judgment) is hash-chained to a permissioned blockchain ledger for tamper evidence",
    "Standard encryption, RBAC, and append-only audit logging sit underneath all of it",
    "Out of MVP scope by conscious choice: POCSO/juvenile pathways, appeals, multi-jurisdiction transfer, compensation tracking",
  ], { size: 13.5, gap: 8 });
  pageNum(s, 2);
}

// ============================================================
// SLIDE 3 — CONSTRAINTS / SCALE TIER
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Scale Tier & Constraints");
  title(s, "Built for a judged demo — with a clear path to real scale");

  const stats = [["1 wk", "to demoable build"], ["5", "person team"], ["57", "document types mapped"], ["0", "external SaaS deps"]];
  const sw = 2.65, sgap = 0.22, sx = 0.9, sy = 2.15;
  stats.forEach((st, i) => statPill(s, sx + i * (sw + sgap), sy, sw, 1.5, st[0], st[1]));

  card(s, 0.9, 4.05, 11.5, 2.7, {});
  s.addText("Team profile", { x: 1.15, y: 4.25, w: 5, h: 0.35, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletBox(s, 1.15, 4.65, 5.2, 1.9, [
    "React-strong frontend developer",
    "CNN/ML background, pivoting to backend + owns AI Parser config",
    "Java-strong, conceptual Python",
    "General full-stack",
    "One strong pipeline-experienced generalist",
  ], { size: 12.5, gap: 6 });

  s.addShape("line", { x: 6.5, y: 4.3, w: 0, h: 2.25, line: { color: "D8DFEA", width: 1 } });

  s.addText("Governing rule for every choice below", { x: 6.85, y: 4.25, w: 5.35, h: 0.35, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletBox(s, 6.85, 4.65, 5.35, 1.9, [
    "Demonstrable correctness over production polish",
    "Anything heavier than needed is deferred with a stated trigger — not built because it looks impressive",
    "Scope grew mid-build (all 57 doc types, AI redaction layer) — timeline did not, so every add had to earn its place",
  ], { size: 12.5, gap: 8 });
  pageNum(s, 3);
}

// ============================================================
// SLIDE 4 — TECH STACK AT A GLANCE
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Technology Stack");
  title(s, "One backend language, end to end");
  subtitle(s, "Python everywhere except the browser — the one deliberate exception is named below");

  const items = [
    ["React", "Web App"], ["FastAPI", "API Server"], ["PostgreSQL", "Primary DB"], ["MinIO", "Object Storage"],
    ["Redis + Celery", "Job Queue"], ["PaddleOCR", "OCR Worker"], ["Presidio + spaCy", "AI Parser"], ["fabric-sdk-py", "Chain Worker"],
  ];
  const cols = 4, cw = 2.7, ch = 1.5, gx = 0.18, gy = 0.22, ox = 0.9, oy = 2.35;
  items.forEach((it, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = ox + col * (cw + gx), y = oy + row * (ch + gy);
    card(s, x, y, cw, ch, {});
    s.addText(it[0], { x: x + 0.12, y: y + 0.22, w: cw - 0.24, h: 0.55, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(it[1], { x: x + 0.12, y: y + 0.8, w: cw - 0.24, h: 0.4, fontFace: FONT_BODY, fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0 });
  });

  card(s, 0.9, 6.15, 11.5, 0.85, { fill: "FBF3DD", line: "E9D89A" });
  s.addText([
    { text: "One deliberate exception: ", options: { bold: true, color: NAVY } },
    { text: "fabric-sdk-py is Fabric's community-maintained SDK, less current than the Node/Java/Go paths — chosen for stack consistency, with the maturity risk explicitly accepted, not overlooked.", options: { color: TEXT } },
  ], { x: 1.15, y: 6.15, w: 11, h: 0.85, valign: "middle", fontFace: FONT_BODY, fontSize: 11.5, isTextBox: true, margin: 0 });
  pageNum(s, 4);
}

// ============================================================
// SLIDE 5 — C4 CONTEXT DIAGRAM
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Architecture — Context");
  title(s, "Who talks to the system");

  const actors = [
    "Victim / Complainant", "Duty Officer", "SHO", "Investigating Officer", "External Authority",
    "Public Prosecutor", "Court", "Defense / Accused", "System Admin", "Records / NCRB Analyst (new)",
  ];
  const ax = 0.7, ay = 1.85, aw = 2.05, ah = 0.43, agapY = 0.10;
  const step5 = ah + agapY;
  actors.forEach((a, i) => box(s, ax, ay + i * step5, aw, ah, a, null, { fill: i === 9 ? GOLD : STEEL, color: i === 9 ? NAVY_DARK : WHITE, size: 8.5 }));

  const sysH = actors.length * step5 - agapY;
  const sysX = 4.55, sysY = ay, sysW = 4.3;
  card(s, sysX, sysY, sysW, sysH, { fill: NAVY, line: NAVY, noShadow: true });
  s.addText("Secure Digital DMS", { x: sysX, y: sysY + sysH / 2 - 0.55, w: sysW, h: 0.5, align: "center", fontFace: FONT_HEAD, fontSize: 18, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("Case · Document · Evidence ·\nBail · Audit management", { x: sysX + 0.3, y: sysY + sysH / 2 - 0.02, w: sysW - 0.6, h: 0.9, align: "center", fontFace: FONT_BODY, fontSize: 11, color: ICE, isTextBox: true, margin: 0 });

  actors.forEach((_, i) => {
    const y = ay + i * step5 + ah / 2;
    arrowH(s, ax + aw, y, sysX - 0.05, { color: "C7CFDD", width: 1 });
  });

  const fx = 10.05, fw = 2.55, fh = 1.5;
  const fy = sysY + sysH / 2 - fh / 2;
  box(s, fx, fy, fw, fh, "Hyperledger\nFabric", "5-node permissioned ledger", { fill: GOLD, color: NAVY_DARK, subColor: NAVY_DARK, size: 13 });
  arrowH(s, sysX + sysW, sysY + sysH / 2, fx - 0.05, { color: GOLD, width: 2 });
  tinyLabel(s, sysX + sysW + 0.05, sysY + sysH / 2 - 0.42, fx - sysX - sysW - 0.1, "writes signed hashes", MUTED);
  pageNum(s, 5);
}

// ============================================================
// SLIDE 6 — C4 CONTAINER DIAGRAM
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Architecture — Containers");
  title(s, "Inside the system boundary");

  box(s, 0.7, 1.95, 2.3, 0.85, "Web App", "React SPA", { fill: STEEL, size: 12 });
  box(s, 3.55, 1.95, 2.5, 0.85, "API Server", "Python / FastAPI", { fill: NAVY, size: 12 });
  arrowH(s, 3.0, 2.375, 3.5, {});

  box(s, 6.6, 1.95, 2.35, 0.85, "Primary DB", "PostgreSQL", { fill: STEEL, size: 12 });
  box(s, 9.5, 1.95, 2.35, 0.85, "Object Storage", "MinIO (S3-compatible)", { fill: STEEL, size: 12 });
  arrowH(s, 6.05, 2.375, 6.55, {});
  arrowH(s, 8.95, 2.375, 9.45, {});

  box(s, 3.55, 3.35, 2.5, 0.75, "Job Queue", "Redis + Celery", { fill: NAVY_DARK, size: 12 });
  arrowV(s, 4.8, 2.8, 3.3, {});

  // Row 3: three workers + Fabric, evenly spaced, no overlaps
  const wy = 4.65, wh = 1.05, ww3 = 2.75, wgap3 = 0.3, wx0 = 0.7;
  const workers = [
    ["OCR & Extraction\nWorker", "Python / PaddleOCR", STEEL, WHITE, ICE],
    ["AI Parser\nWorker", "Presidio + spaCy NER", GOLD, NAVY_DARK, NAVY_DARK],
    ["Blockchain Write\nWorker", "Python / fabric-sdk-py", STEEL, WHITE, ICE],
    ["Hyperledger\nFabric", "5-node ledger", NAVY_DARK, WHITE, ICE],
  ];
  const wPos = workers.map((w, i) => wx0 + i * (ww3 + wgap3));
  workers.forEach((w, i) => {
    box(s, wPos[i], wy, ww3, wh, w[0], w[1], { fill: w[2], color: w[3], subColor: w[4], size: 11.5 });
  });

  // Queue fans out to OCR, AI Parser, and Chain Worker (all three are direct queue consumers)
  const qCenterX = 4.8, qBottomY = 4.10;
  [0, 1, 2].forEach((i) => {
    arrowDiag(s, qCenterX, qBottomY, wPos[i] + ww3 / 2, wy - 0.02, { color: MUTED, width: 1.25 });
  });
  // OCR enqueues the AI-parse job on extraction complete
  arrowH(s, wPos[0] + ww3, wy + wh / 2 - 0.1, wPos[1], { color: STEEL, width: 1.5 });
  // Chain Worker submits directly to Fabric
  arrowH(s, wPos[2] + ww3, wy + wh / 2, wPos[3], { color: GOLD, width: 1.75 });

  s.addText("Queue fans out to all three workers  ·  OCR enqueues the AI-parse job on completion  ·  Chain Worker submits to Fabric directly", {
    x: 0.7, y: wy + wh + 0.15, w: 11.9, h: 0.3, align: "center",
    fontFace: FONT_BODY, fontSize: 9.5, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });

  card(s, 0.7, 6.25, 11.85, 0.65, { fill: "EEF2F8", line: "D8DFEA" });
  s.addText([
    { text: "Three job types, three workers, single producer/consumer each. ", options: { bold: true, color: NAVY } },
    { text: "Hashing runs in parallel with OCR→AI-tagging, not behind it — the hash covers raw bytes, which never change regardless of tagging outcome.", options: { color: TEXT } },
  ], { x: 0.9, y: 6.25, w: 11.35, h: 0.65, valign: "middle", fontFace: FONT_BODY, fontSize: 10.5, isTextBox: true, margin: 0 });
  pageNum(s, 6);
}

// ============================================================
// SLIDE 7 — TECH CHOICE RATIONALE TABLE
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Decisions");
  title(s, "Why each technology, in one line");
  const rows = [
    ["Choice", "Why"],
    ["PostgreSQL over NoSQL", "Case/document/evidence/bail data is deeply relational — joins for stage-requirement checks matter more than schema flexibility"],
    ["Python/FastAPI for the API", "Whole backend standardized on Python; async fits the poll-heavy, queue-heavy request pattern"],
    ["Redis + Celery over BullMQ", "Backend is all-Python now — Celery is the mature, officially-supported choice; avoids a 2nd under-supported client library"],
    ["fabric-sdk-py for Chain Worker", "Stack consistency chosen deliberately over SDK maturity — risk accepted, not overlooked (see Fabric slide)"],
    ["Presidio + spaCy for AI Parser", "Purpose-built, self-hosted PII detection — not a generative LLM; needs config, not training data, to go live in-window"],
    ["MinIO over files-in-Postgres", "Binary evidence (CCTV, device dumps) doesn't belong in relational rows — object storage + DB reference is the standard split"],
  ];
  makeTable(s, rows, { x: 0.6, y: 2.05, w: 12.1, colW: [3.6, 8.5], bodySize: 12, headSize: 12.5 });
  pageNum(s, 7);
}

// ============================================================
// SLIDE 8 — CORE DATA MODEL
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Data Model");
  title(s, "Ten core resources");
  const items = [
    ["Organization / User", "One org per real institution; specialized police units are roles inside Police, not separate orgs"],
    ["Case", "crime_type, court_level, investigation_status, bail_status — the last two are independent columns"],
    ["Document", "Versioned, append-only — originals never overwritten"],
    ["EvidenceRequest", "N parallel requests per case, AND-join gate before charge-sheet filing"],
    ["BailRecord", "Tracks bail_status independently of investigation_status on the same case"],
    ["DocumentSchema", "Field-level sensitivity registry + AI Parser recognizer mappings, tiered by document type"],
    ["StageRequirements", "Config-driven mandatory-document/evidence rules per crime type"],
    ["CaseDiaryEntry", "Append-only running log the IO writes to (new this pass)"],
    ["AuditLog", "Append-only, hash-chained; includes AI Parser decisions + a meta-audit of who read them"],
  ];
  const cols = 3, cw = 3.9, ch = 1.55, gx = 0.15, gy = 0.15, ox = 0.6, oy = 2.05;
  items.forEach((it, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = ox + col * (cw + gx), y = oy + row * (ch + gy);
    card(s, x, y, cw, ch, {});
    s.addText(it[0], { x: x + 0.15, y: y + 0.13, w: cw - 0.3, h: 0.4, fontFace: FONT_HEAD, fontSize: 13.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(it[1], { x: x + 0.15, y: y + 0.55, w: cw - 0.3, h: 0.95, fontFace: FONT_BODY, fontSize: 10, color: TEXT, isTextBox: true, margin: 0, valign: "top" });
  });
  pageNum(s, 8);
}

// ============================================================
// SLIDE 9 — FLOW 1: FIR REGISTRATION
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Flow 1 — Synchronous");
  title(s, "FIR Registration & Case Creation");
  subtitle(s, "Victim needs the case number immediately — this stays synchronous end to end");

  const steps = [
    "Victim submits complaint + ID",
    "API creates Case + Document(complaint, ID) in one DB transaction",
    "Case number assigned",
    "Blockchain hash-write job enqueued (async, doesn't block the response)",
    "201 Created — case number shown to victim immediately",
  ];
  let sy = 2.35;
  steps.forEach((st, i) => {
    numberBadge(s, 0.9, sy, 0.42, i + 1, i === steps.length - 1 ? GREEN : GOLD);
    s.addText(st, { x: 1.5, y: sy - 0.04, w: 10.4, h: 0.55, fontFace: FONT_BODY, fontSize: 14, color: TEXT, valign: "middle", isTextBox: true, margin: 0 });
    if (i < steps.length - 1) arrowV(s, 1.11, sy + 0.42, sy + 0.78, { color: "C7CFDD", width: 1.5 });
    sy += 0.82;
  });
  pageNum(s, 9);
}

// ============================================================
// SLIDE 10 — FLOW 2: DOCUMENT PIPELINE (core differentiator)
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Flow 2 — The Core Differentiator");
  title(s, "Upload → OCR → AI-Parsed Redaction → Blockchain Hash", { size: 26 });

  box(s, 0.6, 1.95, 2.1, 0.7, "Upload", "202 Accepted, doc_id", { fill: NAVY, size: 12 });
  arrowH(s, 2.7, 2.3, 3.15, {});

  // Track A: hashing
  s.addText("TRACK A — HASHING (independent of tagging)", { x: 3.25, y: 1.55, w: 9.3, h: 0.3, fontFace: FONT_BODY, fontSize: 10.5, bold: true, color: GOLD, isTextBox: true, margin: 0 });
  box(s, 3.25, 1.95, 2.3, 0.7, "Chain Worker", "sign + submit", { fill: GOLD, color: NAVY_DARK, subColor: NAVY_DARK, size: 11.5 });
  arrowH(s, 5.6, 2.3, 6.05, {});
  box(s, 6.05, 1.95, 2.3, 0.7, "Fabric", "block confirmed", { fill: GOLD, color: NAVY_DARK, subColor: NAVY_DARK, size: 11.5 });
  arrowH(s, 8.4, 2.3, 8.85, {});
  box(s, 8.85, 1.95, 2.7, 0.7, "chain_status =\nconfirmed", null, { fill: STEEL, size: 11 });

  // Track B: extraction+tagging
  s.addText("TRACK B — EXTRACTION + AUTO-REDACTION (text documents only)", { x: 3.25, y: 3.05, w: 9.3, h: 0.3, fontFace: FONT_BODY, fontSize: 10.5, bold: true, color: STEEL, isTextBox: true, margin: 0 });
  box(s, 3.25, 3.45, 2.3, 0.8, "OCR Worker", "PaddleOCR extract", { fill: STEEL, size: 11.5 });
  arrowH(s, 5.6, 3.85, 6.05, {});
  box(s, 6.05, 3.45, 2.7, 0.8, "AI Parser", "Presidio + spaCy tag", { fill: STEEL, size: 11.5 });
  arrowH(s, 8.8, 3.85, 9.25, {});
  box(s, 9.25, 3.45, 2.3, 0.8, "status = ready\n(redacted view)", null, { fill: NAVY, size: 10.5 });

  card(s, 3.25, 4.55, 8.3, 0.85, { fill: "FBEDEA", line: "E7C6BE" });
  s.addText([
    { text: "Fail-safe: ", options: { bold: true, color: RED } },
    { text: "if AI Parser tagging fails repeatedly → document defaults to fully redacted + flagged \"needs review\", never fully exposed. Officer can still correct any tag via redact-tag (human override retained).", options: { color: TEXT } },
  ], { x: 3.5, y: 4.55, w: 7.8, h: 0.85, valign: "middle", fontFace: FONT_BODY, fontSize: 10.5, isTextBox: true, margin: 0 });

  s.addText("Binary evidence (CCTV / device dumps): skip OCR + AI Parser — hash the raw file directly.", {
    x: 0.6, y: 5.65, w: 11.9, h: 0.3, fontFace: FONT_BODY, fontSize: 10.5, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });

  card(s, 0.6, 6.15, 11.9, 0.95, { fill: NAVY, line: NAVY, noShadow: true });
  s.addText([
    { text: "Both tracks finish → ", options: { color: ICE } },
    { text: "GET /documents/:id (poll) returns a role-filtered, redacted view using the auto-tagged spans. ", options: { bold: true, color: WHITE } },
    { text: "No WebSockets anywhere — short polling is the simplest thing that works at this scale.", options: { color: ICE } },
  ], { x: 0.85, y: 6.15, w: 11.4, h: 0.95, valign: "middle", fontFace: FONT_BODY, fontSize: 11.5, isTextBox: true, margin: 0 });
  pageNum(s, 10);
}

// ============================================================
// SLIDE 11 — AI PARSER DEEP DIVE
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "AI Parser Worker");
  title(s, "Automatic redaction — without an LLM");

  card(s, 0.6, 1.95, 5.75, 4.5, {});
  s.addText("What it actually is", { x: 0.85, y: 2.15, w: 5.25, h: 0.4, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletBox(s, 0.85, 2.6, 5.25, 3.65, [
    "Presidio + spaCy NER, self-hosted — pattern recognizers + a pretrained named-entity model",
    "Classical NLP, not a generative model: no prompt-assembly, no LLM API call, no token-budget concern",
    "\"Training\" is reframed as one-time config: map entity types (name, phone, medical condition...) to each DocumentSchema's sensitivity fields",
    "Fully automatic at runtime after that config step — no human in the loop per document",
    "Runs entirely local — the \"zero external SaaS dependency\" claim survives fully intact",
  ], { size: 12.5, gap: 10 });

  card(s, 6.55, 1.95, 5.75, 4.5, {});
  s.addText("Honest limitation, stated up front", { x: 6.8, y: 2.15, w: 5.25, h: 0.4, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletBox(s, 6.8, 2.6, 5.25, 3.65, [
    "Off-the-shelf NER is trained on general text — not Indian legal/medical/police-report language",
    "Expect real gaps on domain-specific fields (FIR section numbers, caste/religion fields, diagnosis codes) until recognizer patterns are tuned",
    "This is exactly why the manual redact-tag override matters — it's the safety net for a system that will misclassify some spans out of the box",
    "Fail-safe direction: on repeated failure, default to fully redacted, never fully exposed — failing closed is the only acceptable direction here",
  ], { size: 12.5, gap: 10, bulletColor: RED });
  pageNum(s, 11);
}

// ============================================================
// SLIDE 12 — AI PARSER AUDIT & SECURITY
// ============================================================
{
  const s = bgSlide(NAVY);
  kicker(s, "Security — asked directly by the team", { color: GOLD });
  title(s, "Can we prove what the AI redacted, and who looked at it?", { color: WHITE, size: 26 });

  const rowsL = [
    ["Logged", "Every auto-tag and every human correction — same append-only, hash-chained audit log as any other action"],
    ["Never logged", "The actual redacted text itself — only metadata (entity type, location, confidence). Otherwise the audit log becomes the leak redaction was meant to stop"],
  ];
  let ly = 2.1;
  rowsL.forEach((r) => {
    card(s, 0.7, ly, 5.85, 1.55, { fill: NAVY_DARK, line: NAVY_DARK, noShadow: true });
    s.addText(r[0], { x: 0.95, y: ly + 0.15, w: 5.35, h: 0.35, fontFace: FONT_HEAD, fontSize: 14, bold: true, color: GOLD, isTextBox: true, margin: 0 });
    s.addText(r[1], { x: 0.95, y: ly + 0.55, w: 5.35, h: 0.95, fontFace: FONT_BODY, fontSize: 11.5, color: ICE, isTextBox: true, margin: 0, valign: "top" });
    ly += 1.75;
  });

  const rowsR = [
    ["Default access", "Most roles see only an aggregate line: \"3 fields auto-tagged, 1 corrected\" — never the specifics"],
    ["Full detail", "Entity-level detail (which field, confidence, who corrected) is System Admin only, via GET /cases/:id/audit-log/ai-parser"],
    ["Meta-audit", "Every read of that endpoint is itself logged — we know who has ever looked at the AI's decisions, not just that the decisions are tamper-evident"],
  ];
  let ry = 2.1;
  const rh = [1.15, 1.15, 1.15];
  rowsR.forEach((r, i) => {
    card(s, 6.75, ry, 5.9, rh[i], { fill: NAVY_DARK, line: NAVY_DARK, noShadow: true });
    s.addText(r[0], { x: 7.0, y: ry + 0.1, w: 5.4, h: 0.3, fontFace: FONT_HEAD, fontSize: 13, bold: true, color: GOLD, isTextBox: true, margin: 0 });
    s.addText(r[1], { x: 7.0, y: ry + 0.42, w: 5.4, h: 0.65, fontFace: FONT_BODY, fontSize: 10.5, color: ICE, isTextBox: true, margin: 0, valign: "top" });
    ry += rh[i] + 0.2;
  });

  card(s, 0.7, 6.05, 11.4, 0.8, { fill: GOLD, line: GOLD, noShadow: true });
  s.addText("No bulk / cross-case export on this endpoint — one case at a time, so a single compromised Admin credential can't pull the whole redaction history in one request.", {
    x: 0.95, y: 6.05, w: 10.9, h: 0.8, valign: "middle", fontFace: FONT_BODY, fontSize: 11.5, bold: true, color: NAVY_DARK, isTextBox: true, margin: 0,
  });
  pageNum(s, 12);
}

// ============================================================
// SLIDE 13 — FLOW 3: EVIDENCE REQUESTS + CHARGE SHEET
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Flow 3 — AND-Join Gate");
  title(s, "Parallel Evidence Requests → Charge Sheet Filing");

  s.addText("IO creates N independent requests — any order, any timing", { x: 0.6, y: 1.85, w: 11.5, h: 0.35, fontFace: FONT_BODY, fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  const auths = ["Bank", "Telecom", "Digital FSL"];
  const aw = 3.55, agap = 0.28, ax = 0.9, ay = 2.35;
  auths.forEach((a, i) => {
    const x = ax + i * (aw + agap);
    box(s, x, ay, aw, 0.85, a, "submits independently", { fill: STEEL, size: 13 });
    arrowV(s, x + aw / 2, ay + 0.85, ay + 1.35, {});
    box(s, x, ay + 1.35, aw, 0.6, "status = completed", null, { fill: "8CA6C4", size: 11 });
  });

  s.addShape("line", { x: 0.9, y: ay + 2.15, w: 10.4, h: 0, line: { color: MUTED, width: 1, dashType: "dash" } });
  s.addText("AND-JOIN — all three converge here", { x: 0.9, y: ay + 2.2, w: 10.4, h: 0.3, align: "center", fontFace: FONT_BODY, fontSize: 10, italic: true, color: MUTED, isTextBox: true, margin: 0 });

  const gy = ay + 2.60;
  box(s, 3.9, gy, 3.4, 0.7, "Prosecutor:\nfile-charge-sheet", null, { fill: NAVY, size: 12 });
  arrowV(s, 5.6, gy + 0.7, gy + 1.0, {});
  card(s, 1.4, gy + 1.0, 4.5, 0.8, { fill: "E9F3EE", line: "BFDFCF" });
  s.addText("✓ All mandatory satisfied\n200 — charge sheet filed", { x: 1.6, y: gy + 1.0, w: 4.1, h: 0.8, valign: "middle", fontFace: FONT_BODY, fontSize: 11.5, bold: true, color: GREEN, isTextBox: true, margin: 0 });
  card(s, 6.3, gy + 1.0, 4.5, 0.8, { fill: "FBEDEA", line: "E7C6BE" });
  s.addText("✗ Missing items\n409 — explicit list returned", { x: 6.5, y: gy + 1.0, w: 4.1, h: 0.8, valign: "middle", fontFace: FONT_BODY, fontSize: 11.5, bold: true, color: RED, isTextBox: true, margin: 0 });

  tinyLabel(s, 0.6, gy + 1.95, 11.5, "Validated against Stage Requirements config — which documents/requests are mandatory vs. optional, per crime type", MUTED);
  pageNum(s, 13);
}

// ============================================================
// SLIDE 14 — FLOW 4: BAIL TRACK + CONCURRENT STATE
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Flow 4 — Runs Independently");
  title(s, "The Bail Track — the demo's core differentiator");
  subtitle(s, "Domestic Violence chosen as the showcase case — it's the only women-safety case with a confirmed bail pathway (\"Yes\")");

  const steps = ["Arrest\nrecorded", "Application\nfiled", "Hearing\nscheduled", "Order\nissued", "Surety\nregistered"];
  const bw2 = 2.05, bgap = 0.22, bx = 0.7, byy = 2.55;
  steps.forEach((st, i) => {
    const x = bx + i * (bw2 + bgap);
    box(s, x, byy, bw2, 0.85, st, null, { fill: GOLD, color: NAVY_DARK, size: 11.5 });
    if (i < steps.length - 1) arrowH(s, x + bw2, byy + 0.425, x + bw2 + bgap, { color: GOLD });
  });
  s.addText("IO/Police → Defense/Accused → Court → Court → Defense/Accused", { x: 0.7, y: byy + 0.95, w: 11.6, h: 0.3, align: "center", fontFace: FONT_BODY, fontSize: 10, italic: true, color: MUTED, isTextBox: true, margin: 0 });

  card(s, 0.7, 4.1, 11.9, 2.85, { fill: LIGHT_BG, line: "D8DFEA" });
  s.addText("Why this matters architecturally", { x: 0.95, y: 4.3, w: 6, h: 0.35, fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletBox(s, 0.95, 4.7, 5.6, 2.1, [
    "investigation_status and bail_status are two independent columns on the same case row",
    "Neither blocks the other — a case can be \"Charge Sheet Ready\" while bail is still \"Hearing Scheduled\", and vice versa",
  ], { size: 12.5, gap: 10 });

  s.addShape("line", { x: 6.85, y: 4.35, w: 0, h: 2.4, line: { color: "D8DFEA", width: 1 } });
  s.addText("Why Domestic Violence, specifically", { x: 7.2, y: 4.3, w: 5.2, h: 0.35, fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletBox(s, 7.2, 4.7, 5.2, 2.1, [
    "Bail pathway confirmed \"Yes\" — the demo can show both tracks live",
    "Rape's pathway is unconfirmed / typically non-bailable — bail-track half of the demo would sit empty",
    "Stronger redaction story than Cyber Fraud, given NCRB / Women Safety Division ownership",
  ], { size: 12.5, gap: 10 });
  pageNum(s, 14);
}

// ============================================================
// SLIDE 15 — ROLE & AUTHORITY TAXONOMY
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "RBAC Foundation");
  title(s, "25 roles across 5 institution types");
  subtitle(s, "Internal specialized police units are roles inside the Police org — not separate organizations");

  const groups = [
    ["Case-initiating", "Victim / Complainant / Owner", STEEL],
    ["Internal — police (general)", "Duty Officer · SHO · Investigating Officer", STEEL],
    ["Internal — specialized police units", "Women Cell · Cyber Cell · Narcotics Police · Traffic Police · Crime Scene Unit · Rescue Team · Counselor", NAVY],
    ["External authorities (own org each)", "FSL · Digital FSL · Hospital · Bank · Telecom · RTO", STEEL],
    ["Judiciary (own org each)", "Magistrate Court · Sessions Court · NDPS Court", STEEL],
    ["Legal / platform / other", "Public Prosecutor · System Admin · Defense/Accused (submission-only)", STEEL],
  ];
  let gy2 = 2.05;
  groups.forEach((g) => {
    card(s, 0.6, gy2, 8.05, 0.72, {});
    s.addShape("roundRect", { x: 0.6, y: gy2, w: 0.12, h: 0.72, fill: { color: g[2] }, line: { type: "none" }, rectRadius: 0 });
    s.addText(g[0], { x: 0.9, y: gy2 + 0.06, w: 7.6, h: 0.28, fontFace: FONT_BODY, fontSize: 10.5, bold: true, color: MUTED, isTextBox: true, margin: 0 });
    s.addText(g[1], { x: 0.9, y: gy2 + 0.32, w: 7.6, h: 0.36, fontFace: FONT_BODY, fontSize: 11, color: TEXT, isTextBox: true, margin: 0 });
    gy2 += 0.84;
  });

  card(s, 8.9, 2.05, 3.75, 4.9, { fill: "FBF3DD", line: "E9D89A" });
  s.addText("New this pass", { x: 9.15, y: 2.25, w: 3.25, h: 0.35, fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText("Records / NCRB Analyst", { x: 9.15, y: 2.7, w: 3.25, h: 0.35, fontFace: FONT_BODY, fontSize: 13, bold: true, color: GOLD, isTextBox: true, margin: 0 });
  bulletBox(s, 9.15, 3.1, 3.25, 3.7, [
    "Sees de-identified case metadata only — no identity/sensitive fields, even in redacted form",
    "Backed by a dedicated Postgres view, not a new redaction system",
    "Wasn't in the endpoint table or RBAC model at all until this review",
  ], { size: 11.5, gap: 10 });
  pageNum(s, 15);
}

// ============================================================
// SLIDE 16 — ACCESS MODEL SUMMARY
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Access Model");
  title(s, "Who sees what, at a glance");
  const rows = [
    ["Role", "Sees", "Cannot see"],
    ["Duty Officer", "Complaint, ID, FIR registration fields", "Forensic reports, sensitive statement content"],
    ["Investigating Officer", "Full case file for assigned case", "Other officers' unrelated cases"],
    ["External Authority", "Only the specific request routed to them + their own report", "Rest of case file; victim identity beyond what's needed"],
    ["Women Cell", "Full case file for women-safety cases, redaction-toggle view", "—"],
    ["Public Prosecutor", "Charge sheet, evidence list, case file", "Internal IO notes not marked for court"],
    ["Court", "Complete case file as filed", "Pre-charge-sheet internal drafts"],
    ["Defense / Accused", "Own bail-related submissions only", "Investigation materials during active investigation"],
    ["Records / NCRB Analyst", "De-identified case metadata only", "Any sensitive or identity field"],
  ];
  makeTable(s, rows, { x: 0.6, y: 2.0, w: 12.1, colW: [2.6, 4.9, 4.6], bodySize: 10.8, headSize: 12 });
  pageNum(s, 16);
}

// ============================================================
// SLIDE 17 — DOCUMENT TAXONOMY / TIERED SCHEMA
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "DocumentSchema Build Plan");
  title(s, "57 document types, 3 tiers, ~2-3 days of work");

  const tiers = [
    ["TIER 1", "3 types", "FIR · MLC · Witness Statement", "Full custom schema — universal + highest sensitivity concentration", GOLD],
    ["TIER 2", "~10 types", "Domestic Violence showcase set + full Bail Lifecycle (6 types)", "Full custom schema — your one demo showcase case, built deep", STEEL],
    ["TIER 3", "~40+ types", "Every other canonical document type", "One generic default sensitivity profile, inherited until individually authored", NAVY],
  ];
  const tw = 3.85, tgap = 0.2, tx = 0.6, ty = 2.05, th = 3.15;
  tiers.forEach((t, i) => {
    const x = tx + i * (tw + tgap);
    card(s, x, ty, tw, th, { fill: t[4], line: t[4], noShadow: true });
    const textColor = i === 0 ? NAVY_DARK : WHITE;
    s.addText(t[0], { x: x + 0.2, y: ty + 0.2, w: tw - 0.4, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: textColor, isTextBox: true, margin: 0 });
    s.addText(t[1], { x: x + 0.2, y: ty + 0.6, w: tw - 0.4, h: 0.5, fontFace: FONT_HEAD, fontSize: 26, bold: true, color: i === 0 ? NAVY_DARK : GOLD, isTextBox: true, margin: 0 });
    s.addText(t[2], { x: x + 0.2, y: ty + 1.25, w: tw - 0.4, h: 0.85, fontFace: FONT_BODY, fontSize: 11, bold: true, color: textColor, isTextBox: true, margin: 0, valign: "top" });
    s.addText(t[3], { x: x + 0.2, y: ty + 2.15, w: tw - 0.4, h: 0.9, fontFace: FONT_BODY, fontSize: 10, color: i === 0 ? NAVY_DARK : ICE, isTextBox: true, margin: 0, valign: "top" });
  });

  card(s, 0.6, 5.45, 11.9, 1.55, {});
  s.addText([
    { text: "Reversed from an earlier \"build all 57 fully custom\" instruction. ", options: { bold: true, color: NAVY } },
    { text: "The source taxonomy document itself called that scope creep. This tiered plan still means \"every one of the 57 types has a schema\" — just not all at the same depth. Recognizer-mapping config owner: the ML-background teammate, working directly with whoever understands the legal/medical field semantics.", options: { color: TEXT } },
  ], { x: 0.85, y: 5.6, w: 11.4, h: 1.3, valign: "top", fontFace: FONT_BODY, fontSize: 11.5, isTextBox: true, margin: 0 });
  pageNum(s, 17);
}

// ============================================================
// SLIDE 18 — INTERFACE CONTRACTS OVERVIEW
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Interface Contracts");
  title(s, "36 endpoints across 8 resource groups");

  const rows = [
    ["Resource group", "Count", "New / changed this review"],
    ["Auth & Org", "3", "—"],
    ["Case lifecycle", "6", "Case Diary (create + list) — new"],
    ["Evidence requests", "3", "—"],
    ["Documents", "8", "needs_review filter — new; retry-chain-write idempotency rule specified; redact-tag now a correction path, not primary"],
    ["Bail track", "5", "—"],
    ["Trial / judgment", "2", "Both new — closes a state-diagram transition that had no endpoint at all"],
    ["Admin & config", "5", "Recognizer-mapping config endpoint — new"],
    ["Audit & reporting", "3", "AI-parser audit endpoint (Admin-only) — new; Records/NCRB reporting endpoint — new"],
  ];
  makeTable(s, rows, { x: 0.6, y: 2.05, w: 12.1, colW: [3.0, 1.4, 7.7], bodySize: 11, headSize: 12 });
  tinyLabel(s, 0.6, 6.75, 11.9, "Grew from 25 → 36 rows across this review's two gap-check passes", MUTED);
  pageNum(s, 18);
}

// ============================================================
// SLIDE 19 — ASYNC PATTERN DECISIONS
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Sync vs. Async");
  title(s, "Only what's actually slow goes on the queue");

  card(s, 0.6, 2.0, 5.75, 4.6, { fill: "E9F3EE", line: "BFDFCF" });
  s.addText("SYNCHRONOUS", { x: 0.85, y: 2.2, w: 5.25, h: 0.35, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: GREEN, isTextBox: true, margin: 0 });
  bulletBox(s, 0.85, 2.65, 5.25, 3.8, [
    "FIR registration — victim needs the case number immediately",
    "Document upload acknowledgment (202) — the processing after it is async",
    "Evidence request submission",
    "Charge sheet filing — fast DB validation + state transition",
    "All bail stage actions — fast state transitions",
    "All trial/judgment actions — same reasoning",
  ], { size: 12.5, gap: 10, bulletColor: GREEN });

  card(s, 6.6, 2.0, 5.75, 4.6, { fill: "EEF2F8", line: "D8DFEA" });
  s.addText("ASYNC — QUEUE + WORKER", { x: 6.85, y: 2.2, w: 5.25, h: 0.35, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: STEEL, isTextBox: true, margin: 0 });
  bulletBox(s, 6.85, 2.65, 5.25, 3.8, [
    "OCR / field extraction — slow, status via short-poll",
    "AI Parser tagging — chained after OCR, doc stays \"processing\" until done",
    "Blockchain hash-write — runs in parallel with OCR/AI-parse, not behind it",
  ], { size: 12.5, gap: 10, bulletColor: STEEL });

  card(s, 0.6, 6.75, 11.75, 0.6, { fill: NAVY, line: NAVY, noShadow: true });
  s.addText("No WebSockets anywhere in this design — short-polling a status endpoint is the simplest thing that works at this scale.", {
    x: 0.85, y: 6.75, w: 11.25, h: 0.6, valign: "middle", fontFace: FONT_BODY, fontSize: 11, italic: true, color: ICE, isTextBox: true, margin: 0,
  });
  pageNum(s, 19);
}

// ============================================================
// SLIDE 20 — ENVIRONMENTS + ZERO EXTERNAL SAAS
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Environments & Dependencies");
  title(s, "Every dependency, self-hosted");

  const rows = [
    ["Env", "What's different"],
    ["local / dev", "Dockerized Postgres, local Fabric test network (5 peers), MinIO container, synthetic seed data"],
    ["demo (judging day)", "Same stack, seeded with the real 15-case dataset; no seed-reset route once finalized"],
    ["production (stated, not built)", "Managed Postgres, real multi-org Fabric consortium, HSM-backed signing keys — named as the LATER target throughout"],
  ];
  makeTable(s, rows, { x: 0.6, y: 2.0, w: 7.4, colW: [2.4, 5.0], bodySize: 11, headSize: 12 });

  card(s, 8.25, 2.0, 4.45, 4.55, { fill: NAVY, line: NAVY, noShadow: true });
  s.addText("Zero external SaaS", { x: 8.5, y: 2.2, w: 3.95, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: GOLD, isTextBox: true, margin: 0 });
  bulletBox(s, 8.5, 2.7, 3.95, 3.7, [
    "Fabric, Postgres, MinIO, Redis/Celery, Presidio + spaCy — all self-hosted",
    "No LLM API. No external maps/payment/identity provider.",
    "This survived adding the \"AI\" component fully intact — worth stating precisely to judges",
  ], { size: 11.5, gap: 10, color: ICE, bulletColor: GOLD });
  pageNum(s, 20);
}

// ============================================================
// SLIDE 21 — CONCEPTS CHECKLIST HIGHLIGHTS
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "Build Checklist");
  title(s, "NOW vs. LATER vs. WATCHLIST");

  const cols = [
    ["NOW", GREEN, ["Docker + Compose everywhere", "Fail-safe: AI failure → redact closed, not open", "Chain Worker retry + manual recovery endpoint", "Rate limiting, TLS, encryption at rest", "CI/CD + trunk-based branching, lightweight review"]],
    ["LATER", STEEL, ["Automated chain-status reconciliation", "Recognizer active-learning / auto-tuning", "Self-service org onboarding", "Distributed tracing / full APM", "Formal DR runbook"]],
    ["WATCHLIST", MUTED, ["Kubernetes — team/timeline says no", "Kafka — Celery is correctly sized", "WebSockets — no real-time need identified", "CDN, load balancer, sharding — not this scale", "Full WCAG audit — baseline is enough for MVP"]],
  ];
  const cw2 = 3.85, cgap = 0.2, cx2 = 0.6, cy2 = 2.05;
  cols.forEach((c, i) => {
    const x = cx2 + i * (cw2 + cgap);
    card(s, x, cy2, cw2, 4.6, {});
    s.addShape("roundRect", { x, y: cy2, w: cw2, h: 0.55, fill: { color: c[1] }, line: { type: "none" }, rectRadius: 0.08 });
    s.addText(c[0], { x, y: cy2, w: cw2, h: 0.55, align: "center", valign: "middle", fontFace: FONT_HEAD, fontSize: 15, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    bulletBox(s, x + 0.22, cy2 + 0.75, cw2 - 0.44, 3.75, c[2], { size: 10.8, gap: 11, bulletColor: c[1] });
  });
  pageNum(s, 21);
}

// ============================================================
// SLIDE 22 — OPEN ITEMS / DECISIONS NEEDED
// ============================================================
{
  const s = bgSlide(WHITE);
  kicker(s, "For This Meeting");
  title(s, "What the team needs to decide right now");

  const items = [
    ["1", "Role-model capacity", "Can we build the full expanded role set (Women Cell, Cyber Cell, Records/NCRB Analyst, etc.) in the time left — or do some fold back into generic buckets for the demo?", GOLD],
    ["2", "Bail-pathway data gaps", "9 of 15 crime types have \"bail pathway not yet confirmed\" in the source data (some legally load-bearing, e.g. NDPS, sexual-offence classifications). Doesn't block the Domestic Violence demo — but a real gap if judges ask about other crime types.", STEEL],
  ];
  let iy = 2.1;
  items.forEach((it) => {
    card(s, 0.6, iy, 11.9, 1.9, {});
    numberBadge(s, 0.9, iy + 0.3, 0.6, it[0], it[3]);
    s.addText(it[1], { x: 1.75, y: iy + 0.22, w: 10.5, h: 0.4, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(it[2], { x: 1.75, y: iy + 0.68, w: 10.5, h: 1.1, fontFace: FONT_BODY, fontSize: 12, color: TEXT, isTextBox: true, margin: 0, valign: "top" });
    iy += 2.15;
  });
  tinyLabel(s, 0.6, 6.6, 11.9, "Everything else in the design doc is confirmed and buildable as-is.", MUTED);
  pageNum(s, 22);
}

// ============================================================
// SLIDE 23 — BUILD PRIORITY ORDER
// ============================================================
{
  const s = bgSlide(NAVY);
  kicker(s, "Execution Order", { color: GOLD });
  title(s, "Build priority for this session", { color: WHITE });

  const steps = [
    ["Stand up Fabric + confirm one signed hash tx end-to-end", "Highest setup risk — do this before anything else"],
    ["Trial/judgment endpoints", "Copy the bail hearing-notice/order pattern — ~15 min"],
    ["needs_review filter endpoint", "Plain filtered query, no new infra — ~15 min"],
    ["Team decision: specialized units = roles inside Police org", "5-minute alignment, unblocks RBAC work"],
    ["Case Diary feature", "New table + 2 endpoints — ~1-2 hrs"],
    ["Records/NCRB Analyst de-identified view + endpoint", "~1-2 hrs"],
    ["Wire Flow 2 end-to-end (OCR → AI Parser → redaction filter)", "The core differentiator — start early, it's the riskiest integration"],
    ["Recognizer-mapping config for Tier 1+2 document types", "ML-background teammate — real domain work, start now"],
  ];
  let sy2 = 1.8;
  steps.forEach((st, i) => {
    numberBadge(s, 0.7, sy2, 0.5, i + 1, GOLD);
    s.addText(st[0], { x: 1.4, y: sy2 - 0.03, w: 8.2, h: 0.4, fontFace: FONT_BODY, fontSize: 13, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(st[1], { x: 9.75, y: sy2 - 0.03, w: 2.75, h: 0.5, fontFace: FONT_BODY, fontSize: 9, italic: true, color: ICE, isTextBox: true, margin: 0, valign: "top" });
    sy2 += 0.62;
  });
  pageNum(s, 23);
}

// ============================================================
// SLIDE 24 — DISCUSSION
// ============================================================
{
  const s = bgSlide(NAVY);
  s.addShape("ellipse", { x: -2.5, y: -2.5, w: 6, h: 6, fill: { color: NAVY_DARK }, line: { type: "none" } });
  s.addShape("ellipse", { x: 9.5, y: 4.5, w: 5.5, h: 5.5, fill: { color: STEEL, transparency: 55 }, line: { type: "none" } });
  s.addText("Discussion", { x: 0.9, y: 2.9, w: 8, h: 1.0, fontFace: FONT_HEAD, fontSize: 40, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("Two decisions needed today · everything else is confirmed and buildable", {
    x: 0.9, y: 3.85, w: 9.5, h: 0.5, fontFace: FONT_BODY, fontSize: 15, italic: true, color: ICE, isTextBox: true, margin: 0,
  });
  s.addText("Full technical detail — endpoint contracts, arrow specs, state ownership — lives in the companion design document.", {
    x: 0.9, y: 6.6, w: 10, h: 0.4, fontFace: FONT_BODY, fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0,
  });
}

const outPath = "C:/Users/swaya/AppData/Local/Temp/claude/C--projects-N8N-automations-Vibrant-Designs/518aa0a5-81bd-4fb1-ab65-8cd96217d654/scratchpad/SIH26190_Architecture.pptx";
pres.writeFile({ fileName: outPath }).then(() => console.log("WROTE", outPath));

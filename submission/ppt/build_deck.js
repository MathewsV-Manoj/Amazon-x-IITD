// Chakravyuh — RAKSHAM Round 1 presentation (PowerPoint).
// All numbers are read from eval/out/final.json (eval/final_numbers.py).
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const F = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../../eval/out/final.json"), "utf8"));
const C = F.chakravyuh, B = F.baselines;
const pct = (x, d = 1) => (x * 100).toFixed(d) + "%";
const ci = (m, d = 1) => `[${(m.lo * 100).toFixed(d)}%, ${(m.hi * 100).toFixed(d)}%]`;
const adv = Object.fromEntries(F.adversarial.map(a => [a.suppressed, a.recall]));
const abl = Object.fromEntries(F.ablation.map(a => [a.removed, a.recall]));
const loo = F.loo.map(d => d.recall);
const UPPER_CR = Math.round(22845 * 0.02 * C.recall.mean);
const SESSIONS = 30e6 * 250;
const HOLDS_DAY = Math.round(SESSIONS * C.t3_fp.mean / 1000 / 365);
const AGENT_H = Math.round(HOLDS_DAY * 5 / 60);

// ---------- design tokens ----------
const NAVY = "111A2B", INK = "1B2433", INK2 = "3A4353", MUTED = "6E747E", RULE = "D9DCE1",
  TINT = "F3F4F6", ORANGE = "D9480F", ONNAVY = "ECE8E0", NAVYMUTED = "8E97A6", NAVYRULE = "2C3850", WHITE = "FFFFFF";
const HEAD = "Cambria", BODY = "Calibri";
const W = 13.333, H = 7.5, MX = 0.6;
const TOTAL = 16;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Mathews V Manoj";
pres.title = "Chakravyuh — RAKSHAM Round 1";

// ---------- helpers ----------
function base(n, section, dark = false) {
  const s = pres.addSlide();
  s.background = { color: dark ? NAVY : WHITE };
  if (section) {
    s.addText(section, { x: MX, y: 0.28, w: 6, h: 0.3, fontFace: BODY, fontSize: 11,
      color: dark ? NAVYMUTED : MUTED, margin: 0, isTextBox: true });
    s.addText("Chakravyuh", { x: W - MX - 3, y: 0.28, w: 3, h: 0.3, fontFace: BODY, fontSize: 11,
      color: dark ? NAVYMUTED : MUTED, align: "right", margin: 0, isTextBox: true });
    s.addText(`${n} / ${TOTAL}`, { x: W - MX - 2, y: H - 0.45, w: 2, h: 0.25, fontFace: BODY, fontSize: 10,
      color: dark ? NAVYMUTED : MUTED, align: "right", margin: 0, isTextBox: true });
  }
  return s;
}
function title(s, text, dark = false, y = 0.7, size = 34) {
  s.addText(text, { x: MX, y, w: W - 2 * MX, h: 0.8, fontFace: HEAD, fontSize: size, bold: true,
    color: dark ? ONNAVY : INK, margin: 0, valign: "top", isTextBox: true });
}
function text(s, t, o) {
  s.addText(t, Object.assign({ fontFace: BODY, fontSize: 15, color: INK2, margin: 0, valign: "top",
    isTextBox: true, paraSpaceAfter: 4 }, o));
}
function dot(s, x, y, d, fill, line) {
  s.addShape(pres.shapes.OVAL, { x: x - d / 2, y: y - d / 2, w: d, h: d,
    fill: { color: fill }, line: { color: line || fill, width: 1.5 } });
}
function hline(s, x, y, w, color, width = 1) {
  s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color, width } });
}
function vline(s, x, y, h, color, width = 1.5) {
  s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color, width } });
}
const HB = (c = RULE, pt = 0.75) => [{ type: "solid", pt, color: c }, { type: "none" }, { type: "solid", pt, color: c }, { type: "none" }];
function tag(s, word, x, y) {
  const style = { built: [INK, "solid"], measured: [INK, "solid"], simulated: [MUTED, "dash"],
    planned: [MUTED, "sysDot"], "design only": [MUTED, "dash"] }[word];
  s.addText(word, { x, y, w: 1.05, h: 0.26, fontFace: BODY, fontSize: 10, color: style[0], align: "center",
    valign: "middle", margin: 0, line: { color: style[0], width: 0.75, dashType: style[1] }, isTextBox: true });
}

// ============ 1. Cover ============
{
  const s = base(1, null, true);
  s.addText("RAKSHAM  ·  Amazon × IIT Delhi  ·  Round 1  ·  Track 2: AI-driven scam pattern recognition",
    { x: MX + 0.1, y: 0.45, w: 10, h: 0.3, fontFace: BODY, fontSize: 12, color: NAVYMUTED, margin: 0, isTextBox: true });
  s.addText("Chakravyuh", { x: MX + 0.1, y: 1.9, w: 8, h: 1.2, fontFace: HEAD, fontSize: 66, bold: true,
    color: ONNAVY, margin: 0, isTextBox: true });
  s.addText("Intercept the scam workflow,\nnot the transaction.", { x: MX + 0.1, y: 3.15, w: 8, h: 1.2,
    fontFace: HEAD, fontSize: 28, italic: true, color: ONNAVY, margin: 0, isTextBox: true });
  text(s, "Chakravyuh checks a UPI payment for the steps that usually come before a scam payment. " +
    "It interrupts only when several of them show up together, tells the customer why, and keeps a signed record for the bank.",
    { x: MX + 0.1, y: 4.55, w: 7.4, h: 1.0, fontSize: 15, color: NAVYMUTED });
  // motif: the four-stage chain, vertical
  const cx = 10.3, labels = ["Contact", "Control", "Extraction", "Cash-out", "Decision"];
  labels.forEach((l, i) => {
    const y = 1.95 + i * 0.72;
    if (i < 4) vline(s, cx, y, 0.72, i === 3 ? ORANGE : NAVYMUTED, 1.5);
    dot(s, cx, y, 0.2, i === 4 ? ORANGE : NAVY, i === 4 ? ORANGE : ONNAVY);
    s.addText(l, { x: cx + 0.3, y: y - 0.15, w: 2, h: 0.3, fontFace: BODY, fontSize: 14,
      color: i === 4 ? ORANGE : ONNAVY, margin: 0, isTextBox: true });
  });
  hline(s, MX + 0.1, 6.35, W - 2 * MX - 0.2, NAVYRULE, 0.75);
  s.addText([{ text: "Mathews V Manoj", options: { bold: true, color: ONNAVY } },
    { text: "   B.Tech Electronics & Communication, Muthoot Institute of Technology and Science (KTU)", options: { color: NAVYMUTED } }],
    { x: MX + 0.1, y: 6.5, w: 8.5, h: 0.35, fontFace: BODY, fontSize: 13, margin: 0, isTextBox: true });
  s.addText("All results come from synthetic data we generated.\nNo real customer or bank data was used.",
    { x: W - MX - 4.2, y: 6.47, w: 4.1, h: 0.5, fontFace: BODY, fontSize: 11, color: NAVYMUTED, align: "right",
      margin: 0, isTextBox: true });
  s.addNotes("Chakravyuh is a scam-detection engine for UPI payments. The name comes from the layered trap in the Mahabharata, " +
    "which is how these scams work: the victim is walked through several steps before paying. We look at those steps, not just the payment.");
}

// ============ 2. Problem ============
{
  const s = base(2, "1  ·  Problem");
  title(s, "In these scams, the victim makes the payment");
  text(s, "Most of the scam happens before any money moves. By the time the victim pays, the PIN is correct, the phone is " +
    "their own and they mean to pay, so a check on the payment alone has little to go on.",
    { x: MX, y: 1.45, w: 8.6, h: 0.8, fontSize: 16 });
  const steps = [["Contact", "A fake “CBI officer” video-calls about a money-laundering case"],
    ["Control", "She is told to install a screen-sharing app “for verification”"],
    ["Money extraction", "She breaks a fixed deposit and types in a new payee"],
    ["She pays", "₹2,50,000 to a personal UPI ID"]];
  const x0 = MX + 0.12, y0 = 2.75, dy = 0.95;
  vline(s, x0, y0, dy * 3, INK2, 1.5);
  steps.forEach(([h, b], i) => {
    const y = y0 + i * dy, last = i === 3;
    dot(s, x0, y, 0.2, last ? ORANGE : WHITE, last ? ORANGE : INK2);
    s.addText(h, { x: x0 + 0.35, y: y - 0.2, w: 5.5, h: 0.35, fontFace: BODY, fontSize: 18, bold: true,
      color: last ? ORANGE : INK, margin: 0, isTextBox: true });
    text(s, b, { x: x0 + 0.35, y: y + 0.15, w: 5.6, h: 0.4, fontSize: 14 });
  });
  // what a payment check sees
  vline(s, 6.75, y0 - 0.2, dy * 2 + 0.55, RULE, 1.25);
  text(s, "A payment-level check\ndoes not see these steps", { x: 6.95, y: y0 + 0.75, w: 2.3, h: 0.6, fontSize: 13, color: MUTED });
  vline(s, 6.75, y0 + dy * 3 - 0.25, 0.6, ORANGE, 1.5);
  text(s, "This is the only step\nit checks", { x: 6.95, y: y0 + dy * 3 - 0.2, w: 2.3, h: 0.6, fontSize: 13, color: ORANGE });
  // stats
  const sx = 9.6;
  s.addText("₹22,845 cr", { x: sx, y: 2.6, w: 3.2, h: 0.8, fontFace: HEAD, fontSize: 40, bold: true, color: INK, margin: 0, isTextBox: true });
  text(s, "lost to cyber fraud in India in 2024", { x: sx, y: 3.4, w: 3.2, h: 0.35, fontSize: 14 });
  s.addText("36.37 lakh", { x: sx, y: 4.0, w: 3.2, h: 0.8, fontFace: HEAD, fontSize: 40, bold: true, color: INK, margin: 0, isTextBox: true });
  text(s, "complaints filed in 2024", { x: sx, y: 4.8, w: 3.2, h: 0.35, fontSize: 14 });
  text(s, "Source: Ministry of Home Affairs, reply in Lok Sabha, July 2025 (NCRP and CFCFRMS data).",
    { x: sx, y: 5.35, w: 3.2, h: 0.55, fontSize: 11, color: MUTED });
  s.addText("Our idea: use the steps before the payment as evidence, not just the payment.",
    { x: MX, y: 6.45, w: 10, h: 0.4, fontFace: HEAD, italic: true, fontSize: 17, color: INK, margin: 0, isTextBox: true });
  s.addNotes("This is a digital-arrest scam, one of the common patterns in India. The victim authorises the payment herself, " +
    "so the bank sees a valid PIN on her own phone. Rules that only look at the payment either miss it or fire on genuine payments.");
}

// ============ 3. Idea (dark) ============
{
  const s = base(3, "2  ·  Idea", true);
  title(s, "A scam has four stages. We look for all of them.", true);
  const stages = [["Contact", "from the phone", ["call with an unknown number", "call longer than 20 min", "scam-lure SMS, checked on the phone"]],
    ["Control", "from the phone", ["screen-sharing app running", "app sideloaded in last 24 h", "OTP opened during the call"]],
    ["Extraction", "from the bank", ["first-time payee, typed UPI ID", "more than 70% of the balance", "fixed deposit broken in last 24 h"]],
    ["Cash-out", "from the receiving account", ["account behaves like a mule", "account less than 30 days old", "account on a suspect list"]]];
  const x0 = MX, cw = (W - 2 * MX) / 4, ly = 2.15;
  hline(s, x0, ly, W - 2 * MX, ONNAVY, 1.25);
  stages.forEach(([name, src, sig], i) => {
    const x = x0 + i * cw;
    dot(s, x + 0.1, ly, 0.2, NAVY, ONNAVY);
    s.addText(`0${i + 1}`, { x, y: ly + 0.3, w: 1, h: 0.25, fontFace: BODY, fontSize: 11, color: NAVYMUTED, margin: 0, isTextBox: true });
    s.addText(name, { x, y: ly + 0.55, w: cw - 0.2, h: 0.6, fontFace: HEAD, fontSize: 28, bold: true, color: ONNAVY, margin: 0, isTextBox: true });
    s.addText(sig.map((t, j) => ({ text: t, options: { breakLine: j < sig.length - 1 } })),
      { x, y: ly + 1.3, w: cw - 0.3, h: 1.3, fontFace: BODY, fontSize: 15, color: ONNAVY, margin: 0,
        paraSpaceAfter: 9, valign: "top", isTextBox: true });
    s.addText(src, { x, y: ly + 2.75, w: cw - 0.2, h: 0.3, fontFace: BODY, fontSize: 12, italic: true, color: NAVYMUTED, margin: 0, isTextBox: true });
  });
  s.addText([{ text: "One odd signal is not enough to stop a payment. ", options: { color: ONNAVY } },
    { text: "We act when several stages show up together.", options: { color: ORANGE, bold: true } }],
    { x: MX, y: 5.3, w: W - 2 * MX, h: 0.95, fontFace: HEAD, fontSize: 23, margin: 0, valign: "top", isTextBox: true });
  text(s, "A genuine payment can look odd on its own, like a new payee on rent day or a long call with a plumber. " +
    "A scam is easier to spot from the sequence. All 20 signals are listed in the appendix.",
    { x: MX, y: 6.35, w: 10.5, h: 0.6, fontSize: 14, color: NAVYMUTED });
  s.addNotes("This is the core idea. Each stage has signals, 20 in total: 9 from the phone, 7 the bank already has, " +
    "and 4 about the receiving account. We only interrupt when at least two stages are active.");
}

// ============ 4. Levels ============
{
  const s = base(4, "3  ·  Response");
  title(s, "Three levels of response");
  text(s, "The more stages we see, the stronger the response. The bank chooses how many alerts per 1,000 payments it will " +
    "accept at each level, and we set the thresholds to match on separate test data.", { x: MX, y: 1.45, w: 9.5, h: 0.8, fontSize: 16 });
  const L = [["1", "Log it", "Score above threshold 1", "Nothing. The session goes to the bank’s fraud team for later review.",
    C.t1_fp.mean.toFixed(1), "20", RULE, INK],
  ["2", "Warn and ask", "Score above threshold 2, and at least 2 stages active",
    "A warning that names the likely scam, and two questions. The customer can still pay.", C.fp.mean.toFixed(2), "3", INK, WHITE],
  ["3", "Hold and review", "Score above threshold 3, and 3 stages (or 2 plus a suspect-list match)",
    "The payment is held for up to 30 minutes and a bank agent calls. Two staff must approve a release.",
    C.t3_fp.mean.toFixed(2), "0.5", ORANGE, WHITE]];
  const cw = 3.85, gap = 0.3;
  L.forEach(([n, name, when, sees, rate, tgt, fill, fg], i) => {
    const x = MX + i * (cw + gap), y = 2.55;
    const d = 0.55 + i * 0.12;
    s.addShape(pres.shapes.OVAL, { x, y: y + (0.79 - d) / 2, w: d, h: d, fill: { color: fill }, line: { color: fill } });
    s.addText(n, { x, y: y + (0.79 - d) / 2, w: d, h: d, fontFace: HEAD, fontSize: 18 + i * 3, bold: true, color: fg,
      align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(name, { x: x + 0.95, y: y + 0.12, w: cw - 0.95, h: 0.55, fontFace: HEAD, fontSize: 24, bold: true,
      color: i === 2 ? ORANGE : INK, margin: 0, isTextBox: true });
    s.addText("When", { x, y: y + 1.05, w: cw, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: INK2, margin: 0, isTextBox: true });
    text(s, when, { x, y: y + 1.35, w: cw, h: 0.6, fontSize: 14 });
    s.addText("Customer sees", { x, y: y + 2.0, w: cw, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: INK2, margin: 0, isTextBox: true });
    text(s, sees, { x, y: y + 2.3, w: cw, h: 0.85, fontSize: 14 });
    hline(s, x, y + 3.25, cw, RULE, 1);
    s.addText(rate, { x, y: y + 3.35, w: 1.2, h: 0.55, fontFace: HEAD, fontSize: 28, bold: true, color: INK, margin: 0, isTextBox: true });
    text(s, `genuine sessions per 1,000\nmeasured on synthetic data (target ${tgt})`, { x: x + 1.25, y: y + 3.42, w: cw - 1.25, h: 0.55, fontSize: 12, color: MUTED });
  });
  s.addText("Nothing is blocked permanently. A person decides every hold.", { x: MX, y: 6.65, w: 9, h: 0.35,
    fontFace: HEAD, italic: true, fontSize: 16, color: INK, margin: 0, isTextBox: true });
  s.addNotes("The response grows with the evidence. Level 1 is silent. Level 2 warns and asks two questions but never blocks. " +
    "Level 3 holds the payment for up to 30 minutes and a bank agent reviews it. The rates shown are measured on our synthetic test data.");
}

// ============ 5. Example ============
{
  const s = base(5, "4  ·  Example");
  title(s, "Example: Mrs R., 68");
  s.addText("A made-up case based on reported digital-arrest scams.", { x: MX, y: 1.38, w: 8, h: 0.35, fontFace: BODY,
    italic: true, fontSize: 14, color: MUTED, margin: 0, isTextBox: true });
  const ev = [["Fake CBI video call", "contact"], ["Remote-access app", "control"], ["FD broken", "extraction"],
    ["First-time payee", "extraction"], ["Mule-like account", "cash-out"], ["₹2,50,000 payment", "payment"]];
  const x0 = MX + 0.1, ew = 1.45, y0 = 2.2;
  hline(s, x0, y0, ew * 5, INK2, 1.25);
  ev.forEach(([a, st], i) => {
    const x = x0 + i * ew, last = i === 5;
    dot(s, x, y0, 0.2, last ? ORANGE : WHITE, last ? ORANGE : INK2);
    s.addText(a, { x: x - 0.1, y: y0 + 0.25, w: ew - 0.1, h: 0.6, fontFace: BODY, fontSize: 14, bold: true,
      color: last ? ORANGE : INK, margin: 0, isTextBox: true });
    s.addText(st, { x: x - 0.1, y: y0 + 0.85, w: ew - 0.1, h: 0.3, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0, isTextBox: true });
  });
  // two outcomes
  const oy = 3.75, ow = 4.1;
  s.addText("Today", { x: MX, y: oy, w: ow, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: MUTED, margin: 0, isTextBox: true });
  s.addText("The money is gone.", { x: MX, y: oy + 0.3, w: ow, h: 0.55, fontFace: HEAD, fontSize: 24, bold: true, color: INK, margin: 0, isTextBox: true });
  text(s, "A “new payee and high amount” rule shows a general warning. The caller tells her to ignore it and she pays. " +
    "The money goes to a mule account and moves on within hours.", { x: MX, y: oy + 0.95, w: ow - 0.2, h: 1.4, fontSize: 15 });
  const x2 = MX + ow + 0.3;
  s.addShape(pres.shapes.RECTANGLE, { x: x2 - 0.2, y: oy - 0.2, w: ow + 0.3, h: 2.75, fill: { color: "FDF1EA" }, line: { color: "FDF1EA" } });
  s.addText("With Chakravyuh", { x: x2, y: oy, w: ow, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: ORANGE, margin: 0, isTextBox: true });
  s.addText("The payment is held.", { x: x2, y: oy + 0.3, w: ow, h: 0.55, fontFace: HEAD, fontSize: 24, bold: true, color: ORANGE, margin: 0, isTextBox: true });
  text(s, "All four stages show up, so it goes to level 3. The screen tells her real officials never ask for money on a call, " +
    "and a bank agent calls her before anything is released.", { x: x2, y: oy + 0.95, w: ow - 0.2, h: 1.4, fontSize: 15 });
  // phone
  s.addImage({ path: path.resolve(__dirname, "mockup_tier3.png"), x: 10.25, y: 1.2, w: 2.45, h: 2.45 * 2790 / 1350,
    altText: "Mock-up of the level 3 hold screen on a phone" });
  s.addText("Level 3 screen (mock-up)", { x: 10.25, y: 6.4, w: 2.45, h: 0.3, fontFace: BODY, fontSize: 11, color: MUTED,
    align: "center", margin: 0, isTextBox: true });
  s.addNotes("Five warning signs appear before the payment. Today a generic rule shows a warning the caller talks her past. " +
    "With Chakravyuh all four stages are active, so the payment is held and she sees a specific message.");
}

// ============ 6. How the score works ============
{
  const s = base(6, "5  ·  Model");
  title(s, "How the score works");
  const P = [["20", "yes/no signals", "9 phone · 7 bank · 4 receiving account"], ["4", "stage scores", "weighted sum per stage, with a cap"],
    ["≥ 2", "stages needed", "before we interrupt a payment"], ["0–3", "response level", "plus the reasons and a signed record"]];
  const pw = 2.75, gap = 0.37;
  P.forEach(([n, l, d], i) => {
    const x = MX + i * (pw + gap), y = 1.6, last = i === 3;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: pw, h: 1.55, fill: { color: last ? "FDF1EA" : TINT }, line: { color: last ? "FDF1EA" : TINT } });
    s.addText(n, { x: x + 0.2, y: y + 0.15, w: pw - 0.4, h: 0.65, fontFace: HEAD, fontSize: 34, bold: true, color: last ? ORANGE : INK, margin: 0, isTextBox: true });
    s.addText(l, { x: x + 0.2, y: y + 0.8, w: pw - 0.4, h: 0.3, fontFace: BODY, fontSize: 15, bold: true, color: INK, margin: 0, isTextBox: true });
    text(s, d, { x: x + 0.2, y: y + 1.1, w: pw - 0.4, h: 0.35, fontSize: 12, color: MUTED });
    if (i < 3) s.addText("→", { x: x + pw + 0.02, y: y + 0.55, w: 0.33, h: 0.4, fontFace: BODY, fontSize: 20, color: MUTED, align: "center", margin: 0, isTextBox: true });
  });
  // equation
  s.addText("Score", { x: MX, y: 3.55, w: 5, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: INK2, margin: 0, isTextBox: true });
  s.addText([{ text: "s(x) = b + Σ", options: {} }, { text: "g", options: { subscript: true } },
    { text: " min( C", options: {} }, { text: "g", options: { subscript: true } }, { text: " ,  Σ", options: {} },
    { text: "k in g", options: { subscript: true } }, { text: " w", options: {} }, { text: "k", options: { subscript: true } },
    { text: " x", options: {} }, { text: "k", options: { subscript: true } }, { text: " )", options: {} }],
    { x: MX, y: 3.9, w: 6, h: 0.6, fontFace: HEAD, fontSize: 24, color: INK, margin: 0, isTextBox: true });
  s.addText("Decision", { x: MX, y: 4.65, w: 5, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: INK2, margin: 0, isTextBox: true });
  text(s, [{ text: "Level 2", options: { bold: true, color: INK } }, { text: " if s ≥ τ2 and at least 2 stages are active", options: { breakLine: true } },
    { text: "Level 3", options: { bold: true, color: INK } }, { text: " if s ≥ τ3 and 3 stages are active (or 2 plus a suspect-list match)" }],
    { x: MX, y: 4.95, w: 6, h: 0.8, fontSize: 15 });
  text(s, "g is one of the four stages; x is 1 when a signal is present and 0 when it is not. Weights come from a logistic " +
    "regression (L2) on labelled sessions and are kept at zero or above.", { x: MX, y: 5.9, w: 5.9, h: 0.7, fontSize: 12, color: MUTED });
  // principles
  const rows = [["Non-negative weights", "A missing signal does not change the score, because a fraudster can always hide one."],
    ["Stage caps", "One stage cannot push the score up on its own (C = 5, 5, 6, 6)."],
    ["Two-stage rule", "We only interrupt when at least two stages are active."],
    ["Real-world scam rate", "Training data is 3.8% scams; we adjust to an assumed 1 in 5,000."],
    ["Fixed thresholds", "Set on a separate dataset to meet the bank’s alert limit, then fixed."]];
  s.addTable(rows.map(([a, b]) => [{ text: a, options: { bold: true, color: INK } }, { text: b, options: { color: INK2 } }]),
    { x: 7.1, y: 3.55, w: 5.63, colW: [1.85, 3.78], fontFace: BODY, fontSize: 13, valign: "top",
      border: HB(), margin: [0.07, 0.08, 0.07, 0.0], rowH: 0.56 });
  s.addNotes("Each signal has a weight learned by logistic regression. Weights are summed per stage and capped. " +
    "The two-stage rule is what stops one odd signal, like a new payee, from interrupting a genuine payment.");
}

// ============ 7. Results ============
{
  const s = base(7, "6  ·  Results");
  title(s, "Results on synthetic data");
  s.addText("These numbers come from 8 synthetic test sets the model never saw. They are not results from a real bank.",
    { x: MX, y: 1.38, w: 11, h: 0.35, fontFace: BODY, italic: true, fontSize: 14, color: MUTED, margin: 0, isTextBox: true });
  const K = [[pct(C.recall.mean), "of scam sessions reach level 2 or 3", `95% confidence interval ${ci(C.recall)}`, ORANGE],
    [`${C.fp.mean.toFixed(2)} / 1,000`, "genuine sessions interrupted", `95% CI [${C.fp.lo.toFixed(2)}, ${C.fp.hi.toFixed(2)}] · target 3.0`, INK],
    [C.auprc.mean.toFixed(3), "area under the precision-recall curve", `95% CI [${C.auprc.lo.toFixed(3)}, ${C.auprc.hi.toFixed(3)}]`, INK]];
  K.forEach(([big, lab, sub, col], i) => {
    const y = 2.0 + i * 1.5;
    s.addText(big, { x: MX, y, w: 3.8, h: 0.7, fontFace: HEAD, fontSize: 38, bold: true, color: col, margin: 0, isTextBox: true });
    text(s, lab, { x: MX, y: y + 0.72, w: 3.8, h: 0.3, fontSize: 14, color: INK });
    text(s, sub, { x: MX, y: y + 1.0, w: 3.8, h: 0.3, fontSize: 12, color: MUTED });
  });
  const names = ["Chakravyuh", "Without two-stage rule", "Logistic regression", "Gradient boosting", "XGBoost", "MLP", "“New payee + high amount” rule"];
  const rec = [C.recall.mean, C.recall_nogate.mean, B["Logistic regression"].recall.mean, B["Gradient boosting"].recall.mean,
    B["XGBoost"].recall.mean, B["MLP"].recall.mean, B["Rule: new payee + high amount"].recall.mean].map(v => +(v * 100).toFixed(1));
  const fp = [C.fp.mean, C.fp_nogate.mean, B["Logistic regression"].fp.mean, B["Gradient boosting"].fp.mean,
    B["XGBoost"].fp.mean, B["MLP"].fp.mean, B["Rule: new payee + high amount"].fp.mean].map(v => +v.toFixed(2));
  const common = { x: 0, y: 0, w: 0, h: 0, barDir: "bar", catAxisLabelColor: INK2, valAxisLabelColor: MUTED, catAxisLabelFontSize: 11,
    valAxisLabelFontSize: 10, catAxisLabelFontFace: BODY, valAxisLabelFontFace: BODY, valGridLine: { color: "E8EAED", size: 0.5 },
    catGridLine: { style: "none" }, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelFontFace: BODY,
    dataLabelColor: INK, showLegend: false, showTitle: true, titleFontFace: BODY, titleFontSize: 13, titleColor: INK,
    catAxisOrientation: "maxMin", barGapWidthPct: 45 };
  s.addChart(pres.charts.BAR, [{ name: "Recall (%)", labels: names, values: rec }], Object.assign({}, common,
    { x: 4.6, y: 1.9, w: 4.5, h: 4.1, title: "Scams caught (%)", valAxisMinVal: 0, valAxisMaxVal: 100,
      chartColors: [ORANGE, "B7BCC4", "4A5568", "4A5568", "4A5568", "4A5568", "B7BCC4"], dataLabelFormatCode: "0.0" }));
  s.addChart(pres.charts.BAR, [{ name: "Interruptions per 1,000", labels: names, values: fp }], Object.assign({}, common,
    { x: 9.15, y: 1.9, w: 3.6, h: 4.1, title: "Genuine payments interrupted per 1,000", valAxisMinVal: 0, valAxisMaxVal: 11,
      catAxisHidden: true, chartColors: [ORANGE, "B7BCC4", "4A5568", "4A5568", "4A5568", "4A5568", "B7BCC4"], dataLabelFormatCode: "0.00" }));
  const red = Math.round((1 - C.fp.mean / C.fp_nogate.mean) * 100);
  text(s, [{ text: "What we give up. ", options: { bold: true, color: INK } },
    { text: `Standard classifiers catch ${(B["Logistic regression"].recall.mean * 100).toFixed(1)}–${(B["MLP"].recall.mean * 100).toFixed(1)}% of scams ` +
      `but interrupt more genuine payments. The two-stage rule costs us ${((C.recall_nogate.mean - C.recall.mean) * 100).toFixed(1)} points ` +
      `of recall; in return there are ${red}% fewer interruptions and every alert lists the signals behind it.` }],
    { x: 4.6, y: 6.15, w: 8.1, h: 0.75, fontSize: 13 });
  s.addNotes(`Recall ${pct(C.recall.mean)} with a 95% interval of ${ci(C.recall)}, at ${C.fp.mean.toFixed(2)} interruptions per 1,000. ` +
    "Trained on one synthetic dataset, thresholds set on another, tested on 8 more. Standard classifiers catch slightly more scams, " +
    "but they interrupt more genuine payments and cannot explain why.");
}

// ============ 8. Tactics ============
{
  const s = base(8, "7  ·  Robustness");
  title(s, "What if the fraudster changes tactics?");
  const rows = [
    ["Hide their tracks?\nHang up before paying, skip screen-sharing, send less.",
      "Payment and receiving-account signals come from the bank, which the caller cannot hide.",
      `${pct(C.recall_adapted.mean)} of these sessions still caught. Worst case, hiding the strongest signal: ${pct(adv[1], 0)}; two: ${pct(adv[2], 0)}.`, "measured"],
    ["Split one payment into several?\nFour payments of ₹25,000 instead of one ₹1,00,000.",
      "A signal for two or more payments to new payees within 60 minutes.", "Not separately simulated yet.", "design only"],
    ["Use older, rented mule accounts?\nAn old account avoids the ‘new account’ signal.",
      "The mule score also checks how many new senders an account has and how fast money leaves it.",
      `Mule score catches only 24% of old mule accounts; payments to them are still caught ${pct(C.recall_aged_mule.mean)} of the time.`, "measured"],
    ["Poison the training data?\nSend lots of false reports.", "Retrain only on cases the bank has confirmed.", "Not evaluated.", "design only"]];
  const hdr = ["Can they…", "Our answer", "What we found", "Status"].map(t => ({ text: t, options: { bold: true, color: INK2, fontSize: 12 } }));
  const body = rows.map(r => {
    const [q, ...rest] = r[0].split("\n");
    return [{ text: [{ text: q, options: { bold: true, color: INK, fontSize: 14, breakLine: true } }, { text: rest.join(" "), options: { color: MUTED, fontSize: 12 } }] },
      { text: r[1], options: { color: INK2 } }, { text: r[2], options: { color: INK2 } },
      { text: r[3], options: { color: r[3] === "measured" ? INK : MUTED, italic: r[3] !== "measured", fontSize: 12 } }];
  });
  s.addTable([hdr, ...body], { x: MX, y: 1.55, w: 8.6, colW: [2.75, 2.55, 2.45, 0.85], fontFace: BODY, fontSize: 13, valign: "top",
    border: HB(), margin: [0.08, 0.12, 0.08, 0.0], rowH: [0.4, 1.25, 1.05, 1.25, 0.9] });
  s.addChart(pres.charts.LINE, [{ name: "Recall", labels: F.adversarial.map(a => String(a.suppressed)), values: F.adversarial.map(a => +(a.recall * 100).toFixed(0)) }],
    { x: 9.45, y: 1.5, w: 3.3, h: 2.7, chartColors: [ORANGE], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6,
      showValue: true, dataLabelPosition: "t", dataLabelFontSize: 10, dataLabelColor: INK, valAxisMinVal: 0, valAxisMaxVal: 100,
      valAxisHidden: true, catAxisLabelColor: MUTED, catAxisLabelFontSize: 10, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showLegend: false, showTitle: true, title: "Recall (%) as the strongest signals are hidden", titleFontSize: 11, titleColor: INK, titleFontFace: BODY,
      showCatAxisTitle: true, catAxisTitle: "signals hidden", catAxisTitleFontSize: 10, catAxisTitleColor: MUTED });
  text(s, "We assume the fraudster has read our weights and removes the strongest signals first. Thresholds are not changed.",
    { x: 9.5, y: 4.25, w: 3.2, h: 0.75, fontSize: 12, color: MUTED });
  s.addText("A scam type it has not seen", { x: 9.5, y: 5.1, w: 3.2, h: 0.3, fontFace: BODY, bold: true, fontSize: 13, color: INK, margin: 0, isTextBox: true });
  text(s, `Trained without one type, tested on it: ${(Math.min(...loo) * 100).toFixed(0)}–${(Math.max(...loo) * 100).toFixed(0)}% recall.`,
    { x: 9.5, y: 5.4, w: 3.2, h: 0.5, fontSize: 12 });
  s.addText("Removing one stage", { x: 9.5, y: 5.95, w: 3.2, h: 0.3, fontFace: BODY, bold: true, fontSize: 13, color: INK, margin: 0, isTextBox: true });
  text(s, `Recall without contact, control, extraction or cash-out signals: ${[abl.contact, abl.control, abl.extraction, abl.cashout].map(v => (v * 100).toFixed(0) + "%").join(", ")}.`,
    { x: 9.5, y: 6.25, w: 3.2, h: 0.6, fontSize: 12 });
  s.addNotes("We tested what happens if the fraudster adapts. Hiding the strongest signal hurts, so we report it honestly. " +
    "Two of these defences are designs we have not tested yet, and they are marked that way.");
}

// ============ 9. Data ============
{
  const s = base(9, "8  ·  Privacy");
  title(s, "What data we use");
  const colY = 1.65;
  s.addText("Stays on the phone", { x: MX, y: colY, w: 3, h: 0.35, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  ["Call audio", "Screen frames", "Message text", "Contact list", "OTP values", "App list"].forEach((t, i) => {
    const y = colY + 0.55 + i * 0.52;
    s.addText("✕", { x: MX, y, w: 0.3, h: 0.35, fontFace: BODY, fontSize: 16, bold: true, color: ORANGE, margin: 0, isTextBox: true });
    s.addText(t, { x: MX + 0.4, y, w: 2.5, h: 0.35, fontFace: BODY, fontSize: 17, color: INK, margin: 0, isTextBox: true });
    hline(s, MX, y + 0.44, 2.9, RULE, 0.75);
  });
  s.addShape(pres.shapes.LINE, { x: 3.85, y: colY, w: 0, h: 3.6, line: { color: INK2, width: 1.25, dashType: "dash" } });
  const x2 = 4.25;
  s.addText("Sent to the bank", { x: x2, y: colY, w: 4.5, h: 0.35, fontFace: BODY, bold: true, fontSize: 15, color: ORANGE, margin: 0, isTextBox: true });
  s.addText([{ text: "9", options: { fontFace: HEAD, fontSize: 30, bold: true, color: ORANGE } },
    { text: "  yes/no values, plus the amount", options: { fontSize: 16, color: INK, breakLine: true } },
    { text: "and a hashed payee ID", options: { fontSize: 16, color: INK } }],
    { x: x2, y: colY + 0.4, w: 4.6, h: 0.85, fontFace: BODY, margin: 0, valign: "top", isTextBox: true });
  const dev = ["on a call with an unknown number", "call longer than 20 minutes", "video call active", "scam-lure SMS in last 24 h",
    "screen-sharing app running", "app sideloaded in last 24 h", "app drawing over the payment screen", "OTP opened during the call",
    "payee typed in by hand"];
  s.addText(dev.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < dev.length - 1 } })),
    { x: x2, y: colY + 1.35, w: 4.4, h: 2.55, fontFace: BODY, fontSize: 13, color: INK2, margin: 0, paraSpaceAfter: 3, valign: "top", isTextBox: true });
  const x3 = 9.1;
  s.addText("Already at the bank", { x: x3, y: colY, w: 3.6, h: 0.35, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  s.addText([{ text: "7", options: { fontFace: HEAD, fontSize: 26, bold: true, color: INK } },
    { text: "  from the bank’s own data: first-time payee, amount compared with past payments, share of balance, broken fixed deposit, recent small credits.", options: { fontSize: 13, color: INK2 } }],
    { x: x3, y: colY + 0.45, w: 3.65, h: 1.3, fontFace: BODY, margin: 0, valign: "top", isTextBox: true });
  s.addText([{ text: "4", options: { fontFace: HEAD, fontSize: 26, bold: true, color: INK } },
    { text: "  about the receiving account: mule score, account age, suspect-list match, collect request.", options: { fontSize: 13, color: INK2 } }],
    { x: x3, y: colY + 1.9, w: 3.65, h: 1.0, fontFace: BODY, margin: 0, valign: "top", isTextBox: true });
  text(s, "9 + 7 + 4 = 20 signals", { x: x3, y: colY + 3.0, w: 3.6, h: 0.3, fontSize: 13, color: MUTED });
  // signed record
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 5.5, w: W - 2 * MX, h: 1.28, fill: { color: TINT }, line: { color: TINT } });
  s.addText("Signed decision record", { x: MX + 0.25, y: 5.62, w: 3, h: 0.3, fontFace: BODY, bold: true, fontSize: 13, color: INK, margin: 0, isTextBox: true });
  s.addText("{ log_id, time, session, amount, signals present, score, level, scam type, active stages, action } + HMAC-SHA256",
    { x: MX + 0.25, y: 5.93, w: 11.6, h: 0.3, fontFace: "Courier New", fontSize: 12, color: INK, margin: 0, isTextBox: true });
  text(s, "Each decision gets one ID, so the customer, the bank agent and any complaint point to the same evidence. " +
    "Already built: the server accepts only the 20 known signals and rejects repeated or old (> 15 s) requests.",
    { x: MX + 0.25, y: 6.25, w: 11.6, h: 0.5, fontSize: 12 });
  s.addText("Designed around the DPDP Act 2023 idea of collecting only what is needed. This is a design choice, not a legal certification.",
    { x: MX, y: 6.9, w: 10, h: 0.25, fontFace: BODY, fontSize: 10, italic: true, color: MUTED, margin: 0, isTextBox: true });
  s.addNotes("No audio, screen content, messages or contacts ever leave the phone. Only nine yes/no values, the amount and a hashed payee ID. " +
    "Every decision is signed so it can be checked later in a complaint.");
}

// ============ 10. Comparison ============
{
  const s = base(10, "9  ·  Comparison");
  title(s, "How it compares");
  const Y = "✓", N = "—";
  const hdr = ["", "Uses payment\ndetails", "Uses steps\nbefore payment", "Gives a\nreason", "Scaled\nresponse"]
    .map(t => ({ text: t, options: { bold: true, color: INK2, fontSize: 13, align: t ? "center" : "left" } }));
  const rows = [["Transaction rules", Y, N, Y, N], ["Standard ML classifier", Y, "partly", "after the fact", N], ["Chakravyuh", Y, Y, Y, Y]]
    .map(r => r.map((c, i) => ({ text: c, options: { align: i ? "center" : "left", color: r[0] === "Chakravyuh" ? ORANGE : (i ? INK2 : INK),
      bold: r[0] === "Chakravyuh", fontSize: i && c.length === 1 ? 18 : 15 } })));
  s.addTable([hdr, ...rows], { x: MX, y: 1.55, w: 7.4, colW: [2.6, 1.2, 1.3, 1.15, 1.15], fontFace: BODY, valign: "middle",
    border: HB(), rowH: [0.7, 0.52, 0.52, 0.52], margin: [0.05, 0.08, 0.05, 0.0] });
  s.addText("The main difference: we use what happened before the payment, not only the payment.",
    { x: 8.5, y: 1.75, w: 4.2, h: 1.4, fontFace: HEAD, fontSize: 22, color: INK, margin: 0, valign: "top", isTextBox: true });
  s.addText("Why not just use a standard classifier?", { x: 8.5, y: 3.35, w: 4.2, h: 0.35, fontFace: BODY, bold: true, fontSize: 14, color: INK, margin: 0, isTextBox: true });
  text(s, "On our synthetic data it catches about 4 points more scams. But it cannot say why, and one strong signal can stop a genuine " +
    "payment. Customers, bank agents and the ombudsman all need to know why a payment was held.", { x: 8.5, y: 3.7, w: 4.2, h: 1.5, fontSize: 14 });
  s.addImage({ path: path.resolve(__dirname, "mockup_agent.png"), x: MX, y: 4.2, w: 4.4, h: 4.4 * 1710 / 2880,
    altText: "Mock-up of the bank agent screen showing a held payment and its reasons" });
  text(s, "What a bank agent would see for a held payment (mock-up): the stages that fired and the signals behind them.",
    { x: MX + 4.65, y: 5.2, w: 2.6, h: 1.2, fontSize: 12, color: MUTED });
  s.addNotes("The table shows the gap we fill. Rules explain but ignore context; classifiers use features but cannot explain. " +
    "We use the whole scam sequence and always give a reason.");
}

// ============ 11. Architecture ============
{
  const s = base(11, "10  ·  Architecture");
  title(s, "System architecture");
  [["built", "solid", INK, 1.5], ["simulated with synthetic data", "dash", MUTED, 1], ["planned, not built", "sysDot", MUTED, 1]].forEach(([l, d, c, wd], i) => {
    const lx = MX + [0, 1.4, 4.55][i];
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.45, w: 0.45, h: 0.25, fill: { color: WHITE }, line: { color: c, width: wd, dashType: d } });
    s.addText(l, { x: lx + 0.55, y: 1.43, w: 2.3, h: 0.3, fontFace: BODY, fontSize: 13, color: INK2, margin: 0, isTextBox: true });
  });
  const box = (x, y, w, h, t, sub, st) => {
    const style = { built: [INK, "solid", 1.5, WHITE], simulated: [MUTED, "dash", 1, WHITE], planned: [MUTED, "sysDot", 1, WHITE] }[st];
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: style[3] }, line: { color: style[0], width: style[2], dashType: style[1] } });
    s.addText(t, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: 0.32, fontFace: BODY, fontSize: 14, bold: true, color: st === "planned" ? INK2 : INK, margin: 0, isTextBox: true });
    text(s, sub, { x: x + 0.12, y: y + 0.44, w: w - 0.24, h: h - 0.5, fontSize: 11.5, color: st === "planned" ? MUTED : INK2 });
  };
  const plane = (y, label) => { hline(s, MX, y, W - 2 * MX, INK, 1); s.addText(label, { x: MX, y: y + 0.06, w: 6, h: 0.28, fontFace: BODY, fontSize: 13, bold: true, color: INK, margin: 0, isTextBox: true }); };
  const bw = (W - 2 * MX - 0.4) / 3, bh = 0.95;
  plane(1.9, "Phone (inside the bank’s app)");
  box(MX, 2.3, bw, bh, "Signal readers", "Call state, accessibility, app installs, SMS check on the phone.", "simulated");
  box(MX + bw + 0.2, 2.3, bw, bh, "Request builder", "9 yes/no values, amount, payee hash, nonce, timestamp, Play Integrity token.", "planned");
  box(MX + 2 * (bw + 0.2), 2.3, bw, bh, "Warning screens", "Scam message, two questions, hold screen. Mock-ups and a web demo.", "simulated");
  text(s, "1. signals sent ↓        5. level, message and record ID sent back ↑", { x: MX, y: 3.3, w: 10, h: 0.3, fontSize: 11, color: MUTED });
  plane(3.65, "Bank fraud team servers");
  const bw4 = (W - 2 * MX - 0.6) / 4;
  box(MX, 4.05, bw4, bh, "Scoring server", "FastAPI endpoint: stage scores, two-stage rule, level, reasons.", "built");
  box(MX + (bw4 + 0.2), 4.05, bw4, bh, "Input checks", "Rejects repeated nonces, old requests and unknown signals.", "built");
  box(MX + 2 * (bw4 + 0.2), 4.05, bw4, bh, "Signed records", "HMAC-SHA256 on every decision.", "built");
  box(MX + 3 * (bw4 + 0.2), 4.05, bw4, bh, "Agent screen", "Queue of held payments; two staff to release.", "planned");
  text(s, "2. payee data looked up ↑        3. scored        4. level-3 hold sent to payments →        6. confirmed outcomes saved ↓",
    { x: MX, y: 5.05, w: 11, h: 0.3, fontSize: 11, color: MUTED });
  plane(5.4, "Bank data, payments and reporting");
  const bw5 = (W - 2 * MX - 0.8) / 5, bh2 = 1.05;
  box(MX, 5.8, bw5, bh2, "Mule score", "New senders, speed of outflow, account age.", "simulated");
  box(MX + (bw5 + 0.2), 5.8, bw5, bh2, "Suspect list", "A yes/no flag, never shown to customers.", "simulated");
  box(MX + 2 * (bw5 + 0.2), 5.8, bw5, bh2, "Retraining", "Weekly, bank-confirmed cases only.", "planned");
  box(MX + 3 * (bw5 + 0.2), 5.8, bw5, bh2, "Payment hold", "Time-limited, through the bank’s payment system.", "planned");
  box(MX + 4 * (bw5 + 0.2), 5.8, bw5, bh2, "Reporting", "Confirmed scams to I4C (CFCFRMS / 1930).", "planned");
  s.addText("We have no integration with Amazon, NPCI, I4C or any bank yet.", { x: MX, y: 6.95, w: 9, h: 0.25, fontFace: BODY, fontSize: 11, italic: true, color: MUTED, margin: 0, isTextBox: true });
  s.addNotes("This separates what is built from what is simulated and what is planned. The scoring server, input checks and signed records " +
    "are built and tested. The phone SDK, payment hold and agent screen are planned.");
}

// ============ 12. Security ============
{
  const s = base(12, "11  ·  Security");
  title(s, "Following one payment through the system");
  const steps = [["Customer taps Pay", "The app sends the signals that are true, the amount, a payee hash, a nonce and a timestamp."],
    ["Check the request", "The server rejects unknown signals, repeated nonces and anything older than 15 seconds."],
    ["Score", "Payee data is added, then stage scores, the two-stage rule, the level and the top five reasons."],
    ["Respond", "Level 0 allows, 1 logs, 2 warns and asks two questions, 3 holds the payment."],
    ["Review", "Held payments go to a bank agent with the record and reasons. Two staff approve a release."],
    ["Close", "Released, or confirmed and reported. The result is saved for retraining."]];
  steps.forEach(([h, b], i) => {
    const y = 1.6 + i * 0.85;
    s.addShape(pres.shapes.OVAL, { x: MX, y, w: 0.42, h: 0.42, fill: { color: i === 3 ? ORANGE : NAVY }, line: { color: i === 3 ? ORANGE : NAVY } });
    s.addText(String(i + 1), { x: MX, y, w: 0.42, h: 0.42, fontFace: HEAD, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(h, { x: MX + 0.6, y: y - 0.02, w: 4.6, h: 0.3, fontFace: BODY, fontSize: 15, bold: true, color: INK, margin: 0, isTextBox: true });
    text(s, b, { x: MX + 0.6, y: y + 0.28, w: 4.6, h: 0.5, fontSize: 12 });
  });
  const ctl = [["Old or repeated requests", "One-time nonce and a 15-second limit", "built"],
    ["Extra or fake fields", "Only the 20 known signals are accepted", "built"],
    ["Edited decision records", "Each record signed with HMAC-SHA256", "built"],
    ["Fake or modified app", "Play Integrity token tied to a hash of the request", "planned"],
    ["Staff misuse", "Two approvers, both written into the record", "planned"],
    ["Record store leak", "No raw content in records; identity stored apart", "design only"],
    ["Poisoned labels", "Retrain only on bank-confirmed cases", "design only"]];
  s.addText("Security checks", { x: 6.2, y: 1.55, w: 4, h: 0.3, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  s.addTable([[{ text: "Risk", options: { bold: true, color: INK2 } }, { text: "What we do", options: { bold: true, color: INK2 } }, { text: "", options: {} }],
    ...ctl.map(([a, b]) => [{ text: a, options: { color: INK } }, { text: b, options: { color: INK2 } }, { text: "" }])],
    { x: 6.2, y: 1.95, w: 6.53, colW: [2.2, 3.13, 1.2], fontFace: BODY, fontSize: 12.5, valign: "middle",
      border: HB(), rowH: 0.52, margin: [0.04, 0.08, 0.04, 0.0] });
  ctl.forEach((c, i) => tag(s, c[2], 6.2 + 5.33 + 0.1, 1.95 + 0.52 * (i + 1) + 0.13));
  text(s, "If a customer complains about a hold, they quote the record ID on their screen and the bank can see exactly which signals caused it.",
    { x: 6.2, y: 6.25, w: 6.5, h: 0.6, fontSize: 12, color: MUTED });
  s.addNotes("The three built controls are covered by automated tests, including one that replays a request and checks it is rejected. " +
    "The others are planned or design-only and labelled that way.");
}

// ============ 13. Rollout & cost ============
{
  const s = base(13, "12  ·  Rollout and cost");
  title(s, "Rollout plan and cost estimates");
  const R = [["Weeks 0–6", "Shadow mode", "Score real payments but show nothing. Measure the alert rate and reset thresholds."],
    ["Weeks 6–10", "Levels 1 and 2", "Customers who opt in, and large payments to individuals. Move on only if alerts stay within the limit."],
    ["From week 10", "Level 3", "Payment holds with agent review and two-person release."]];
  R.forEach(([w, h, b], i) => {
    const y = 1.7 + i * 1.2;
    s.addText(w, { x: MX, y, w: 1.5, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: ORANGE, margin: 0, isTextBox: true });
    s.addText(h, { x: MX + 1.6, y, w: 3.8, h: 0.3, fontFace: BODY, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true });
    text(s, b, { x: MX + 1.6, y: y + 0.35, w: 3.9, h: 0.75, fontSize: 13 });
  });
  s.addText("Speed", { x: MX, y: 5.35, w: 3, h: 0.3, fontFace: BODY, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true });
  text(s, `Scoring takes about ${C.latency_us.toFixed(0)} µs per session on our machine. We aim for under 40 ms for the full round trip from the phone, but have not measured it.`,
    { x: MX, y: 5.65, w: 5.4, h: 0.9, fontSize: 13 });
  // estimates panel
  const px = 6.6;
  s.addShape(pres.shapes.RECTANGLE, { x: px, y: 1.55, w: 6.13, h: 5.35, fill: { color: TINT }, line: { color: TINT } });
  s.addText("Estimates based on assumptions, not measured results", { x: px + 0.3, y: 1.72, w: 5.6, h: 0.3, fontFace: BODY, italic: true, fontSize: 13, color: ORANGE, margin: 0, isTextBox: true });
  const tbl = (y, head, rows, totalIdx) => {
    s.addText(head, { x: px + 0.3, y, w: 5.6, h: 0.3, fontFace: BODY, bold: true, fontSize: 14, color: INK, margin: 0, isTextBox: true });
    s.addTable(rows.map((r, i) => [{ text: r[0], options: { color: i === totalIdx ? INK : INK2, bold: i === totalIdx } },
      { text: r[1], options: { align: "right", color: i === totalIdx ? ORANGE : INK, bold: i === totalIdx } }]),
      { x: px + 0.3, y: y + 0.35, w: 5.55, colW: [4.0, 1.55], fontFace: BODY, fontSize: 12.5, rowH: 0.36,
        border: HB(RULE, 0.5), margin: [0.03, 0.02, 0.03, 0.0] });
  };
  tbl(2.2, "Most that could be saved per year", [["National reported loss, 2024 (MHA)", "₹22,845 cr"],
    ["× share for one pilot bank (our assumption)", "2%"], ["× recall on synthetic data", pct(C.recall.mean)],
    ["= upper limit on savings", `₹${UPPER_CR} cr`]], 3);
  text(s, "Assumes every level-2 or level-3 alert stops the whole loss. Some customers pay anyway, so the real figure would be lower.",
    { x: px + 0.3, y: 3.95, w: 5.55, h: 0.5, fontSize: 11, color: MUTED });
  tbl(4.5, "Cost for 30 million users, 250 payments each per year", [["Servers (6 instances)", "₹4.2 lakh / yr"],
    ["Storing signed records (2.6 TB / yr)", "₹0.6 lakh / yr"], ["Genuine payments held at level 3", `≈ ${HOLDS_DAY.toLocaleString("en-IN")} / day`],
    ["Agent time at 5 minutes each", `≈ ${AGENT_H} h / day`]], 3);
  text(s, "Servers are cheap; staff time for reviews is the main cost. Development cost not included.",
    { x: px + 0.3, y: 6.35, w: 5.55, h: 0.45, fontSize: 11, color: MUTED });
  s.addNotes("The savings number is an upper limit based on an assumed share of the national loss, not a result. " +
    "The main running cost is people reviewing held payments, so the bank should set the level-3 limit carefully.");
}

// ============ 14. Finale plan ============
{
  const s = base(14, "13  ·  Next steps");
  title(s, "What we will build and show in the 48-hour finale");
  const plan = [["H+0–8", "Replay harness", "Run saved test sessions through the server and check the records."],
    ["H+8–20", "Android signals", "Read the 9 phone signals on a real Android phone and check them."],
    ["H+20–32", "Attack our model", "Try to beat it with three changed scams, then retrain."],
    ["H+32–44", "End-to-end run", "100 sessions through to agent review and release or report."],
    ["H+44–48", "Security review", "Walk through records, replay checks, two-person release, known limits."]];
  const cw = (W - 2 * MX) / 5, y = 2.25;
  hline(s, MX, y, W - 2 * MX - 0.3, INK2, 1.25);
  plan.forEach(([t, h, b], i) => {
    const x = MX + i * cw;
    dot(s, x + 0.1, y, 0.22, i === 4 ? ORANGE : NAVY, i === 4 ? ORANGE : NAVY);
    s.addText(t, { x, y: y + 0.35, w: cw - 0.25, h: 0.3, fontFace: BODY, fontSize: 14, bold: true, color: ORANGE, margin: 0, isTextBox: true });
    s.addText(h, { x, y: y + 0.7, w: cw - 0.2, h: 0.4, fontFace: HEAD, fontSize: 17, bold: true, color: INK, margin: 0, isTextBox: true });
    text(s, b, { x, y: y + 1.2, w: cw - 0.3, h: 1.1, fontSize: 14 });
  });
  const by = 4.7, bw = (W - 2 * MX - 0.4) / 2;
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y: by, w: bw, h: 1.75, fill: { color: TINT }, line: { color: TINT } });
  s.addText("Built so far", { x: MX + 0.3, y: by + 0.2, w: bw - 0.6, h: 0.3, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  text(s, "Scoring server · threshold setting · signed records with replay checks · synthetic data generator and evaluation · 8 automated tests",
    { x: MX + 0.3, y: by + 0.6, w: bw - 0.6, h: 1.0, fontSize: 14 });
  s.addShape(pres.shapes.RECTANGLE, { x: MX + bw + 0.4, y: by, w: bw, h: 1.75, fill: { color: WHITE }, line: { color: MUTED, width: 1, dashType: "sysDot" } });
  s.addText("Not built yet", { x: MX + bw + 0.7, y: by + 0.2, w: bw - 0.6, h: 0.3, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  text(s, "Android SDK · payment hold · agent screen · testing on real bank data",
    { x: MX + bw + 0.7, y: by + 0.6, w: bw - 0.6, h: 1.0, fontSize: 14 });
  s.addNotes("In the finale we will move the phone signals from synthetic to real, attack our own model, and run 100 sessions end to end.");
}

// ============ 15. Closing (dark) ============
{
  const s = base(15, null, true);
  s.addText("Chakravyuh", { x: MX + 0.1, y: 0.9, w: 8, h: 0.9, fontFace: HEAD, fontSize: 44, bold: true, color: ONNAVY, margin: 0, isTextBox: true });
  s.addText("Intercept the scam workflow, not the transaction.", { x: MX + 0.1, y: 1.8, w: 10, h: 0.5, fontFace: HEAD, italic: true, fontSize: 22, color: NAVYMUTED, margin: 0, isTextBox: true });
  const K = [[pct(C.recall.mean), "of synthetic scam sessions reach level 2 or 3"], [`${C.fp.mean.toFixed(2)} / 1,000`, "genuine payments interrupted"],
    ["20", "signals, none of them raw audio, text or screen content"]];
  K.forEach(([a, b], i) => {
    const x = MX + 0.1 + i * 4.0;
    s.addText(a, { x, y: 3.1, w: 3.7, h: 0.9, fontFace: HEAD, fontSize: 40, bold: true, color: i === 0 ? ORANGE : ONNAVY, margin: 0, isTextBox: true });
    text(s, b, { x, y: 4.0, w: 3.5, h: 0.7, fontSize: 15, color: NAVYMUTED });
  });
  hline(s, MX + 0.1, 5.5, W - 2 * MX - 0.2, NAVYRULE, 0.75);
  s.addText("Thank you. Questions welcome.", { x: MX + 0.1, y: 5.75, w: 7, h: 0.5, fontFace: HEAD, fontSize: 24, color: ONNAVY, margin: 0, isTextBox: true });
  s.addText("Mathews V Manoj  ·  24ec357@mgits.ac.in", { x: MX + 0.1, y: 6.35, w: 7, h: 0.35, fontFace: BODY, fontSize: 14, color: NAVYMUTED, margin: 0, isTextBox: true });
  s.addText("All results are on synthetic data.", { x: W - MX - 4.1, y: 6.35, w: 4, h: 0.35, fontFace: BODY, fontSize: 12, italic: true, color: NAVYMUTED, align: "right", margin: 0, isTextBox: true });
  s.addNotes("To sum up: we look at the steps before a scam payment, only interrupt when several appear together, and always give a reason.");
}

// ============ 16. Appendix: signals ============
{
  const s = base(16, "Appendix");
  title(s, "All 20 signals and their weights", false, 0.7, 28);
  const SIG = [["call_unknown_active", "contact", "phone", "On a call with a number not in contacts"], ["call_long", "contact", "phone", "Call longer than 20 minutes"],
    ["video_call", "contact", "phone", "Video/VoIP call active"], ["sms_scam_flag", "contact", "phone", "Scam-lure SMS in the last 24 h"],
    ["bait_credit_7d", "contact", "bank", "Small ‘profit’ credits from strangers, last 7 days"], ["remote_access", "control", "phone", "Screen-sharing app running"],
    ["sideload_24h", "control", "phone", "App installed outside Play Store, last 24 h"], ["accessibility_overlay", "control", "phone", "App can read and draw over the screen"],
    ["otp_read_in_call", "control", "phone", "OTP opened during the unknown call"], ["first_time_payee", "extraction", "bank", "Never paid this account before"],
    ["amount_high", "extraction", "bank", "Amount far above usual"], ["amount_very_high", "extraction", "bank", "Top 0.1% of the customer’s history"],
    ["balance_drain", "extraction", "bank", "More than 70% of the balance"], ["staircase", "extraction", "bank", "Several new-payee payments in 60 min"],
    ["fd_broken_24h", "extraction", "bank", "Fixed deposit broken or loan taken, last 24 h"], ["vpa_typed", "extraction", "phone", "Payee typed instead of scanned or picked"],
    ["collect_from_p2p", "extraction", "receiving acct.", "Collect request from an individual"], ["payee_mule_high", "cash-out", "receiving acct.", "Account behaves like a mule"],
    ["payee_new_account", "cash-out", "receiving acct.", "Account less than 30 days old"], ["payee_registry_hit", "cash-out", "receiving acct.", "Account on a suspect list"]];
  const Wt = F.weights;
  const hdr = ["Signal", "Stage", "Source", "Weight", "Meaning"].map(t => ({ text: t, options: { bold: true, color: INK2 } }));
  const half = (arr) => arr.map(([k, st, src, m]) => [{ text: k, options: { fontFace: "Courier New", color: INK, fontSize: 9.5 } },
    { text: st }, { text: src }, { text: "+" + Wt[k].toFixed(2), options: { align: "right" } }, { text: m }]);
  const opts = (x) => ({ x, y: 1.45, w: 6.0, colW: [1.95, 0.75, 0.9, 0.55, 1.85], fontFace: BODY, fontSize: 10, color: INK2, valign: "middle",
    border: HB(RULE, 0.5), rowH: 0.43, margin: [0.02, 0.06, 0.02, 0.0] });
  s.addTable([hdr, ...half(SIG.slice(0, 10))], opts(MX));
  s.addTable([hdr, ...half(SIG.slice(10))], opts(MX + 6.15));
  text(s, "Weights from logistic regression (L2, C = 0.3) on synthetic dataset 7, kept at zero or above. Stage caps 5 / 5 / 6 / 6; a stage is active at 1.5 or more. " +
    "Full methods, confidence intervals and assumptions are in the written submission PDF.", { x: MX, y: 6.35, w: 12, h: 0.55, fontSize: 11, color: MUTED });
  s.addNotes("Reference slide with every signal and its learned weight.");
}

pres.writeFile({ fileName: path.resolve(__dirname, "Chakravyuh_RAKSHAM_Round1.pptx") }).then(f => console.log("wrote", f));

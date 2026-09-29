// Chakravyuh — RAKSHAM Round 1 presentation (PowerPoint).
// All numbers are read from eval/out/final.json (eval/final_numbers.py).
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const F = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../../eval/out/final.json"), "utf8"));
const C = F.chakravyuh, B = F.baselines, J = F.judge;
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


// ------------ slide ------------
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


// ------------ slide ------------
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


// ------------ slide ------------
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


// ------------ slide ------------
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
  s.addText("Nothing is blocked permanently. A person decides every hold.", { x: MX, y: 6.8, w: 9, h: 0.35,
    fontFace: HEAD, italic: true, fontSize: 16, color: INK, margin: 0, isTextBox: true });
  s.addNotes("The response grows with the evidence. Level 1 is silent. Level 2 warns and asks two questions but never blocks. " +
    "Level 3 holds the payment for up to 30 minutes and a bank agent reviews it. The rates shown are measured on our synthetic test data.");
}


// ------------ slide ------------
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
  const oy = 3.75, ow = 3.9;
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
  // level 2 and level 3 screens
  [["mockup_tier2.png", "Level 2: warn and ask"], ["mockup_tier3.png", "Level 3: hold (her case)"]].forEach(([f, cap], i) => {
    const x = 9.0 + i * 1.95;
    s.addImage({ path: path.resolve(__dirname, f), x, y: 1.3, w: 1.8, h: 1.8 * 2790 / 1350, altText: cap + " screen mock-up" });
    s.addText(cap, { x: x - 0.1, y: 5.12, w: 2.0, h: 0.3, fontFace: BODY, fontSize: 11, color: MUTED, align: "center", margin: 0, isTextBox: true });
  });
  s.addNotes("Five warning signs appear before the payment. Today a generic rule shows a warning the caller talks her past. " +
    "With Chakravyuh all four stages are active, so the payment is held and she sees a specific message.");
}


// ------------ slide ------------
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
    ["Stage caps", "A safety limit (C = 5, 5, 6, 6). It made no measurable difference on our data."],
    ["Two-stage rule", "We only interrupt when at least two stages are active."],
    ["Real-world scam rate", "Training data is 3.8% scams; we adjust to an assumed 1 in 5,000."],
    ["Fixed thresholds", "Set on a separate dataset to meet the bank’s alert limit, then fixed."]];
  s.addTable(rows.map(([a, b]) => [{ text: a, options: { bold: true, color: INK } }, { text: b, options: { color: INK2 } }]),
    { x: 7.1, y: 3.55, w: 5.63, colW: [1.85, 3.78], fontFace: BODY, fontSize: 13, valign: "top",
      border: HB(), margin: [0.07, 0.08, 0.07, 0.0], rowH: 0.56 });
  s.addNotes("Each signal has a weight learned by logistic regression. Weights are summed per stage and capped. " +
    "The two-stage rule is what stops one odd signal, like a new payee, from interrupting a genuine payment.");
}


// ------------ slide ------------
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
  // hand-drawn chart: scams caught vs genuine payments interrupted (baselines at a matched alert rate)
  const gx0 = 5.6, gx1 = 12.5, gy0 = 5.45, gy1 = 2.15, X0 = 2.4, X1 = 3.1, Y0 = 91, Y1 = 98;
  const px = (v) => gx0 + (v - X0) / (X1 - X0) * (gx1 - gx0), py = (v) => gy0 - (v - Y0) / (Y1 - Y0) * (gy0 - gy1);
  s.addText("Scams caught vs genuine payments interrupted", { x: gx0, y: 1.72, w: 6.9, h: 0.3, fontFace: BODY, bold: true, fontSize: 13, color: INK, margin: 0, isTextBox: true });
  for (let v = 92; v <= 98; v += 2) {
    s.addShape(pres.shapes.LINE, { x: gx0, y: py(v), w: gx1 - gx0, h: 0, line: { color: "E8EAED", width: 0.75 } });
    s.addText(v + "%", { x: gx0 - 0.6, y: py(v) - 0.12, w: 0.5, h: 0.24, fontFace: BODY, fontSize: 10.5, color: MUTED, align: "right", margin: 0, isTextBox: true });
  }
  s.addShape(pres.shapes.LINE, { x: gx0, y: gy0, w: gx1 - gx0, h: 0, line: { color: "9AA3AE", width: 0.75 } });
  for (const v of [2.4, 2.6, 2.8, 3.0]) s.addText(v.toFixed(1), { x: px(v) - 0.3, y: gy0 + 0.05, w: 0.6, h: 0.24, fontFace: BODY, fontSize: 10.5, color: MUTED, align: "center", margin: 0, isTextBox: true });
  s.addText("genuine payments interrupted per 1,000  →  fewer is better", { x: gx0, y: gy0 + 0.3, w: gx1 - gx0, h: 0.25, fontFace: BODY, fontSize: 11, color: INK2, align: "center", margin: 0, isTextBox: true });
  const mp = J.matched_fp;
  const dots = [["Chakravyuh", C.fp.mean, C.recall.mean, ORANGE, "r"],
    ["Logistic regression", mp["Logistic regression"].fp.mean, mp["Logistic regression"].recall.mean, "4A5568", "r"],
    ["Gradient boosting", mp["Gradient boosting"].fp.mean, mp["Gradient boosting"].recall.mean, "4A5568", "a"],
    ["XGBoost", mp["XGBoost"].fp.mean, mp["XGBoost"].recall.mean, "4A5568", "b"],
    ["MLP", mp["MLP"].fp.mean, mp["MLP"].recall.mean, "4A5568", "r"]];
  dots.forEach(([n, fx, ry, col, pos]) => {
    const cx = px(fx), cy = py(ry * 100), r = 0.09;
    s.addShape(pres.shapes.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { color: col }, line: { color: col } });
    const lab = `${n}  ${pct(ry)}`;
    const o = { fontFace: BODY, fontSize: 11, color: col === ORANGE ? ORANGE : INK2, bold: col === ORANGE, margin: 0, isTextBox: true, h: 0.24, w: 2.4 };
    if (pos === "r") s.addText(lab, { ...o, x: cx + 0.15, y: cy - 0.12 });
    else if (pos === "a") s.addText(lab, { ...o, x: cx - 1.2, y: cy - 0.38, align: "center" });
    else s.addText(lab, { ...o, x: cx - 1.2, y: cy + 0.13, align: "center" });
  });
  const mm = J.matched_fp, mlo = Math.min(...Object.values(mm).map(v => v.recall.mean)), mhi = Math.max(...Object.values(mm).map(v => v.recall.mean));
  text(s, [{ text: "What we give up. ", options: { bold: true, color: INK } },
    { text: `At a similar alert rate (each tuned to ours), standard classifiers catch ${pct(mlo)}–${pct(mhi)} of scams, about 4 points more. ` +
      `${Math.round(J.gap_by_scenario.collect_request * 100)}% of that gap is collect-request scams, which only show one stage. ` +
      `The rule-based check (“new payee + high amount”, not shown) catches ${pct(B["Rule: new payee + high amount"].recall.mean)} at ${B["Rule: new payee + high amount"].fp.mean.toFixed(1)} per 1,000.` }],
    { x: 4.6, y: 6.2, w: 8.1, h: 0.75, fontSize: 12.5 });
  s.addNotes(`Recall ${pct(C.recall.mean)} with a 95% interval of ${ci(C.recall)}, at ${C.fp.mean.toFixed(2)} interruptions per 1,000. ` +
    "Every model is trained, tuned and tested on the same synthetic data. The standard classifiers catch slightly more scams; the next slide shows what our two-stage rule buys in exchange.");
}

// ------------ slide ------------
{
  const s = base(8, "7  ·  Why the two-stage rule");
  title(s, "Why not just use logistic regression?");
  text(s, "Logistic regression is also explainable and catches more scams. So we measured what our two-stage rule adds, at the same alert rate.",
    { x: MX, y: 1.45, w: 11, h: 0.5, fontSize: 16 });
  const ss = J.single_stage, lrm = J.matched_fp["Logistic regression"], ex = ss.example;
  const rows = [["", "Logistic regression", "Chakravyuh"],
    ["Scams caught", pct(lrm.recall.mean), pct(C.recall.mean)],
    ["Genuine payments interrupted per 1,000", lrm.fp.mean.toFixed(2), C.fp.mean.toFixed(2)],
    ["…of which showed only one stage", Math.round(ss.lr_single_stage_share_of_genuine_alerts * 100) + "%", "0%"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0 || (i === 3 && j === 2), align: j ? "right" : "left",
    color: i === 0 ? INK2 : (j === 2 && i === 3 ? ORANGE : INK), fontSize: i === 0 ? 13 : 16 } }))),
    { x: MX, y: 2.3, w: 6.6, colW: [3.8, 1.5, 1.3], fontFace: BODY, border: HB(), rowH: [0.45, 0.6, 0.6, 0.6], valign: "middle", margin: [0.04, 0.08, 0.04, 0.0] });
  // example
  const ex_x = 7.7;
  s.addShape(pres.shapes.RECTANGLE, { x: ex_x, y: 2.2, w: 5.03, h: 2.75, fill: { color: TINT }, line: { color: TINT } });
  s.addText("A genuine payment the rule spares", { x: ex_x + 0.3, y: 2.38, w: 4.5, h: 0.3, fontFace: BODY, bold: true, fontSize: 14, color: INK, margin: 0, isTextBox: true });
  s.addText(`₹${ex.amount.toLocaleString("en-IN")}`, { x: ex_x + 0.3, y: 2.75, w: 4.5, h: 0.6, fontFace: HEAD, bold: true, fontSize: 30, color: INK, margin: 0, isTextBox: true });
  text(s, "A shopkeeper pays on a collect request from a new payee. No call, no screen-sharing, a normal receiving account. " +
    "Logistic regression interrupts it. Chakravyuh sees one stage, so it only logs it.", { x: ex_x + 0.3, y: 3.45, w: 4.45, h: 1.3, fontSize: 14 });
  s.addText("From our synthetic test data.", { x: ex_x + 0.3, y: 4.62, w: 4.45, h: 0.25, fontFace: BODY, italic: true, fontSize: 11, color: MUTED, margin: 0, isTextBox: true });
  // cost
  s.addText("The cost", { x: MX, y: 5.35, w: 4, h: 0.35, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  text(s, "Scams that only ever show one stage get through, mostly collect-request scams. We will add a specific warning for " +
    "collect requests from individuals and test it in the finale.", { x: MX, y: 5.7, w: 11.5, h: 0.8, fontSize: 15 });
  s.addNotes("This answers the obvious question from an ML judge. At the same alert rate, logistic regression catches about 4 points more scams, " +
    "but half of the genuine payments it interrupts show only one stage of a scam. Our rule never does that. The price is collect-request scams, which we will handle with a targeted warning.");
}

// ------------ slide ------------
{
  const s = base(9, "8  ·  Robustness");
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


// ------------ slide ------------
{
  const s = base(10, "9  ·  Feasibility");
  title(s, "Which phone signals a banking app can actually read");
  text(s, "Android and Google Play restrict some of what an app can see. We checked each of our 9 phone signals.",
    { x: MX, y: 1.45, w: 11, h: 0.4, fontSize: 16 });
  const ok = [["Call active and how long", "phone-state permission"], ["Video or VoIP call", "audio mode, no permission"],
    ["Screen-sharing or remote-control app", "known app list + accessibility services"], ["App drawing over our screen", "obscured-touch flag"],
    ["Payee typed in by hand", "our own payment screen"]];
  const no = [["Caller not in contacts", "call log is restricted", "use call length only"], ["Scam SMS received", "SMS access is restricted", "drop on the phone"],
    ["Any app sideloaded", "all-apps visibility is restricted", "check a fixed list of apps"], ["OTP opened during a call", "other apps’ notifications", "bank checks its own OTP timing"]];
  s.addText("Readable (5)", { x: MX, y: 2.1, w: 5, h: 0.35, fontFace: BODY, bold: true, fontSize: 16, color: INK, margin: 0, isTextBox: true });
  s.addTable(ok.map(([a, b]) => [{ text: "✓", options: { color: INK, bold: true } }, { text: a, options: { color: INK } }, { text: b, options: { color: MUTED, fontSize: 12 } }]),
    { x: MX, y: 2.5, w: 5.8, colW: [0.35, 2.85, 2.6], fontFace: BODY, fontSize: 14, border: HB(), rowH: 0.5, valign: "middle", margin: [0.03, 0.06, 0.03, 0.0] });
  s.addText("Restricted (4), with fallbacks", { x: 6.85, y: 2.1, w: 5.5, h: 0.35, fontFace: BODY, bold: true, fontSize: 16, color: ORANGE, margin: 0, isTextBox: true });
  s.addTable(no.map(([a, b, c]) => [{ text: a, options: { color: INK } }, { text: b, options: { color: MUTED, fontSize: 12 } }, { text: c, options: { color: INK2, fontSize: 12 } }]),
    { x: 6.85, y: 2.5, w: 5.88, colW: [2.3, 1.9, 1.68], fontFace: BODY, fontSize: 14, border: HB(), rowH: 0.62, valign: "middle", margin: [0.03, 0.06, 0.03, 0.0] });
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 5.45, w: W - 2 * MX, h: 1.25, fill: { color: "FDF1EA" }, line: { color: "FDF1EA" } });
  s.addText(pct(J.feasible_only.recall.mean), { x: MX + 0.3, y: 5.6, w: 2.4, h: 0.9, fontFace: HEAD, bold: true, fontSize: 40, color: ORANGE, margin: 0, isTextBox: true });
  text(s, `Recall when we retrain with only the 5 readable phone signals, at ${J.feasible_only.fp.mean.toFixed(2)} interruptions per 1,000 ` +
    `(synthetic data). With all 9 it is ${pct(C.recall.mean)}. Most of the evidence comes from the bank side, so losing the restricted signals costs little.`,
    { x: MX + 2.8, y: 5.65, w: 8.9, h: 0.95, fontSize: 15 });
  s.addNotes("Four of the phone signals need access that Google Play restricts, such as the call log and SMS. We removed them and retrained: recall only drops from 92.3 to 91.5 percent.");
}

// ------------ slide ------------
{
  const s = base(11, "10  ·  Privacy");
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
    { text: "and a hashed payee ID", options: { fontSize: 16, color: INK, breakLine: true } },
    { text: "Items 1, 4, 6 and 8 are restricted on Android; see slide 10.", options: { fontSize: 11, color: MUTED } }],
    { x: x2, y: colY + 0.4, w: 4.6, h: 0.95, fontFace: BODY, margin: 0, valign: "top", isTextBox: true });
  const dev = ["on a call with an unknown number", "call longer than 20 minutes", "video call active", "scam-lure SMS in last 24 h",
    "screen-sharing app running", "app sideloaded in last 24 h", "app drawing over the payment screen", "OTP opened during the call",
    "payee typed in by hand"];
  s.addText(dev.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < dev.length - 1 } })),
    { x: x2, y: colY + 1.45, w: 4.4, h: 2.45, fontFace: BODY, fontSize: 13, color: INK2, margin: 0, paraSpaceAfter: 2, valign: "top", isTextBox: true });
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


// ------------ slide ------------
{
  const s = base(12, "11  ·  Deployment");
  title(s, "How it would run in a bank");
  [["built", "solid", INK, 1.5], ["synthetic data", "dash", MUTED, 1], ["planned", "sysDot", MUTED, 1]].forEach(([l, d, c, wd], i) => {
    const lx = MX + [0, 1.3, 3.4][i];
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.45, w: 0.45, h: 0.25, fill: { color: WHITE }, line: { color: c, width: wd, dashType: d } });
    s.addText(l, { x: lx + 0.55, y: 1.43, w: 1.8, h: 0.3, fontFace: BODY, fontSize: 13, color: INK2, margin: 0, isTextBox: true });
  });
  const box = (x, y, w, h, t, sub, st) => {
    const style = { built: [INK, "solid", 1.5], simulated: [MUTED, "dash", 1], planned: [MUTED, "sysDot", 1] }[st];
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: WHITE }, line: { color: style[0], width: style[2], dashType: style[1] } });
    s.addText(t, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: st === "planned" ? INK2 : INK, margin: 0, isTextBox: true });
    text(s, sub, { x: x + 0.12, y: y + 0.4, w: w - 0.24, h: h - 0.45, fontSize: 11, color: st === "planned" ? MUTED : INK2 });
  };
  const L = MX, bw = 2.35, g = 0.15, bh = 0.95;
  const row = (y, label, items) => {
    s.addText(label, { x: L, y, w: 7.5, h: 0.28, fontFace: BODY, fontSize: 12, bold: true, color: INK2, margin: 0, isTextBox: true });
    items.forEach((it, i) => box(L + i * (bw + g), y + 0.32, bw, bh, ...it));
  };
  row(1.95, "Phone (inside the bank’s app)", [["Signal readers", "5 readable phone signals.", "simulated"],
    ["Request builder", "Nonce, timestamp, Play Integrity.", "planned"], ["Warning screens", "Level 2 and 3 screens.", "simulated"]]);
  row(3.35, "Bank fraud servers", [["Scoring server", "Stages, rule, level, reasons.", "built"],
    ["Input checks + records", "Replay checks, HMAC signing.", "built"], ["Agent screen", "Held payments, 2-person release.", "planned"]]);
  row(4.75, "Bank data and payments", [["Mule score, suspect list", "From the bank’s own data.", "simulated"],
    ["Payment hold", "Time-limited, before the PIN.", "planned"], ["Reporting", "Confirmed scams to I4C / 1930.", "planned"]]);
  s.addText("No integration with Amazon, NPCI, I4C or any bank exists yet.", { x: MX, y: 6.2, w: 7.4, h: 0.3, fontFace: BODY, italic: true, fontSize: 11, color: MUTED, margin: 0, isTextBox: true });
  // right column: rollout + cost
  const rx = 8.55;
  s.addText("Rollout", { x: rx, y: 1.95, w: 4, h: 0.3, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  [["Weeks 0–6", "Shadow mode: score, show nothing, tune thresholds."], ["Weeks 6–10", "Levels 1 and 2 for customers who opt in."],
    ["From week 10", "Level 3 holds with agent review."]].forEach(([a, b], i) => {
    const y = 2.35 + i * 0.62;
    s.addText(a, { x: rx, y, w: 1.3, h: 0.3, fontFace: BODY, bold: true, fontSize: 12, color: ORANGE, margin: 0, isTextBox: true });
    text(s, b, { x: rx + 1.35, y, w: 2.85, h: 0.55, fontSize: 12 });
  });
  s.addText("Running cost (estimate)", { x: rx, y: 4.4, w: 4.2, h: 0.3, fontFace: BODY, bold: true, fontSize: 15, color: INK, margin: 0, isTextBox: true });
  text(s, [{ text: "Servers and storage: ", options: { bold: true, color: INK } }, { text: "about ₹5 lakh a year for 30 million users.", options: { breakLine: true } },
    { text: "Staff: ", options: { bold: true, color: INK } }, { text: `about ${HOLDS_DAY.toLocaleString("en-IN")} genuine payments held a day, roughly ${AGENT_H} agent-hours. This is the real cost.` }],
    { x: rx, y: 4.75, w: 4.2, h: 1.4, fontSize: 12.5 });
  s.addNotes("The scoring server, input checks and signed records are built and tested. The phone SDK, payment hold and agent screen are planned. " +
    "Running cost is small for servers; the main cost is staff reviewing held payments.");
}

// ------------ slide ------------
{
  const s = base(13, "12  ·  Next steps");
  title(s, "What we will build and show in the 48-hour finale");
  const plan = [["H+0–8", "Replay harness", "Run saved test sessions through the server and check the records."],
    ["H+8–20", "Android signals", "Read the 5 allowed phone signals on one test phone."],
    ["H+20–32", "Collect-request rule", "Add the targeted warning, re-test, then attack our own model."],
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
  text(s, "Android SDK · collect-request rule · payment hold · agent screen · testing on real bank data",
    { x: MX + bw + 0.7, y: by + 0.6, w: bw - 0.6, h: 1.0, fontSize: 14 });
  s.addNotes("The finale plan is scoped to what we can show: the five allowed phone signals on one phone, the collect-request warning, and a 100-session end-to-end run.");
}

// ------------ slide ------------
{
  const s = base(14, null, true);
  s.addText("Chakravyuh", { x: MX + 0.1, y: 0.9, w: 8, h: 0.9, fontFace: HEAD, fontSize: 40, bold: true, color: NAVYMUTED, margin: 0, isTextBox: true });
  s.addText("A scam is a sequence.\nWe wait for the sequence before we stop a payment.", { x: MX + 0.1, y: 2.3, w: 11.5, h: 1.9,
    fontFace: HEAD, fontSize: 40, bold: true, color: ONNAVY, margin: 0, valign: "top", isTextBox: true });
  text(s, `On synthetic data: ${pct(C.recall.mean)} of scams caught, ${C.fp.mean.toFixed(2)} genuine payments interrupted per 1,000, ` +
    "and, by design, no payment stopped on the evidence of one stage alone.", { x: MX + 0.1, y: 4.45, w: 10.5, h: 0.8, fontSize: 17, color: NAVYMUTED });
  hline(s, MX + 0.1, 5.5, W - 2 * MX - 0.2, NAVYRULE, 0.75);
  s.addText("Thank you. Questions welcome.", { x: MX + 0.1, y: 5.75, w: 7, h: 0.5, fontFace: HEAD, fontSize: 24, color: ONNAVY, margin: 0, isTextBox: true });
  s.addText("Mathews V Manoj  ·  24ec357@mgits.ac.in", { x: MX + 0.1, y: 6.35, w: 7, h: 0.35, fontFace: BODY, fontSize: 14, color: NAVYMUTED, margin: 0, isTextBox: true });
  s.addNotes("One line to remember: a scam is a sequence, and we wait for the sequence.");
}

// ------------ slide ------------
{
  const s = base(15, "Appendix");
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


// ------------ slide ------------
{
  const s = base(16, "Appendix");
  title(s, "Security checks", false, 0.7, 28);
  const ctl = [["Old or repeated requests", "One-time nonce and a 15-second limit", "built"],
    ["Extra or fake fields", "Only the 20 known signals are accepted", "built"],
    ["Edited decision records", "Each record signed with HMAC-SHA256", "built"],
    ["Fake or modified app", "Play Integrity token tied to a hash of the request", "planned"],
    ["Staff misuse", "Two approvers, both written into the record", "planned"],
    ["Record store leak", "No raw content in records; identity stored apart", "design only"],
    ["Poisoned labels", "Retrain only on bank-confirmed cases", "design only"]];
  s.addTable([["Risk", "What we do", "Status"].map(t => ({ text: t, options: { bold: true, color: INK2 } })),
    ...ctl.map(([a, b, c]) => [{ text: a, options: { color: INK } }, { text: b, options: { color: INK2 } },
      { text: c, options: { color: c === "built" ? INK : MUTED, italic: c !== "built" } }])],
    { x: MX, y: 1.5, w: 9.5, colW: [3.0, 5.0, 1.5], fontFace: BODY, fontSize: 15, valign: "middle", border: HB(), rowH: 0.55, margin: [0.04, 0.08, 0.04, 0.0] });
  text(s, "The three built checks are covered by automated tests, including one that replays a request and checks it is rejected.",
    { x: MX, y: 6.05, w: 11, h: 0.5, fontSize: 13, color: MUTED });
  s.addNotes("Reference slide for security questions.");
}

pres.writeFile({ fileName: path.resolve(__dirname, "Chakravyuh_RAKSHAM_Round1.pptx") }).then(f => console.log("wrote", f));

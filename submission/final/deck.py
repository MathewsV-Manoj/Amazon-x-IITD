"""Generate the final RAKSHAM Round-1 deck as HTML (printed to PDF by render.js).

Every number is read from eval/out/final.json (eval/final_numbers.py).
Modelled figures are computed here from explicit, labelled assumptions.
"""
from __future__ import annotations

import json
from pathlib import Path

import charts
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from chakravyuh.signals import SIGNALS, STAGE_LABELS  # noqa: E402

HERE = Path(__file__).resolve().parent
F = json.loads((ROOT / "eval" / "out" / "final.json").read_text())
C = F["chakravyuh"]; B = F["baselines"]
TOTAL = 16

TEAM = [("Mathews V Manoj", "B.Tech Electronics & Communication, Muthoot Institute of Technology and Science (KTU)")]


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def ci_pct(m, d=1):
    return f"[{m['lo'] * 100:.{d}f}%, {m['hi'] * 100:.{d}f}%]"


# ---------------- modelled figures (explicit assumptions) ----------------
USERS = 30e6; SESS_PER_USER = 250
SESSIONS = USERS * SESS_PER_USER
AVG_QPS = SESSIONS / (365 * 24 * 3600)
PEAK_QPS = AVG_QPS * 10
PER_INSTANCE_QPS = 1000
INSTANCES = max(6, -(-int(PEAK_QPS) // PER_INSTANCE_QPS) * 2)
INSTANCE_INR_HR = 8.0
COMPUTE_INR = INSTANCES * INSTANCE_INR_HR * 24 * 365
RECEIPT_B = 350
STORAGE_GB = SESSIONS * RECEIPT_B / 1e9
STORAGE_INR = STORAGE_GB * 2.0 * 12
INFRA_LAKH = (COMPUTE_INR + STORAGE_INR) / 1e5
FALSE_HOLDS_DAY = SESSIONS * C["t3_fp"]["mean"] / 1000 / 365
AGENT_HOURS_DAY = FALSE_HOLDS_DAY * 5 / 60
NATIONAL_LOSS_CR = 22845
EXPOSURE_SHARE = 0.02
EXPOSURE_CR = NATIONAL_LOSS_CR * EXPOSURE_SHARE
UPPER_CR = EXPOSURE_CR * C["recall"]["mean"]

# ---------------- building blocks ----------------


ZOOM = {2: 1.2, 3: 1.1, 4: 1.16, 5: 1.2, 6: 1.2, 7: 1.1, 8: 1.16, 9: 1.16, 10: 1.2, 11: 1.12, 12: 1.12, 13: 1.18}


def frame(n, section, body, dark=False, cls=""):
    return f"""
<section class="slide {'dark' if dark else ''} {cls}">
  <header><span class="sec">{section}</span><span class="brand">CHAKRAVYUH</span></header>
  <div class="body" style="zoom:{ZOOM.get(n, 1.0)}">{body}</div>
  <footer><span>RAKSHAM · Amazon × IIT Delhi · Round 1 · Track 02 — AI-driven scam pattern recognition</span>
  <span class="pg">{n:02d} / {TOTAL}</span></footer>
</section>"""


def status(s):
    return f'<span class="st st-{s.lower()}">{s}</span>'


ARROW = '<span class="arr">→</span>'


def svg_inline(name):
    s = (ROOT / "submission" / "assets" / name).read_text()
    return s[s.index("<svg"):]


# ---------------- slides ----------------


def s01():
    team = "".join(f"<div><b>{n}</b><span>{d}</span></div>" for n, d in TEAM)
    return f"""
<section class="slide dark cover">
  <div class="cv-top mono">RAKSHAM · AMAZON × IIT DELHI · ROUND 1 &nbsp;/&nbsp; TRACK 02 — AI-DRIVEN SCAM PATTERN RECOGNITION</div>
  <div class="cv-main">
    <h1 class="cv-title">Chakravyuh</h1>
    <p class="cv-tag">Intercept the scam workflow,<br>not the transaction.</p>
    <p class="cv-lede">A decision engine for UPI and bank payments that reads each payment session as a
    four-stage scam workflow — contact, control, extraction, cash-out — and escalates only when
    that workflow forms, with a reason the customer can read and a signed receipt the bank can audit.</p>
  </div>
  <div class="cv-chain">
    <div class="node"><i></i><span>Contact</span></div><div class="link"></div>
    <div class="node"><i></i><span>Control</span></div><div class="link"></div>
    <div class="node"><i></i><span>Extraction</span></div><div class="link"></div>
    <div class="node"><i></i><span>Cash-out</span></div><div class="link gate"></div>
    <div class="node end"><i></i><span>Decision</span></div>
  </div>
  <div class="cv-foot">
    <div class="team"><span class="mono lbl">TEAM</span>{team}</div>
    <div class="note mono">All results in this document come from synthetic data.<br>No real customer, bank or platform data was used.</div>
  </div>
</section>"""


def s02():
    body = f"""
<h2>The victim presses Pay.</h2>
<p class="lede">In authorised-payment scams the fraud happens <em>before</em> the transaction.
When the payment is finally made, the PIN is correct, the device is the customer's own and the customer means to pay.</p>
<div class="prob">
  <div class="seq">
    <div class="who mono">SCAMMER</div>
    <div class="step s1"><b>Contact</b><span>A “CBI officer” video-calls about a money-laundering case</span></div>
    <div class="step s2"><b>Control</b><span>A screen-sharing app is installed “for verification”</span></div>
    <div class="step s3"><b>Money extraction</b><span>A fixed deposit is broken; a new payee is typed in</span></div>
    <div class="step pay"><b>Victim presses Pay</b><span>₹2,50,000 to a personal UPI ID</span></div>
    <div class="brk b1"><span>Invisible to a transaction-only view</span></div>
    <div class="brk b2"><span>The only moment a transaction system scores</span></div>
  </div>
  <div class="stats">
    <div class="stat"><div class="big">₹22,845 cr</div><div class="cap">lost to cyber fraud in India in 2024</div></div>
    <div class="stat"><div class="big">36.37 lakh</div><div class="cap">complaints filed in 2024</div></div>
    <div class="src mono">Source: Ministry of Home Affairs, reply in Lok Sabha, July 2025 (NCRP and CFCFRMS data).</div>
    <p class="punch">Traditional fraud systems often see only the final transaction — and every
    credential in it is genuine.</p>
  </div>
</div>"""
    return frame(2, "01 — Problem", body)


def s03():
    stages = [
        ("01", "Contact", "device", ["call with an unknown number", "call longer than 20 min", "scam-lure SMS (classified on-device)"]),
        ("02", "Control", "device", ["screen-sharing app running", "app sideloaded in last 24 h", "OTP opened during the call"]),
        ("03", "Extraction", "bank", ["first-time payee, typed VPA", "&gt; 70% of balance", "fixed deposit broken in last 24 h"]),
        ("04", "Cash-out", "network", ["payee behaves like a mule", "payee account &lt; 30 days old", "payee on a suspect registry"]),
    ]
    cols = "".join(f"""<div class="stg"><div class="n mono">{n}</div><div class="name">{name}</div>
      <ul>{''.join(f'<li>{s}</li>' for s in sig)}</ul><div class="src mono">signals from {src}</div></div>"""
                   for n, name, src, sig in stages)
    body = f"""
<h2>Score the workflow, not the transaction.</h2>
<div class="cmp">
  <div class="row"><span class="mono lbl">TRANSACTION VIEW</span><span class="box">one payment</span>{ARROW}<span class="out">suspicious / not suspicious</span></div>
  <div class="row"><span class="mono lbl acc">WORKFLOW VIEW</span><span class="chainline">contact {ARROW} control {ARROW} extraction {ARROW} cash-out</span>{ARROW}<span class="out acc">graduated response</span></div>
</div>
<div class="stages">{cols}</div>
<div class="rule-line"></div>
<p class="thesis">A single signal should not trigger a severe intervention. <b>The workflow must form.</b></p>
<p class="thesis-sub">A legitimate payment can look odd in isolation — a new payee on rent day, a long call with a plumber.
A scam becomes visible through its sequence. Full catalogue of 20 signals: Appendix A.</p>"""
    return frame(3, "02 — Insight", body, dark=True, cls="hero")


def s04():
    t = [("Tier 1", "Observe", "Fused score above τ₁", "Nothing. The session is logged to the bank's fraud queue.",
          f'{C["t1_fp"]["mean"]:.1f}', "20"),
         ("Tier 2", "Explain + verify", "Score above τ₂ <b>and</b> ≥ 2 stages active",
          "A warning naming the specific scam pattern, and two questions. The customer can still pay.",
          f'{C["fp"]["mean"]:.2f}', "3"),
         ("Tier 3", "Cool off + human review", "Score above τ₃ <b>and</b> ≥ 3 stages, or 2 stages + registry hit",
          "A 30-minute hold before the PIN screen. A bank agent reviews; release needs two approvers.",
          f'{C["t3_fp"]["mean"]:.2f}', "0.5")]
    steps = "".join(f"""<div class="tier t{i + 1}">
      <div class="tk mono">{a.upper()}</div><div class="tn">{b}</div>
      <div class="tt"><span class="mono lbl">TRIGGER</span>{c}</div>
      <div class="tu"><span class="mono lbl">CUSTOMER SEES</span>{d}</div>
      <div class="tr"><span class="num">{e}</span><span>legit sessions per 1,000<br><i>measured, synthetic · budget {f}</i></span></div>
    </div>""" for i, (a, b, c, d, e, f) in enumerate(t))
    body = f"""
<h2>Escalate only as the workflow forms.</h2>
<p class="lede">Friction grows with evidence. The bank sets an alert budget for each tier; thresholds are
calibrated to it on held-out data.</p>
<div class="stair">{steps}</div>
<p class="foot-note">No tier blocks a customer permanently. Every hold is time-boxed and released or confirmed by a person.</p>"""
    return frame(4, "03 — Response", body)


def s05():
    seq = [("Fake CBI video call", "contact"), ("Remote-access app", "control"), ("FD broken", "extraction"),
           ("First-time payee", "extraction"), ("Mule-like account", "cash-out"), ("₹2,50,000 payment", "")]
    chain = "".join(f"""<div class="ev {'last' if not st else ''}"><b>{a}</b><span class="mono">{st or 'the transaction'}</span></div>"""
                    + ("" if i == len(seq) - 1 else '<div class="evl"></div>') for i, (a, st) in enumerate(seq))
    body = f"""
<h2>Mrs R., 68. Five warning signs before one payment.</h2>
<p class="tag mono">ILLUSTRATIVE COMPOSITE SCENARIO</p>
<div class="story">
  <div class="left">
    <div class="evrow">{chain}</div>
    <div class="split">
      <div class="side without"><span class="mono lbl">WITHOUT CHAKRAVYUH</span>
        <p class="out">The payment proceeds.</p>
        <p>A “new payee + high amount” rule shows a generic warning. She reads it aloud to the caller and confirms.
        The money reaches a mule account.</p></div>
      <div class="side with"><span class="mono lbl acc">WITH CHAKRAVYUH</span>
        <p class="out">Held before the PIN screen.</p>
        <p>All four stages are active → Tier 3 → 30-minute hold → bank agent review.
        The screen names the pattern: real officials never ask for money on a call.</p></div>
    </div>
  </div>
  <div class="phone">{svg_inline('mockup_tier3.svg')}<div class="mono cap">Tier-3 screen (illustrative mock-up)</div></div>
</div>"""
    return frame(5, "04 — Worked case", body)


def s06():
    body = f"""
<h2>Four stages. One decision.</h2>
<div class="pipe">
  <div class="pb"><div class="pn">20</div><div class="pl">binary signals</div><div class="pd">9 device · 7 bank · 4 network</div></div>{ARROW}
  <div class="pb"><div class="pn">4</div><div class="pl">capped stage scores</div><div class="pd">sum of non-negative weights, capped per stage</div></div>{ARROW}
  <div class="pb"><div class="pn">≥ 2</div><div class="pl">kill-chain gate</div><div class="pd">active stages needed to interrupt</div></div>{ARROW}
  <div class="pb acc"><div class="pn">0–3</div><div class="pl">risk tier + reasons</div><div class="pd">top signals, scam playbook, signed receipt</div></div>
</div>
<div class="ml">
  <div class="eq">
    <div class="mono lbl">SCORE</div>
    <div class="formula">s(x) = b + <span class="big-s">Σ</span><sub>g</sub> min( C<sub>g</sub> , <span class="big-s">Σ</span><sub>k in g</sub> w<sub>k</sub> x<sub>k</sub> )</div>
    <div class="mono lbl" style="margin-top:14px">DECISION</div>
    <div class="formula sm"><b>Tier 2</b> &nbsp;if&nbsp; s ≥ τ<sub>2</sub> &nbsp;and&nbsp; active stages ≥ 2<br>
    <b>Tier 3</b> &nbsp;if&nbsp; s ≥ τ<sub>3</sub> &nbsp;and&nbsp; ( active stages ≥ 3 &nbsp;or&nbsp; ≥ 2 plus a registry hit )</div>
    <p class="small">g runs over the four stages; x<sub>k</sub> is 0 or 1; weights w<sub>k</sub> ≥ 0 from L2-regularised logistic regression on labelled
    sessions, clipped at zero. A stage is active when its capped score ≥ 1.5. Weights, caps and thresholds: Appendix A.</p>
  </div>
  <div class="principles">
    <div><b>Non-negative weights</b><span>A missing signal never adds or removes suspicion — attackers can always hide one.</span></div>
    <div><b>Stage caps</b><span>No single stage can carry a decision on its own (C = 5, 5, 6, 6).</span></div>
    <div><b>Cross-stage gate</b><span>An interruption needs evidence from at least two stages of the workflow.</span></div>
    <div><b>Prevalence adjustment</b><span>Intercept shifted from 3.8% scams in training to an assumed 1 in 5,000 in deployment.</span></div>
    <div><b>Calibrated thresholds</b><span>τ set on a separate validation world to the bank's alert budget, then frozen.</span></div>
  </div>
</div>"""
    return frame(6, "05 — Model", body)


def s07():
    gb = [B[k] for k in ["Logistic regression", "Gradient boosting", "XGBoost", "MLP"]]
    lo_r = min(b["recall"]["mean"] for b in gb); hi_r = max(b["recall"]["mean"] for b in gb)
    lo_f = min(b["fp"]["mean"] for b in gb); hi_f = max(b["fp"]["mean"] for b in gb)
    red = 1 - C["fp"]["mean"] / C["fp_nogate"]["mean"]
    body = f"""
<h2>What we measured — on synthetic data.</h2>
<div class="banner mono">SYNTHETIC EVALUATION · 8 INDEPENDENT UNSEEN WORLDS · NOT REAL-BANK VALIDATION</div>
<div class="res">
  <div class="kpis">
    <div class="kpi"><div class="k acc">{pct(C['recall']['mean'])}</div><div class="kl">Tier ≥ 2 recall on 8 unseen synthetic worlds</div>
      <div class="kc mono">95% CI {ci_pct(C['recall'])}</div></div>
    <div class="kpi"><div class="k">{C['fp']['mean']:.2f} / 1k</div><div class="kl">legitimate sessions interrupted — same evaluation</div>
      <div class="kc mono">95% CI [{C['fp']['lo']:.2f}, {C['fp']['hi']:.2f}] · budget 3.0</div></div>
    <div class="kpi"><div class="k">{C['auprc']['mean']:.3f}</div><div class="kl">AUPRC of the fused score</div>
      <div class="kc mono">95% CI [{C['auprc']['lo']:.3f}, {C['auprc']['hi']:.3f}]</div></div>
  </div>
  <div class="chart">{charts.operating_points(F)}
    <div class="mono cap">Same training, calibration and test worlds for every system. Bars: 95% bootstrap CI over the 8 worlds.</div></div>
</div>
<div class="res-note">
  <p><b>The trade-off, stated plainly.</b> Black-box classifiers reach {lo_r * 100:.1f}–{hi_r * 100:.1f}% recall at
  {lo_f:.1f}–{hi_f:.1f} interruptions per 1,000. Our own score with the gate removed reaches
  {pct(C['recall_nogate']['mean'])} at {C['fp_nogate']['mean']:.2f}. The kill-chain gate gives up
  {(C['recall_nogate']['mean'] - C['recall']['mean']) * 100:.1f} points of recall for {red * 100:.0f}% fewer interruptions,
  a guarantee that no single signal can interrupt a payment, and a reason that decomposes into named signals.</p>
  <p class="mono small">Train: world 7 · thresholds: world 21 · test: worlds 101–108 · each world 60,000 legitimate + 2,400 scam sessions.
  Engine time {C['latency_us']:.0f} µs per session (in-process, measured).</p>
</div>"""
    return frame(7, "06 — Evidence", body)


def s08():
    a = {d["suppressed"]: d["recall"] for d in F["adversarial"]}
    abl = {d["removed"]: d["recall"] for d in F["ablation"]}
    loo = [d["recall"] for d in F["loo"]]
    rows = [
        ("hide the signals they control?", "Hang up before paying, avoid screen-share, lower the amount.",
         "Independent stages. Extraction and cash-out evidence is observed by the bank, not the caller.",
         f"{pct(C['recall_adapted']['mean'])} recall on the adapted cohort (25% of scam sessions). "
         f"Worst case — hiding the strongest emitted signal, even ones a fraudster cannot really hide: {pct(a[1], 0)}; two: {pct(a[2], 0)}.",
         "MEASURED"),
        ("split one payment into several?", "Four payments of ₹25,000 instead of one of ₹1,00,000.",
         "“Staircase” signal: two or more payments to new payees within 60 minutes.",
         "Not separately simulated in Round 1.", "DESIGN"),
        ("pay into older, rented mule accounts?", "Aged accounts hide the ‘young account’ signal.",
         "Mule score uses fan-in, first-time-sender share and pass-through — not age alone. Other stages still fire.",
         f"Mule score flags only 24% of aged mules; sessions paying them are still caught at {pct(C['recall_aged_mule']['mean'])}.",
         "MEASURED"),
        ("poison the training data?", "Flood the system with false ‘scam’ or ‘genuine’ reports.",
         "Retrain only on bank-confirmed outcomes; customer reports never become labels on their own.",
         "Not evaluated.", "DESIGN"),
    ]
    tr = "".join(f"""<tr><td class="q"><span class="mono">{i + 1:02d}</span><b>… {q}</b><span>{ex}</span></td>
      <td>{d}</td><td>{e}</td><td>{status(s)}</td></tr>""" for i, (q, ex, d, e, s) in enumerate(rows))
    body = f"""
<h2>What survives when the attacker adapts?</h2>
<div class="adv">
  <table class="tbl"><thead><tr><th>Can the attacker…</th><th>Defence</th><th>Evidence</th><th></th></tr></thead><tbody>{tr}</tbody></table>
  <div class="aside">
    <div class="mono lbl">RECALL AS THE ATTACKER HIDES MORE</div>
    {charts.adversarial(F)}
    <p class="small">Attacker knows the published weights and removes the highest-weight signals present in each scam session.
    Thresholds are not re-tuned.</p>
    <div class="mono lbl" style="margin-top:10px">UNSEEN SCAM PLAYBOOK</div>
    <p class="small">Trained without one playbook, tested on it: {min(loo) * 100:.0f}–{max(loo) * 100:.0f}% recall.</p>
    <div class="mono lbl" style="margin-top:10px">NO STAGE IS DECORATIVE</div>
    <p class="small">Removing contact, control, extraction or cash-out evidence leaves
    {abl['contact'] * 100:.0f}%, {abl['control'] * 100:.0f}%, {abl['extraction'] * 100:.0f}%, {abl['cashout'] * 100:.0f}% recall.</p>
  </div>
</div>"""
    return frame(8, "07 — Adversary", body)


def s09():
    dev = [s for s in SIGNALS if s.source == "device"]
    never = ["Call audio", "Screen frames", "Message text", "Contact list", "OTP values", "App inventory"]
    body = f"""
<h2>What never leaves the phone.</h2>
<div class="priv">
  <div class="pcol never">
    <div class="mono lbl">NEVER LEAVES THE DEVICE</div>
    <ul>{''.join(f'<li><span class="x"></span>{n}</li>' for n in never)}</ul>
  </div>
  <div class="boundary"><span class="mono">DEVICE BOUNDARY</span></div>
  <div class="pcol leaves">
    <div class="mono lbl acc">LEAVES THE DEVICE</div>
    <div class="eqn"><b>9</b> derived booleans <span>+</span> amount <span>+</span> hashed payee VPA</div>
    <ol>{''.join(f'<li>{s.why}</li>' for s in dev)}</ol>
  </div>
  <div class="pcol bank">
    <div class="mono lbl">ALREADY INSIDE THE BANK</div>
    <p><b>7</b> bank-side signals computed on data the bank already holds — first-time payee, amount against
    the customer's history, balance drain, fixed-deposit break, recent small credits.</p>
    <p><b>4</b> network signals looked up in the bank's own feature store — mule score, account age,
    suspect-registry hit, collect request.</p>
    <p class="mono small">9 + 7 + 4 = 20 signals.</p>
  </div>
</div>
<div class="receipt">
  <div class="mono lbl acc">SIGNED DECISION RECEIPT</div>
  <code>{{ log_id, ts, session, amount, evidence (true only), score, tier, playbook, active_stages, action }} + HMAC-SHA256</code>
  <p>One identifier ties the customer's screen, the agent desk and any complaint to the exact evidence and weights.
  <b>Implemented:</b> the server accepts only the 20 catalogued keys and rejects replayed nonces and evidence older than 15 seconds.</p>
</div>
<p class="legal mono">Designed with the DPDP Act 2023 principles of purpose limitation and data minimisation.
This is a design alignment, not a legal certification. The on-device SDK is proposed; the server contract is implemented.</p>"""
    return frame(9, "08 — Privacy", body)


def s10():
    Y = '<svg class="ok" viewBox="0 0 12 12" width="12" height="12"><path d="M2 6.5 L5 9.2 L10.2 2.8" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
    N = '<span class="no">—</span>'
    rows = [("Transaction rules", Y, N, Y, N),
            ("Black-box ML classifier", Y, "only if engineered", "post-hoc only", N),
            ("Chakravyuh", Y, Y, Y, Y)]
    tr = "".join(f"<tr class='{'me' if r[0] == 'Chakravyuh' else ''}'><td>{r[0]}</td>" +
                 "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    plan = [("H+0–8", "Replay harness", "Synthetic sessions through /decide with signed receipts and replay checks."),
            ("H+8–20", "Android signal validation", "Measure the 9 device signals on a real handset against ground truth."),
            ("H+20–32", "Attacker adaptation", "Red-team three playbooks against published weights; retrain; compare."),
            ("H+32–44", "End-to-end replay", "100 sessions → tiers → agent-desk review → release or report."),
            ("H+44–48", "Security + audit walkthrough", "Receipts, replay rejection, dual-approver release, limitations.")]
    pl = "".join(f"<div class='ph'><div class='mono t'>{a}</div><b>{b}</b><span>{c}</span></div>" for a, b, c in plan)
    body = f"""
<h2>Workflow context is the difference.</h2>
<div class="diff">
  <table class="mx"><thead><tr><th></th><th>Transaction<br>context</th><th>Workflow<br>context</th><th>Explainable<br>reason</th><th>Graduated<br>response</th></tr></thead>
  <tbody>{tr}</tbody></table>
  <div>
    <p class="claim">Chakravyuh treats the surrounding scam workflow as first-class evidence.</p>
    <div class="why"><span class="mono lbl">WHY NOT A GENERIC CLASSIFIER?</span>
    <p>On the same synthetic worlds a black box catches about 4 points more scams (slide 7), but it cannot say which
    stage fired, and nothing stops one strong signal from interrupting a genuine payment. A customer, an agent and an
    ombudsman all need the reason.</p></div>
  </div>
</div>
<div class="plan">
  <div class="mono lbl">WHAT WE WILL PROVE IN THE 48-HOUR FINALE</div>
  <div class="phases">{pl}</div>
  <p class="small"><b>Built for Round 1:</b> decision engine, threshold calibration, signed receipts with replay checks,
  synthetic generator and evaluation, 8 automated tests. <b>Not yet built:</b> Android SDK, payment-rail hold, agent desk.</p>
</div>"""
    return frame(10, "09 — Position & next", body)


# ---------------- architecture ----------------


def box(title, sub, st):
    return f'<div class="ab ab-{st.lower()}"><div class="abh"><b>{title}</b>{status(st)}</div><span>{sub}</span></div>'


def a1():
    body = f"""
<h2>System architecture</h2>
<p class="lede">Four planes. Solid outlines are implemented in Round 1; dashed are simulated with synthetic data; dotted are proposed.</p>
<div class="arch">
  <div class="plane"><div class="pt mono">DEVICE · bank app SDK</div><div class="pr">
    {box('Signal probes', 'Call state, accessibility, installer, on-device SMS classifier. Synthetic in Round 1.', 'SIMULATED')}
    {box('Evidence composer', '9 booleans + amount + payee hash + nonce + timestamp + Play Integrity token.', 'PROPOSED')}
    {box('Tier 1–3 screens', 'Playbook message, two questions, hold screen. Mock-ups + web demo.', 'SIMULATED')}
  </div></div>
  <div class="flow mono">1 evidence ↓ &nbsp;&nbsp;&nbsp;&nbsp; 5 tier, message and receipt id ↑</div>
  <div class="plane"><div class="pt mono">BANK FRAUD-OPS VPC</div><div class="pr">
    {box('/decide engine', 'FastAPI. Stage scores, gate, tier, playbook, top reasons. Stateless.', 'IMPLEMENTED')}
    {box('Replay + schema guard', 'Nonce, 15 s freshness, only the 20 catalogued keys accepted.', 'IMPLEMENTED')}
    {box('Signed receipt log', 'HMAC-SHA256 over every decision. Key in a KMS is proposed.', 'IMPLEMENTED')}
    {box('Agent desk', 'Tier-3 queue, reasons, dual-approver release.', 'PROPOSED')}
  </div></div>
  <div class="flow mono">2 payee features ↑ &nbsp;&nbsp;&nbsp;&nbsp; 3 score inside /decide &nbsp;&nbsp;&nbsp;&nbsp; 4 tier-3 hold → rail &nbsp;&nbsp;&nbsp;&nbsp; 6 confirmed outcomes ↓</div>
  <div class="two">
    <div class="plane"><div class="pt mono">BANK DATA PLATFORM</div><div class="pr">
      {box('Mule-score features', 'Fan-in, first-time-sender share, pass-through, age. Synthetic 7-day graph.', 'SIMULATED')}
      {box('Suspect-registry lookup', 'Flag only; never shown to customers. Synthetic flag in Round 1.', 'SIMULATED')}
      {box('Weekly retrain', 'Bank-confirmed labels only; shadow-mode before rollout.', 'PROPOSED')}
    </div></div>
    <div class="plane"><div class="pt mono">PAYMENT RAIL / REPORTING</div><div class="pr">
      {box('Payment hold', 'Time-boxed hold for Tier 3 via the bank’s payment switch.', 'PROPOSED')}
      {box('Reporting path', 'Agent files to I4C CFCFRMS / 1930 when a scam is confirmed.', 'PROPOSED')}
    </div></div>
  </div>
</div>
<div class="legend mono"><span class="lg impl">implemented</span><span class="lg sim">simulated</span><span class="lg prop">proposed</span>
<span>No Amazon, NPCI, I4C or bank integration exists today; every proposed item is marked as such.</span></div>"""
    return frame(11, "Architecture 1 / 3", body, cls="archp")


def a2():
    steps = [("1", "Pay pressed", "SDK composes evidence: only true booleans, amount, payee hash, nonce, timestamp."),
             ("2", "Guard", "/decide rejects unknown keys, replayed nonces and evidence older than 15 s."),
             ("3", "Score", "Payee features joined from the feature store; stage scores, gate, tier, playbook, top-5 reasons."),
             ("4", "Act", "Tier 0 allow · Tier 1 log · Tier 2 warn + two questions · Tier 3 hold before the PIN screen."),
             ("5", "Review", "Tier 3 reaches a bank agent with the receipt and reasons. Release needs two approvers."),
             ("6", "Close", "Released, or confirmed and reported. The outcome becomes a bank-confirmed label.")]
    st = "".join(f"<div class='fs'><div class='fn mono'>{a}</div><b>{b}</b><span>{c}</span></div>" for a, b, c in steps)
    ctl = [("Replayed or stale evidence", "Nonce + 15 s freshness window at /decide", "IMPLEMENTED"),
           ("Injected or unknown fields", "Only the 20 catalogued keys are accepted", "IMPLEMENTED"),
           ("Tampered decision record", "HMAC-SHA256 receipt per decision", "IMPLEMENTED"),
           ("Modified or fake app", "Play Integrity token bound to a hash of the evidence", "PROPOSED"),
           ("Insider releasing holds", "Two approvers; approver ids written into the receipt", "PROPOSED"),
           ("Receipt-store breach", "Receipts hold no raw content; identity kept separately", "DESIGN"),
           ("Label poisoning", "Retrain on bank-confirmed outcomes only", "DESIGN")]
    ct = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{status(c)}</td></tr>" for a, b, c in ctl)
    body = f"""
<h2>One payment, traced — and what protects each step</h2>
<div class="a2">
  <div class="fl">{st}</div>
  <div class="a2r">
    <div class="mono lbl">SECURITY CONTROLS</div>
    <table class="tbl sm"><thead><tr><th>Threat</th><th>Control</th><th></th></tr></thead><tbody>{ct}</tbody></table>
    <div class="desk">{svg_inline('mockup_agent.svg')}</div>
  </div>
</div>
<p class="small">Escalation and evidence path: customer screen → receipt id → agent desk → release or report. The same receipt id is what a
customer quotes in a complaint, so a hold is never an unexplained outcome.</p>"""
    return frame(12, "Architecture 2 / 3", body, cls="archp")


def a3():
    body = f"""
<h2>Rollout, performance and modelled economics</h2>
<div class="a3">
  <div class="a3c">
    <div class="mono lbl">ROLLOUT — GATED BY MEASUREMENT</div>
    <div class="ro"><b>Weeks 0–6 · Shadow</b><span>Receipts only, no customer impact. Measure interruptions on real traffic;
      recalibrate τ to the bank's budget.</span></div>
    <div class="ro"><b>Weeks 6–10 · Tiers 1–2</b><span>Opted-in segment and high-value person-to-person payments.
      Proceed only if interruptions ≤ budget.</span></div>
    <div class="ro"><b>Week 10+ · Tier 3</b><span>Payment hold with agent desk and two-approver release.</span></div>
    <div class="mono lbl" style="margin-top:16px">PERFORMANCE</div>
    <p><b>{C['latency_us']:.0f} µs</b> per session for scoring, measured in-process on the evaluation machine.
    <b>&lt; 40 ms</b> end-to-end SDK round trip is a design target, not a measurement.</p>
    <div class="mono lbl" style="margin-top:16px">VALIDATION IN A PILOT</div>
    <p>Real-traffic interruption rate, confirmed-scam recall from bank case outcomes, complaint rate and
    agent review time — reported weekly against the synthetic baseline in this document.</p>
  </div>
  <div class="a3c model">
    <div class="mtag mono">MODELLED / ASSUMPTION — NOT OBSERVED RESULTS</div>
    <div class="mono lbl">VALUE: AN UPPER BOUND</div>
    <div class="calc">
      <div><span>national reported loss, 2024 (MHA)</span><b>₹{NATIONAL_LOSS_CR:,} cr</b></div>
      <div><span>× share borne by one pilot bank's customers <i>(assumed)</i></span><b>{EXPOSURE_SHARE * 100:.0f}%</b></div>
      <div><span>× Tier ≥ 2 recall (synthetic)</span><b>{pct(C['recall']['mean'])}</b></div>
      <div class="tot"><span>= upper-bound value intercepted per year</span><b>₹{UPPER_CR:,.0f} cr</b></div>
    </div>
    <p class="small">Upper bound: assumes every Tier ≥ 2 detection prevents the full loss. Tier-2 customers may still pay,
    so real prevention will be lower. Scenario projection — not observed loss prevention.</p>
    <div class="mono lbl" style="margin-top:14px">COST AT 30 M USERS × 250 SESSIONS / YEAR</div>
    <div class="calc">
      <div><span>engine compute ({INSTANCES} instances, peak ≈ {PEAK_QPS:,.0f} req/s)</span><b>₹{COMPUTE_INR / 1e5:.1f} lakh / yr</b></div>
      <div><span>signed receipts ({STORAGE_GB / 1000:.1f} TB / yr)</span><b>₹{STORAGE_INR / 1e5:.1f} lakh / yr</b></div>
      <div><span>false Tier-3 holds to review (measured rate × volume)</span><b>≈ {FALSE_HOLDS_DAY:,.0f} / day</b></div>
      <div class="tot"><span>agent time at 5 min per review</span><b>≈ {AGENT_HOURS_DAY:,.0f} h / day</b></div>
    </div>
    <p class="small">Assumptions: peak = 10× average load, 1,000 req/s per instance, doubled for availability,
    ₹8 per instance-hour, 350-byte receipt, ₹2 per GB-month. Compute is cheap; <b>human review is the real
    operating cost</b>, which is why the Tier-3 budget is set separately. Excludes engineering and SDK work.</p>
  </div>
</div>"""
    return frame(13, "Architecture 3 / 3", body, cls="archp")


# ---------------- appendix ----------------


SHORT = {"contact": "contact", "control": "control", "extraction": "extraction", "cashout": "cash-out"}


def x1():
    W = F["weights"]
    order = {"contact": 0, "control": 1, "extraction": 2, "cashout": 3}
    rows = sorted(SIGNALS, key=lambda s: (order[s.stage], -W[s.key]))
    tr = "".join(f"<tr><td class='mono'>{s.key}</td><td>{SHORT[s.stage]}</td><td>{s.source}</td>"
                 f"<td class='r mono'>{W[s.key]:+.2f}</td><td>{s.why}</td></tr>" for s in rows)
    th = {int(k): v for k, v in C["thresholds"].items()}
    body = f"""
<h2>Appendix A — signal catalogue and model specification</h2>
<div class="xa">
  <table class="tbl xs"><thead><tr><th>Signal</th><th>Stage</th><th>Source</th><th class="r">Weight</th><th>Meaning (shown to users and agents)</th></tr></thead><tbody>{tr}</tbody></table>
  <div class="spec">
    <div class="mono lbl">MODEL</div>
    <p class="formula sm">s(x) = b + Σ<sub>g</sub> min(C<sub>g</sub>, Σ<sub>k in g</sub> w<sub>k</sub>x<sub>k</sub>)</p>
    <p>Weights: logistic regression, L2, C = 0.3, fitted on world 7 (60,000 legitimate + 2,400 scam sessions), clipped at 0.
    Absent signals contribute nothing.</p>
    <p>Intercept b shifted from training prevalence (3.85%) to an assumed deployment prevalence of 1 in 5,000.</p>
    <p>Caps C: contact 5, control 5, extraction 6, cash-out 6. Stage active when capped score ≥ 1.5.</p>
    <p>Thresholds (log-odds), calibrated on world 21 to 20 / 3 / 0.5 legitimate alerts per 1,000:
    τ₁ = {th[1]:.2f}, τ₂ = {th[2]:.2f}, τ₃ = {th[3]:.2f}.</p>
    <p>Playbook label (digital arrest, remote-access KYC, investment/task, collect request) chosen by overlap with
    each playbook's signal fingerprint; it selects the customer message, not the tier.</p>
    <p class="small">Source split: 9 device, 7 bank, 4 network = 20. Weights are published here deliberately;
    slide 8 measures what an attacker who reads them can achieve.</p>
  </div>
</div>"""
    return frame(14, "Appendix A", body, cls="appx")


def aup(a):
    return "—" if a is None else f"{a['mean']:.3f}"


def x2():
    rows = [("Chakravyuh (tier ≥ 2)", C["recall"], C["fp"], C["auprc"])]
    rows.append(("Chakravyuh score, gate removed", C["recall_nogate"], C["fp_nogate"], None))
    for k in ["Logistic regression", "Gradient boosting", "XGBoost", "MLP", "Rule: new payee + high amount"]:
        rows.append((k, B[k]["recall"], B[k]["fp"], B[k].get("auprc")))
    bt = "".join(f"<tr><td>{n}</td><td class='r mono'>{r['mean'] * 100:.1f}% <i>{ci_pct(r)}</i></td>"
                 f"<td class='r mono'>{f['mean']:.2f} <i>[{f['lo']:.2f}, {f['hi']:.2f}]</i></td>"
                 f"<td class='r mono'>{aup(a)}</td></tr>" for n, r, f, a in rows)
    adv = " · ".join(f"{d['suppressed']}: {d['recall'] * 100:.0f}%" for d in F["adversarial"])
    abl = " · ".join(f"{d['removed']}: {d['recall'] * 100:.0f}% ({d['fp']:.2f}/1k)" for d in F["ablation"])
    loo = " · ".join(f"{d['held_out'].replace('_', ' ')}: {d['recall'] * 100:.0f}%" for d in F["loo"])
    sc = " · ".join(f"{k.replace('_', ' ')}: {v * 100:.0f}%" for k, v in C["by_scenario"].items())
    pp = " · ".join(f"{k}: {v['recall'] * 100:.0f}% / {v['fp']:.2f}" for k, v in C["by_persona"].items())
    cal = F["calibration"]
    body = f"""
<h2>Appendix B — evaluation methodology and full results</h2>
<div class="xb">
  <div>
    <p><b>Data.</b> A seeded generator (chakravyuh/synth.py) produces legitimate sessions with realistic confounders
    (paying a plumber during his call, rent day, ignored scam SMS) and four scam playbooks. 25% of scam sessions are
    “adapted”: call, video and screen-share signals hidden and amounts lowered. Payees come from a synthetic 7-day payment
    graph with 120 mules (25% aged 120+ days). No real data is used anywhere.</p>
    <p><b>Protocol.</b> Train on world 7; calibrate thresholds on world 21; test on worlds 101–108, each 60,000 legitimate +
    2,400 scam sessions. Every system uses the same worlds and a 3 / 1,000 budget. CIs: bootstrap over the 8 worlds.</p>
    <table class="tbl xs"><thead><tr><th>System</th><th class="r">Recall [95% CI]</th><th class="r">Interruptions / 1k</th><th class="r">AUPRC</th></tr></thead><tbody>{bt}</tbody></table>
    <p class="small">The fixed rule cannot be tuned to a budget, so it is reported at its natural operating point.</p>
  </div>
  <div class="xb2">
    <div class="mini"><div class="mono lbl">RECALL PER TEST WORLD</div>{charts.per_world(F)}</div>
    <div class="mini"><div class="mono lbl">RELIABILITY (PREVALENCE-ADJUSTED)</div>{charts.reliability(F)}</div>
    <p class="small"><b>Calibration.</b> Scores are shifted to the 1-in-5,000 deployment prior; for this check they are shifted
    back to the test prevalence ({cal['eval_prevalence'] * 100:.2f}%). Brier {cal['brier']:.4f}, ECE {cal['ece']:.4f}.</p>
    <p class="small"><b>Adversary</b> (strongest emitted signals hidden): {adv}.</p>
    <p class="small"><b>Stage ablation</b> (retrained without the stage): {abl}.</p>
    <p class="small"><b>Leave one playbook out:</b> {loo}. <b>Per playbook:</b> {sc}.</p>
    <p class="small"><b>Per persona</b> (recall / interruptions per 1k): {pp}.</p>
    <p class="small"><b>Stage caps</b> produced no measurable change on these worlds (identical recall and interruptions
    without caps); they remain as a guarantee against a single extreme stage. Tier-3 recall: {pct(C['t3_recall']['mean'])}.</p>
  </div>
</div>"""
    return frame(15, "Appendix B", body, cls="appx")


def x3():
    kt = """class ChakravyuhProbes(ctx: Context, integrity: StandardIntegrityTokenProvider) {
  fun evidence(nonce: String): Evidence {
    val ev = mapOf(
      "call_unknown_active"   to isUnknownCallActive(),
      "call_long"             to callDurationSec() >= 20 * 60,
      "video_call"            to voipAudioModeActive(),
      "sms_scam_flag"         to onDeviceLureClassifier.hitWithin(24.hours),
      "remote_access"         to screenShareOrRemoteAppRunning(),
      "sideload_24h"          to installedOutsideStore(within = 24.hours),
      "accessibility_overlay" to thirdPartyOverlayAndA11yEnabled(),
      "otp_read_in_call"      to (isUnknownCallActive() && otpNotificationOpened()),
      "vpa_typed"             to payeeEnteredManually())       // 9 device signals
      .filterValues { it }                                    // send only true ones
    val body = canonicalJson(ev, amount, payeeHash, nonce, now())
    val token = integrity.request(requestHash = sha256(body)) // server verifies
    return Evidence(body, token)
  }
}"""
    assum = [("Deployment prevalence", "1 scam per 5,000 sessions", "intercept shift only"),
             ("Alert budgets", "20 / 3 / 0.5 per 1,000", "bank-chosen, per tier"),
             ("Adapted cohort", "25% of scam sessions", "synthetic"),
             ("Pilot exposure share", "2% of national reported loss", "value model"),
             ("Load", "30 M users × 250 sessions / yr; peak 10× average", "cost model"),
             ("Unit costs", "₹8 / instance-hour; ₹2 / GB-month; 5 min / review", "cost model")]
    at = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in assum)
    reg = [("DPDP Act 2023", "Purpose limitation, data minimisation: only derived booleans leave the device."),
           ("RBI Master Direction on Digital Payment Security Controls (2021)", "Fraud-risk monitoring: graduated, explainable interruption with human review."),
           ("RBI Integrated Ombudsman Scheme (2021)", "The receipt id gives a complaint a single, verifiable reference."),
           ("PMLA 2002 record-keeping", "Receipts retained for the statutory period, stored apart from identity data."),
           ("I4C CFCFRMS / 1930", "Proposed reporting path for confirmed scams; no integration exists today.")]
    rt = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in reg)
    body = f"""
<h2>Appendix C — assumptions, design alignment, SDK sketch, sources</h2>
<div class="xc">
  <div>
    <div class="mono lbl">ASSUMPTIONS</div>
    <table class="tbl xs"><thead><tr><th>Item</th><th>Value</th><th>Used in</th></tr></thead><tbody>{at}</tbody></table>
    <div class="mono lbl" style="margin-top:12px">REGULATORY DESIGN ALIGNMENT — NOT CERTIFICATION</div>
    <table class="tbl xs"><tbody>{rt}</tbody></table>
    <div class="mono lbl" style="margin-top:12px">SOURCES</div>
    <p class="small">Ministry of Home Affairs, reply in Lok Sabha, July 2025: ₹22,845.73 crore lost to cyber fraud in 2024;
    36.37 lakh complaints (NCRP and CFCFRMS). Digital Personal Data Protection Act, 2023. RBI Master Direction on Digital Payment
    Security Controls, 2021. RBI Integrated Ombudsman Scheme, 2021. I4C Suspect Registry, launched September 2024.</p>
  </div>
  <div>
    <div class="mono lbl">ANDROID SIGNAL PROBES — SKETCH, NOT YET BUILT</div>
    <pre>{kt}</pre>
    <div class="mono lbl" style="margin-top:12px">DISCLOSURES</div>
    <p class="small">All data is synthetic. No models are pre-trained; no LLM is used at decision time. Code: Python (FastAPI,
    scikit-learn, XGBoost, NumPy, NetworkX, Matplotlib). Typeface: IBM Plex (SIL Open Font License). Drafting, code and layout
    were produced with the help of an AI assistant (Claude Code); every number was computed by the project's evaluation scripts
    (eval/final_numbers.py) and checked against them. Phone and agent-desk screens are illustrative mock-ups.</p>
  </div>
</div>"""
    return frame(16, "Appendix C", body, cls="appx")


CSS = (HERE / "deck.css").read_text()


def build():
    pages = [s01(), s02(), s03(), s04(), s05(), s06(), s07(), s08(), s09(), s10(), a1(), a2(), a3(), x1(), x2(), x3()]
    assert len(pages) == TOTAL
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Chakravyuh — RAKSHAM Round 1</title>
<style>{CSS}</style></head><body>{''.join(pages)}</body></html>"""
    (HERE / "deck.html").write_text(html)
    print("wrote deck.html;", f"upper={UPPER_CR:.0f}cr compute={COMPUTE_INR/1e5:.1f}L storage={STORAGE_INR/1e5:.2f}L "
          f"holds/day={FALSE_HOLDS_DAY:.0f} agent_h={AGENT_HOURS_DAY:.0f} inst={INSTANCES} peak={PEAK_QPS:.0f}")


if __name__ == "__main__":
    build()

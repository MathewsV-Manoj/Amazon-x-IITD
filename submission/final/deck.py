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
C = F["chakravyuh"]; B = F["baselines"]; J = F["judge"]
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
  <header><span class="sec">{section}</span><span class="brand">Chakravyuh</span></header>
  <div class="body" style="zoom:{ZOOM.get(n, 1.0)}">{body}</div>
  <footer><span>RAKSHAM Round 1 · Track 2: AI-driven scam pattern recognition</span>
  <span class="pg">{n:02d} / {TOTAL}</span></footer>
</section>"""


STATUS_WORD = {"IMPLEMENTED": "built", "MEASURED": "measured", "SIMULATED": "simulated", "PROPOSED": "planned", "DESIGN": "design only"}


def status(s):
    return f'<span class="st st-{s.lower()}">{STATUS_WORD[s]}</span>'


ARROW = '<span class="arr">→</span>'


def svg_inline(name):
    s = (ROOT / "submission" / "assets" / name).read_text()
    return s[s.index("<svg"):]


# ---------------- slides ----------------


def s01():
    team = "".join(f"<div><b>{n}</b><span>{d}</span></div>" for n, d in TEAM)
    return f"""
<section class="slide dark cover">
  <div class="cv-top">RAKSHAM, Amazon × IIT Delhi · Round 1 · Track 2: AI-driven scam pattern recognition</div>
  <div class="cv-main">
    <h1 class="cv-title">Chakravyuh</h1>
    <p class="cv-tag">Intercept the scam workflow,<br>not the transaction.</p>
    <p class="cv-lede">Chakravyuh checks a UPI payment for the steps that usually come before a scam payment:
    a suspicious call, someone controlling the phone, an unusual payment, and a receiving account that looks like a mule.
    It interrupts only when several of these show up together, tells the customer why, and keeps a signed record for the bank.</p>
  </div>
  <div class="cv-chain">
    <div class="node"><i></i><span>Contact</span></div><div class="link"></div>
    <div class="node"><i></i><span>Control</span></div><div class="link"></div>
    <div class="node"><i></i><span>Extraction</span></div><div class="link"></div>
    <div class="node"><i></i><span>Cash-out</span></div><div class="link gate"></div>
    <div class="node end"><i></i><span>Decision</span></div>
  </div>
  <div class="cv-foot">
    <div class="team"><span class="lbl">Team</span>{team}</div>
    <div class="note">All results here come from synthetic data we generated.<br>No real customer, bank or platform data was used.</div>
  </div>
</section>"""


def s02():
    body = f"""
<h2>In these scams, the victim makes the payment</h2>
<p class="lede">Most of the scam happens before any money moves. By the time the victim pays, the PIN is correct,
the phone is their own and they intend to pay, so a check on the payment alone has little to go on.</p>
<div class="prob">
  <div class="seq">
    <div class="who">A typical digital-arrest scam</div>
    <div class="step s1"><b>Contact</b><span>A fake “CBI officer” video-calls about a money-laundering case</span></div>
    <div class="step s2"><b>Control</b><span>She is told to install a screen-sharing app “for verification”</span></div>
    <div class="step s3"><b>Money extraction</b><span>She breaks a fixed deposit and types in a new payee</span></div>
    <div class="step pay"><b>She pays</b><span>₹2,50,000 to a personal UPI ID</span></div>
    <div class="brk b1"><span>A payment-level check does not see these steps</span></div>
    <div class="brk b2"><span>This is the only step it checks</span></div>
  </div>
  <div class="stats">
    <div class="stat"><div class="big">₹22,845 cr</div><div class="cap">lost to cyber fraud in India in 2024</div></div>
    <div class="stat"><div class="big">36.37 lakh</div><div class="cap">complaints filed in 2024</div></div>
    <div class="src">Source: Ministry of Home Affairs, reply in Lok Sabha, July 2025 (NCRP and CFCFRMS data).</div>
    <p class="punch">Our idea: use the steps before the payment as evidence, not just the payment itself.</p>
  </div>
</div>"""
    return frame(2, "1. Problem", body)


def s03():
    stages = [
        ("01", "Contact", "device", ["call with an unknown number", "call longer than 20 min", "scam-lure SMS (classified on-device)"]),
        ("02", "Control", "device", ["screen-sharing app running", "app sideloaded in last 24 h", "OTP opened during the call"]),
        ("03", "Extraction", "bank", ["first-time payee, typed VPA", "&gt; 70% of balance", "fixed deposit broken in last 24 h"]),
        ("04", "Cash-out", "network", ["payee behaves like a mule", "payee account &lt; 30 days old", "payee on a suspect registry"]),
    ]
    cols = "".join(f"""<div class="stg"><div class="n">{n}</div><div class="name">{name}</div>
      <ul>{''.join(f'<li>{s}</li>' for s in sig)}</ul><div class="src">from the {src}</div></div>"""
                   for n, name, src, sig in stages)
    body = f"""
<h2>A scam has four stages. We look for all of them.</h2>
<div class="cmp">
  <div class="row"><span class="lbl">Usual approach</span><span class="box">one payment</span>{ARROW}<span class="out">suspicious or not</span></div>
  <div class="row"><span class="lbl acc">Chakravyuh</span><span class="chainline">contact {ARROW} control {ARROW} extraction {ARROW} cash-out</span>{ARROW}<span class="out acc">response scaled to the evidence</span></div>
</div>
<div class="stages">{cols}</div>
<div class="rule-line"></div>
<p class="thesis">One odd signal is not enough to stop a payment. <b>We act when several stages show up together.</b></p>
<p class="thesis-sub">A genuine payment can look odd on its own, like a new payee on rent day or a long call with a plumber.
A scam is easier to spot from the sequence. All 20 signals are listed in Appendix A.</p>"""
    return frame(3, "2. Idea", body, dark=True, cls="hero")


def s04():
    t = [("Level 1", "Log it", "Score above τ₁", "Nothing. The session goes to the bank's fraud team for later review.",
          f'{C["t1_fp"]["mean"]:.1f}', "20"),
         ("Level 2", "Warn and ask", "Score above τ₂ <b>and</b> ≥ 2 stages active",
          "A warning that names the likely scam, and two questions. The customer can still pay.",
          f'{C["fp"]["mean"]:.2f}', "3"),
         ("Level 3", "Hold and review", "Score above τ₃ <b>and</b> ≥ 3 stages, or 2 stages + registry hit",
          "The payment is held for up to 30 minutes and a bank agent calls. Two staff must approve a release.",
          f'{C["t3_fp"]["mean"]:.2f}', "0.5")]
    steps = "".join(f"""<div class="tier t{i + 1}">
      <div class="tk">{a}</div><div class="tn">{b}</div>
      <div class="tt"><span class="lbl">When</span>{c}</div>
      <div class="tu"><span class="lbl">Customer sees</span>{d}</div>
      <div class="tr"><span class="num">{e}</span><span>genuine sessions per 1,000 reach this level<br><i>measured on synthetic data (target {f})</i></span></div>
    </div>""" for i, (a, b, c, d, e, f) in enumerate(t))
    body = f"""
<h2>Three levels of response</h2>
<p class="lede">The more stages we see, the stronger the response. The bank chooses how many alerts per 1,000 payments it
will accept at each level, and we set the thresholds to match that on separate test data.</p>
<div class="stair">{steps}</div>
<p class="foot-note">Nothing is blocked permanently. A person decides every hold.</p>"""
    return frame(4, "3. Response", body)


def s05():
    seq = [("Fake CBI video call", "contact"), ("Remote-access app", "control"), ("FD broken", "extraction"),
           ("First-time payee", "extraction"), ("Mule-like account", "cash-out"), ("₹2,50,000 payment", "")]
    chain = "".join(f"""<div class="ev {'last' if not st else ''}"><b>{a}</b><span>{st or 'payment'}</span></div>"""
                    + ("" if i == len(seq) - 1 else '<div class="evl"></div>') for i, (a, st) in enumerate(seq))
    body = f"""
<h2>Example: Mrs R., 68</h2>
<p class="tag">A made-up case based on reported digital-arrest scams.</p>
<div class="story">
  <div class="left">
    <div class="evrow">{chain}</div>
    <div class="split">
      <div class="side without"><span class="lbl">Today</span>
        <p class="out">The money is gone.</p>
        <p>A “new payee and high amount” rule shows a general warning. The caller tells her to ignore it, and she pays.
        The money goes to a mule account and is moved on within hours.</p></div>
      <div class="side with"><span class="lbl acc">With Chakravyuh</span>
        <p class="out">The payment is held.</p>
        <p>All four stages show up, so it goes to level 3. The screen tells her real officials never ask for money on a call,
        and a bank agent calls her before anything is released.</p></div>
    </div>
  </div>
  <div class="phones"><div class="phone">{svg_inline('mockup_tier2.svg')}<div class="cap">Level 2: warn and ask</div></div>
  <div class="phone">{svg_inline('mockup_tier3.svg')}<div class="cap">Level 3: hold (her case)</div></div></div>
</div>"""
    return frame(5, "4. Example", body)


def s06():
    body = f"""
<h2>How the score works</h2>
<div class="pipe">
  <div class="pb"><div class="pn">20</div><div class="pl">yes/no signals</div><div class="pd">9 device · 7 bank · 4 network</div></div>{ARROW}
  <div class="pb"><div class="pn">4</div><div class="pl">capped stage scores</div><div class="pd">weighted sum per stage, with a cap</div></div>{ARROW}
  <div class="pb"><div class="pn">≥ 2</div><div class="pl">stages needed</div><div class="pd">before we interrupt a payment</div></div>{ARROW}
  <div class="pb acc"><div class="pn">0–3</div><div class="pl">response level</div><div class="pd">plus the reasons and a signed record</div></div>
</div>
<div class="ml">
  <div class="eq">
    <div class="lbl">Score</div>
    <div class="formula">s(x) = b + <span class="big-s">Σ</span><sub>g</sub> min( C<sub>g</sub> , <span class="big-s">Σ</span><sub>k in g</sub> w<sub>k</sub> x<sub>k</sub> )</div>
    <div class="lbl" style="margin-top:14px">Decision</div>
    <div class="formula sm"><b>Level 2</b> &nbsp;if&nbsp; s ≥ τ<sub>2</sub> &nbsp;and&nbsp; active stages ≥ 2<br>
    <b>Level 3</b> &nbsp;if&nbsp; s ≥ τ<sub>3</sub> &nbsp;and&nbsp; ( active stages ≥ 3 &nbsp;or&nbsp; ≥ 2 plus a registry hit )</div>
    <p class="small">g is one of the four stages and x<sub>k</sub> is 1 if signal k is present. The weights w<sub>k</sub> come from a
    logistic regression (L2) on labelled sessions and are kept at zero or above. A stage counts as active when its capped score
    is at least 1.5. All values are in Appendix A.</p>
  </div>
  <div class="principles">
    <div><b>Non-negative weights</b><span>A missing signal does not change the score, because a fraudster can always hide one.</span></div>
    <div><b>Stage caps</b><span>A safety limit so one stage cannot dominate (C = 5, 5, 6, 6). It made no measurable difference on our data.</span></div>
    <div><b>Two-stage rule</b><span>We only interrupt when at least two stages are active.</span></div>
    <div><b>Prevalence adjustment</b><span>Training data is 3.8% scams; we adjust the model to an assumed 1 in 5,000 in real use.</span></div>
    <div><b>Thresholds</b><span>τ is set on a separate dataset to meet the bank's alert limit, then fixed.</span></div>
  </div>
</div>"""
    return frame(6, "5. Model", body)


def s07():
    gb = [B[k] for k in ["Logistic regression", "Gradient boosting", "XGBoost", "MLP"]]
    lo_r = min(b["recall"]["mean"] for b in gb); hi_r = max(b["recall"]["mean"] for b in gb)
    lo_f = min(b["fp"]["mean"] for b in gb); hi_f = max(b["fp"]["mean"] for b in gb)
    red = 1 - C["fp"]["mean"] / C["fp_nogate"]["mean"]
    mm = J["matched_fp"]; mlo = min(v["recall"]["mean"] for v in mm.values()); mhi = max(v["recall"]["mean"] for v in mm.values())
    body = f"""
<h2>Results on synthetic data</h2>
<p class="banner">These numbers come from 8 synthetic test sets the model never saw. They are not results from a real bank.</p>
<div class="res">
  <div class="kpis">
    <div class="kpi"><div class="k acc">{pct(C['recall']['mean'])}</div><div class="kl">of scam sessions reach level 2 or 3 (recall)</div>
      <div class="kc">95% confidence interval {ci_pct(C['recall'])}</div></div>
    <div class="kpi"><div class="k">{C['fp']['mean']:.2f} / 1k</div><div class="kl">genuine sessions interrupted per 1,000</div>
      <div class="kc">95% CI [{C['fp']['lo']:.2f}, {C['fp']['hi']:.2f}], target 3.0</div></div>
    <div class="kpi"><div class="k">{C['auprc']['mean']:.3f}</div><div class="kl">area under the precision-recall curve</div>
      <div class="kc">95% CI [{C['auprc']['lo']:.3f}, {C['auprc']['hi']:.3f}]</div></div>
  </div>
  <div class="chart">{charts.operating_points(F)}
    <div class="cap">All models use the same training, threshold and test data. Bars show 95% confidence intervals.</div></div>
</div>
<div class="res-note">
  <p><b>What we give up.</b> Even when set to the same alert rate as ours, standard classifiers catch {mlo * 100:.1f}–{mhi * 100:.1f}%
  of scams, about 4 points more. {J['gap_by_scenario']['collect_request'] * 100:.0f}% of that gap is collect-request scams, which only
  ever show one stage. Without the two-stage rule our own score catches {pct(C['recall_nogate']['mean'])}. Slide 10 shows what the rule buys.</p>
  <p class="small">Trained on dataset 7, thresholds set on dataset 21, tested on datasets 101 to 108. Each has 60,000 genuine and
  2,400 scam sessions. Scoring takes about {C['latency_us']:.0f} µs per session on our machine.</p>
</div>"""
    return frame(7, "6. Results", body)


def s08():
    a = {d["suppressed"]: d["recall"] for d in F["adversarial"]}
    abl = {d["removed"]: d["recall"] for d in F["ablation"]}
    loo = [d["recall"] for d in F["loo"]]
    rows = [
        ("hide their tracks?", "Ask the victim to hang up before paying, skip screen-sharing, send less.",
         "The payment and receiving-account signals come from the bank, which the caller cannot hide.",
         f"{pct(C['recall_adapted']['mean'])} recall on scam sessions where the fraudster hides these signals (25% of scams). "
         f"Worst case, hiding the strongest signal in each session (even ones a fraudster could not really hide): {pct(a[1], 0)}. Two signals: {pct(a[2], 0)}.",
         "MEASURED"),
        ("split one payment into several?", "Four payments of ₹25,000 instead of one of ₹1,00,000.",
         "A signal for two or more payments to new payees within 60 minutes.",
         "Not separately simulated in Round 1.", "DESIGN"),
        ("use older, rented mule accounts?", "An old account avoids the ‘new account’ signal.",
         "The mule score also looks at how many new senders an account has and how fast money leaves it. Other stages still count.",
         f"The mule score catches only 24% of old mule accounts, but payments to them are still caught {pct(C['recall_aged_mule']['mean'])} of the time.",
         "MEASURED"),
        ("poison the training data?", "Send lots of false ‘scam’ or ‘genuine’ reports.",
         "Retrain only on cases the bank has confirmed. Customer reports alone are never used as labels.",
         "Not evaluated.", "DESIGN"),
    ]
    tr = "".join(f"""<tr><td class="q"><b>Can they {q}</b><span>{ex}</span></td>
      <td>{d}</td><td>{e}</td><td>{status(s)}</td></tr>""" for i, (q, ex, d, e, s) in enumerate(rows))
    body = f"""
<h2>What if the fraudster changes tactics?</h2>
<div class="adv">
  <table class="tbl"><thead><tr><th>Question</th><th>Our answer</th><th>What we found</th><th></th></tr></thead><tbody>{tr}</tbody></table>
  <div class="aside">
    <div class="lbl">Recall as more signals are hidden</div>
    {charts.adversarial(F)}
    <p class="small">We assume the fraudster has read our weights and removes the strongest signals first. Thresholds are not changed.</p>
    <div class="lbl" style="margin-top:10px">A scam type it has not seen</div>
    <p class="small">We trained without one scam type and tested on it: {min(loo) * 100:.0f}–{max(loo) * 100:.0f}% recall.</p>
    <div class="lbl" style="margin-top:10px">Removing one stage</div>
    <p class="small">Without contact, control, extraction or cash-out signals, recall is
    {abl['contact'] * 100:.0f}%, {abl['control'] * 100:.0f}%, {abl['extraction'] * 100:.0f}%, {abl['cashout'] * 100:.0f}%.</p>
  </div>
</div>"""
    return frame(8, "7. Robustness", body)


def s09():
    dev = [s for s in SIGNALS if s.source == "device"]
    never = ["Call audio", "Screen frames", "Message text", "Contact list", "OTP values", "App inventory"]
    body = f"""
<h2>What data we use</h2>
<div class="priv">
  <div class="pcol never">
    <div class="lbl">Stays on the phone</div>
    <ul>{''.join(f'<li><span class="x"></span>{n}</li>' for n in never)}</ul>
  </div>
  <div class="boundary"><span>phone</span></div>
  <div class="pcol leaves">
    <div class="lbl acc">Sent to the bank</div>
    <div class="eqn"><b>9</b> yes/no values, the amount and a hashed payee ID</div>
    <div class="feas"><b>A banking app can read 5 of them</b> under Android and Play rules: call active and its length
    (phone-state permission), video/VoIP call (audio mode), a known screen-sharing app or accessibility service, an app drawing
    over our screen, and whether the payee was typed.</div>
    <div class="feas r"><b>4 need restricted access</b>, so we plan fallbacks: caller not in contacts (call-log access),
    scam SMS (SMS access), any app sideloaded (all-apps visibility), OTP opened in a call (other apps' notifications). Fallbacks:
    call length only, the bank's own OTP timing, and a fixed list of known remote-access apps.</div>
    <div class="feas-num">Retrained with only the 5 readable signals: <b>{pct(J['feasible_only']['recall']['mean'])}</b> recall at
    {J['feasible_only']['fp']['mean']:.2f} per 1,000 (synthetic), against {pct(C['recall']['mean'])} with all 9.</div>
  </div>
  <div class="pcol bank">
    <div class="lbl">Already at the bank</div>
    <p><b>7</b> signals the bank can work out from data it already has: first-time payee, amount compared with past payments,
    share of balance, a broken fixed deposit, recent small credits.</p>
    <p><b>4</b> signals about the receiving account: mule score, account age, a suspect-registry match,
    and whether it is a collect request.</p>
    <p class="small">9 + 7 + 4 = 20 signals.</p>
  </div>
</div>
<div class="receipt">
  <div class="lbl acc">Signed decision record</div>
  <code>{{ log_id, ts, session, amount, evidence (true only), score, tier, playbook, active_stages, action }} + HMAC-SHA256</code>
  <p>Each decision gets one ID, so the customer, the bank agent and any complaint all point to the same evidence.
  <b>Already built:</b> the server accepts only the 20 known signal names and rejects repeated or more-than-15-second-old requests.</p>
</div>
<p class="legal">We followed the DPDP Act 2023 ideas of collecting only what is needed and using it for one purpose. This is a design
choice, not a legal certification. The phone SDK is not built yet; the server side is.</p>"""
    return frame(9, "8. Privacy", body)


def s10():
    ss = J["single_stage"]; mm = J["matched_fp"]; lrm = mm["Logistic regression"]
    ex = ss["example"]
    plan = [("H+0–8", "Replay harness", "Run saved test sessions through the server and check the records."),
            ("H+8–20", "Android signals", "Read the 5 allowed phone signals on one test phone and compare with the synthetic values."),
            ("H+20–32", "Collect-request rule", "Add a warning for collect requests from individuals and re-test; then attack our own model."),
            ("H+32–44", "End-to-end replay", "Run 100 sessions through to agent review and release or report."),
            ("H+44–48", "Security review", "Walk through the records, replay checks, two-person release and known limits.")]
    pl = "".join(f"<div class='ph'><div class='t'>{a}</div><b>{b}</b><span>{c}</span></div>" for a, b, c in plan)
    body = f"""
<h2>Why the two-stage rule, and our plan for the finale</h2>
<div class="diff">
  <div>
    <p class="claim">A plain logistic regression is also explainable and catches more scams. So what does the rule add?</p>
    <table class="tbl sm why-t"><thead><tr><th>Same alert rate, synthetic test data</th><th class="r">Logistic regression</th><th class="r">Chakravyuh</th></tr></thead><tbody>
    <tr><td>Scams caught</td><td class="r">{pct(lrm['recall']['mean'])}</td><td class="r">{pct(C['recall']['mean'])}</td></tr>
    <tr><td>Genuine payments interrupted per 1,000</td><td class="r">{lrm['fp']['mean']:.2f}</td><td class="r">{C['fp']['mean']:.2f}</td></tr>
    <tr><td>…of which showed only one stage</td><td class="r">{ss['lr_single_stage_share_of_genuine_alerts'] * 100:.0f}%</td><td class="r"><b>0%</b></td></tr>
    </tbody></table>
  </div>
  <div class="why">
    <span class="lbl">A genuine payment the rule spares (from our test data)</span>
    <p>A shopkeeper pays ₹{ex['amount']:,.0f} on a collect request from a new payee. Nothing else is unusual: no call,
    no screen-sharing, a normal receiving account. Logistic regression interrupts it. Chakravyuh sees one stage, so it only logs it.</p>
    <p class="small">The cost: scams that only ever show one stage, mostly collect-request scams. We plan a specific collect-request
    warning for those (finale step 3).</p>
  </div>
</div>
<div class="plan">
  <div class="lbl">What we plan to build and show in the 48-hour finale</div>
  <div class="phases">{pl}</div>
  <p class="small"><b>Built so far:</b> scoring server, threshold setting, signed records with replay checks, synthetic data
  generator and evaluation, 8 automated tests. <b>Not built yet:</b> Android SDK, payment hold, agent screen.</p>
</div>"""
    return frame(10, "9. Comparison and next steps", body)


# ---------------- architecture ----------------


def box(title, sub, st):
    return f'<div class="ab ab-{st.lower()}"><div class="abh"><b>{title}</b>{status(st)}</div><span>{sub}</span></div>'


def a1():
    body = f"""
<h2>System architecture</h2>
<p class="lede">Solid boxes are built. Dashed boxes are simulated with synthetic data. Dotted boxes are planned but not built.</p>
<div class="arch">
  <div class="plane"><div class="pt">Phone (inside the bank's app)</div><div class="pr">
    {box('Signal readers', 'Call state, audio mode, accessibility, known remote apps. 5 of 9 allowed; synthetic for now.', 'SIMULATED')}
    {box('Request builder', '9 yes/no values, amount, payee hash, one-time nonce, timestamp, Play Integrity token.', 'PROPOSED')}
    {box('Warning screens', 'Scam message, two questions, hold screen. Mock-ups and a web demo.', 'SIMULATED')}
  </div></div>
  <div class="flow">1. signals sent ↓ &nbsp;&nbsp;&nbsp;&nbsp; 5. response level, message and record ID sent back ↑</div>
  <div class="plane"><div class="pt">Bank fraud team servers</div><div class="pr">
    {box('Scoring server', 'FastAPI /decide endpoint: stage scores, two-stage rule, level, reasons.', 'IMPLEMENTED')}
    {box('Input checks', 'Rejects repeated nonces, requests older than 15 s and unknown signal names.', 'IMPLEMENTED')}
    {box('Signed records', 'HMAC-SHA256 on every decision. Moving the key to a KMS is planned.', 'IMPLEMENTED')}
    {box('Agent screen', 'Queue of level-3 holds with reasons; two staff to release.', 'PROPOSED')}
  </div></div>
  <div class="flow">2. payee data looked up ↑ &nbsp;&nbsp;&nbsp;&nbsp; 3. scored &nbsp;&nbsp;&nbsp;&nbsp; 4. level-3 hold sent to payments → &nbsp;&nbsp;&nbsp;&nbsp; 6. confirmed outcomes saved ↓</div>
  <div class="two">
    <div class="plane"><div class="pt">Bank data systems</div><div class="pr">
      {box('Mule score', 'Number of new senders, how fast money leaves, account age. Synthetic 7-day graph.', 'SIMULATED')}
      {box('Suspect list check', 'A yes/no flag, never shown to customers. Synthetic for now.', 'SIMULATED')}
      {box('Weekly retraining', 'Only bank-confirmed cases; tested in shadow mode first.', 'PROPOSED')}
    </div></div>
    <div class="plane"><div class="pt">Payments and reporting</div><div class="pr">
      {box('Payment hold', 'A time-limited hold through the bank’s payment system.', 'PROPOSED')}
      {box('Reporting', 'Agent reports confirmed scams to I4C (CFCFRMS / 1930).', 'PROPOSED')}
    </div></div>
  </div>
</div>
<div class="legend"><span class="lg impl">built</span><span class="lg sim">simulated</span><span class="lg prop">planned</span>
<span>We have no integration with Amazon, NPCI, I4C or any bank yet.</span></div>"""
    return frame(11, "Architecture, page 1 of 3", body, cls="archp")


def a2():
    steps = [("1", "Customer taps Pay", "The app sends the signals that are true, the amount, a payee hash, a nonce and a timestamp."),
             ("2", "Check the request", "The server rejects unknown signals, repeated nonces and anything older than 15 seconds."),
             ("3", "Score", "Payee data is added, then stage scores, the two-stage rule, the level and the top five reasons."),
             ("4", "Respond", "Level 0 allows, level 1 logs, level 2 warns and asks two questions, level 3 holds the payment."),
             ("5", "Review", "Level-3 cases go to a bank agent with the record and reasons. Two staff must approve a release."),
             ("6", "Close", "The payment is released, or the scam is confirmed and reported. The result is saved for retraining.")]
    st = "".join(f"<div class='fs'><div class='fn'>{a}</div><b>{b}</b><span>{c}</span></div>" for a, b, c in steps)
    ctl = [("Old or repeated requests", "One-time nonce and a 15-second limit", "IMPLEMENTED"),
           ("Extra or fake fields", "Only the 20 known signal names are accepted", "IMPLEMENTED"),
           ("Edited decision records", "Each record is signed with HMAC-SHA256", "IMPLEMENTED"),
           ("Fake or modified app", "Play Integrity token tied to a hash of the request", "PROPOSED"),
           ("Staff misuse", "Two approvers, both recorded in the signed record", "PROPOSED"),
           ("Record store leak", "Records hold no raw content; identity is stored apart", "DESIGN"),
           ("Poisoned training labels", "Retrain only on bank-confirmed cases", "DESIGN")]
    ct = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{status(c)}</td></tr>" for a, b, c in ctl)
    body = f"""
<h2>Following one payment through the system</h2>
<div class="a2">
  <div class="fl">{st}</div>
  <div class="a2r">
    <div class="lbl">Security checks</div>
    <table class="tbl sm"><thead><tr><th>Risk</th><th>What we do</th><th></th></tr></thead><tbody>{ct}</tbody></table>
    <div class="desk">{svg_inline('mockup_agent.svg')}</div>
  </div>
</div>
<p class="small">If a customer complains about a hold, they quote the record ID shown on their screen. The bank can then see exactly which
signals caused it.</p>"""
    return frame(12, "Architecture, page 2 of 3", body, cls="archp")


def a3():
    body = f"""
<h2>Rollout, speed and cost estimates</h2>
<div class="a3">
  <div class="a3c">
    <div class="lbl">Rollout plan</div>
    <div class="ro"><b>Weeks 0 to 6: shadow</b><span>Score real payments but show nothing to customers. Measure the alert rate and
      reset the thresholds.</span></div>
    <div class="ro"><b>Weeks 6 to 10: levels 1 and 2</b><span>Customers who opt in, and large payments to individuals.
      Move on only if alerts stay within the limit.</span></div>
    <div class="ro"><b>From week 10: level 3</b><span>Payment holds, with agent review and two-person release.</span></div>
    <div class="lbl" style="margin-top:16px">Speed</div>
    <p>Scoring takes about <b>{C['latency_us']:.0f} µs</b> per session on our machine. We are aiming for under
    <b>40 ms</b> for the full round trip from the phone, but have not measured it.</p>
    <div class="lbl" style="margin-top:16px">What a pilot would measure</div>
    <p>Alert rate on real payments, how many confirmed scams were caught, complaints, and agent review time,
    compared each week with the synthetic results here.</p>
  </div>
  <div class="a3c model">
    <div class="mtag">Estimates based on assumptions, not measured results</div>
    <div class="lbl">Possible savings (upper limit)</div>
    <div class="calc">
      <div><span>national reported loss, 2024 (MHA)</span><b>₹{NATIONAL_LOSS_CR:,} cr</b></div>
      <div><span>× share for one pilot bank <i>(our assumption)</i></span><b>{EXPOSURE_SHARE * 100:.0f}%</b></div>
      <div><span>× recall on synthetic data</span><b>{pct(C['recall']['mean'])}</b></div>
      <div class="tot"><span>= most that could be saved per year</span><b>₹{UPPER_CR:,.0f} cr</b></div>
    </div>
    <p class="small">This assumes every level-2 or level-3 alert stops the whole loss. Some customers will pay anyway after a
    warning, so the real figure would be lower. It is an estimate, not a measured saving.</p>
    <div class="lbl" style="margin-top:14px">Cost for 30 million users, 250 payments each per year</div>
    <div class="calc">
      <div><span>servers ({INSTANCES} instances, peak about {PEAK_QPS:,.0f} requests/s)</span><b>₹{COMPUTE_INR / 1e5:.1f} lakh / yr</b></div>
      <div><span>storing signed records ({STORAGE_GB / 1000:.1f} TB / yr)</span><b>₹{STORAGE_INR / 1e5:.1f} lakh / yr</b></div>
      <div><span>genuine payments held at level 3</span><b>≈ {FALSE_HOLDS_DAY:,.0f} / day</b></div>
      <div class="tot"><span>agent time at 5 minutes each</span><b>≈ {AGENT_HOURS_DAY:,.0f} h / day</b></div>
    </div>
    <p class="small">Assumptions: peak is 10 times the average load, 1,000 requests/s per server, doubled for backup,
    ₹8 per server-hour, 350 bytes per record, ₹2 per GB per month. Servers are cheap. <b>Staff time for reviews is the main
    cost</b>, so the bank should set the level-3 limit carefully. Development cost is not included.</p>
  </div>
</div>"""
    return frame(13, "Architecture, page 3 of 3", body, cls="archp")


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
<h2>Appendix A: signals and model details</h2>
<div class="xa">
  <table class="tbl xs"><thead><tr><th>Signal</th><th>Stage</th><th>Source</th><th class="r">Weight</th><th>Meaning (as shown to customers and agents)</th></tr></thead><tbody>{tr}</tbody></table>
  <div class="spec">
    <div class="lbl">Model</div>
    <p class="formula sm">s(x) = b + Σ<sub>g</sub> min(C<sub>g</sub>, Σ<sub>k in g</sub> w<sub>k</sub>x<sub>k</sub>)</p>
    <p>Weights: logistic regression with L2 (C = 0.3), trained on dataset 7 (60,000 genuine and 2,400 scam sessions),
    negative weights set to 0. A missing signal adds nothing.</p>
    <p>The intercept b is adjusted from the training scam rate (3.85%) to an assumed real rate of 1 in 5,000.</p>
    <p>Caps C: contact 5, control 5, extraction 6, cash-out 6. A stage is active when its capped score is 1.5 or more.</p>
    <p>Thresholds (log-odds), set on dataset 21 to give 20, 3 and 0.5 genuine alerts per 1,000:
    τ₁ = {th[1]:.2f}, τ₂ = {th[2]:.2f}, τ₃ = {th[3]:.2f}.</p>
    <p>The scam type shown to the customer (digital arrest, remote-access KYC, investment or task scam, collect request)
    is picked by which signals are present. It changes the message, not the level.</p>
    <p class="small">Sources: 9 from the phone, 7 from the bank, 4 about the receiving account, 20 in total. We publish the
    weights on purpose; slide 8 tests a fraudster who has read them.</p>
  </div>
</div>"""
    return frame(14, "Appendix A", body, cls="appx")


def aup(a):
    return "—" if a is None else f"{a['mean']:.3f}"


def x2():
    rows = [("Chakravyuh (tier ≥ 2)", C["recall"], C["fp"], C["auprc"])]
    rows.append(("Chakravyuh without two-stage rule", C["recall_nogate"], C["fp_nogate"], None))
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
<h2>Appendix B: how we tested, and all results</h2>
<div class="xb">
  <div>
    <p><b>Data.</b> Our generator (chakravyuh/synth.py) creates genuine sessions that include confusing cases (paying a plumber
    while on a call with him, rent day, ignored scam SMS) and four types of scam. In 25% of scam sessions the fraudster hides the
    call, video and screen-sharing signals and asks for less money. Payees come from a synthetic 7-day payment network with
    120 mule accounts, a quarter of them over 120 days old. No real data is used.</p>
    <p><b>Method.</b> Train on dataset 7, set thresholds on dataset 21, test on datasets 101 to 108 (60,000 genuine and 2,400 scam
    sessions each). Every model uses the same data and a limit of 3 alerts per 1,000. Confidence intervals are bootstrapped over
    the 8 test sets.</p>
    <table class="tbl xs"><thead><tr><th>Model</th><th class="r">Recall [95% CI]</th><th class="r">Alerts per 1,000</th><th class="r">AUPRC</th></tr></thead><tbody>{bt}</tbody></table>
    <p class="small">The fixed rule has no threshold to tune, so it is shown as is.</p>
  </div>
  <div class="xb2">
    <div class="mini"><div class="lbl">Recall on each test set</div>{charts.per_world(F)}</div>
    <div class="mini"><div class="lbl">Calibration</div>{charts.reliability(F)}</div>
    <p class="small"><b>Calibration.</b> Scores are set for a 1-in-5,000 scam rate, so for this check we shift them back to the
    test rate ({cal['eval_prevalence'] * 100:.2f}%). Brier score {cal['brier']:.4f}, ECE {cal['ece']:.4f}. Mid-range scores are a
    little under-confident.</p>
    <p class="small"><b>Hidden signals</b> (strongest first), number hidden and recall: {adv}.</p>
    <p class="small"><b>One stage removed</b> (retrained without it): {abl}.</p>
    <p class="small"><b>Unseen scam type:</b> {loo}. <b>By scam type:</b> {sc}.</p>
    <p class="small"><b>By user type</b> (recall / alerts per 1,000): {pp}.</p>
    <p class="small"><b>Stage caps</b> made no difference on this data (same results without them). We keep them as a safety
    limit. Level-3 recall: {pct(C['t3_recall']['mean'])}.</p>
  </div>
</div>"""
    return frame(15, "Appendix B", body, cls="appx")


def x3():
    kt = """class ChakravyuhProbes(ctx: Context, integrity: StandardIntegrityTokenProvider) {
  // Readable by a banking app (5 signals)
  fun evidence(nonce: String): Evidence {
    val ev = mapOf(
      "call_long"   to (callActive() && callSeconds() >= 20 * 60),  // TelephonyCallback, READ_PHONE_STATE
      "video_call"  to (audio.mode == AudioManager.MODE_IN_COMMUNICATION),
      "remote_access" to (knownRemoteAppInstalled()              // <queries> list of package names
                          || a11yServicesEnabledByOthers()),       // AccessibilityManager
      "accessibility_overlay" to lastTouchWasObscured(),           // FLAG_WINDOW_IS_OBSCURED
      "vpa_typed"   to payeeEnteredManually())                     // our own payment screen
      .filterValues { it }
    // Restricted, not read: caller number (call log), SMS text, all installed apps,
    // other apps' notifications. Fallback: bank checks if its own OTP was sent during a call.
    val body = canonicalJson(ev, amount, payeeHash, nonce, now())
    return Evidence(body, integrity.request(requestHash = sha256(body)))
  }
}"""
    assum = [("Real scam rate", "1 in 5,000 sessions", "intercept adjustment"),
             ("Alert limits", "20, 3 and 0.5 per 1,000", "set by the bank, per level"),
             ("Fraudster hides signals", "25% of scam sessions", "synthetic data"),
             ("Pilot bank share", "2% of national reported loss", "savings estimate"),
             ("Load", "30 M users × 250 payments/yr; peak 10× average", "cost estimate"),
             ("Unit costs", "₹8 per server-hour; ₹2 per GB-month; 5 min per review", "cost estimate")]
    at = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in assum)
    reg = [("DPDP Act 2023", "Collect only what is needed: only yes/no values leave the phone."),
           ("RBI Master Direction on Digital Payment Security Controls (2021)", "Fraud monitoring: step-by-step response with reasons and human review."),
           ("RBI Integrated Ombudsman Scheme (2021)", "The record ID gives each complaint one reference to check."),
           ("PMLA 2002 record-keeping", "Records kept for the required period, stored apart from identity data."),
           ("I4C CFCFRMS / 1930", "Planned route for reporting confirmed scams. Not connected yet.")]
    rt = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in reg)
    body = f"""
<h2>Appendix C: assumptions, regulations, code sketch, sources</h2>
<div class="xc">
  <div>
    <div class="lbl">Assumptions</div>
    <table class="tbl xs"><thead><tr><th>Item</th><th>Value</th><th>Used in</th></tr></thead><tbody>{at}</tbody></table>
    <div class="lbl" style="margin-top:12px">Regulations we designed around (not a legal certification)</div>
    <table class="tbl xs"><tbody>{rt}</tbody></table>
    <div class="lbl" style="margin-top:12px">Sources</div>
    <p class="small">Ministry of Home Affairs, reply in Lok Sabha, July 2025: ₹22,845.73 crore lost to cyber fraud in 2024;
    36.37 lakh complaints (NCRP and CFCFRMS). Digital Personal Data Protection Act, 2023. RBI Master Direction on Digital Payment
    Security Controls, 2021. RBI Integrated Ombudsman Scheme, 2021. I4C Suspect Registry, launched September 2024.</p>
  </div>
  <div>
    <div class="lbl">Android signal code (sketch, not built yet)</div>
    <pre>{kt}</pre>
    <div class="lbl" style="margin-top:12px">Disclosures</div>
    <p class="small">All data is synthetic. We use no pre-trained models and no LLM in the decision. Code: Python (FastAPI,
    scikit-learn, XGBoost, NumPy, NetworkX, Matplotlib). Font: IBM Plex (SIL Open Font License). We used an AI assistant
    (Claude Code) to help write the code, text and layout. Every number comes from our evaluation script (eval/final_numbers.py).
    The phone and agent screens are mock-ups.</p>
  </div>
</div>"""
    return frame(16, "Appendix C", body, cls="appx")


CSS = (HERE / "deck.css").read_text()


def build():
    pages = [s01(), s02(), s03(), s04(), s05(), s06(), s07(), s08(), s09(), s10(), a1(), a2(), a3(), x1(), x2(), x3()]
    assert len(pages) == TOTAL
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Chakravyuh, RAKSHAM Round 1</title>
<style>{CSS}</style></head><body>{''.join(pages)}</body></html>"""
    (HERE / "deck.html").write_text(html)
    print("wrote deck.html;", f"upper={UPPER_CR:.0f}cr compute={COMPUTE_INR/1e5:.1f}L storage={STORAGE_INR/1e5:.2f}L "
          f"holds/day={FALSE_HOLDS_DAY:.0f} agent_h={AGENT_HOURS_DAY:.0f} inst={INSTANCES} peak={PEAK_QPS:.0f}")


if __name__ == "__main__":
    build()

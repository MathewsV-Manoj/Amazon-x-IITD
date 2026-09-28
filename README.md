# Chakravyuh — scam kill-chain interceptor

Round-1 submission for the **Amazon AI Cyber Security Hackathon**
(IIT Delhi · ARIES + DevClub · Track 02 — AI-Driven Scam Pattern Recognition).

**Author:** Mathews V Manoj, Muthoot Institute of Technology and Science (KTU),
Electronics & Communication Engineering.

> Intercept the **scam workflow**, not the transaction.

Chakravyuh reads a UPI payment session as a four-stage **kill chain**
(contact → control → extraction → cash-out), fuses 20 device + bank + network
signals into per-stage evidence, and only interrupts a payment when a
credible *workflow* — not a single strong signal — forms. Every decision
comes with a specific playbook name, a top-5 reason list, and a signed audit
receipt.

All data in this repository is **synthetic**. No real bank, customer, or
platform data is used anywhere.

## The submission PDF

`submission/Chakravyuh_Round1.pdf`
10-slide pitch deck (landscape A4) + 3-page architectural overview (portrait A4)
+ optional appendix (assumptions, disclosures, references, Kotlin SDK sketch).

Rebuild it:
```
pip install -r requirements.txt
python3 eval/run_eval.py          # writes eval/out/{model,results}.json + charts
python3 eval/deep_eval.py         # adds ablation, LOO, adversarial, calibration
python3 submission/assets/mockups.py                # mobile UI mockups
PYTHONPATH=. python3 submission/build_pdf.py        # rebuilds the PDF
```
Every number and every chart on the deck is regenerated from JSON.

## Headline results (unseen synthetic test world, alert budget 3 / 1,000 legit)

| System                                       | Recall | FP / 1k | AUPRC | Adapted recall |
|----------------------------------------------|-------:|--------:|------:|---------------:|
| **Chakravyuh (kill-chain fusion)**           | **95%**| **3.1** | **0.981** | **88%**    |
| Rule: new payee + high amount                | 49%    | 9.2     | 0.354 | 8%             |
| Logistic regression (no stage gate)          | 97%    | 3.3     | 0.985 | 92%            |
| Gradient boosting (sklearn)                  | 97%    | 3.3     | 0.986 | 93%            |
| XGBoost (tuned)                              | 97%    | 3.4     | 0.986 | 94%            |
| MLP (2 hidden layers)                        | 97%    | 3.5     | 0.986 | 94%            |

We give up ~2 pp of recall against black-box baselines and gain per-signal
explanations, a stage-gate that no single signal can bypass, and a signed
receipt for every decision.

**Ablation** (recall at same budget after zeroing each stage's signals):

| Stage removed | Recall |
|---|---:|
| — (all four) | 95% |
| contact | 87% |
| control | 93% |
| extraction | 89% |
| cash-out | 66% |

**Leave-one-scenario-out** (train without one playbook, test on it):

| Held-out scenario | Recall on unseen sessions |
|---|---:|
| digital arrest | 94% |
| remote-access KYC | 96% |
| investment / task | 85% |
| collect request | 80% |

**Adversarial robustness** (attacker suppresses top-N highest-weight signals):

| N suppressed | Recall kept |
|---:|---:|
| 0 | 95% |
| 1 | 77% |
| 2 | 54% |
| 3 | 33% |

**Fairness / per-persona** (all recall / FP within ± 2 pp of the average).

**Pilot economics** (30 M users, 250 sessions/user/year, ₹42 k avg ticket):
projected ₹5,982 crore saved / year. At 100 M users: ₹19,941 crore.
Engine latency: ~25 µs / session in-process.

## Code map

- `chakravyuh/signals.py` — the 20-signal catalogue (source, why-text, "not-collected" clause).
- `chakravyuh/synth.py` — 4 India-specific playbooks + 25% adapted-fraudster cohort.
- `chakravyuh/mule_graph.py` — 7-day synthetic payment graph, payee mule score.
- `chakravyuh/fusion.py` — additive non-negative weights (L2 logistic) + stage caps + kill-chain gate + playbook match.
- `chakravyuh/service.py` — FastAPI `/decide` with HMAC-signed decision receipts.
- `chakravyuh/demo.py` + `web/index.html` — interactive dashboard.
- `eval/run_eval.py`, `eval/deep_eval.py` — three seeded worlds + baselines + ablation + LOO + adversarial + calibration + impact math.
- `submission/build_pdf.py`, `submission/assets/mockups.py` — deck + mobile mockups.
- `tests/test_smoke.py` — 7 pytest tests including "no single signal can breach tier 2".
- `docs/ASSUMPTIONS.md` — what is real, what is synthetic, what a pilot replaces.

## Interactive demo

```
python3 -m uvicorn chakravyuh.demo:app --port 8765
# open http://127.0.0.1:8765/
```
Toggle signals or pick a scenario; the fused score, active kill-chain stages,
playbook match and top reasons update live. The privacy contract sits next
to the signal list.

## References

- Ministry of Home Affairs, Lok Sabha reply, 22 Jul 2025 — ₹22,845 crore lost
  to cyber fraud in 2024; 36.37 lakh NCRP + CFCFRMS complaints.
- Reserve Bank of India, Annual Report 2024-25 (May 2025) — UPI-related fraud
  ₹981 crore across 12.64 lakh incidents in FY25.
- Indian Cyber Crime Coordination Centre — Suspect Registry (Sep 2024).
- Digital Personal Data Protection Act, 2023.

## Third-party assets

FastAPI, uvicorn, scikit-learn, numpy, networkx, matplotlib, xgboost,
reportlab, svglib, pymupdf — all permissively licensed. Font: DejaVu Sans
(public domain). Prose drafted by the team and refined with Claude Code;
every reviewer-facing number and chart is computed from the code in this
repository.

# Chakravyuh -- scam kill-chain interceptor

Round-1 submission for the Amazon AI Cyber Security Hackathon
(IIT Delhi · ARIES + DevClub · Track 02 -- AI-Driven Scam Pattern Recognition).

**Author:** Mathews V Manoj, Muthoot Institute of Technology and Science (KTU),
Electronics & Communication Engineering.

Chakravyuh reads a UPI payment session as a four-stage **kill chain**
(contact → control → extraction → cash-out), fuses 20 device + bank + network
signals into a per-stage evidence score, and interrupts a payment only when a
credible *workflow* -- not a single signal -- forms. Every decision comes with a
specific playbook name, a top-5 reason list, and a signed audit receipt.

All data in this repository is **synthetic**. No real bank, customer, or
platform data is used anywhere.

## The submission PDF

`submission/Chakravyuh_Round1.pdf`
10-slide pitch deck (landscape A4) + 3-page architectural overview (portrait A4)
+ optional appendix (assumptions, disclosures, references).

Rebuild it:
```
python3 eval/run_eval.py          # writes eval/out/{model,results}.json + charts
PYTHONPATH=. python3 submission/build_pdf.py
```
Every number and chart on the deck is regenerated from `results.json`.

## The engine

- `chakravyuh/signals.py` -- the 20-signal catalogue, with the "why" text
  users see and the "not collected" clause for each one.
- `chakravyuh/synth.py` -- synthetic session generator (60k legit + 2.4k scam
  per world) covering four India-specific playbooks, with a 25% adapted-fraudster
  cohort where the caller deliberately suppresses signals.
- `chakravyuh/mule_graph.py` -- 7-day synthetic payment graph and payee
  mule score (fan-in, first-time-sender ratio, pass-through, age).
- `chakravyuh/fusion.py` -- additive non-negative evidence weights learned by
  L2-regularised logistic regression, stage caps, kill-chain gate, tier
  thresholds, playbook match, top-5 reasons.
- `chakravyuh/service.py` -- FastAPI `/decide` endpoint with signed decision
  receipts (HMAC-SHA256).
- `chakravyuh/demo.py` -- serves the interactive web dashboard.

## Interactive demo

```
python3 -m uvicorn chakravyuh.demo:app --port 8765
# then open http://127.0.0.1:8765/
```
Toggle signals or pick a scenario; the fused score, active stages, playbook
and top reasons update live. The privacy contract is shown next to the
signal list.

## Evidence

Reported on an **unseen** synthetic test world (60,000 legit + 2,400 scam
sessions), thresholds calibrated on a validation world to an alert budget of
3 interruptions per 1,000 legit sessions:

| System                                       | Recall | ₹-recall | Legit alerts / 1k | Adapted-fraudster recall |
|----------------------------------------------|-------:|---------:|------------------:|-------------------------:|
| Chakravyuh, tier ≥ 2 (interrupt)             | 92%    | 96%      | 3.6               | 88%                      |
| Chakravyuh, tier 3 (cooling-off hold)        | 67%    | 78%      | 0.9               | 46%                      |
| Rule: new payee + high amount                | 49%    | 87%      | 9.2               | 8%                       |
| Rule: any single strong signal               | 89%    | 94%      | 35                | 82%                      |
| Gradient boosting, black box, same budget    | 97%    | 99%      | 3.3               | 94%                      |

The black-box baseline is ~4 pp ahead of us on recall; Chakravyuh trades that
for a stage-gated, per-signal explanation and a signed audit receipt, which
matters for user trust, false-positive appeal, and regulator review.

Engine latency: ~25 µs/session in-process on a laptop.

## Tests

```
python3 -m pytest tests/ -q
```
Includes the key invariant that no single signal can push a session into
tier ≥ 2 on its own.

## References

- Ministry of Home Affairs, Lok Sabha reply, 22 July 2025: ₹22,845 crore lost
  to cyber fraud in 2024; 36.37 lakh NCRP + CFCFRMS complaints.
- Reserve Bank of India, Annual Report 2024-25 (May 2025): UPI-related frauds
  ₹981 crore across 12.64 lakh incidents in FY25.
- Indian Cyber Crime Coordination Centre: Suspect Registry (Sep 2024).
- Digital Personal Data Protection Act, 2023.

## Third-party assets

FastAPI, uvicorn, scikit-learn, numpy, networkx, matplotlib, reportlab,
svglib -- all permissively licensed. Font: DejaVu Sans (public domain).
Prose drafted by the team and refined with Claude Code; every reviewer-facing
number and chart is computed from the code in this repository.

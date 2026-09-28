# Assumptions register

Every number that ends up in the pitch deck or the architecture is fed by a
value in one of these files. Where a value is a modelling choice, it is listed
here so it can be replaced with partner-bank calibration data.

## Real-world context (external, cited)

| Value | Source |
|---|---|
| ₹22,845 crore lost to cyber fraud in India, 2024 | MHA reply, Lok Sabha, 22 July 2025 |
| 36.37 lakh NCRP + CFCFRMS complaints in 2024 | MHA reply, Lok Sabha, 22 July 2025 |
| ₹981 crore in UPI-related frauds, 12.64 lakh incidents, FY25 | RBI Annual Report 2024-25 |
| I4C Suspect Registry launched Sep 2024, ~11 lakh identifiers | I4C statements |
| 206% year-on-year growth in cyber-fraud losses | MHA reply, Lok Sabha, 22 July 2025 |

## Deployment prior (real prevalence)

| Value | Where |
|---|---|
| 1 scam in every 5,000 *high-value P2P* payment sessions | `chakravyuh/fusion.py::fit`, `eval/run_eval.py::REAL_PREVALENCE` |

Used only to shift the intercept from training prevalence to real prevalence
before threshold calibration; not used to inflate any reported metric.

## Alert budget (SLO)

| Tier | Budget per 1,000 legit sessions | Where |
|---|---|---|
| 1 -- silent watch-list | ≤ 20 | `eval/run_eval.py::BUDGET_T1` |
| 2 -- interrupt | ≤ 3   | `eval/run_eval.py::BUDGET_T2` |
| 3 -- cooling-off hold | ≤ 0.5 | `eval/run_eval.py::BUDGET_T3` |

Set by the bank in production; the engine self-calibrates thresholds on the
validation world to hit the chosen budget.

## Synthetic-world knobs

Values are set in `chakravyuh/synth.py` and `chakravyuh/mule_graph.py`.

| Value | Value | Rationale (replace in pilot) |
|---|---|---|
| Legit sessions / world | 60,000 | large enough for stable per-1k false-alert estimation |
| Scam sessions / world | 2,400  | 4% enrichment; prevalence-shift applied at inference |
| Adapted-fraudster fraction | 25% | conservative -- fraudsters actively suppress ~1-3 signals |
| Persona split | student / professional / senior / shopkeeper | broad coverage; seniors are 40% of scam victims in the model |
| Mule accounts | 120 per world | roughly matches the fan-in load of scam sessions |
| Aged (rented) mule fraction | 25% | a real adversarial adaptation seen in the wild |
| Cash-out endpoints | 15 per world | corresponds to a small ring; will be much larger in reality |
| Payment graph horizon | 7 days | matches typical mule-account life cycle |

## Model choices

| Choice | Value | Rationale |
|---|---|---|
| Regularisation strength (logistic C) | 0.3 | keeps weights compact, discourages spurious high weights |
| Weight sign | non-negative (clipped) | absence of a signal must never exonerate or accumulate suspicion |
| Stage cap (contact / control / extraction / cash-out) | 5 / 5 / 6 / 6 log-odds | no single stage can breach a tier alone |
| Tier 2 gate | ≥ 2 active stages | prevents "one very rare signal" alerts |
| Tier 3 gate | ≥ 3 active stages OR (≥ 2 stages AND registry hit) | proportional friction |
| Retrain cadence | weekly | pilot posture; move to daily if drift observed |

## What we assume the bank / SDK can deliver in a pilot

- SDK read of Android call state (`READ_PHONE_STATE`) and accessibility scan
  (user consent flow). Both are already used by many banking apps for
  screen-share detection.
- Bank-side first-time payee flag and per-user amount z-score (already
  computed for card fraud).
- Mule feature-store row per payee VPA, refreshed nightly, keyed by hash.
- Push channel for the app to display the tier-1/2 message.
- PSP hook capable of issuing a short-lived debit freeze token for tier-3.

## What we deliberately do *not* assume

- Access to raw call audio, message text, screen frames, contacts, or app inventory.
- Cross-bank data sharing beyond the I4C suspect registry (opt-in only).
- Any user PII inside the decision receipt (only the session id hash).
- A confusion between the user-reported "this is fraud" signal and a
  bank-confirmed mule label. Only the latter feeds retraining.

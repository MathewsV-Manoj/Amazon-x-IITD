"""Kill-chain evidence fusion.

1. Each binary signal contributes an additive, non-negative evidence weight
   (log-odds units) learned with regularised logistic regression -- every
   decision decomposes exactly into "which signals, how much".
2. LLRs are summed *per stage* and each stage is capped, so no single stage
   (e.g. a huge amount, or one unknown call) can push a user into a high tier.
3. A tier needs evidence from multiple *distinct* stages -- the "kill chain
   gate". This is the core anti-false-positive rule: we alert on workflows,
   not on single weak signals.
4. The matched scam playbook drives a specific, human message.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

from .signals import SIGNAL_BY_KEY, SIGNAL_KEYS, STAGES

STAGE_CAP = {"contact": 5.0, "control": 5.0, "extraction": 6.0, "cashout": 6.0}
STAGE_ACTIVE = 1.5      # a stage "fires" when its capped evidence exceeds this (LLR units)

# Signal fingerprints of each playbook (used to pick the user-facing message).
PLAYBOOKS = {
    "digital_arrest": {"call_unknown_active", "call_long", "video_call", "amount_very_high",
                       "fd_broken_24h", "staircase", "balance_drain"},
    "remote_access_kyc": {"remote_access", "sideload_24h", "accessibility_overlay",
                          "otp_read_in_call", "sms_scam_flag"},
    "investment_task": {"bait_credit_7d", "sideload_24h", "vpa_typed"},
    "collect_request": {"collect_from_p2p"},
}


@dataclass
class Decision:
    score: float                      # posterior-like log-odds
    probability: float
    stage_scores: dict
    active_stages: list
    tier: int
    playbook: str | None
    reasons: list = field(default_factory=list)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


class KillChainModel:
    def __init__(self, llr: dict | None = None, prior_logodds: float = -6.0,
                 thresholds: dict | None = None):
        self.llr = llr or {}
        self.prior = prior_logodds
        # thresholds on fused log-odds; calibrated by eval/run_eval.py against an alert budget
        self.thresholds = thresholds or {1: -3.0, 2: 0.0, 3: 3.0}

    # ---------- training ----------
    def fit(self, X: list[dict], y: list[int], C: float = 0.3, deployment_prior: float = 2e-4):
        """Learn additive evidence weights with L2-regularised logistic regression.

        Weights are clipped to be non-negative: the *absence* of a signal never
        adds suspicion and never exonerates (a fraudster can always suppress a
        signal). Correlated signals share weight instead of double counting.
        """
        from sklearn.linear_model import LogisticRegression
        import numpy as np

        A = np.array([[float(x[k]) for k in SIGNAL_KEYS] for x in X])
        lr = LogisticRegression(C=C, max_iter=3000).fit(A, y)
        self.llr = {k: round(max(0.0, float(w)), 3) for k, w in zip(SIGNAL_KEYS, lr.coef_[0])}
        # Shift the intercept from the enriched training prevalence to real-world prevalence.
        train_prev = float(np.mean(y))
        shift = math.log(deployment_prior / (1 - deployment_prior)) - math.log(train_prev / (1 - train_prev))
        self.prior = round(float(lr.intercept_[0]) + shift, 3)
        return self

    # ---------- inference ----------
    def score(self, x: dict) -> Decision:
        stage_scores = {s: 0.0 for s in STAGES}
        contrib = []
        for k, present in x.items():
            if not present or k not in self.llr:
                continue
            w = self.llr[k]
            stage_scores[SIGNAL_BY_KEY[k].stage] += w
            contrib.append((w, k))
        for s in STAGES:
            stage_scores[s] = round(max(-2.0, min(STAGE_CAP[s], stage_scores[s])), 3)
        active = [s for s in STAGES if stage_scores[s] >= STAGE_ACTIVE]
        logodds = self.prior + sum(stage_scores.values())
        prob = 1 / (1 + math.exp(-logodds))

        tier = 0
        if logodds >= self.thresholds[1]:
            tier = 1
        if logodds >= self.thresholds[2] and len(active) >= 2:
            tier = 2
        if logodds >= self.thresholds[3] and (len(active) >= 3 or (
                len(active) >= 2 and x.get("payee_registry_hit"))):
            tier = 3

        present = {k for k, v in x.items() if v}
        best, best_hits = None, 0
        for name, keys in PLAYBOOKS.items():
            hits = len(present & keys)
            if hits > best_hits:
                best, best_hits = name, hits
        contrib.sort(reverse=True)
        reasons = [{"signal": k, "stage": SIGNAL_BY_KEY[k].stage, "weight": w,
                    "text": SIGNAL_BY_KEY[k].why} for w, k in contrib if w > 0.3][:5]
        return Decision(round(logodds, 3), round(prob, 5), stage_scores, active, tier,
                        best if tier >= 1 else None, reasons)

    # ---------- persistence ----------
    def save(self, path):
        with open(path, "w") as f:
            json.dump({"llr": self.llr, "prior": self.prior, "thresholds": self.thresholds}, f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            d = json.load(f)
        return cls(d["llr"], d["prior"], {int(k): v for k, v in d["thresholds"].items()})

"""HTTP inference service (FastAPI). Stateless.

POST /decide  { evidence: {signal_key: bool, ...}, session_id, amount }
             -> { tier, action, message, score, stage_scores, reasons, log_id }

The service *never* sees raw call audio, message text, screen contents or
contact lists. The client (bank SDK on the device + bank rails) sends only the
booleans in the signal catalogue plus payee, amount and a hashed session id.

A signed decision receipt (see docs/DECISION_RECEIPT.md) is emitted so the
bank can audit and reproduce every alert, and so the user can appeal a hold.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .fusion import KillChainModel
from .signals import SIGNAL_BY_KEY, SIGNAL_KEYS, SIGNALS, STAGE_LABELS

MODEL_PATH = Path(os.environ.get("CHAKRAVYUH_MODEL", "eval/out/model.json"))
SECRET = os.environ.get("CHAKRAVYUH_SECRET", "dev-secret-not-for-production").encode()

ACTIONS = {
    0: ("allow", "Pay normally"),
    1: ("nudge", "We flagged this payment for review; please read before you pay"),
    2: ("interrupt", "Wait — this looks like a scam workflow. Answer 2 questions before you pay"),
    3: ("cooling_off", "This payment is being held for 30 minutes. Please review it with a bank agent"),
}

PLAYBOOK_MESSAGE = {
    "digital_arrest": ("This pattern matches the 'digital arrest' scam. Real police, CBI or RBI"
                       " officials never demand payment on a call, and no Indian agency asks you to"
                       " send money to a personal UPI ID."),
    "remote_access_kyc": ("A remote-access app is running on your phone. If you were told to install"
                          " it for KYC or a refund, the person on the call can see everything you type."),
    "investment_task": ("This looks like a task or investment scam. Small 'profits' first, then a"
                        " request to send a larger amount to unlock earnings, is the standard playbook."),
    "collect_request": ("This is a 'collect' request. Entering your UPI PIN here SENDS money away —"
                        " it does not receive money."),
}


class Evidence(BaseModel):
    session_id: str = Field(..., min_length=6, max_length=128)
    amount: float = Field(..., ge=0)
    payee_kind: str | None = None
    evidence: dict[str, bool]


class DecisionOut(BaseModel):
    tier: int
    action: str
    message: str
    reasons: list
    stage_scores: dict
    active_stages: list
    playbook: str | None
    score: float
    probability: float
    log_id: str
    receipt_sig: str


app = FastAPI(title="Chakravyuh scam kill-chain interceptor",
              description="Stateless UPI scam-workflow scoring. Synthetic-data prototype.")
_model: KillChainModel | None = None


def get_model() -> KillChainModel:
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"model not found at {MODEL_PATH}; run eval/run_eval.py first")
        _model = KillChainModel.load(MODEL_PATH)
    return _model


def _sign(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()


@app.get("/healthz")
def healthz():
    return {"ok": True, "signals": len(SIGNAL_KEYS), "model": MODEL_PATH.exists()}


@app.get("/signals")
def signals():
    return {"stages": STAGE_LABELS,
            "signals": [{"key": s.key, "stage": s.stage, "source": s.source,
                         "why": s.why, "not_collected": s.not_collected} for s in SIGNALS]}


@app.post("/decide", response_model=DecisionOut)
def decide(req: Evidence, x_api_key: str | None = Header(default=None)):
    # In production an authenticated bank API gateway sits in front; in dev we
    # keep the surface intentionally small.
    m = get_model()
    unknown = set(req.evidence) - set(SIGNAL_KEYS)
    if unknown:
        raise HTTPException(400, f"unknown signals: {sorted(unknown)}")
    x = {k: bool(req.evidence.get(k, False)) for k in SIGNAL_KEYS}
    d = m.score(x)
    action, base_msg = ACTIONS[d.tier]
    message = base_msg
    if d.tier >= 2 and d.playbook and d.playbook in PLAYBOOK_MESSAGE:
        message = PLAYBOOK_MESSAGE[d.playbook]
    if d.tier == 3 and req.amount >= 100000:
        message += " Amounts above ₹1 lakh have a mandatory 30-minute review."

    ts = int(time.time() * 1000)
    log_id = hashlib.sha256(f"{req.session_id}:{ts}".encode()).hexdigest()[:16]
    receipt = {
        "log_id": log_id, "ts_ms": ts, "session_id": req.session_id,
        "amount": req.amount, "evidence": {k: v for k, v in x.items() if v},
        "score": d.score, "tier": d.tier, "playbook": d.playbook,
        "active_stages": d.active_stages, "action": action,
    }
    sig = _sign(receipt)
    return DecisionOut(tier=d.tier, action=action, message=message, reasons=d.reasons,
                       stage_scores=d.stage_scores, active_stages=d.active_stages,
                       playbook=d.playbook, score=d.score, probability=d.probability,
                       log_id=log_id, receipt_sig=sig)

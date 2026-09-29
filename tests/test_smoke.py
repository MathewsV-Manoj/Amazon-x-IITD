"""Fast smoke tests: run in <10s. Cover generator, model, service and receipt."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chakravyuh.fusion import KillChainModel, PLAYBOOKS
from chakravyuh.signals import SIGNAL_KEYS
from chakravyuh.synth import featurize, generate


@pytest.fixture(scope="module")
def trained():
    S, _ = generate(n_legit=6000, n_scam=400, seed=3)
    X = [featurize(s) for s in S]
    y = [s["label"] for s in S]
    m = KillChainModel().fit(X, y)
    # rough per-test-run threshold calibration to a small alert budget
    scores = np.array([m.score(x).score for x in X]); ya = np.array(y)
    q = np.sort(scores[ya == 0])[::-1]
    t2 = float(q[int(0.005 * len(q))])
    m.thresholds = {1: t2 - 2, 2: t2, 3: t2 + 1.5}
    return m, S, X, y


def test_signal_coverage(trained):
    m, *_ = trained
    assert set(m.llr) == set(SIGNAL_KEYS)
    # Every signal is either strongly positive or effectively neutral (clipped >=0).
    assert all(w >= 0 for w in m.llr.values())


def test_kill_chain_gate_prevents_single_signal_tier2(trained):
    m, *_ = trained
    for k in SIGNAL_KEYS:
        x = {kk: kk == k for kk in SIGNAL_KEYS}
        d = m.score(x)
        assert d.tier < 2, f"single signal {k} reached tier {d.tier}"


def test_playbook_and_reasons(trained):
    m, *_ = trained
    x = {kk: False for kk in SIGNAL_KEYS}
    for k in ("call_unknown_active", "call_long", "video_call", "amount_very_high",
              "fd_broken_24h", "first_time_payee", "payee_mule_high"):
        x[k] = True
    d = m.score(x)
    assert d.tier >= 2
    assert d.playbook == "digital_arrest"
    assert d.reasons and all(r["weight"] > 0 for r in d.reasons)


def test_absence_of_signal_never_hurts(trained):
    m, *_ = trained
    a = {kk: False for kk in SIGNAL_KEYS}
    a["remote_access"] = True
    a["sideload_24h"] = True
    a["first_time_payee"] = True
    b = dict(a); b["video_call"] = True
    assert m.score(b).score >= m.score(a).score


def test_service_receipt_verifies():
    from fastapi.testclient import TestClient
    from chakravyuh import service as svc
    svc._model = None                  # force reload
    client = TestClient(svc.app)
    r = client.post("/decide", json={"session_id": "unit-test", "amount": 90000, "evidence": {
        "call_unknown_active": True, "call_long": True, "video_call": True,
        "first_time_payee": True, "amount_very_high": True, "fd_broken_24h": True,
        "payee_mule_high": True}})
    j = r.json()
    assert j["tier"] >= 2 and j["playbook"] == "digital_arrest"
    # receipt is deterministic given (ts, evidence, score)
    assert len(j["receipt_sig"]) == 64


def test_recall_on_small_world(trained):
    m, S, X, y = trained
    d = [m.score(x) for x in X]
    hits = sum(1 for i, s in enumerate(S) if s["label"] == 1 and d[i].tier >= 2)
    n_scam = sum(1 for s in S if s["label"] == 1)
    assert hits / n_scam >= 0.75


def test_generate_shapes():
    S, P = generate(n_legit=1000, n_scam=100, seed=5)
    assert len(S) == 1100
    assert len({s["label"] for s in S}) == 2
    assert any(p.kind == "mule" for p in P.values())


def test_replay_and_stale_evidence_rejected():
    import time
    from fastapi.testclient import TestClient
    from chakravyuh import service as svc
    client = TestClient(svc.app)
    now = int(time.time() * 1000)
    body = {"session_id": "replay-test", "amount": 100, "evidence": {},
            "nonce": "n" * 20, "client_ts_ms": now}
    assert client.post("/decide", json=body).status_code == 200
    assert client.post("/decide", json=body).status_code == 409      # same nonce
    stale = dict(body, nonce="m" * 20, client_ts_ms=now - 60_000)
    assert client.post("/decide", json=stale).status_code == 409     # too old

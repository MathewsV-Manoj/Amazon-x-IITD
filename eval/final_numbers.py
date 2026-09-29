"""Single source of truth for every number in the final submission PDF.

Protocol (identical for every system):
  train      : synthetic world seed 7
  calibrate  : synthetic world seed 21  (thresholds set to a legit-alert budget)
  test       : 8 independent synthetic worlds, seeds 101..108 (never seen)

Chakravyuh is evaluated with its real decision logic (stage caps + kill-chain
gate + tier thresholds), not a raw-score threshold. Baselines are evaluated at
the same budget on the same worlds. Everything is synthetic.

Writes eval/out/final.json
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chakravyuh.fusion import KillChainModel  # noqa: E402
from chakravyuh import fusion as fusion_mod  # noqa: E402
from chakravyuh.signals import SIGNAL_BY_KEY, SIGNAL_KEYS, SIGNALS, STAGES  # noqa: E402
from chakravyuh.synth import SCENARIOS, featurize, generate  # noqa: E402

OUT = ROOT / "eval" / "out"
TEST_SEEDS = list(range(101, 109))
BUDGET = {1: 20.0, 2: 3.0, 3: 0.5}      # legit alerts per 1,000 sessions (design targets)
DEPLOY_PRIOR = 2e-4                      # 1 scam per 5,000 sessions (assumption)


def world(seed):
    S, P = generate(seed=seed)
    X = [featurize(s) for s in S]
    y = np.array([s["label"] for s in S])
    return S, X, y


def mat(X):
    return np.array([[float(x[k]) for k in SIGNAL_KEYS] for x in X])


def thr_for_budget(scores, y, budget, eligible=None):
    elig = np.ones(len(scores), bool) if eligible is None else eligible
    legit = np.sort(scores[(y == 0) & elig])[::-1]
    k = int(budget / 1000.0 * (y == 0).sum())
    if k >= len(legit):
        return float(legit[-1]) - 1e-6 if len(legit) else -1e9
    return float(legit[k]) + 1e-6


def calibrate(model, X_va, y_va):
    d = [model.score(x) for x in X_va]
    s = np.array([e.score for e in d])
    na = np.array([len(e.active_stages) for e in d])
    reg = np.array([bool(x["payee_registry_hit"]) for x in X_va])
    t1 = thr_for_budget(s, y_va, BUDGET[1])
    t2 = thr_for_budget(s, y_va, BUDGET[2], na >= 2)
    t3 = thr_for_budget(s, y_va, BUDGET[3], (na >= 3) | ((na >= 2) & reg))
    model.thresholds = {1: t1, 2: max(t1, t2), 3: max(t1, t2, t3)}
    return model


def ci(vals, n=4000, seed=0):
    v = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    b = np.array([rng.choice(v, len(v)).mean() for _ in range(n)])
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def auprc(y, s):
    from sklearn.metrics import average_precision_score
    return float(average_precision_score(y, s))


def main():
    t0 = time.time()
    S_tr, X_tr, y_tr = world(7)
    S_va, X_va, y_va = world(21)
    tests = [world(s) for s in TEST_SEEDS]
    print(f"worlds ready in {time.time() - t0:.0f}s")

    model = calibrate(KillChainModel().fit(X_tr, list(y_tr), deployment_prior=DEPLOY_PRIOR), X_va, y_va)

    # ---------------- Chakravyuh per world (real tier logic) ----------------
    per = {k: [] for k in ["recall", "fp", "t3_recall", "t3_fp", "t1_fp", "auprc",
                           "recall_adapted", "recall_standard", "recall_aged_mule",
                           "recall_nogate", "fp_nogate"]}
    scen_hits = {k: [0, 0] for k in SCENARIOS}
    persona = {}
    pooled = {"S": [], "X": [], "y": [], "tier": [], "score": [], "nact": []}
    lat = []
    for S, X, y in tests:
        t = time.perf_counter()
        d = [model.score(x) for x in X]
        lat.append((time.perf_counter() - t) / len(X) * 1e6)
        tier = np.array([e.tier for e in d]); sc = np.array([e.score for e in d])
        na = np.array([len(e.active_stages) for e in d])
        a2 = tier >= 2
        per["recall"].append(a2[y == 1].mean()); per["fp"].append(1000 * a2[y == 0].mean())
        per["t3_recall"].append((tier == 3)[y == 1].mean()); per["t3_fp"].append(1000 * (tier == 3)[y == 0].mean())
        per["t1_fp"].append(1000 * (tier >= 1)[y == 0].mean())
        per["auprc"].append(auprc(y, sc))
        adapted = np.array([s["adapted"] for s in S])
        aged = np.array([s["payee"].kind == "mule" and s["payee"].age_days >= 120 for s in S])
        per["recall_adapted"].append(a2[(y == 1) & adapted].mean())
        per["recall_standard"].append(a2[(y == 1) & ~adapted].mean())
        per["recall_aged_mule"].append(a2[(y == 1) & aged].mean())
        # same model, gate removed (score threshold only, same budget)
        t_ng = thr_for_budget(np.array([model.score(x).score for x in X_va]), y_va, BUDGET[2])
        ng = sc >= t_ng
        per["recall_nogate"].append(ng[y == 1].mean()); per["fp_nogate"].append(1000 * ng[y == 0].mean())
        for i, s in enumerate(S):
            if y[i] == 1:
                scen_hits[s["scenario"]][0] += int(a2[i]); scen_hits[s["scenario"]][1] += 1
            p = persona.setdefault(s["persona"], [0, 0, 0, 0])
            if y[i] == 1:
                p[0] += int(a2[i]); p[1] += 1
            else:
                p[2] += int(a2[i]); p[3] += 1
        for k, v in [("S", S), ("X", X), ("y", list(y)), ("tier", list(tier)), ("score", list(sc)), ("nact", list(na))]:
            pooled[k].extend(v)

    chak = {k: dict(zip(["mean", "lo", "hi"], ci(v))) for k, v in per.items()}
    chak["per_world_recall"] = [float(v) for v in per["recall"]]
    chak["per_world_fp"] = [float(v) for v in per["fp"]]
    chak["by_scenario"] = {k: v[0] / v[1] for k, v in scen_hits.items()}
    chak["by_persona"] = {k: {"recall": v[0] / v[1], "fp": 1000 * v[2] / v[3]} for k, v in persona.items()}
    chak["latency_us"] = float(np.mean(lat))
    chak["thresholds"] = model.thresholds

    # ---------------- Baselines, same protocol ----------------
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    import xgboost as xgb
    A_tr, A_va = mat(X_tr), mat(X_va)
    A_te = [mat(X) for _, X, _ in tests]
    models = {
        "Logistic regression": LogisticRegression(C=1.0, max_iter=3000).fit(A_tr, y_tr),
        "Gradient boosting": HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(A_tr, y_tr),
        "XGBoost": xgb.XGBClassifier(n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.9,
                                     colsample_bytree=0.9, random_state=0, eval_metric="logloss",
                                     tree_method="hist").fit(A_tr, y_tr),
        "MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=80, random_state=0,
                             early_stopping=True).fit(A_tr, y_tr),
    }
    baselines = {}
    for name, m in models.items():
        f = (lambda A, m=m: m.decision_function(A)) if hasattr(m, "decision_function") else \
            (lambda A, m=m: m.predict_proba(A)[:, 1])
        t = thr_for_budget(f(A_va), y_va, BUDGET[2])
        rs, fs, aps = [], [], []
        for A, (_, _, y) in zip(A_te, tests):
            s = f(A); a = s >= t
            rs.append(a[y == 1].mean()); fs.append(1000 * a[y == 0].mean()); aps.append(auprc(y, s))
        baselines[name] = {"recall": dict(zip(["mean", "lo", "hi"], ci(rs))),
                           "fp": dict(zip(["mean", "lo", "hi"], ci(fs))),
                           "auprc": dict(zip(["mean", "lo", "hi"], ci(aps)))}
    # the incumbent-style rule (fixed, no budget tuning possible)
    rs, fs = [], []
    for _, X, y in tests:
        a = np.array([x["first_time_payee"] and x["amount_high"] for x in X])
        rs.append(a[y == 1].mean()); fs.append(1000 * a[y == 0].mean())
    baselines["Rule: new payee + high amount"] = {"recall": dict(zip(["mean", "lo", "hi"], ci(rs))),
                                                  "fp": dict(zip(["mean", "lo", "hi"], ci(fs)))}

    # ---------------- pooled robustness analyses ----------------
    Xp, yp = pooled["X"], np.array(pooled["y"])
    order = sorted(SIGNAL_KEYS, key=lambda k: -model.llr[k])
    adv = []
    for n in range(0, 6):
        tiers = []
        for x in Xp:
            xa = dict(x)
            for k in [k for k in order if xa.get(k)][:n]:
                xa[k] = False
            tiers.append(model.score(xa).tier)
        tiers = np.array(tiers)
        adv.append({"suppressed": n, "recall": float((tiers >= 2)[yp == 1].mean()),
                    "fp": float(1000 * (tiers >= 2)[yp == 0].mean())})

    ablation = []
    for st in [None] + list(STAGES):
        keep = [k for k in SIGNAL_KEYS if st is None or SIGNAL_BY_KEY[k].stage != st]
        z = lambda X: [{k: (x[k] if k in keep else False) for k in SIGNAL_KEYS} for x in X]  # noqa: E731
        m = calibrate(KillChainModel().fit(z(X_tr), list(y_tr), deployment_prior=DEPLOY_PRIOR), z(X_va), y_va)
        tiers = np.array([m.score(x).tier for x in z(Xp)])
        ablation.append({"removed": st or "none", "recall": float((tiers >= 2)[yp == 1].mean()),
                         "fp": float(1000 * (tiers >= 2)[yp == 0].mean())})

    loo = []
    scen_tr = np.array([s["scenario"] for s in S_tr])
    scen_p = np.array([s["scenario"] for s in pooled["S"]])
    for held in SCENARIOS:
        keep = (scen_tr != held)
        m = calibrate(KillChainModel().fit([X_tr[i] for i in np.where(keep)[0]], list(y_tr[keep]),
                                           deployment_prior=DEPLOY_PRIOR), X_va, y_va)
        idx = np.where(scen_p == held)[0]
        tiers = np.array([m.score(Xp[i]).tier for i in idx])
        loo.append({"held_out": held, "recall": float((tiers >= 2).mean())})

    # stage cap: compare with caps effectively removed
    caps = dict(fusion_mod.STAGE_CAP)
    try:
        for k in fusion_mod.STAGE_CAP:
            fusion_mod.STAGE_CAP[k] = 1e9
        m = calibrate(KillChainModel().fit(X_tr, list(y_tr), deployment_prior=DEPLOY_PRIOR), X_va, y_va)
        tiers = np.array([m.score(x).tier for x in Xp])
        nocap = {"recall": float((tiers >= 2)[yp == 1].mean()), "fp": float(1000 * (tiers >= 2)[yp == 0].mean())}
    finally:
        fusion_mod.STAGE_CAP.update(caps)

    # calibration: score is prevalence-shifted to 1/5000; shift to the test prevalence to assess it
    prev = yp.mean()
    shift = math.log(prev / (1 - prev)) - math.log(DEPLOY_PRIOR / (1 - DEPLOY_PRIOR))
    p = 1 / (1 + np.exp(-(np.array(pooled["score"]) + shift)))
    edges = np.linspace(0, 1, 11); bins = []; ece = 0.0
    for i in range(10):
        msk = (p >= edges[i]) & ((p < edges[i + 1]) if i < 9 else (p <= 1))
        if msk.sum() >= 20:
            bins.append({"conf": float(p[msk].mean()), "acc": float(yp[msk].mean()), "n": int(msk.sum())})
            ece += msk.sum() * abs(p[msk].mean() - yp[msk].mean())
    calib = {"brier": float(((p - yp) ** 2).mean()), "ece": float(ece / len(yp)), "bins": bins,
             "eval_prevalence": float(prev)}

    # ---------------- signal accounting (from source) ----------------
    src = {}
    for s in SIGNALS:
        src.setdefault(s.source, []).append(s.key)

    out = {"protocol": {"train_seed": 7, "calib_seed": 21, "test_seeds": TEST_SEEDS,
                        "sessions_per_world": {"legit": int((tests[0][2] == 0).sum()),
                                               "scam": int((tests[0][2] == 1).sum())},
                        "budget_per_1000": BUDGET, "deployment_prior": DEPLOY_PRIOR},
           "chakravyuh": chak, "baselines": baselines, "adversarial": adv, "ablation": ablation,
           "loo": loo, "no_stage_cap": nocap, "calibration": calib,
           "signals": {k: v for k, v in src.items()}, "weights": model.llr,
           "stage_cap": caps, "stage_active": fusion_mod.STAGE_ACTIVE}
    (OUT / "final.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps({k: out["chakravyuh"][k] for k in ["recall", "fp", "t3_recall", "t3_fp", "t1_fp", "auprc",
                                                          "recall_adapted", "recall_aged_mule",
                                                          "recall_nogate", "fp_nogate"]}, indent=1))
    print("scen", out["chakravyuh"]["by_scenario"])
    print("persona", out["chakravyuh"]["by_persona"])
    print("latency", out["chakravyuh"]["latency_us"])
    for k, v in baselines.items():
        print(f"{k:32s} {v['recall']['mean']:.3f} fp {v['fp']['mean']:.2f}")
    print("adv", adv); print("abl", ablation); print("loo", loo); print("nocap", nocap)
    print("calib", calib["brier"], calib["ece"], prev); print("signals", {k: len(v) for k, v in src.items()})
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

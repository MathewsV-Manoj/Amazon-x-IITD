"""Extra measurements requested by the judge review. Same protocol as final_numbers.py.

1. Baselines at the SAME false-alarm rate as Chakravyuh (threshold matched on the
   calibration world), so recall is compared like for like.
2. Genuine payments a standard model interrupts on evidence from only one stage
   (Chakravyuh cannot do this by construction), with the most common pattern.
3. Chakravyuh retrained with only the phone signals a banking app can realistically
   read under Android / Google Play policy (restricted signals removed).

Merges results into eval/out/final.json under "judge".
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chakravyuh.fusion import KillChainModel  # noqa: E402
from chakravyuh.signals import SIGNAL_BY_KEY, SIGNAL_KEYS  # noqa: E402
from eval.final_numbers import (BUDGET, DEPLOY_PRIOR, TEST_SEEDS, calibrate, ci, mat,  # noqa: E402
                                thr_for_budget, world)

# Phone signals that need Play-restricted access (call log, SMS, all-package
# visibility, other apps' notifications). See the deck for the per-signal notes.
RESTRICTED = ["call_unknown_active", "sms_scam_flag", "sideload_24h", "otp_read_in_call"]


def main():
    out_path = ROOT / "eval" / "out" / "final.json"
    F = json.loads(out_path.read_text())
    S_tr, X_tr, y_tr = world(7)
    S_va, X_va, y_va = world(21)
    tests = [world(s) for s in TEST_SEEDS]
    m = calibrate(KillChainModel().fit(X_tr, list(y_tr), deployment_prior=DEPLOY_PRIOR), X_va, y_va)

    # Chakravyuh's own interruption rate on the calibration world
    tv = np.array([m.score(x).tier for x in X_va])
    va_rate = 1000 * (tv >= 2)[y_va == 0].mean()

    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    import xgboost as xgb
    A_tr, A_va = mat(X_tr), mat(X_va)
    models = {
        "Logistic regression": LogisticRegression(C=1.0, max_iter=3000).fit(A_tr, y_tr),
        "Gradient boosting": HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(A_tr, y_tr),
        "XGBoost": xgb.XGBClassifier(n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.9,
                                     colsample_bytree=0.9, random_state=0, eval_metric="logloss",
                                     tree_method="hist").fit(A_tr, y_tr),
        "MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=80, random_state=0,
                             early_stopping=True).fit(A_tr, y_tr),
    }

    def scorer(mdl):
        return (lambda A: mdl.decision_function(A)) if hasattr(mdl, "decision_function") else \
            (lambda A: mdl.predict_proba(A)[:, 1])

    matched = {}
    for name, mdl in models.items():
        f = scorer(mdl)
        t = thr_for_budget(f(A_va), y_va, va_rate)
        rs, fs = [], []
        for _, X, y in tests:
            a = f(mat(X)) >= t
            rs.append(a[y == 1].mean()); fs.append(1000 * a[y == 0].mean())
        matched[name] = {"recall": dict(zip(["mean", "lo", "hi"], ci(rs))),
                         "fp": dict(zip(["mean", "lo", "hi"], ci(fs)))}

    # 2. single-stage interruptions by logistic regression at the standard 3/1k budget
    lr = scorer(models["Logistic regression"])
    t_lr = thr_for_budget(lr(A_va), y_va, BUDGET[2])
    n_leg = n_leg_single = n_scam = n_scam_single_lr = n_scam_single_kc = 0
    lr_leg_alerts = 0
    patterns = Counter()
    example = None
    for S, X, y in tests:
        a = lr(mat(X)) >= t_lr
        for i, x in enumerate(X):
            d = m.score(x)
            single = len(d.active_stages) <= 1
            if y[i] == 0:
                n_leg += 1
                if a[i]:
                    lr_leg_alerts += 1
                    if single:
                        n_leg_single += 1
                        key = tuple(sorted(k for k, v in x.items() if v))
                        patterns[key] += 1
                        if example is None and len(key) >= 2:
                            s = S[i]
                            example = {"signals": list(key), "amount": s["amount"], "persona": s["persona"],
                                       "active_stages": d.active_stages, "tier": d.tier}
            else:
                n_scam += 1
                if single and a[i]:
                    n_scam_single_lr += 1
                if single and d.tier >= 2:
                    n_scam_single_kc += 1
    top = [{"signals": list(k), "per_1000_genuine": 1000 * c / n_leg, "count": c} for k, c in patterns.most_common(4)]
    single_stage = {"lr_genuine_alerts_per_1000": 1000 * lr_leg_alerts / n_leg,
                    "lr_single_stage_genuine_per_1000": 1000 * n_leg_single / n_leg,
                    "lr_single_stage_share_of_genuine_alerts": n_leg_single / max(1, lr_leg_alerts),
                    "chakravyuh_single_stage_genuine_per_1000": 0.0,
                    "scams_single_stage_caught_by_lr_share": n_scam_single_lr / n_scam,
                    "top_patterns": top, "example": example}

    # scam types Chakravyuh misses that LR catches (where the recall gap comes from)
    gap = Counter()
    for S, X, y in tests:
        a = lr(mat(X)) >= t_lr
        for i, x in enumerate(X):
            if y[i] == 1 and a[i] and m.score(x).tier < 2:
                gap[S[i]["scenario"]] += 1
    tot = sum(gap.values())
    gap_share = {k: v / tot for k, v in gap.items()}

    # 3. feasible phone signals only
    keep = [k for k in SIGNAL_KEYS if k not in RESTRICTED]
    z = lambda X: [{k: (x[k] if k in keep else False) for k in SIGNAL_KEYS} for x in X]  # noqa: E731
    mf = calibrate(KillChainModel().fit(z(X_tr), list(y_tr), deployment_prior=DEPLOY_PRIOR), z(X_va), y_va)
    rs, fs = [], []
    for _, X, y in tests:
        t = np.array([mf.score(x).tier for x in z(X)])
        rs.append((t >= 2)[y == 1].mean()); fs.append(1000 * (t >= 2)[y == 0].mean())
    feasible = {"removed": RESTRICTED, "device_signals_kept": [k for k in keep if SIGNAL_BY_KEY[k].source == "device"],
                "recall": dict(zip(["mean", "lo", "hi"], ci(rs))), "fp": dict(zip(["mean", "lo", "hi"], ci(fs)))}

    F["judge"] = {"calib_interrupt_rate": va_rate, "matched_fp": matched, "single_stage": single_stage,
                  "gap_by_scenario": gap_share, "feasible_only": feasible}
    out_path.write_text(json.dumps(F, indent=2, default=float))
    print("Chakravyuh calib-world rate", round(va_rate, 2))
    for k, v in matched.items():
        print(f"  matched {k:22s} recall {v['recall']['mean']*100:.1f}%  fp {v['fp']['mean']:.2f}")
    print("single-stage:", json.dumps({k: v for k, v in single_stage.items() if k != 'top_patterns'}, default=float))
    for p in top:
        print("  pattern", p)
    print("gap by scenario", gap_share)
    print("feasible only", feasible["recall"], feasible["fp"], feasible["device_signals_kept"])


if __name__ == "__main__":
    main()

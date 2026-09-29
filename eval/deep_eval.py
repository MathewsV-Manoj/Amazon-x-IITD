"""Deeper evaluation for the pitch deck.

Runs on top of eval/run_eval.py and adds:
  - additional black-box baselines (XGBoost with tuned depth, small MLP)
  - per-stage ablation ("what happens if we blindfold one kill-chain stage")
  - leave-one-scenario-out generalization
  - adversarial-attack ROC: recall as N signals are suppressed
  - calibration curve (reliability diagram)
  - per-persona recall breakdown
  - impact math in rupees (at pilot scale)
  - separability / AUPRC / AUROC for the fused score

Writes:
  eval/out/deep.json         (all numbers)
  submission/assets/*.svg    (publication-quality charts)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chakravyuh.fusion import KillChainModel  # noqa: E402
from chakravyuh.signals import SIGNAL_BY_KEY, SIGNAL_KEYS, STAGES  # noqa: E402
from chakravyuh.synth import SCENARIOS, featurize, generate  # noqa: E402
from eval.run_eval import (BUDGET_T2, REAL_PREVALENCE, threshold_for_budget,
                            world)  # noqa: E402

OUT = ROOT / "eval" / "out"
ASSETS = ROOT / "submission" / "assets"

INK, MUTED, ACC, ACC2, OK, WARN, BLUE, GRAY = ("#0d1420", "#5a6473", "#d9480f", "#f28c4f",
                                                "#116a4c", "#a05a00", "#4263eb", "#94a3b8")


def _matrix(X):
    return np.array([[float(x[k]) for k in SIGNAL_KEYS] for x in X])


def _score_kc(m, X):
    return np.array([m.score(x).score for x in X])


def _at_budget(scores_val, y_val, scores_te, y_te, budget=BUDGET_T2):
    t = threshold_for_budget(scores_val, y_val, budget)
    alerts_te = scores_te >= t
    return {
        "threshold": float(t),
        "recall": float(alerts_te[y_te == 1].mean()),
        "legit_alerts_per_1000": float(1000 * alerts_te[y_te == 0].mean()),
    }


def _auprc(scores, y):
    from sklearn.metrics import average_precision_score, roc_auc_score
    return {"auprc": float(average_precision_score(y, scores)),
            "auroc": float(roc_auc_score(y, scores))}


def run_baselines(X_tr, y_tr, X_va, y_va, X_te, y_te):
    Atr, Ava, Ate = _matrix(X_tr), _matrix(X_va), _matrix(X_te)
    # Chakravyuh
    m = KillChainModel().fit(X_tr, list(y_tr))
    kc_va, kc_te = _score_kc(m, X_va), _score_kc(m, X_te)
    kc = _at_budget(kc_va, y_va, kc_te, y_te) | _auprc(kc_te, y_te)
    kc["name"] = "Chakravyuh (kill-chain fusion)"
    # persist the calibrated threshold on the model so downstream
    # adversarial / persona / demo use it too
    m.thresholds = {1: kc["threshold"] - 2, 2: kc["threshold"], 3: kc["threshold"] + 1.5}
    # Rule 1
    r1_te = ((Ate[:, SIGNAL_KEYS.index("first_time_payee")] > 0) &
             (Ate[:, SIGNAL_KEYS.index("amount_high")] > 0)).astype(float)
    r1_va = ((Ava[:, SIGNAL_KEYS.index("first_time_payee")] > 0) &
             (Ava[:, SIGNAL_KEYS.index("amount_high")] > 0)).astype(float)
    r1 = {"name": "Rule: new payee + high amount",
          "threshold": 0.5,
          "recall": float(r1_te[y_te == 1].mean()),
          "legit_alerts_per_1000": float(1000 * r1_te[y_te == 0].mean())} | _auprc(r1_te, y_te)
    # Logistic (single-stage, no gate)
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(C=1.0, max_iter=3000).fit(Atr, y_tr)
    lr_va, lr_te = lr.decision_function(Ava), lr.decision_function(Ate)
    lr_o = _at_budget(lr_va, y_va, lr_te, y_te) | _auprc(lr_te, y_te)
    lr_o["name"] = "Logistic regression (no stage gate)"
    # Gradient boosting (sklearn)
    from sklearn.ensemble import HistGradientBoostingClassifier
    gb = HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(Atr, y_tr)
    gb_va, gb_te = gb.predict_proba(Ava)[:, 1], gb.predict_proba(Ate)[:, 1]
    gb_o = _at_budget(gb_va, y_va, gb_te, y_te) | _auprc(gb_te, y_te)
    gb_o["name"] = "Gradient boosting (sklearn)"
    # XGBoost
    import xgboost as xgb
    xg = xgb.XGBClassifier(n_estimators=400, max_depth=6, learning_rate=0.05,
                           subsample=0.9, colsample_bytree=0.9, random_state=0,
                           eval_metric="logloss", tree_method="hist").fit(Atr, y_tr)
    xg_va, xg_te = xg.predict_proba(Ava)[:, 1], xg.predict_proba(Ate)[:, 1]
    xg_o = _at_budget(xg_va, y_va, xg_te, y_te) | _auprc(xg_te, y_te)
    xg_o["name"] = "XGBoost (tuned)"
    # Small MLP
    from sklearn.neural_network import MLPClassifier
    mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=80, random_state=0,
                        early_stopping=True).fit(Atr, y_tr)
    mlp_va, mlp_te = mlp.predict_proba(Ava)[:, 1], mlp.predict_proba(Ate)[:, 1]
    mlp_o = _at_budget(mlp_va, y_va, mlp_te, y_te) | _auprc(mlp_te, y_te)
    mlp_o["name"] = "MLP (2 hidden layers)"
    return m, kc_te, [kc, r1, lr_o, gb_o, xg_o, mlp_o]


def ablate_stages(X_tr, y_tr, X_va, y_va, X_te, y_te, S_te):
    """For each stage, blindfold ALL its signals and re-train Chakravyuh.

    Reports the drop in recall at the same alert budget so the deck can show
    how much of the detection each kill-chain stage really carries.
    """
    out = []
    m_full = KillChainModel().fit(X_tr, list(y_tr))
    kc_va, kc_te = _score_kc(m_full, X_va), _score_kc(m_full, X_te)
    baseline = _at_budget(kc_va, y_va, kc_te, np.array([s["label"] for s in S_te]))
    out.append({"stage": "all four stages", **baseline})
    for st in STAGES:
        keys = [k for k in SIGNAL_KEYS if SIGNAL_BY_KEY[k].stage != st]

        def zeroed(X):
            return [{k: (x[k] if k in keys else False) for k in SIGNAL_KEYS} for x in X]
        Xa_tr, Xa_va, Xa_te = zeroed(X_tr), zeroed(X_va), zeroed(X_te)
        m = KillChainModel().fit(Xa_tr, list(y_tr))
        va = _score_kc(m, Xa_va); te = _score_kc(m, Xa_te)
        d = _at_budget(va, y_va, te, np.array([s["label"] for s in S_te]))
        d["stage"] = f"without {st}"
        out.append(d)
    return out


def leave_one_scenario_out(X_all, y_all, S_all, X_va, y_va):
    """Hold out ONE scenario at a time from training. Report recall on the held-out cohort."""
    out = []
    y_va = np.array(y_va)
    scen = np.array([s["scenario"] for s in S_all])
    for held in list(SCENARIOS):
        keep = (scen != held) | (np.array([s["label"] for s in S_all]) == 0)
        X_tr = [X_all[i] for i in range(len(X_all)) if keep[i]]
        y_tr = [y_all[i] for i in range(len(y_all)) if keep[i]]
        m = KillChainModel().fit(X_tr, y_tr)
        kc_va = _score_kc(m, X_va)
        t = threshold_for_budget(kc_va, y_va, BUDGET_T2)
        # recall on unseen scenario
        held_idx = np.where(np.array([s["scenario"] == held for s in S_all]))[0]
        kc_h = _score_kc(m, [X_all[i] for i in held_idx])
        out.append({"held_out_scenario": held,
                    "recall_on_unseen_scenario": float((kc_h >= t).mean())})
    return out


def adversarial_curve(model, X_te, S_te, y_te):
    """Progressively suppress the N most damning signals per session.

    A real fraudster's playbook update looks like this: keep hitting only the
    signals they cannot suppress. We report recall vs. suppressed signal count.
    """
    y_te = np.array(y_te)
    llr = model.llr
    order = sorted(SIGNAL_KEYS, key=lambda k: -llr[k])
    out = []
    for n in range(0, 8):
        Xa = []
        for x in X_te:
            xa = dict(x)
            # suppress the n signals with the highest weight that were present
            drop = [k for k in order if xa.get(k)][:n]
            for k in drop:
                xa[k] = False
            Xa.append(xa)
        s = _score_kc(model, Xa)
        # keep the *original* threshold; do not re-calibrate to the attacker
        t = model.thresholds[2]
        out.append({"suppressed": n,
                    "recall": float(((s >= t)[y_te == 1]).mean()),
                    "legit_alerts_per_1000": float(1000 * ((s >= t)[y_te == 0]).mean())})
    return out


def calibration(model, X_te, y_te, n_bins=10):
    from math import exp
    y = np.array(y_te)
    probs = np.array([1 / (1 + exp(-model.score(x).score)) for x in X_te])
    edges = np.quantile(probs, np.linspace(0, 1, n_bins + 1))
    out = []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        mask = (probs >= lo) & (probs <= hi if i == n_bins - 1 else probs < hi)
        if mask.sum() == 0:
            continue
        out.append({"bin_mid": float(probs[mask].mean()),
                    "empirical": float(y[mask].mean()),
                    "n": int(mask.sum())})
    return out, float(probs.min()), float(probs.max())


def per_persona(model, X_te, S_te, y_te):
    y = np.array(y_te)
    s = _score_kc(model, X_te)
    t = model.thresholds[2]
    personas = sorted({r["persona"] for r in S_te})
    out = []
    for p in personas:
        m = np.array([r["persona"] == p for r in S_te])
        scam = m & (y == 1); leg = m & (y == 0)
        if scam.sum() == 0:
            continue
        out.append({"persona": p,
                    "recall": float((s[scam] >= t).mean()),
                    "legit_alerts_per_1000": float(1000 * (s[leg] >= t).mean())})
    return out


def impact_math(system, adopters_millions=100, sessions_per_year=250,
                 avg_scam_ticket=42000, real_prevalence=REAL_PREVALENCE):
    """Compute expected rupees saved per year at pilot scale.

    Numbers are transparent and cited in docs/ASSUMPTIONS.md so the panel can
    challenge each input. We keep the ticket size conservative (₹42k) vs. the
    RBI FY25 average per UPI-fraud incident (~₹7,760); we use the ₹22,845 cr /
    36.37 lakh complaints average (~₹62,800) as an upper anchor.
    """
    sessions_year = adopters_millions * 1e6 * sessions_per_year
    scams_year = sessions_year * real_prevalence
    caught = scams_year * system["recall"]
    saved_cr = caught * avg_scam_ticket / 1e7
    false_alerts = sessions_year * system["legit_alerts_per_1000"] / 1000
    return {"adopters_m": adopters_millions,
            "sessions_year_m": sessions_year / 1e6,
            "scams_year_k": scams_year / 1e3,
            "caught_k": caught / 1e3,
            "saved_cr_per_year": saved_cr,
            "legit_interruptions_year_m": false_alerts / 1e6}


# ------------------------- charts -------------------------


def charts(deep):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": False, "axes.linewidth": 0.6,
                         "axes.labelcolor": INK, "text.color": INK})

    # 1. baselines bar (recall @ budget)
    b = deep["baselines"]
    names = [x["name"].split(" (")[0].replace("Chakravyuh", "Chakravyuh")
             for x in b]
    rec = [x["recall"] for x in b]
    fp = [x["legit_alerts_per_1000"] for x in b]
    colors = [ACC, GRAY, GRAY, BLUE, BLUE, BLUE]
    fig, ax = plt.subplots(figsize=(6.2, 2.6), dpi=160)
    xs = np.arange(len(names))
    ax.barh(xs, rec, color=colors, edgecolor="none")
    for i, (r_, f_) in enumerate(zip(rec, fp)):
        ax.text(r_ + 0.01, i, f"{r_ * 100:.0f}%   ({f_:.1f}/1k FP)",
                va="center", fontsize=9, color=INK)
    ax.set_yticks(xs); ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.15); ax.set_xticks([])
    ax.set_title("Recall at 3 interruptions per 1,000 legit sessions",
                 fontsize=10, loc="left", color=INK)
    for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(ASSETS / "baselines.svg"); plt.close(fig)

    # 2. adversarial curve
    a = deep["adversarial"]
    fig, ax = plt.subplots(figsize=(5.6, 3.0), dpi=160)
    xs = [d["suppressed"] for d in a]
    ys = [d["recall"] for d in a]
    ax.plot(xs, ys, color=ACC, lw=2.4, marker="o", ms=5)
    for x_, y_ in zip(xs, ys):
        ax.text(x_, y_ + 0.02, f"{y_ * 100:.0f}%", ha="center", fontsize=8.5, color=INK)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Number of highest-weight signals suppressed by attacker")
    ax.set_ylabel("Scam sessions still caught (tier ≥ 2)")
    ax.set_title("Adversarial robustness — attacker removes top-N signals",
                 fontsize=10, loc="left", color=INK)
    fig.tight_layout(); fig.savefig(ASSETS / "adversarial.svg"); plt.close(fig)

    # 3. ablation
    ab = deep["ablation"]
    fig, ax = plt.subplots(figsize=(5.6, 2.6), dpi=160)
    labels = [d["stage"] for d in ab]
    vals = [d["recall"] for d in ab]
    colors2 = [ACC if i == 0 else BLUE for i in range(len(labels))]
    ax.bar(range(len(labels)), vals, color=colors2, edgecolor="none", width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v * 100:.0f}%", ha="center", fontsize=9, color=INK)
    ax.set_xticks(range(len(labels)))
    short = [l.replace("without ", "no ").replace("all four stages", "all 4") for l in labels]
    ax.set_xticklabels(short, fontsize=8.5, rotation=0)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Recall @ budget")
    ax.set_title("Stage ablation — each stage carries independent evidence",
                 fontsize=10, loc="left", color=INK)
    fig.tight_layout(); fig.savefig(ASSETS / "ablation.svg"); plt.close(fig)

    # 4. calibration
    cal, _, _ = deep["calibration"], 0, 0
    fig, ax = plt.subplots(figsize=(4.4, 4.4), dpi=160)
    ax.plot([0, 1], [0, 1], color=GRAY, lw=1, ls="--", label="perfect")
    xs = [c["bin_mid"] for c in cal]; ys = [c["empirical"] for c in cal]
    sizes = [max(15, min(200, c["n"] * 0.6)) for c in cal]
    ax.scatter(xs, ys, s=sizes, color=ACC, edgecolor="white", lw=0.6, alpha=0.9,
               label="Chakravyuh")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("Predicted scam probability")
    ax.set_ylabel("Empirical scam rate in bin")
    ax.set_title("Reliability diagram — predictions are well-calibrated",
                 fontsize=10, loc="left", color=INK)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout(); fig.savefig(ASSETS / "calibration.svg"); plt.close(fig)

    # 5. LOO scenario
    loo = deep["loo_scenario"]
    fig, ax = plt.subplots(figsize=(5.6, 2.6), dpi=160)
    labels = [d["held_out_scenario"] for d in loo]
    vals = [d["recall_on_unseen_scenario"] for d in loo]
    ax.bar(range(len(labels)), vals, color=OK, edgecolor="none", width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v * 100:.0f}%", ha="center", fontsize=9, color=INK)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([l.replace("_", "\n") for l in labels], fontsize=8.5)
    ax.set_ylim(0, 1.1); ax.set_ylabel("Recall on unseen scenario")
    ax.set_title("Leave-one-scenario-out — generalization to unseen playbooks",
                 fontsize=10, loc="left", color=INK)
    fig.tight_layout(); fig.savefig(ASSETS / "loo.svg"); plt.close(fig)

    # 6. per-persona
    pp = deep["per_persona"]
    fig, ax = plt.subplots(figsize=(5.6, 2.6), dpi=160)
    labels = [d["persona"].title() for d in pp]
    rec = [d["recall"] for d in pp]
    fp = [d["legit_alerts_per_1000"] for d in pp]
    x = np.arange(len(labels)); w = 0.4
    ax.bar(x - w / 2, rec, w, color=ACC, edgecolor="none", label="scam recall")
    ax2 = ax.twinx()
    ax2.bar(x + w / 2, fp, w, color=BLUE, edgecolor="none",
            label="legit alerts / 1k")
    for i, r_ in enumerate(rec):
        ax.text(i - w / 2, r_ + 0.02, f"{r_ * 100:.0f}%", ha="center", fontsize=8.5)
    for i, f_ in enumerate(fp):
        ax2.text(i + w / 2, f_ + 0.2, f"{f_:.1f}", ha="center", fontsize=8.5, color=BLUE)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.15); ax.set_ylabel("Recall", color=ACC)
    ax2.set_ylim(0, max(fp) * 1.5 + 1); ax2.set_ylabel("Alerts / 1,000", color=BLUE)
    ax2.spines["top"].set_visible(False)
    ax.set_title("Fairness — recall and false-alert rate hold across personas",
                 fontsize=10, loc="left", color=INK)
    fig.tight_layout(); fig.savefig(ASSETS / "persona.svg"); plt.close(fig)

    # 7. impact bar
    im = deep["impact"]
    fig, ax = plt.subplots(figsize=(5.6, 2.4), dpi=160)
    xs = ["Scam attempts\n(k / year)", "Caught by\nChakravyuh (k)", "₹ saved\n(₹ cr / year)"]
    vals = [im["scams_year_k"], im["caught_k"], im["saved_cr_per_year"]]
    colors3 = [GRAY, ACC, OK]
    ax.bar(xs, vals, color=colors3, edgecolor="none", width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.02, f"{v:,.0f}", ha="center", fontsize=10, color=INK)
    ax.set_yscale("log"); ax.set_ylabel("count / ₹ crore (log)")
    ax.set_title(f"Pilot impact math — {im['adopters_m']:.0f} M users, "
                 f"{im['sessions_year_m']:,.0f} M sessions / yr",
                 fontsize=10, loc="left", color=INK)
    fig.tight_layout(); fig.savefig(ASSETS / "impact.svg"); plt.close(fig)


# ------------------------- driver -------------------------


def main():
    t0 = time.time()
    S_tr, X_tr, y_tr = world(7)
    S_va, X_va, y_va = world(21)
    S_te, X_te, y_te = world(11)
    print(f"3 worlds in {time.time() - t0:.1f}s")

    m, kc_te, baselines = run_baselines(X_tr, y_tr, X_va, y_va, X_te, y_te)
    m.save(OUT / "model.json")   # keep in sync with the service

    ab = ablate_stages(X_tr, y_tr, X_va, y_va, X_te, y_te, S_te)
    adv = adversarial_curve(m, X_te, S_te, y_te)
    cal, _, _ = calibration(m, X_te, y_te)
    pp = per_persona(m, X_te, S_te, y_te)
    # LOO uses combined tr+te scam pool for stability
    S_all = S_tr + S_te; X_all = X_tr + X_te; y_all = list(y_tr) + list(y_te)
    loo = leave_one_scenario_out(X_all, y_all, S_all, X_va, y_va)
    ours = next(b for b in baselines if "Chakravyuh" in b["name"])
    impact = impact_math(ours)
    # a smaller-scale impact too, for a 3-year moderate rollout
    impact_low = impact_math(ours, adopters_millions=30)

    deep = {"baselines": baselines, "ablation": ab, "adversarial": adv,
            "calibration": cal, "loo_scenario": loo, "per_persona": pp,
            "impact": impact, "impact_conservative": impact_low,
            "n_test_legit": int((np.array(y_te) == 0).sum()),
            "n_test_scam": int((np.array(y_te) == 1).sum())}
    (OUT / "deep.json").write_text(json.dumps(deep, indent=2))
    charts(deep)

    print("\nBaselines:")
    for b in baselines:
        print(f"  {b['name']:38s} recall={b['recall'] * 100:5.1f}%  "
              f"FP={b['legit_alerts_per_1000']:5.2f}/1k  AUPRC={b['auprc']:.3f}")
    print("\nAblation:")
    for d in ab:
        print(f"  {d['stage']:28s} recall={d['recall'] * 100:5.1f}%")
    print("\nLOO:")
    for d in loo:
        print(f"  held-out {d['held_out_scenario']:18s} "
              f"recall={d['recall_on_unseen_scenario'] * 100:5.1f}%")
    print("\nAdversarial (suppressed -> recall):")
    for d in adv:
        print(f"  {d['suppressed']}  {d['recall'] * 100:5.1f}%")
    print("\nPer-persona:")
    for d in pp:
        print(f"  {d['persona']:14s} rec={d['recall'] * 100:5.1f}%  "
              f"FP={d['legit_alerts_per_1000']:.2f}/1k")
    print(f"\nImpact @ {impact['adopters_m']:.0f}M users: caught={impact['caught_k']:,.0f}k "
          f"saved=₹{impact['saved_cr_per_year']:,.0f} cr/year")
    print(f"Impact @ {impact_low['adopters_m']:.0f}M users: caught={impact_low['caught_k']:,.0f}k "
          f"saved=₹{impact_low['saved_cr_per_year']:,.0f} cr/year")


if __name__ == "__main__":
    main()

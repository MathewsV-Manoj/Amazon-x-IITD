"""Offline evaluation on synthetic data.

Train on one synthetic world (seed 7), calibrate thresholds to an *alert budget*
on a validation world (seed 21), report on an unseen test world (seed 11) that
has its own mule graph. Writes results.json, model.json and charts.
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
from chakravyuh.signals import SIGNAL_KEYS  # noqa: E402
from chakravyuh.synth import SCENARIOS, featurize, generate  # noqa: E402

OUT = ROOT / "eval" / "out"
ASSETS = ROOT / "submission" / "assets"
BUDGET_T2 = 3.0     # max interruptive alerts (tier >= 2) per 1,000 legit sessions
BUDGET_T3 = 0.5     # max cooling-off holds (tier 3) per 1,000 legit sessions
BUDGET_T1 = 20.0    # silent watch-list entries per 1,000 legit sessions
REAL_PREVALENCE = 1 / 5000   # assumed scam share of *high-value P2P* sessions


def world(seed, n_legit=60000, n_scam=2400):
    S, _ = generate(n_legit=n_legit, n_scam=n_scam, seed=seed)
    X = [featurize(s) for s in S]
    return S, X, np.array([s["label"] for s in S])


def per_1000(mask_alert, y):
    return 1000.0 * mask_alert[y == 0].mean()


def threshold_for_budget(scores, y, budget, eligible=None):
    """Smallest threshold such that legit alerts/1000 <= budget."""
    elig = np.ones_like(scores, dtype=bool) if eligible is None else eligible
    legit = np.sort(scores[(y == 0) & elig])[::-1]
    k = int(budget / 1000.0 * (y == 0).sum())
    if k >= len(legit):
        return float(legit[-1]) - 1e-6 if len(legit) else -1e9
    return float(legit[k]) + 1e-6


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    S_tr, X_tr, y_tr = world(7)
    S_va, X_va, y_va = world(21)
    S_te, X_te, y_te = world(11)
    print(f"generated 3 worlds in {time.time() - t0:.1f}s")

    model = KillChainModel().fit(X_tr, list(y_tr))

    # ---- calibrate tier thresholds on validation to the alert budget ----
    dv = [model.score(x) for x in X_va]
    sv = np.array([d.score for d in dv])
    nact = np.array([len(d.active_stages) for d in dv])
    reg = np.array([bool(x["payee_registry_hit"]) for x in X_va])
    t1 = threshold_for_budget(sv, y_va, BUDGET_T1)
    t2 = threshold_for_budget(sv, y_va, BUDGET_T2, eligible=nact >= 2)
    t3 = threshold_for_budget(sv, y_va, BUDGET_T3, eligible=(nact >= 3) | ((nact >= 2) & reg))
    model.thresholds = {1: round(t1, 3), 2: round(max(t2, t1), 3), 3: round(max(t3, t2), 3)}
    model.save(OUT / "model.json")
    print("thresholds", model.thresholds)

    # ---- test ----
    t0 = time.perf_counter()
    dt = [model.score(x) for x in X_te]
    lat_us = (time.perf_counter() - t0) / len(X_te) * 1e6
    tiers = np.array([d.tier for d in dt])
    scores = np.array([d.score for d in dt])
    amounts = np.array([s["amount"] for s in S_te])
    scen = np.array([s["scenario"] for s in S_te])
    adapted = np.array([s["adapted"] for s in S_te])
    Xm = np.array([[float(x[k]) for k in SIGNAL_KEYS] for x in X_te])

    def summarize(alert, name):
        rec = alert[y_te == 1].mean()
        fp1000 = per_1000(alert, y_te)
        fpr = fp1000 / 1000
        prec = rec * REAL_PREVALENCE / (rec * REAL_PREVALENCE + fpr * (1 - REAL_PREVALENCE)) if rec > 0 else 0
        val = amounts[(y_te == 1) & alert].sum() / amounts[y_te == 1].sum()
        r = {"name": name, "recall": round(float(rec), 3), "value_recall": round(float(val), 3),
             "legit_alerts_per_1000": round(float(fp1000), 2),
             "precision_at_real_prevalence": round(float(prec), 3),
             "recall_standard": round(float(alert[(y_te == 1) & ~adapted].mean()), 3),
             "recall_adapted": round(float(alert[(y_te == 1) & adapted].mean()), 3),
             "by_scenario": {k: round(float(alert[(y_te == 1) & (scen == k)].mean()), 3) for k in SCENARIOS}}
        return r

    results = {"n_test_legit": int((y_te == 0).sum()), "n_test_scam": int((y_te == 1).sum()),
               "thresholds": model.thresholds, "latency_us_per_session": round(lat_us, 1),
               "budget": {"tier1": BUDGET_T1, "tier2": BUDGET_T2, "tier3": BUDGET_T3},
               "real_prevalence_assumed": REAL_PREVALENCE, "systems": []}

    ours_t2 = summarize(tiers >= 2, "Chakravyuh (tier>=2 interrupt)")
    ours_t3 = summarize(tiers >= 3, "Chakravyuh (tier 3 cooling-off hold)")
    ours_t1 = summarize(tiers >= 1, "Chakravyuh (tier>=1 silent watch)")

    b1 = np.array([x["first_time_payee"] and x["amount_high"] for x in X_te])
    b2 = np.array([x["remote_access"] or x["call_unknown_active"] or x["payee_mule_high"]
                   or x["collect_from_p2p"] for x in X_te])
    base1 = summarize(b1, "Rule: new payee + high amount")
    base2 = summarize(b2, "Rule: any single strong signal")

    # black-box ML baseline at the same alert budget (no stage gate, no explanation)
    from sklearn.ensemble import HistGradientBoostingClassifier
    Xtr = np.array([[float(x[k]) for k in SIGNAL_KEYS] for x in X_tr])
    Xva = np.array([[float(x[k]) for k in SIGNAL_KEYS] for x in X_va])
    gb = HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(Xtr, y_tr)
    tg = threshold_for_budget(gb.predict_proba(Xva)[:, 1], y_va, BUDGET_T2)
    pg = gb.predict_proba(Xm)[:, 1]
    base3 = summarize(pg >= tg, "Gradient boosting (black box, same budget)")

    results["systems"] = [ours_t1, ours_t2, ours_t3, base1, base2, base3]
    results["tier_distribution_legit_per_1000"] = {
        t: round(float(1000 * (tiers[y_te == 0] == t).mean()), 2) for t in range(4)}
    results["tier_distribution_scam"] = {
        t: round(float((tiers[y_te == 1] == t).mean()), 3) for t in range(4)}
    results["llr"] = model.llr
    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    for r in results["systems"]:
        print(f"{r['name']:45s} recall={r['recall']:.3f} value={r['value_recall']:.3f} "
              f"alerts/1k={r['legit_alerts_per_1000']:7.2f} prec@real={r['precision_at_real_prevalence']:.3f} "
              f"adapted={r['recall_adapted']:.3f}")
    print("latency us/session", round(lat_us, 1))

    charts(results, scores, y_te, model, gb, Xm, X_te)


def charts(results, scores, y, model, gb, Xm, X_te):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False})
    INK, MUTED, ACC, B1, B2 = "#1b2430", "#8a94a3", "#d9480f", "#4263eb", "#94a3b8"

    # 1) recall vs legit alerts per 1000 (operating curve)
    fig, ax = plt.subplots(figsize=(5.4, 3.0), dpi=150)
    legit = np.sort(scores[y == 0])[::-1]
    xs, ys = [], []
    for b in np.linspace(0.2, 40, 120):
        k = int(b / 1000 * len(legit))
        t = legit[min(k, len(legit) - 1)]
        xs.append(b)
        ys.append((scores[y == 1] > t).mean())
    ax.plot(xs, ys, color=ACC, lw=2.4, label="Chakravyuh fused score")
    pg = gb.predict_proba(Xm)[:, 1]
    lg = np.sort(pg[y == 0])[::-1]
    ys2 = []
    for b in xs:
        k = int(b / 1000 * len(lg))
        ys2.append((pg[y == 1] > lg[min(k, len(lg) - 1)]).mean())
    ax.plot(xs, ys2, color=B2, lw=1.8, ls="--", label="Black-box gradient boosting")
    for r, c, mk in [(results["systems"][3], B1, "s"), (results["systems"][4], INK, "^")]:
        ax.scatter([r["legit_alerts_per_1000"]], [r["recall"]], color=c, marker=mk, s=60, zorder=5,
                   label=r["name"])
    ax.axvline(3, color=MUTED, lw=1, ls=":")
    ax.text(3.4, 0.08, "alert budget\n3 / 1,000", color=MUTED, fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.2, 200)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Interruptions to genuine users per 1,000 payments (log)")
    ax.set_ylabel("Scam sessions caught")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(ASSETS / "curve.svg")
    plt.close(fig)

    # 2) per-scenario recall, tier>=2, standard vs adapted
    ours = results["systems"][1]
    fig, ax = plt.subplots(figsize=(5.4, 2.4), dpi=150)
    names = list(SCENARIOS)
    labels = ["Digital\narrest", "Remote-access\nKYC", "Investment /\ntask", "Collect\nrequest"]
    vals = [ours["by_scenario"][n] for n in names]
    ax.bar(range(4), vals, color=ACC, width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.0%}", ha="center", color=INK, fontsize=10)
    ax.set_xticks(range(4), labels)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Caught at tier ≥ 2")
    fig.tight_layout()
    fig.savefig(ASSETS / "scenarios.svg")
    plt.close(fig)


if __name__ == "__main__":
    main()

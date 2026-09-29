"""Restrained charts for the final deck. Every value comes from eval/out/final.json."""
from __future__ import annotations

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

FONTS = Path(__file__).resolve().parents[1] / "fonts"
for f in FONTS.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))

INK, MUTED, RULE, ORANGE, PAPER = "#111A2B", "#7A808A", "#CFCAC0", "#D9480F", "#F5F3EE"

plt.rcParams.update({
    "font.family": "IBM Plex Sans", "font.size": 9, "axes.edgecolor": MUTED,
    "axes.linewidth": 0.6, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "svg.fonttype": "path", "figure.facecolor": "none",
    "axes.facecolor": "none", "savefig.transparent": True,
})


def _svg(fig) -> str:
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    s = buf.getvalue()
    return s[s.index("<svg"):]


def operating_points(F) -> str:
    """Recall vs. interruptions per 1,000 legit sessions, with 95% CIs (zoomed to the budget region)."""
    c = F["chakravyuh"]; B = F["baselines"]
    fig, ax = plt.subplots(figsize=(5.8, 3.3))
    ax.axvline(3.0, color=RULE, lw=1, ls=(0, (3, 3)), zorder=0)
    ax.text(2.985, 0.905, "alert limit 3 / 1,000", color=MUTED, fontsize=7.5, ha="right", va="bottom", rotation=90)

    def pt(x, y, color, filled=True):
        ax.errorbar(x["mean"], y["mean"], xerr=[[x["mean"] - x["lo"]], [x["hi"] - x["mean"]]],
                    yerr=[[y["mean"] - y["lo"]], [y["hi"] - y["mean"]]], fmt="o", ms=5.5,
                    color=color, mfc=color if filled else "white", mec=color, elinewidth=0.9, capsize=0, zorder=3)

    def lab(x, y, text, tx, ty, color, weight="normal", ha="left"):
        ax.annotate(text, (x, y), xytext=(tx, ty), fontsize=8, color=color, ha=ha, va="center", fontweight=weight,
                    arrowprops=dict(arrowstyle="-", color=RULE, lw=0.7, shrinkA=0, shrinkB=4))

    pt(c["fp"], c["recall"], ORANGE)
    lab(c["fp"]["mean"], c["recall"]["mean"], "Chakravyuh", 2.62, 0.915, ORANGE, "semibold", "left")
    pt(c["fp_nogate"], c["recall_nogate"], MUTED, filled=False)
    lab(c["fp_nogate"]["mean"], c["recall_nogate"]["mean"], "without two-stage rule", 3.62, 0.935, MUTED)
    names = ["Logistic regression", "Gradient boosting", "XGBoost", "MLP"]
    for name in names:
        pt(B[name]["fp"], B[name]["recall"], INK)
    cx = sum(B[n]["fp"]["mean"] for n in names) / 4; cy = sum(B[n]["recall"]["mean"] for n in names) / 4
    lo = min(B[n]["recall"]["mean"] for n in names); hi = max(B[n]["recall"]["mean"] for n in names)
    lab(cx, cy + 0.004, f"standard classifiers (logistic, gradient boosting,\nXGBoost, MLP): {lo * 100:.1f}–{hi * 100:.1f}% recall",
        2.6, 0.99, INK)
    r = B["Rule: new payee + high amount"]
    ax.text(3.78, 0.905, f"not shown: “new payee + high amount” rule,\n{r['recall']['mean'] * 100:.0f}% recall at "
            f"{r['fp']['mean']:.1f} / 1,000", fontsize=7.5, color=MUTED, ha="right", va="bottom")
    ax.set_xlim(2.55, 3.8); ax.set_ylim(0.90, 1.0)
    ax.set_xlabel("Legitimate sessions interrupted per 1,000", fontsize=8.5)
    ax.set_ylabel("Scam sessions caught (recall)", fontsize=8.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.tick_params(labelsize=8)
    return _svg(fig)


def adversarial(F) -> str:
    a = F["adversarial"]
    fig, ax = plt.subplots(figsize=(2.9, 1.9))
    xs = [d["suppressed"] for d in a]; ys = [d["recall"] for d in a]
    ax.plot(xs, ys, color=ORANGE, lw=1.6, marker="o", ms=3.5)
    for x, y in zip(xs, ys):
        ax.text(x, y + 0.05, f"{y * 100:.0f}", ha="center", fontsize=7.5, color=INK)
    ax.set_ylim(0, 1.08); ax.set_xticks(xs)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("strongest emitted signals hidden", fontsize=7.5)
    ax.set_ylabel("recall", fontsize=7.5)
    ax.tick_params(labelsize=7)
    return _svg(fig)


def reliability(F) -> str:
    b = F["calibration"]["bins"]
    fig, ax = plt.subplots(figsize=(2.5, 2.3))
    ax.plot([0, 1], [0, 1], color=RULE, lw=1, ls=(0, (3, 3)))
    ax.plot([d["conf"] for d in b], [d["acc"] for d in b], color=ORANGE, lw=1.3, marker="o", ms=3)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("predicted probability", fontsize=7.5); ax.set_ylabel("observed scam rate", fontsize=7.5)
    ax.tick_params(labelsize=7)
    return _svg(fig)


def per_world(F) -> str:
    r = F["chakravyuh"]["per_world_recall"]; c = F["chakravyuh"]["recall"]
    fig, ax = plt.subplots(figsize=(2.9, 1.7))
    ax.axhspan(c["lo"], c["hi"], color=ORANGE, alpha=0.12, lw=0)
    ax.axhline(c["mean"], color=ORANGE, lw=1)
    ax.plot(range(1, len(r) + 1), r, "o", color=INK, ms=3.5)
    ax.set_ylim(0.88, 0.96); ax.set_xticks(range(1, len(r) + 1))
    ax.set_xticklabels([str(101 + i) for i in range(len(r))], fontsize=6.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("test world (seed)", fontsize=7.5); ax.tick_params(labelsize=7)
    return _svg(fig)

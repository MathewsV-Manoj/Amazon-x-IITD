"""Payee-side mule detection on a (synthetic) 7-day payment graph.

Mule accounts in APP (authorised push payment) fraud show a distinctive shape:
many *unrelated* first-time senders (fan-in), personal (P2P) VPAs rather than
verified merchants, young accounts, and fast pass-through (money leaves within
hours). Legit high fan-in accounts (kirana stores, tuition teachers) are
usually P2M-verified, older, and keep balances.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import networkx as nx
import numpy as np


@dataclass
class PayeeProfile:
    vpa: str
    kind: str                 # person | merchant | mule | cashout
    age_days: int
    is_merchant_verified: bool
    registry_hit: bool
    distinct_senders_24h: int = 0
    first_time_sender_ratio: float = 0.0
    passthrough_ratio: float = 0.0
    mule_score: float = 0.0


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def mule_score(p: PayeeProfile) -> float:
    """Transparent scorecard (log-odds). Weights hand-set, validated on synthetic data;
    in production they are re-fit on bank-confirmed mule labels."""
    z = -5.0
    z += 1.1 * math.log1p(p.distinct_senders_24h)
    z += 2.0 * p.first_time_sender_ratio
    z += 2.5 * p.passthrough_ratio * min(1.0, p.distinct_senders_24h / 3)
    z += 1.2 if p.age_days < 30 else 0.0
    z -= 2.5 if p.is_merchant_verified else 0.0
    return _sigmoid(z)


def build_graph(rng: np.random.Generator, n_people=4000, n_merchants=400, n_mules=120,
                n_cashout=15):
    """Generate a 7-day payment graph and return (graph, {vpa: PayeeProfile})."""
    G = nx.MultiDiGraph()
    profiles: dict[str, PayeeProfile] = {}

    def add(vpa, kind, age, merchant, registry=False):
        profiles[vpa] = PayeeProfile(vpa, kind, age, merchant, registry)
        G.add_node(vpa, kind=kind)

    for i in range(n_people):
        # ~6% of genuine people have young accounts (students, new jobs, new SIMs)
        age = int(rng.integers(1, 30)) if rng.random() < 0.06 else int(rng.integers(30, 4000))
        add(f"p{i}@okbank", "person", age, False)
    for i in range(n_merchants):
        add(f"shop{i}@ybl", "merchant", int(rng.integers(90, 3000)), True)
    for i in range(n_cashout):
        add(f"cx{i}@paytm", "cashout", int(rng.integers(5, 200)), False)
    for i in range(n_mules):
        # a quarter of mules are "aged" (rented old accounts) -> adversarial adaptation
        aged = rng.random() < 0.25
        age = int(rng.integers(120, 1500)) if aged else int(rng.integers(3, 45))
        add(f"m{i}@okaxis", "mule", age, False, registry=bool(rng.random() < 0.15))

    people = [v for v, p in profiles.items() if p.kind == "person"]
    merchants = [v for v, p in profiles.items() if p.kind == "merchant"]
    mules = [v for v, p in profiles.items() if p.kind == "mule"]
    cashouts = [v for v, p in profiles.items() if p.kind == "cashout"]

    # Background legit traffic: people pay their own small circle + merchants.
    circles = {v: list(rng.choice(people, size=8, replace=False)) for v in people}
    for v in people:
        for _ in range(int(rng.poisson(6))):
            if rng.random() < 0.6:
                dst = merchants[int(rng.integers(len(merchants)))]
                first = rng.random() < 0.2
            else:
                dst = circles[v][int(rng.integers(8))]
                first = rng.random() < 0.05
            amt = float(np.exp(rng.normal(6.0, 1.0)))
            G.add_edge(v, dst, amount=amt, first_time=first, hours_ago=float(rng.uniform(0, 168)))

    # A few legit people with high fan-in (tuition teacher, society treasurer).
    for v in rng.choice(people, size=40, replace=False):
        for _ in range(int(rng.integers(10, 30))):
            src = people[int(rng.integers(len(people)))]
            G.add_edge(src, v, amount=float(np.exp(rng.normal(7.5, .5))), first_time=bool(rng.random() < .3),
                       hours_ago=float(rng.uniform(0, 24)))

    # Mule traffic: many unrelated victims -> mule -> fast forward to cash-out.
    for m in mules:
        aged = profiles[m].age_days >= 120
        # aged / rented mules are used sparingly and hold funds longer to look normal
        n_victims = int(rng.integers(1, 6)) if aged else int(rng.integers(2, 25))
        total = 0.0
        for _ in range(n_victims):
            src = people[int(rng.integers(len(people)))]
            amt = float(np.exp(rng.normal(10.5, 1.0)))
            total += amt
            G.add_edge(src, m, amount=amt, first_time=True, hours_ago=float(rng.uniform(0, 24)))
        out = total * (float(rng.uniform(0.1, 0.8)) if aged else float(rng.uniform(0.6, 0.98)))
        G.add_edge(m, cashouts[int(rng.integers(len(cashouts)))], amount=out, first_time=False,
                   hours_ago=float(rng.uniform(0, 12)))

    compute_features(G, profiles)
    return G, profiles


def compute_features(G: nx.MultiDiGraph, profiles: dict[str, PayeeProfile]) -> None:
    for v, p in profiles.items():
        ins = [d for _, _, d in G.in_edges(v, data=True) if d["hours_ago"] <= 24]
        outs = [d for _, _, d in G.out_edges(v, data=True) if d["hours_ago"] <= 24]
        senders = {u for u, _, d in G.in_edges(v, data=True) if d["hours_ago"] <= 24}
        p.distinct_senders_24h = len(senders)
        p.first_time_sender_ratio = (sum(d["first_time"] for d in ins) / len(ins)) if ins else 0.0
        in_amt = sum(d["amount"] for d in ins)
        out_amt = sum(d["amount"] for d in outs)
        p.passthrough_ratio = min(1.0, out_amt / in_amt) if in_amt > 0 else 0.0
        p.mule_score = mule_score(p)

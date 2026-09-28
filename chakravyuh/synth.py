"""Synthetic payment-session generator.

Produces legitimate sessions (with realistic confounders: paying a plumber while
on a call with him, rent day, ignoring a scam SMS) and four India-specific scam
workflows. ~25% of scam sessions are "adapted": the fraudster deliberately
suppresses a signal (asks the victim to hang up before paying, uses an aged mule,
splits the amount) so that robustness can be measured.

Every number here is an assumption, documented in docs/ASSUMPTIONS.md, and
is meant to be replaced by partner-bank calibration data in the pilot.
"""
from __future__ import annotations

import numpy as np

from .mule_graph import PayeeProfile, build_graph

SCENARIOS = {
    "digital_arrest": "Digital arrest: fake police / CBI / customs officer on a video call",
    "remote_access_kyc": "Fake KYC / refund: victim installs a screen-share or APK",
    "investment_task": "Investment / part-time task scam with bait 'profits'",
    "collect_request": "Marketplace collect-request / QR 'receive money' scam",
}

PERSONAS = ("student", "professional", "senior", "shopkeeper")


def _b(rng, p) -> bool:
    return bool(rng.random() < p)


def _legit_session(rng, persona, payees_known, payees_new, merchants):
    senior = persona == "senior"
    call_active = _b(rng, 0.10 if senior else 0.07)
    call_unknown = call_active and _b(rng, 0.35)          # plumber, delivery, landlord
    dur = float(rng.lognormal(1.2, 1.0)) if call_active else 0.0
    first = _b(rng, 0.15)
    z = float(rng.normal(0, 1))
    if _b(rng, 0.04):                                      # rent, gadget, fees, hospital
        z = float(rng.uniform(2.0, 4.5))
    if first:
        payee = payees_new[int(rng.integers(len(payees_new)))]
    elif _b(rng, 0.55):
        payee = merchants[int(rng.integers(len(merchants)))]
    else:
        payee = payees_known[int(rng.integers(len(payees_known)))]
    return dict(
        call_active=call_active, call_unknown=call_unknown, call_minutes=dur,
        video_call=_b(rng, 0.015), sms_scam_flag=_b(rng, 0.08),
        bait_credits_7d=int(rng.random() < 0.01),
        remote_access=_b(rng, 0.003), sideload_24h=_b(rng, 0.01),
        accessibility_overlay=_b(rng, 0.03), otp_read_in_call=_b(rng, 0.004),
        first_time_payee=first, amount_z=z,
        balance_drain=float(rng.beta(1.2, 6)) if not _b(rng, 0.02) else float(rng.uniform(.7, 1)),
        payments_new_60m=int(rng.poisson(0.15)), fd_broken_24h=_b(rng, 0.002),
        vpa_typed=_b(rng, 0.12), collect_request=_b(rng, 0.04), collect_from_p2p=_b(rng, 0.004),
        payee=payee,
    )


def _scam_session(rng, scenario, mules, adapted):
    mule = mules[int(rng.integers(len(mules)))]
    s = dict(call_active=False, call_unknown=False, call_minutes=0.0, video_call=False,
             sms_scam_flag=_b(rng, 0.2), bait_credits_7d=0, remote_access=False,
             sideload_24h=False, accessibility_overlay=_b(rng, 0.03), otp_read_in_call=False,
             first_time_payee=_b(rng, 0.9), amount_z=float(rng.uniform(1.5, 5)),
             balance_drain=float(rng.uniform(.3, 1)), payments_new_60m=int(rng.poisson(0.5)),
             fd_broken_24h=False, vpa_typed=_b(rng, 0.6), collect_request=False,
             collect_from_p2p=False, payee=mule)
    if scenario == "digital_arrest":
        s.update(call_active=_b(rng, 0.8), video_call=_b(rng, 0.6), amount_z=float(rng.uniform(2.5, 6.5)),
                 balance_drain=float(rng.uniform(.5, 1)), payments_new_60m=int(rng.poisson(1.2)),
                 fd_broken_24h=_b(rng, 0.35), vpa_typed=_b(rng, 0.85), first_time_payee=_b(rng, 0.95))
        s["call_unknown"] = s["call_active"] and _b(rng, 0.95)
        s["call_minutes"] = float(rng.uniform(25, 240)) if s["call_active"] else 0.0
    elif scenario == "remote_access_kyc":
        s.update(call_active=_b(rng, 0.65), remote_access=_b(rng, 0.7), sideload_24h=_b(rng, 0.55),
                 accessibility_overlay=_b(rng, 0.5), sms_scam_flag=_b(rng, 0.7),
                 amount_z=float(rng.uniform(1, 4.5)), payments_new_60m=int(rng.poisson(0.8)))
        s["call_unknown"] = s["call_active"] and _b(rng, 0.95)
        s["call_minutes"] = float(rng.uniform(5, 45)) if s["call_active"] else 0.0
        s["otp_read_in_call"] = s["call_active"] and _b(rng, 0.5)
    elif scenario == "investment_task":
        s.update(bait_credits_7d=int(rng.integers(1, 5)) if _b(rng, 0.65) else 0,
                 sideload_24h=_b(rng, 0.12), amount_z=float(rng.uniform(0.8, 4)),
                 balance_drain=float(rng.uniform(.2, .9)), first_time_payee=_b(rng, 0.75),
                 sms_scam_flag=_b(rng, 0.35), vpa_typed=_b(rng, 0.7))
    elif scenario == "collect_request":
        s.update(collect_request=True, collect_from_p2p=_b(rng, 0.9), amount_z=float(rng.uniform(-0.5, 2.5)),
                 balance_drain=float(rng.beta(2, 5)), call_active=_b(rng, 0.3), vpa_typed=False,
                 first_time_payee=_b(rng, 0.97), payments_new_60m=int(rng.poisson(0.4)))
        s["call_unknown"] = s["call_active"] and _b(rng, 0.9)
        s["call_minutes"] = float(rng.uniform(1, 10)) if s["call_active"] else 0.0

    if adapted:
        # Fraudster playbook updates observed in the wild: hang up before paying,
        # split into smaller amounts, avoid screen-share apps, use rented aged accounts.
        s["call_active"] = s["call_unknown"] = False
        s["call_minutes"] = 0.0
        s["video_call"] = False
        s["amount_z"] = float(min(s["amount_z"], rng.uniform(0.5, 2.2)))
        s["remote_access"] = False
        s["payments_new_60m"] = 0
    return s


def generate(n_legit=60000, n_scam=2400, adapted_frac=0.25, seed=7):
    """Return (sessions, payee_profiles). Each session has label 0/1 and scenario."""
    rng = np.random.default_rng(seed)
    _, profiles = build_graph(rng)
    people = [p for p in profiles.values() if p.kind == "person"]
    known = [p for p in people if p.age_days >= 365]
    new = people  # includes young accounts (students, new SIMs)
    merchants = [p for p in profiles.values() if p.kind == "merchant"]
    mules = [p for p in profiles.values() if p.kind == "mule"]

    sessions = []
    for i in range(n_legit):
        persona = PERSONAS[int(rng.integers(len(PERSONAS)))]
        s = _legit_session(rng, persona, known, new, merchants)
        s.update(id=f"L{i}", label=0, scenario="legit", persona=persona, adapted=False)
        sessions.append(s)
    names = list(SCENARIOS)
    weights = np.array([0.30, 0.30, 0.25, 0.15])
    for i in range(n_scam):
        sc = names[int(rng.choice(len(names), p=weights))]
        adapted = _b(rng, adapted_frac)
        s = _scam_session(rng, sc, mules, adapted)
        s.update(id=f"S{i}", label=1, scenario=sc,
                 persona=("senior" if _b(rng, 0.4) else PERSONAS[int(rng.integers(4))]), adapted=adapted)
        # amount in rupees from persona baseline for display / value-weighted metrics
        sessions.append(s)
    for s in sessions:
        base = {"student": 400, "professional": 1500, "senior": 1200, "shopkeeper": 2500}[s["persona"]]
        s["amount"] = round(float(base * np.exp(0.9 * max(s["amount_z"], -2)) * rng.uniform(.8, 1.2)), -1)
    order = rng.permutation(len(sessions))
    return [sessions[i] for i in order], profiles


def featurize(s: dict) -> dict:
    """Raw session -> binary evidence (the only thing the scoring engine sees)."""
    p: PayeeProfile = s["payee"]
    return {
        "call_unknown_active": s["call_unknown"],
        "call_long": s["call_active"] and s["call_minutes"] >= 20,
        "video_call": s["video_call"],
        "sms_scam_flag": s["sms_scam_flag"],
        "bait_credit_7d": s["bait_credits_7d"] > 0,
        "remote_access": s["remote_access"],
        "sideload_24h": s["sideload_24h"],
        "accessibility_overlay": s["accessibility_overlay"],
        "otp_read_in_call": s["otp_read_in_call"],
        "first_time_payee": s["first_time_payee"],
        "amount_high": s["amount_z"] >= 2.0,
        "amount_very_high": s["amount_z"] >= 3.1,
        "balance_drain": s["balance_drain"] >= 0.7,
        "staircase": s["payments_new_60m"] >= 2,
        "fd_broken_24h": s["fd_broken_24h"],
        "vpa_typed": s["vpa_typed"],
        "collect_from_p2p": s["collect_from_p2p"],
        "payee_mule_high": p.mule_score >= 0.5,
        "payee_new_account": p.age_days < 30,
        "payee_registry_hit": p.registry_hit,
    }

"""Signal catalogue.

Every signal is a *derived* value computed on-device (bank app SDK) or bank-side.
Raw call audio, message text, contacts and screen contents never leave the phone:
only the booleans / buckets below do. Each signal belongs to one kill-chain stage.
"""
from dataclasses import dataclass

STAGES = ("contact", "control", "extraction", "cashout")

STAGE_LABELS = {
    "contact": "Contact & pretext",
    "control": "Control & isolation",
    "extraction": "Money extraction",
    "cashout": "Mule / cash-out",
}


@dataclass(frozen=True)
class Signal:
    key: str
    stage: str
    source: str          # "device" | "bank" | "network"
    why: str             # plain-language explanation shown to users/analysts
    not_collected: str   # what we deliberately do NOT collect for this signal


SIGNALS = [
    Signal("call_unknown_active", "contact", "device",
           "You are on a call with a number not in your contacts while paying",
           "No call audio, no call content, no contact list upload"),
    Signal("call_long", "contact", "device",
           "That call has lasted more than 20 minutes",
           "Only a duration bucket leaves the phone"),
    Signal("video_call", "contact", "device",
           "A video/VoIP call is active (common in 'digital arrest' scams)",
           "App name is not sent, only the in-communication audio mode"),
    Signal("sms_scam_flag", "contact", "device",
           "A message received in the last 24h matches a known scam lure (KYC, parcel, electricity)",
           "Message text is classified on-device and never uploaded"),
    Signal("bait_credit_7d", "contact", "bank",
           "Small 'profit' credits from unknown senders in the last 7 days",
           "Only a count, no counter-party identity shown to the user"),
    Signal("remote_access", "control", "device",
           "A screen-sharing / remote-control app is running",
           "Screen contents are never captured"),
    Signal("sideload_24h", "control", "device",
           "An app was installed from outside the Play Store in the last 24h",
           "Only a boolean; app inventory is not uploaded"),
    Signal("accessibility_overlay", "control", "device",
           "A non-system app can read your screen and draw over the payment app",
           "Only a boolean"),
    Signal("otp_read_in_call", "control", "device",
           "An OTP was opened while the unknown call was active",
           "OTP value never read by us"),
    Signal("first_time_payee", "extraction", "bank",
           "You have never paid this account before", ""),
    Signal("amount_high", "extraction", "bank",
           "Amount is far above your usual payments", ""),
    Signal("amount_very_high", "extraction", "bank",
           "Amount is extremely high for you (top 0.1% of your history)", ""),
    Signal("balance_drain", "extraction", "bank",
           "This payment empties more than 70% of your balance", ""),
    Signal("staircase", "extraction", "bank",
           "Several payments to new accounts in the last 60 minutes", ""),
    Signal("fd_broken_24h", "extraction", "bank",
           "A fixed deposit was broken / loan taken in the last 24h", ""),
    Signal("vpa_typed", "extraction", "device",
           "Payee was typed or pasted instead of scanned or picked from contacts", ""),
    Signal("collect_from_p2p", "extraction", "network",
           "This is a 'collect' request from an individual (entering PIN SENDS money)", ""),
    Signal("payee_mule_high", "cashout", "network",
           "The receiving account behaves like a mule account (many unrelated senders, money moved out fast)", ""),
    Signal("payee_new_account", "cashout", "network",
           "The receiving account was opened less than 30 days ago", ""),
    Signal("payee_registry_hit", "cashout", "network",
           "The receiving account is on the I4C / bank suspect registry", ""),
]

SIGNAL_BY_KEY = {s.key: s for s in SIGNALS}
SIGNAL_KEYS = [s.key for s in SIGNALS]

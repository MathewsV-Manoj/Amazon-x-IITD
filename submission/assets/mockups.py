"""Render mobile-UI mockup SVGs for each intervention tier / playbook.

Output: submission/assets/mockup_*.svg
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent

# Common phone frame ---------------------------------------------------------
W, H = 300, 620
PHONE = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter, DejaVuSans, sans-serif">
  <defs>
    <linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a1f28"/>
      <stop offset="1" stop-color="#0b0f16"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="34" ry="34" fill="url(#bezel)"/>
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="28" ry="28" fill="#ffffff"/>
  <rect x="{W / 2 - 45}" y="10" width="90" height="18" rx="9" fill="#0b0f16"/>
"""

FOOT = "</svg>"


def status_bar(y=40):
    return (f'<text x="24" y="{y}" font-size="11" fill="#3b4453" font-weight="600">9:41</text>'
            f'<text x="{W - 24}" y="{y}" text-anchor="end" font-size="11" fill="#3b4453">'
            f'●●●○ · UPI</text>')


def top_pill(text, bg, fg, y=68):
    return (f'<rect x="24" y="{y - 14}" width="120" height="20" rx="10" fill="{bg}"/>'
            f'<text x="84" y="{y}" text-anchor="middle" font-size="10.5" '
            f'fill="{fg}" font-weight="700">{text}</text>')


def render_tier3():
    """Digital-arrest tier-3 cooling-off hold."""
    s = PHONE
    s += status_bar()
    s += top_pill("TIER 3  ·  HOLD 30 MIN", "#8a1c1c", "#ffffff")
    s += """
  <!-- headline -->
  <text x="24" y="112" font-size="20" font-weight="800" fill="#0d1420">Wait — this looks</text>
  <text x="24" y="136" font-size="20" font-weight="800" fill="#0d1420">like a scam.</text>
  <text x="24" y="170" font-size="12" fill="#5a6473">Real police, CBI or RBI officials</text>
  <text x="24" y="187" font-size="12" fill="#5a6473">never demand payment on a call.</text>

  <!-- payment card -->
  <rect x="20" y="210" width="260" height="90" rx="12" fill="#f6f7f9" stroke="#e4e7ec"/>
  <text x="34" y="232" font-size="10" fill="#5a6473" letter-spacing="1">TO</text>
  <text x="34" y="252" font-size="14" font-weight="700" fill="#0d1420">arjun.k9214@ybl</text>
  <text x="34" y="270" font-size="10" fill="#8a1c1c" font-weight="600">● account opened 8 days ago</text>
  <text x="266" y="252" text-anchor="end" font-size="20" font-weight="800" fill="#0d1420">₹2,50,000</text>
  <text x="266" y="270" text-anchor="end" font-size="10" fill="#8a1c1c">FD broken 24h ago</text>

  <!-- kill-chain strip -->
  <text x="24" y="326" font-size="10" fill="#5a6473" letter-spacing="1">WHY WE STOPPED THIS</text>
  """
    # kill-chain 4 boxes
    labels = [("Video call\n> 60 min", True), ("Screen-share\napp active", False),
              ("FD broken +\nfirst-time payee", True), ("Payee\nmule-like", True)]
    for i, (lab, on) in enumerate(labels):
        x = 24 + i * 65
        bg = "#fbe9de" if on else "#eef1f5"
        fg = "#d9480f" if on else "#8a94a3"
        s += f'<rect x="{x}" y="336" width="55" height="60" rx="8" fill="{bg}"/>'
        for j, line in enumerate(lab.split("\n")):
            s += (f'<text x="{x + 27}" y="{362 + j * 12}" text-anchor="middle" '
                  f'font-size="9" font-weight="700" fill="{fg}">{line}</text>')
    s += """
  <!-- CTA row -->
  <rect x="20" y="416" width="260" height="46" rx="10" fill="#d9480f"/>
  <text x="150" y="444" text-anchor="middle" font-size="14"
        font-weight="700" fill="#ffffff">Speak to a bank agent now</text>
  <rect x="20" y="470" width="260" height="42" rx="10" fill="#ffffff" stroke="#e4e7ec"/>
  <text x="150" y="496" text-anchor="middle" font-size="12.5" font-weight="600"
        fill="#0d1420">I understand — release in 30 min</text>

  <!-- footer receipt id -->
  <text x="24" y="540" font-size="9.5" fill="#8a94a3">Receipt · 8723987bc76393cd</text>
  <text x="24" y="555" font-size="9.5" fill="#8a94a3">Signed with your bank's audit key</text>
  <circle cx="{W - 34}" cy="548" r="8" fill="#e6f2ec"/>
  <text x="{W - 34}" y="551.5" text-anchor="middle" font-size="10" font-weight="800"
        fill="#116a4c">✓</text>

  <!-- home indicator -->
  <rect x="{W / 2 - 50}" y="{H - 22}" width="100" height="4" rx="2" fill="#0b0f16"/>
"""
    (ASSETS / "mockup_tier3.svg").write_text(s.replace("{W}", str(W)).replace(
        "{W / 2 - 50}", str(W / 2 - 50)).replace("{H - 22}", str(H - 22))
        .replace("{W - 34}", str(W - 34)) + FOOT)


def render_tier2():
    """Remote-access KYC tier-2 interrupt with 2 safety questions."""
    s = PHONE
    s += status_bar()
    s += top_pill("TIER 2  ·  INTERRUPT", "#a05a00", "#ffffff")
    s += """
  <text x="24" y="112" font-size="20" font-weight="800" fill="#0d1420">A remote-access app</text>
  <text x="24" y="136" font-size="20" font-weight="800" fill="#0d1420">is on your phone.</text>
  <text x="24" y="170" font-size="12" fill="#5a6473">If you were told to install it for</text>
  <text x="24" y="187" font-size="12" fill="#5a6473">KYC or a refund, the caller can see</text>
  <text x="24" y="204" font-size="12" fill="#5a6473">everything you type.</text>

  <!-- payment card -->
  <rect x="20" y="228" width="260" height="66" rx="12" fill="#f6f7f9" stroke="#e4e7ec"/>
  <text x="34" y="252" font-size="14" font-weight="700" fill="#0d1420">Pay ₹15,000</text>
  <text x="34" y="272" font-size="11" fill="#5a6473">to jyoti-kyc@axl (first-time payee)</text>

  <!-- safety questions -->
  <text x="24" y="322" font-size="10" fill="#5a6473" letter-spacing="1">TWO QUICK QUESTIONS</text>
  <rect x="20" y="336" width="260" height="60" rx="10" fill="#ffffff" stroke="#e4e7ec"/>
  <text x="34" y="357" font-size="12" font-weight="700" fill="#0d1420">Did anyone ask you to install</text>
  <text x="34" y="374" font-size="12" font-weight="700" fill="#0d1420">this app just now?</text>
  <circle cx="240" cy="370" r="8" fill="#eef1f5"/>
  <text x="248" y="373" font-size="11" fill="#5a6473">Yes / No</text>

  <rect x="20" y="406" width="260" height="60" rx="10" fill="#ffffff" stroke="#e4e7ec"/>
  <text x="34" y="427" font-size="12" font-weight="700" fill="#0d1420">Do you know jyoti-kyc@axl</text>
  <text x="34" y="444" font-size="12" font-weight="700" fill="#0d1420">personally?</text>
  <circle cx="240" cy="440" r="8" fill="#eef1f5"/>
  <text x="248" y="443" font-size="11" fill="#5a6473">Yes / No</text>

  <rect x="20" y="486" width="260" height="42" rx="10" fill="#0d1420"/>
  <text x="150" y="512" text-anchor="middle" font-size="12.5" font-weight="700"
        fill="#ffffff">Continue only if you're sure</text>

  <text x="24" y="552" font-size="9.5" fill="#8a94a3">Receipt · c48a10bf62d18a11</text>
  <rect x="{W / 2 - 50}" y="{H - 22}" width="100" height="4" rx="2" fill="#0b0f16"/>
"""
    (ASSETS / "mockup_tier2.svg").write_text(s.replace("{W}", str(W)).replace(
        "{W / 2 - 50}", str(W / 2 - 50)).replace("{H - 22}", str(H - 22)) + FOOT)


def render_tier1():
    """Investment-task tier-1 silent nudge (top banner)."""
    s = PHONE
    s += status_bar()
    s += """
  <!-- top banner -->
  <rect x="16" y="70" width="{W-32}" height="60" rx="10" fill="#fff6ef" stroke="#f28c4f" stroke-width="1"/>
  <circle cx="42" cy="100" r="12" fill="#d9480f"/>
  <text x="42" y="104" text-anchor="middle" font-size="14" font-weight="800" fill="#ffffff">!</text>
  <text x="62" y="94" font-size="12" font-weight="700" fill="#0d1420">Task-scam pattern nearby</text>
  <text x="62" y="110" font-size="10.5" fill="#5a6473">Small profits, big ask — check before</text>
  <text x="62" y="123" font-size="10.5" fill="#5a6473">investing. Tap for a 30-sec guide.</text>

  <text x="24" y="160" font-size="11" fill="#5a6473" letter-spacing="1">SEND MONEY</text>

  <rect x="20" y="176" width="260" height="70" rx="12" fill="#f6f7f9" stroke="#e4e7ec"/>
  <text x="34" y="200" font-size="14" font-weight="700" fill="#0d1420">crypto-earn@ptsbi</text>
  <text x="34" y="218" font-size="11" fill="#5a6473">First-time payee · seen in group chat</text>
  <text x="266" y="220" text-anchor="end" font-size="20" font-weight="800" fill="#0d1420">₹60,000</text>

  <text x="24" y="272" font-size="11" fill="#5a6473" letter-spacing="1">RECENT SMALL CREDITS FROM UNKNOWN SENDERS</text>
  <rect x="20" y="288" width="260" height="24" rx="6" fill="#eef1f5"/>
  <text x="34" y="304" font-size="10.5" fill="#5a6473">+ ₹150  · Sep 24 · unknown UPI</text>
  <rect x="20" y="316" width="260" height="24" rx="6" fill="#eef1f5"/>
  <text x="34" y="332" font-size="10.5" fill="#5a6473">+ ₹410  · Sep 25 · unknown UPI</text>
  <rect x="20" y="344" width="260" height="24" rx="6" fill="#eef1f5"/>
  <text x="34" y="360" font-size="10.5" fill="#5a6473">+ ₹280  · Sep 26 · unknown UPI</text>

  <rect x="20" y="390" width="260" height="42" rx="10" fill="#d9480f"/>
  <text x="150" y="416" text-anchor="middle" font-size="13" font-weight="700"
        fill="#ffffff">Show me the scam pattern</text>
  <rect x="20" y="442" width="260" height="42" rx="10" fill="#ffffff" stroke="#e4e7ec"/>
  <text x="150" y="468" text-anchor="middle" font-size="12.5" font-weight="600"
        fill="#0d1420">Proceed with ₹60,000 payment</text>

  <text x="24" y="518" font-size="9.5" fill="#8a94a3">Silent watch entry · shared with your bank</text>
  <rect x="{W / 2 - 50}" y="{H - 22}" width="100" height="4" rx="2" fill="#0b0f16"/>
"""
    out = s.replace("{W-32}", str(W - 32)).replace("{W}", str(W))\
        .replace("{W / 2 - 50}", str(W / 2 - 50)).replace("{H - 22}", str(H - 22))
    (ASSETS / "mockup_tier1.svg").write_text(out + FOOT)


def render_agent_desk():
    """Agent-desk console mockup — for architecture page 2."""
    w, h = 640, 380
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Inter, DejaVuSans, sans-serif">'
    s += f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="#0d1420"/>'
    s += f'<rect x="0" y="0" width="{w}" height="34" fill="#151b23"/>'
    s += '<circle cx="18" cy="17" r="6" fill="#8a1c1c"/>'
    s += '<text x="34" y="21" font-size="12" fill="#e7ecf2">Chakravyuh · Agent desk console</text>'
    s += '<text x="620" y="21" text-anchor="end" font-size="11" fill="#9aa5b3">agent · sunita.r@bank</text>'
    # header
    s += '<text x="20" y="66" font-size="14" font-weight="700" fill="#ffffff">Tier-3 hold · 8723987bc76393cd</text>'
    s += '<rect x="410" y="52" width="90" height="22" rx="11" fill="#8a1c1c"/>'
    s += '<text x="455" y="67" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff">HOLD 27:14</text>'
    s += '<rect x="510" y="52" width="110" height="22" rx="11" fill="#12805c"/>'
    s += '<text x="565" y="67" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff">DUAL-AUTH RELEASE</text>'
    # user card
    s += '<rect x="20" y="88" width="290" height="90" rx="8" fill="#151b23"/>'
    s += '<text x="34" y="112" font-size="11" fill="#9aa5b3">USER</text>'
    s += '<text x="34" y="132" font-size="13" font-weight="700" fill="#ffffff">••• 4082  · KOCHI · sr. citizen</text>'
    s += '<text x="34" y="152" font-size="11" fill="#9aa5b3">Amount ₹2,50,000  · FD broken 24 h ago</text>'
    s += '<text x="34" y="169" font-size="11" fill="#9aa5b3">Payee arjun.k9214@ybl (opened 8 d ago)</text>'
    # kill chain
    s += '<text x="330" y="112" font-size="11" fill="#9aa5b3">KILL-CHAIN STAGES</text>'
    for i, (lab, on) in enumerate([("contact", True), ("control", False),
                                    ("extraction", True), ("cashout", True)]):
        x = 330 + i * 75
        col = "#d9480f" if on else "#2a3341"
        s += f'<rect x="{x}" y="122" width="65" height="42" rx="6" fill="{col}"/>'
        s += (f'<text x="{x + 32}" y="147" text-anchor="middle" font-size="10.5" '
              f'font-weight="700" fill="{"#ffffff" if on else "#7a8493"}">'
              f'{lab.upper()}</text>')
    # reasons
    s += '<text x="20" y="204" font-size="11" fill="#9aa5b3">WHY (top signal contributions)</text>'
    rows = [("payee looks like a mule (fan-in + fast passthrough)", "+5.74", "cashout"),
            ("payee opened 8 days ago", "+3.43", "cashout"),
            ("first-time payee", "+2.73", "extraction"),
            ("FD broken in last 24 h", "+1.93", "extraction"),
            ("video call > 20 min", "+1.52", "contact")]
    for i, (r, w_, st) in enumerate(rows):
        y = 224 + i * 22
        s += f'<rect x="20" y="{y - 14}" width="600" height="20" rx="5" fill="#151b23"/>'
        s += f'<text x="34" y="{y}" font-size="11" fill="#e7ecf2">{r}</text>'
        s += f'<text x="500" y="{y}" font-size="11" fill="#9aa5b3">{st}</text>'
        s += (f'<text x="608" y="{y}" text-anchor="end" font-size="11" '
              f'font-weight="700" fill="#ff7a2b">{w_}</text>')
    # release
    s += '<rect x="20" y="344" width="290" height="24" rx="5" fill="#151b23"/>'
    s += '<text x="34" y="360" font-size="11" fill="#9aa5b3">RELEASE REASON</text>'
    s += '<text x="130" y="360" font-size="11" fill="#e7ecf2">confirmed victim call · voice ok</text>'
    s += '<rect x="330" y="344" width="140" height="24" rx="5" fill="#151b23"/>'
    s += '<text x="344" y="360" font-size="11" fill="#9aa5b3">SECOND APPROVER</text>'
    s += '<text x="446" y="360" font-size="11" fill="#e7ecf2">rakesh.n</text>'
    s += FOOT
    (ASSETS / "mockup_agent.svg").write_text(s)


if __name__ == "__main__":
    render_tier1()
    render_tier2()
    render_tier3()
    render_agent_desk()
    print("wrote mockup_*.svg")

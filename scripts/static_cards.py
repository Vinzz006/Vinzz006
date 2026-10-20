"""Generates the animated cards that never change: typing intro, landmarks, link pills, footer waves.
Run once (python scripts/static_cards.py); the workflow only refreshes the live cards."""
from update import write, fu, CSS, MONO, SANS, OUT

# ---------- typing intro (no card background) ----------
LINES = ["I build AI that talks to real hardware",
         "Model → API → Interface → Device",
         "Currently building SatQuery AI for SIH 2026 / ISRO"]
def typing():
    W, H, CW = 900, 80, 13.4; n = len(LINES); out = ""
    for k, t in enumerate(LINES):
        tw = len(t) * CW; x0 = (W - tw) / 2; s = k / n
        pts = [(0, 0), (s, 0), (s + .09, tw), (s + .27, tw), (s + 1 / n, 0), (1, 0)]
        ded = []
        for p in pts:
            if not ded or ded[-1] != p: ded.append(p)
        kt = ";".join(f"{a:.4f}" for a, _ in ded); vals = ";".join(f"{b:.1f}" for _, b in ded)
        cur = ";".join(f"{x0 + b:.1f}" for _, b in ded)
        out += f'''<clipPath id="c{k}"><rect x="{x0:.1f}" y="20" height="40" width="0"><animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="15s" repeatCount="indefinite"/></rect></clipPath>
<text x="{x0:.1f}" y="48" font-family="{MONO}" font-size="22" font-weight="700" fill="#5eead4" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#c{k})">{t}</text>
<rect y="27" width="3" height="26" fill="#2dd4bf"><animate attributeName="x" values="{cur}" keyTimes="{kt}" dur="15s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/></rect>'''
    open(OUT + "typing.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{out}</svg>')

# ---------- landmarks ----------
def landmarks_header():
    write(900, 84, f'''<text x="40" y="48" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="3" fill="#5eead4">PROJECTS.LIST</text>
<text x="210" y="48" font-family="{MONO}" font-size="13" fill="#5eead4" fill-opacity=".8">./projects.sh --all<tspan class="bk">_</tspan></text>
<text x="860" y="48" text-anchor="end" font-family="{MONO}" font-size="13" fill="#5eead4" fill-opacity=".8">4 pinned</text>
<line x1="40" y1="64" x2="860" y2="64" stroke="#2dd4bf" stroke-opacity=".4" stroke-dasharray="820" stroke-dashoffset="820"><animate attributeName="stroke-dashoffset" from="820" to="0" dur="1.2s" fill="freeze"/></line>''', "landmarks-header.svg")

PROJS = [("satquery-ai", "SatQuery AI", "Agentic vision-language assistant for", "satellite imagery · SIH 2026 / ISRO (SAC)", ["PyTorch", "GeoChat", "LoRA", "FastAPI"], "in progress", "#f59e0b", "landmark-satquery.svg"),
         ("canteen-system", "Sundararajan Canteen System", "Campus food-ordering app replacing slow,", "manual canteen ordering.", ["React", "TypeScript", "Vite"], "live", "#34d399", "landmark-canteen.svg"),
         ("mindease", "MindEase", "Private, AI-assisted mental wellness", "check-ins powered by Gemini.", ["React", "TypeScript", "Gemini API"], "live", "#34d399", "landmark-mindease.svg"),
         ("to-do-list", "Task Management App", "Fast, no-bloat daily task tracker.", "", ["React", "TypeScript", "Vite"], "live", "#34d399", "landmark-tasks.svg")]
def landmarks():
    for i, (slug, title, d1, d2, tags, status, sc, fn) in enumerate(PROJS):
        t = ""; x = 40
        for j, tg in enumerate(tags):
            tw = len(tg) * 7.4 + 22
            t += f'<g {fu(.9+j*.12)}><rect x="{x}" y="146" width="{tw}" height="24" rx="12" fill="#0b2a2b" stroke="#2dd4bf" stroke-opacity=".5"/><text x="{x+tw/2}" y="162" text-anchor="middle" font-family="{SANS}" font-size="11.5" fill="#5eead4">{tg}</text></g>'
            x += tw + 8
        fs = 20 if len(title) > 20 else 22; b = i * .15
        write(440, 200, f'''<rect x="20" y="20" width="400" height="160" rx="18" fill="#07191b" fill-opacity=".8" stroke="#2dd4bf" stroke-opacity=".45"/>
<text x="40" y="44" font-family="{MONO}" font-size="11.5" fill="#5eead4" {fu(b)}>▪ {slug}</text>
<circle cx="396" cy="40" r="5" fill="{sc}"><animate attributeName="r" values="4;6.5;4" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.45;1" dur="2s" repeatCount="indefinite"/></circle>
<text x="384" y="44" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5eead4" fill-opacity=".85">{status}</text>
<text x="40" y="82" font-family="{MONO}" font-size="{fs}" font-weight="800" fill="#d1fae5" {fu(b+.2)}>{title}<tspan class="bk"> _</tspan></text>
<text x="40" y="106" font-family="{MONO}" font-size="12" fill="#5eead4" {fu(b+.45)}>{d1}</text>
<text x="40" y="124" font-family="{MONO}" font-size="12" fill="#5eead4" {fu(b+.6)}>{d2}</text>{t}''', fn)

# ---------- link pills ----------
def pills():
    for lab, val, ic, fn in [("GitHub", "@vinzz006", "G", "pill-github.svg"), ("LinkedIn", "Vinesh-Shanmugam", "in", "pill-linkedin.svg"), ("Email", "shanmugamvinesh75", "@", "pill-email.svg")]:
        write(300, 84, f'''<rect x="14" y="14" width="272" height="56" rx="28" fill="#06181a" stroke="#2dd4bf" stroke-width="1.5"><animate attributeName="stroke-opacity" values=".35;1;.35" dur="3s" repeatCount="indefinite"/></rect>
<circle cx="46" cy="42" r="15" fill="#22373a"/><text x="46" y="48" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="800" fill="#d1fae5">{ic}</text>
<text x="74" y="37" font-family="{SANS}" font-size="11" font-weight="800" letter-spacing="1.5" fill="#5eead4">{lab}</text>
<text x="74" y="56" font-family="{SANS}" font-size="14" font-weight="800" fill="#d1fae5">{val}</text>''', fn)

# ---------- wave footer ----------
def footer():
    W, H = 900, 130
    def wave(y, amp, dur, color, op, rev=False):
        d = f"M0 {y} " + "".join(f"q112.5 {-amp if i % 2 == 0 else amp} 225 0 " for i in range(10)) + f"L2250 {H} L0 {H} Z"
        a, b = ("-450 0", "0 0") if rev else ("0 0", "-450 0")
        return f'<path d="{d}" fill="{color}" fill-opacity="{op}"><animateTransform attributeName="transform" type="translate" from="{a}" to="{b}" dur="{dur}s" repeatCount="indefinite"/></path>'
    body = wave(70, 26, 9, "#2dd4bf", .25) + wave(82, 20, 6.5, "#22d3ee", .22, True) + wave(94, 16, 12, "#4a90e2", .3) + wave(106, 12, 8, "#0f4f49", .9, True)
    open(OUT + "footer.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>')

if __name__ == "__main__":
    typing(); landmarks_header(); landmarks(); pills(); footer(); print("static cards written")

"""Generates the animated cards that never change: typing intro, section banners, dividers,
'right now' panel, pipeline, tech ticker, project cards, link pills, footer waves.
Run once: python scripts/static_cards.py  (the workflow only refreshes the live stat cards)."""
from update import write, fu, CSS, MONO, SANS, OUT

def raw(name, w, h, body, defs=""):
    open(OUT + name, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>{CSS}</style><defs>{defs}</defs>{body}</svg>')

def dedupe(pts):
    out = []
    for p in pts:
        if not out or out[-1] != p: out.append(p)
    return out

# ---------- typing intro ----------
LINES = ["I build AI that talks to real hardware", "Model → API → Interface → Device", "Currently building IBVAP and MahaSetu"]
def typing():
    W, H, CW = 900, 80, 13.4; n = len(LINES); body = ""
    for k, t in enumerate(LINES):
        tw = len(t) * CW; x0 = (W - tw) / 2; s0 = k / n
        pts = dedupe([(0, 0), (s0, 0), (s0 + .09, tw), (s0 + .27, tw), (s0 + 1 / n, 0), (1, 0)])
        kt = ";".join(f"{a:.4f}" for a, _ in pts); vals = ";".join(f"{b:.1f}" for _, b in pts); cur = ";".join(f"{x0+b:.1f}" for _, b in pts)
        body += f'''<clipPath id="c{k}"><rect x="{x0:.1f}" y="20" height="40" width="0"><animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="15s" repeatCount="indefinite"/></rect></clipPath>
<text x="{x0:.1f}" y="48" font-family="{MONO}" font-size="22" font-weight="700" fill="#5eead4" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#c{k})">{t}</text>
<rect y="27" width="3" height="26" fill="#2dd4bf"><animate attributeName="x" values="{cur}" keyTimes="{kt}" dur="15s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/></rect>'''
    raw("typing.svg", W, H, body)

# ---------- section banners + divider ----------
def banner(fn, num, title, sub):
    body = f'''<rect x="0" y="14" width="4" height="34" rx="2" fill="#2dd4bf" class="pl"/>
<text x="18" y="30" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="3" fill="#5eead4" {fu(0)}>{num} / {sub.upper()}</text>
<text x="18" y="56" font-family="{SANS}" font-size="30" font-weight="800" fill="#d1fae5" {fu(.15)}>{title}</text>
<rect x="0" y="68" width="900" height="2" fill="url(#ln)" class="gx" style="animation-delay:.3s"/>
<circle cy="69" r="4" fill="#7df9e4" filter="url(#bl)"><animate attributeName="cx" values="0;900" dur="4.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="4.5s" repeatCount="indefinite"/></circle>'''
    defs = '<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset=".6" stop-color="#2dd4bf" stop-opacity=".35"/><stop offset="1" stop-color="#2dd4bf" stop-opacity="0"/></linearGradient><filter id="bl"><feGaussianBlur stdDeviation="2.2"/></filter>'
    raw(fn, 900, 80, body, defs)

def divider():
    body = '<rect x="0" y="9" width="900" height="1.5" fill="url(#ln)" opacity=".5"/><circle cy="10" r="3" fill="#7df9e4" filter="url(#bl)"><animate attributeName="cx" values="-10;910" dur="6s" repeatCount="indefinite"/></circle>'
    defs = '<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf" stop-opacity="0"/><stop offset=".5" stop-color="#2dd4bf"/><stop offset="1" stop-color="#2dd4bf" stop-opacity="0"/></linearGradient><filter id="bl"><feGaussianBlur stdDeviation="2"/></filter>'
    raw("divider.svg", 900, 20, body, defs)

# ---------- right now ----------
def now():
    cols = [("BUILDING", "#f59e0b", "TITAN OS", "currently in development"), ("EXPLORING NEXT", "#9f7aea", "MLOps · Cloud (AWS / GCP)", "System design · Kubernetes"), ("OPEN TO", "#34d399", "Internships", "AI/ML · AI + IoT · Full-stack")]
    out = ""
    for i, (lab, c, l1, l2) in enumerate(cols):
        x = 48 + i * 280
        out += f'''<g {fu(.2+i*.2)}><circle cx="{x+5}" cy="68" r="5" fill="{c}"><animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.4;1" dur="2s" repeatCount="indefinite"/></circle>
<text x="{x+20}" y="72" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="2.5" fill="{c}">{lab}</text>
<text x="{x}" y="108" font-family="{SANS}" font-size="19" font-weight="800" fill="#d1fae5">{l1}</text>
<text x="{x}" y="132" font-family="{MONO}" font-size="12" fill="#5eead4">{l2}</text></g>'''
    write(900, 180, f'<rect x="24" y="24" width="852" height="132" rx="22" fill="#07191b" fill-opacity=".6" stroke="#2dd4bf" stroke-opacity=".35"/>{out}', "now.svg")

# ---------- pipeline ----------
def pipeline():
    nodes = [("Problem", "scope + users"), ("Prototype", "research + build"), ("Model", "ML · CV · LLM"), ("API", "FastAPI"), ("Interface", "React"), ("Device", "ESP32 · IoT"), ("Deploy", "test + ship")]
    xs = [75 + i * 125 for i in range(7)]; out = '<line x1="75" y1="70" x2="825" y2="70" stroke="#2dd4bf" stroke-opacity=".3" stroke-width="2" stroke-dasharray="4 6"/>'
    for i, ((t, sub), x) in enumerate(zip(nodes, xs)):
        tt = i / 6; pts = dedupe([(0, .12), (max(0, tt - .08), .12), (tt, 1), (min(1, tt + .08), .12), (1, .12)])
        kt = ";".join(f"{a:.4f}" for a, _ in pts); v = ";".join(f"{b}" for _, b in pts)
        out += f'''<g {fu(.1+i*.12)}><circle cx="{x}" cy="70" r="24" fill="#08181a" stroke="#2dd4bf" stroke-opacity=".6" stroke-width="1.5"/>
<circle cx="{x}" cy="70" r="24" fill="#2dd4bf"><animate attributeName="fill-opacity" values="{v}" keyTimes="{kt}" dur="8s" repeatCount="indefinite"/></circle>
<text x="{x}" y="76" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="800" fill="#d1fae5">{i+1}</text>
<text x="{x}" y="118" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="800" fill="#d1fae5">{t}</text>
<text x="{x}" y="138" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#5eead4">{sub}</text></g>'''
    out += '<circle cy="70" r="6" fill="#7df9e4"><animate attributeName="cx" values="75;825" dur="8s" repeatCount="indefinite"/></circle>'
    write(900, 180, out, "pipeline.svg")

# ---------- tech ticker ----------
TECH = ["Python", "PyTorch", "TensorFlow", "OpenCV", "scikit-learn", "FastAPI", "Flask", "LangChain", "Ollama", "FAISS", "React", "TypeScript", "JavaScript", "React Native", "Tailwind CSS", "Vite", "Node.js", "C++", "Dart", "ESP32", "Arduino", "Firebase", "PostgreSQL", "MongoDB", "SQLite", "Docker", "Linux", "Git"]
PAL = ["#2dd4bf", "#9f7aea", "#4a90e2", "#22d3ee", "#34d399", "#f59e0b"]
def ticker():
    row = ""; x = 0
    for i, t in enumerate(TECH):
        w = len(t) * 8.2 + 44
        row += f'<g transform="translate({x:.0f},0)"><rect y="14" width="{w:.0f}" height="34" rx="17" fill="#0b2a2b" stroke="#2dd4bf" stroke-opacity=".45"/><circle cx="18" cy="31" r="4" fill="{PAL[i%6]}"/><text x="30" y="36" font-family="{SANS}" font-size="14" font-weight="700" fill="#d1fae5">{t}</text></g>'
        x += w + 12
    body = f'<g mask="url(#m)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{x:.0f} 0" dur="{len(TECH)*2.2:.0f}s" repeatCount="indefinite"/>{row}<g transform="translate({x:.0f},0)">{row}</g></g></g>'
    defs = '<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset=".07" stop-color="#fff"/><stop offset=".93" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient><mask id="m"><rect width="900" height="64" fill="url(#f)"/></mask>'
    raw("ticker.svg", 900, 64, body, defs)

# ---------- project cards ----------
PROJECTS = [
 ("satquery", "satquery-ai", "SatQuery AI", "SIH 2026 · ISRO PS 26167", "in progress · v2.0", "#f59e0b",
  "Agentic assistant for satellite imagery",
  ["Plain-language queries, no GIS expertise needed", "Agent controller routes to specialist tools", "VQA, captioning, grounding, change detection", "Optical–SAR fusion for multi-sensor analysis"],
  ["PyTorch", "GeoChat", "LoRA", "FastAPI", "React"]),
 ("factorylens", "factorylens", "FactoryLens", "Industrial IoT · Digital twin", "prototype", "#34d399",
  "Machine health + predictive maintenance",
  ["ESP32 streams vibration, current, temp and RPM", "MPU6050, ACS712, DS18B20, Hall/IR sensors", "Random Forest fault diagnosis via FastAPI", "Live React dashboard backed by Firebase"],
  ["ESP32", "Firebase", "FastAPI", "Random Forest", "React"]),
 ("croptwin", "croptwin", "CropTwin", "Final-year research project", "research", "#9f7aea",
  "Self-evolving AI digital twin for crop health",
  ["EfficientNet-B0 crop disease identification", "Open-set detection of unseen disease patterns", "Expert verification and health forecasting", "Field digital-twin visualization"],
  ["PyTorch", "EfficientNet-B0", "FastAPI", "SQLite"]),
 ("tinyml", "tinyml-fall-detection", "TinyML Fall Detection", "Wearable · Edge AI", "prototype", "#34d399",
  "Real-time activity and fall detection",
  ["MPU6050 + ESP32 wearable sensor node", "TinyML classifies walking, sitting, running, falls", "FastAPI + WebSocket live streaming", "React dashboard, Docker Compose setup"],
  ["ESP32", "TinyML", "FastAPI", "WebSocket", "React"]),
 ("railsafe", "railsafe-ai", "RailSafe AI", "Hardware hackathon · Indian Railways", "prototype", "#34d399",
  "Screening assistant + luggage surveillance",
  ["Android app + ESP32 device over BLE", "Live telemetry, assistance flags, test logs", "RailGuard Vision flags unattended luggage", "Human review only, no automatic action"],
  ["ESP32", "BLE", "Dart", "Python", "Computer Vision"]),
 ("ibvap", "ibvap", "IBVAP", "MHA / SSB · PS 26187", "prototype", "#34d399",
  "Intelligent Border Video Analytics Platform",
  ["Border CCTV intelligence for MHA / SSB", "Tackles operator fatigue and passive camera feeds", "Targets scene context, trajectories, breaches", "Hackathon prototype for problem statement 26187"],
  ["JavaScript", "Video Analytics"]),
 ("mahasetu", "mahasetu-web", "MahaSetu Web", "SIH 2026 · Maharashtra PS 26129", "prototype", "#34d399",
  "Verifiable digital service passport platform",
  ["One citizen, one consent, one application ID", "Connects existing government systems", "One unified journey across departments", "Interoperability instead of replacement"],
  ["TypeScript", "Web Platform"]),
 ("mahasetu-mobile", "mahasetu-mobile", "MahaSetu Mobile", "SIH 2026 · Maharashtra PS 26129", "prototype", "#34d399",
  "Citizen app for the MahaSetu platform",
  ["Submit information once and give consent", "Track cross-department processing in real time", "Expo SDK 52 with React Native 0.76", "Reproducible setup guide for SIH judges"],
  ["React Native", "Expo", "TypeScript"]),
]
def project_cards():
    for fn, slug, title, badge, status, sc, tag, bullets, chips in PROJECTS:
        b = 0
        rows, x, y = "", 40, 216
        for j, c in enumerate(chips):
            w = len(c) * 7 + 22
            if x + w > 400: x, y = 40, y + 28
            rows += f'<g {fu(.9+j*.1)}><rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="#0b2a2b" stroke="#2dd4bf" stroke-opacity=".5"/><text x="{x+w/2}" y="{y+15}" text-anchor="middle" font-family="{SANS}" font-size="11" fill="#5eead4">{c}</text></g>'
            x += w + 8
        bw = len(badge) * 6.5 + 22; fs = 19 if len(title) > 18 else 22
        bl = "".join(f'<text x="40" y="{150+i*18}" font-family="{SANS}" font-size="12.5" fill="#bdf5ea" {fu(.45+i*.12)}><tspan fill="#2dd4bf">▸ </tspan>{t}</text>' for i, t in enumerate(bullets))
        write(440, 320, f'''<rect x="20" y="20" width="400" height="280" rx="18" fill="#07191b" fill-opacity=".8" stroke="#2dd4bf" stroke-opacity=".45"/>
<text x="40" y="44" font-family="{MONO}" font-size="11.5" fill="#5eead4" {fu(0)}>▪ {slug}</text>
<circle cx="396" cy="40" r="5" fill="{sc}"><animate attributeName="r" values="4;6.5;4" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.45;1" dur="2s" repeatCount="indefinite"/></circle>
<text x="384" y="44" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5eead4" fill-opacity=".85">{status}</text>
<g {fu(.1)}><rect x="40" y="54" width="{bw:.0f}" height="20" rx="10" fill="#2dd4bf" fill-opacity=".14" stroke="#2dd4bf" stroke-opacity=".5"/><text x="{40+bw/2:.0f}" y="68" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#7df9e4">{badge}</text></g>
<text x="40" y="104" font-family="{MONO}" font-size="{fs}" font-weight="800" fill="#d1fae5" {fu(.2)}>{title}<tspan class="bk"> _</tspan></text>
<text x="40" y="126" font-family="{SANS}" font-size="13" font-weight="700" fill="#5eead4" {fu(.3)}>{tag}</text>
{bl}{rows}
<text x="40" y="288" font-family="{MONO}" font-size="11.5" font-weight="700" fill="#7df9e4" {fu(1.4)}>view repository ↗</text>''', f"proj-{fn}.svg")

# ---------- link pills ----------
def pills():
    for lab, val, ic, fn in [("GitHub", "@vinzz006", "G", "pill-github.svg"), ("LinkedIn", "Vinesh-Shanmugam", "in", "pill-linkedin.svg"), ("Email", "shanmugamvinesh75", "@", "pill-email.svg"), ("Portfolio", "vinesh-portfolio-website", "↗", "pill-portfolio.svg")]:
        write(300, 84, f'''<rect x="14" y="14" width="272" height="56" rx="28" fill="#06181a" stroke="#2dd4bf" stroke-width="1.5"><animate attributeName="stroke-opacity" values=".35;1;.35" dur="3s" repeatCount="indefinite"/></rect>
<circle cx="46" cy="42" r="15" fill="#22373a"/><text x="46" y="48" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="800" fill="#d1fae5">{ic}</text>
<text x="74" y="37" font-family="{SANS}" font-size="11" font-weight="800" letter-spacing="1.5" fill="#5eead4">{lab.upper()}</text>
<text x="74" y="56" font-family="{SANS}" font-size="13" font-weight="800" fill="#d1fae5">{val}</text>''', fn)

# ---------- wave footer ----------
def footer():
    W, H = 900, 130
    def wave(y, amp, dur, color, op, rev=False):
        d = f"M0 {y} " + "".join(f"q112.5 {-amp if i % 2 == 0 else amp} 225 0 " for i in range(10)) + f"L2250 {H} L0 {H} Z"
        a, b = ("-450 0", "0 0") if rev else ("0 0", "-450 0")
        return f'<path d="{d}" fill="{color}" fill-opacity="{op}"><animateTransform attributeName="transform" type="translate" from="{a}" to="{b}" dur="{dur}s" repeatCount="indefinite"/></path>'
    raw("footer.svg", W, H, wave(70, 26, 9, "#2dd4bf", .25) + wave(82, 20, 6.5, "#22d3ee", .22, True) + wave(94, 16, 12, "#4a90e2", .3) + wave(106, 12, 8, "#0f4f49", .9, True))

if __name__ == "__main__":
    typing(); divider(); now(); pipeline(); ticker(); project_cards(); pills(); footer()
    for fn, n, t, sub in [("sec-build.svg", "01", "How I build", "process"), ("sec-projects.svg", "02", "Featured projects", "flagship work"), ("sec-more.svg", "03", "More builds", "hackathons and apps"),
                          ("sec-toolkit.svg", "04", "Toolkit", "skills"), ("sec-city.svg", "05", "The city I built this year", "activity"), ("sec-stats.svg", "06", "Population and GitStats", "numbers"), ("sec-connect.svg", "07", "Let's build something", "connect")]:
        banner(fn, n, t, sub)
    print("static cards written")

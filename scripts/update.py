"""Regenerates assets/header.svg, assets/city.svg and assets/signal.svg
from live GitHub data. Standard library only.

Env: GH_TOKEN (required unless --demo), GH_USER (default: Vinzz006)
"""
import json, os, sys, urllib.request, random

USER = os.environ.get("GH_USER", "Vinzz006")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets") + os.sep
MONO = "'JetBrains Mono','SF Mono',ui-monospace,Consolas,monospace"
SANS = "'Segoe UI','Inter',system-ui,-apple-system,Arial,sans-serif"
CHIPS = ["TypeScript", "Python", "JavaScript", "Dart"]

QUERY = """query($login:String!){user(login:$login){
 followers{totalCount}
 pullRequests{totalCount} issues{totalCount}
 repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){totalCount}
 repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount}}
 langRepos: repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false,first:100){nodes{languages(first:6,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
 contributionsCollection{totalCommitContributions contributionCalendar{totalContributions weeks{contributionDays{contributionCount weekday date}}}}}}"""

def build_cells(days):
    """days: list of (date_str, count) in chronological order, Sunday-first weeks."""
    import datetime
    first = datetime.date.fromisoformat(days[0][0])
    lead = (first.weekday() + 1) % 7          # python Mon=0 -> Sun=0
    cells = {}
    for i, (_, c) in enumerate(days):
        cells[((i + lead) // 7, (i + lead) % 7)] = c
    return cells, (len(days) + lead + 6) // 7

def streaks(days):
    counts = [c for _, c in days]
    best = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0; best = max(best, run)
    cur = 0; i = len(counts) - 1
    if i >= 0 and counts[i] == 0: i -= 1       # today may not have activity yet
    while i >= 0 and counts[i] > 0: cur += 1; i -= 1
    return cur, best

def lang_shares(sizes, top=6):
    tot = sum(sizes.values()) or 1
    items = sorted(sizes.items(), key=lambda kv: -kv[1])[:top]
    return [(n, v / tot * 100) for n, v in items]

def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}", "Content-Type": "application/json"})
    res = json.load(urllib.request.urlopen(req))
    if "errors" in res: raise SystemExit(res["errors"])
    u = res["data"]["user"]; cc = u["contributionsCollection"]; cal = cc["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for wk in cal["weeks"] for d in wk["contributionDays"]]
    cells, nweeks = build_cells(days)
    sizes = {}
    for r in u["langRepos"]["nodes"]:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    return dict(total=cal["totalContributions"], cells=cells, nweeks=nweeks, days=days,
        stars=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        repos=u["repositories"]["totalCount"], followers=u["followers"]["totalCount"],
        commits=cc["totalCommitContributions"], prs=u["pullRequests"]["totalCount"], issues=u["issues"]["totalCount"],
        contributed=u["repositoriesContributedTo"]["totalCount"], langs=lang_shares(sizes))

def fetch_public():
    """No-token fallback: scrapes public profile pages. PR/issue/commit counts are unavailable here."""
    import re, html, datetime
    get = lambda url: urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read().decode()
    h = get(f"https://github.com/users/{USER}/contributions")
    tips = {m.group(1): m.group(2) for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', h)}
    days = []
    for m in re.finditer(r'<td[^>]*?data-date="([\d-]+)"[^>]*?id="([^"]+)"', h):
        t = tips.get(m.group(2), ""); n = re.match(r"(\d+) contribution", t)
        days.append((m.group(1), int(n.group(1)) if n else 0))
    days.sort(); cells, nweeks = build_cells(days)
    total = int(re.search(r"([\d,]+)\s+contributions\s+in the last year", h).group(1).replace(",", ""))
    prof = get(f"https://github.com/{USER}")
    fol = re.search(r"([\d,.k]+)\s*</span>\s*followers", prof)
    sizes, stars, repos, page = {}, 0, 0, 1
    while True:
        rp = get(f"https://github.com/{USER}?tab=repositories&page={page}")
        blocks = rp.split('itemprop="name codeRepository"')[1:]
        if not blocks: break
        for b in blocks:
            if "Forked from" in b: continue
            repos += 1
            l = re.search(r'itemprop="programmingLanguage">([^<]+)<', b)
            if l: sizes[l.group(1)] = sizes.get(l.group(1), 0) + 1
            st = re.search(r'/stargazers"[^>]*>(?:\s*<svg.*?</svg>)?\s*([\d,]+)', b, re.S)
            if st: stars += int(st.group(1).replace(",", ""))
        page += 1
    return dict(total=total, cells=cells, nweeks=nweeks, days=days, stars=stars, repos=repos,
        followers=int(fol.group(1)) if fol else 0, commits=None, prs=None, issues=None, contributed=None, langs=lang_shares(sizes))

def demo():
    r = random.Random(1); days = [(f"2026-01-{(i%28)+1:02d}", r.randint(1, 20) if r.random() < .3 else 0) for i in range(371)]
    cells, nw = build_cells([(("2025-10-19" if i == 0 else "2025-10-20"), c) for i, (_, c) in enumerate(days)])
    return dict(total=sum(c for _, c in days), cells=cells, nweeks=nw, days=days, stars=23, repos=35, followers=7,
        commits=240, prs=12, issues=3, contributed=9, langs=[("TypeScript", 42.0), ("Python", 31.0), ("JavaScript", 17.0), ("Dart", 6.0), ("C++", 4.0)])

CSS = """
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes growX{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}
@keyframes glow{0%,100%{opacity:0}50%{opacity:.4}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
.fu{animation:fadeUp .9s cubic-bezier(.2,.8,.2,1) both}
.gr{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1.1s cubic-bezier(.2,.9,.2,1) both}
.gx{transform-box:fill-box;transform-origin:0 50%;animation:growX 1.3s cubic-bezier(.2,.8,.2,1) both}
@keyframes floorIn{0%{transform:scaleY(0);opacity:0}6%{transform:scaleY(1);opacity:1}92%{transform:scaleY(1);opacity:1}98%,100%{transform:scaleY(0);opacity:0}}
@keyframes towerIn{0%{transform:scaleY(0)}9%{transform:scaleY(1)}66%{transform:scaleY(1)}72%,100%{transform:scaleY(0)}}
.fl{transform-box:fill-box;transform-origin:50% 100%;animation:floorIn 16s cubic-bezier(.3,.8,.3,1) infinite both}
.tw{transform-box:fill-box;transform-origin:50% 100%;animation:towerIn 16s cubic-bezier(.2,.9,.2,1) infinite both}
.pl{animation:pulse 2.6s ease-in-out infinite}
.gl{animation:glow 2.2s ease-in-out infinite}
.bk{animation:blink 1.1s step-end infinite}
"""
fu = lambda delay: f'class="fu" style="animation-delay:{delay:.2f}s"'

def bg(w, h):
    return f'''<style>{CSS}</style><defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f4f49"/><stop offset=".5" stop-color="#0a2f31"/><stop offset="1" stop-color="#1c3f63"/></linearGradient>
<radialGradient id="r" cx=".12" cy=".05" r=".6"><stop offset="0" stop-color="#2dd4bf" stop-opacity=".38"/><stop offset="1" stop-color="#2dd4bf" stop-opacity="0"/></radialGradient>
<radialGradient id="b" cx=".92" cy=".95" r=".5"><stop offset="0" stop-color="#3b82f6" stop-opacity=".28"/><stop offset="1" stop-color="#3b82f6" stop-opacity="0"/></radialGradient>
<radialGradient id="r2"><stop offset="0" stop-color="#2dd4bf" stop-opacity=".22"/><stop offset="1" stop-color="#2dd4bf" stop-opacity="0"/></radialGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".11"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="cardclip"><rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="26"/></clipPath>
</defs>
<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="26" fill="url(#g)" stroke="#2dd4bf" stroke-opacity=".55" stroke-width="1.5"/>
<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="26" fill="url(#r)"/>
<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="26" fill="url(#b)"/>
<g clip-path="url(#cardclip)"><g><animateTransform attributeName="transform" type="translate" values="0 0;{w*.55:.0f} {h*.25:.0f};0 0" dur="16s" repeatCount="indefinite"/><circle cx="90" cy="30" r="{max(w,h)*.38:.0f}" fill="url(#r2)"/></g></g>'''

def write(w, h, body, name):
    shine = f'''<g clip-path="url(#cardclip)"><g><animateTransform attributeName="transform" type="translate" values="-220 0;-220 0;{w+260} 0;{w+260} 0" keyTimes="0;.12;.55;1" dur="9s" repeatCount="indefinite"/><rect x="0" y="-10" width="110" height="{h+20}" fill="url(#shine)" transform="skewX(-20)"/></g></g>'''
    with open(OUT + name, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{bg(w,h)}{body}{shine}</svg>')

def header(d):
    W, H = 900, 260; cx = 200; cs = ""
    for i, c in enumerate(CHIPS):
        cw = len(c) * 8.6 + 34
        cs += f'<g {fu(1.0+i*.15)}><rect x="{cx}" y="206" width="{cw}" height="30" rx="15" fill="#0b2a2b" stroke="#2dd4bf" stroke-opacity=".5"/><text x="{cx+cw/2}" y="226" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="700" fill="#d1fae5">{c}</text></g>'
        cx += cw + 14
    write(W, H, f'''<rect x="24" y="24" width="{W-48}" height="{H-48}" rx="22" fill="#07191b" fill-opacity=".8" stroke="#2dd4bf" stroke-opacity=".4"/>
<circle cx="104" cy="130" r="56" fill="#0b2a2b" stroke="#2dd4bf" stroke-width="3" class="pl"/><circle cx="104" cy="130" r="47" fill="#06181a" stroke="#2dd4bf" stroke-opacity=".4"/>
<g><animateTransform attributeName="transform" type="rotate" from="0 104 130" to="360 104 130" dur="6s" repeatCount="indefinite"/><circle cx="104" cy="74" r="4.5" fill="#5eead4"/></g>
<text x="104" y="143" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="800" fill="#5eead4" {fu(.1)}>VS</text>
<path d="M200 92 Q330 70 470 98" fill="none" stroke="#2dd4bf" stroke-opacity=".5" stroke-width="1.5" stroke-dasharray="300" stroke-dashoffset="300"><animate attributeName="stroke-dashoffset" from="300" to="0" dur="1.6s" begin=".3s" fill="freeze"/></path>
<text x="200" y="88" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="3.5" fill="#5eead4" {fu(.2)}>@{USER.lower()}</text>
<text x="200" y="150" font-family="{SANS}" font-size="44" font-weight="800" fill="#d1fae5" {fu(.4)}>Vinesh Shanmugam</text>
<text x="200" y="184" font-family="{SANS}" font-size="16" fill="#5eead4" {fu(.7)}>AI/ML Developer | Full-Stack Developer | IoT &amp; Embedded Systems</text>
{cs}
<g {fu(1.2)}><text x="808" y="140" text-anchor="middle" font-family="{SANS}" font-size="40" font-weight="800" fill="#2dd4bf" class="pl">{d["stars"]}</text>
<text x="808" y="164" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" letter-spacing="3" fill="#5eead4">TOTAL STARS</text></g>''', "header.svg")

PAL = {0: ("#10665f", "#0c4d4a", "#09403e"), 1: ("#2fc9b4", "#1f9e8f", "#187a70"), 2: ("#3fd9c3", "#25ad9d", "#1c8a7f"),
       3: ("#6ae8d6", "#34bfae", "#26998d"), 4: ("#a5f3e6", "#5fd1c1", "#3ea89b")}

def city(d):
    cells, nw = d["cells"], d["nweeks"]
    mx = max(cells.values()) or 1
    active = sum(1 for v in cells.values() if v > 0)
    k_h = min(1.25, 50 / mx)
    def lvl(c):
        if c == 0: return 0
        r = c / mx
        return 1 if r <= .1 else 2 if r <= .3 else 3 if r <= .6 else 4
    W, H = 900, 400; ox, oy = 400, 62; ax, ay, bx, by = 9, 4.5, -9, 4.5
    pt = lambda p: f"{p[0]:.1f},{p[1]:.1f}"
    polys = []
    for s in range(nw + 6):
        for w in range(nw):
            dd = s - w
            if not 0 <= dd < 7: continue
            c = cells.get((w, dd))
            if c is None: continue
            h = 2.5 if c == 0 else 3 + c * k_h
            px, py = ox + w * ax + dd * bx, oy + w * ay + dd * by
            cxm, cym = px + (ax + bx) / 2, py + (ay + by) / 2
            sh = lambda x, y: (cxm + (x - cxm) * .94, cym + (y - cym) * .94)
            T = sh(px, py); R = sh(px + ax, py + ay); B = sh(px + ax + bx, py + ay + by); L = sh(px + bx, py + by)
            up = lambda p: (p[0], p[1] - h)
            Tu, Ru, Bu, Lu = map(up, (T, R, B, L))
            def cube(hh, pal):
                top, left, right = pal
                u = lambda p: (p[0], p[1] - hh)
                Tu, Ru, Bu, Lu = map(u, (T, R, B, L))
                return (f'<polygon points="{pt(Lu)} {pt(Bu)} {pt(B)} {pt(L)}" fill="{left}"/><polygon points="{pt(Bu)} {pt(Ru)} {pt(R)} {pt(B)}" fill="{right}"/>'
                        f'<polygon points="{pt(Tu)} {pt(Ru)} {pt(Bu)} {pt(Lu)}" fill="{top}"/>'), (Tu, Ru, Bu, Lu)
            # floor tile: rises in as a diagonal wave
            flat, _ = cube(2.5, PAL[0])
            polys.append(f'<g class="fl" style="animation-delay:{s*0.03:.2f}s">{flat}</g>')
            if c > 0:
                tower, (Tu, Ru, Bu, Lu) = cube(h, PAL[lvl(c)])
                extra = f'<polygon points="{pt(Tu)} {pt(Ru)} {pt(Bu)} {pt(Lu)}" fill="#ffffff" opacity="0" class="gl"/>' if c == mx else ""
                polys.append(f'<g class="tw" style="animation-delay:{1.4+w*0.025:.2f}s">{tower}{extra}</g>')
    write(W, H, f'''<text x="48" y="78" {fu(0)} font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="3" fill="#5eead4">CONTRIBUTION CITY</text>
<text x="48" y="124" {fu(0.1)} font-family="{SANS}" font-size="46" font-weight="800" fill="#d1fae5">{d["total"]}</text>
<text x="48" y="150" {fu(0.25)} font-family="{SANS}" font-size="15" font-weight="600" fill="#5eead4">contributions in the last year</text>
<text x="48" y="188" {fu(0.4)} font-family="{SANS}" font-size="14" font-weight="600" fill="#5eead4">{active} active days</text>
<text x="48" y="212" {fu(0.5)} font-family="{SANS}" font-size="14" font-weight="600" fill="#5eead4">Busiest day: {mx}</text>
<text x="48" y="360" font-family="{MONO}" font-size="12" fill="#5eead4">@{USER.lower()}</text>
{''.join(polys)}''', "city.svg")

def signal(d):
    W, H = 900, 240; tot = max(d["total"], 1)
    stats = [("Stars", d["stars"], "#4fd1c5"), ("Contributions", d["total"], "#9f7aea"), ("Repos", d["repos"], "#4a90e2"), ("Followers", d["followers"], "#22d3ee")]
    cards = ""
    for n, (lab, val, col) in enumerate(stats):
        x = 40 + n * 208; p = min(1, val / tot)
        cards += f'''<g {fu(.2+n*.15)}><rect x="{x}" y="100" width="196" height="106" rx="20" fill="#08181a" fill-opacity=".75" stroke="#2dd4bf" stroke-opacity=".45"/>
<text x="{x+20}" y="128" font-family="{SANS}" font-size="13" font-weight="700" letter-spacing="1" fill="#5eead4">{lab}</text>
<text x="{x+20}" y="170" font-family="{SANS}" font-size="40" font-weight="800" fill="{col}">{val}</text>
<rect x="{x+20}" y="184" width="156" height="8" rx="4" fill="#ffffff" fill-opacity=".1"/></g>
<rect x="{x+20}" y="184" width="{max(10,156*p):.1f}" height="8" rx="4" fill="{col}" class="gx" style="animation-delay:{.7+n*.15:.2f}s"/>'''
    write(W, H, f'''<rect x="24" y="24" width="852" height="192" rx="22" fill="#07191b" fill-opacity=".55" stroke="#2dd4bf" stroke-opacity=".35"/>
<g><animateTransform attributeName="transform" type="rotate" from="0 800 70" to="360 800 70" dur="18s" repeatCount="indefinite"/><circle cx="800" cy="70" r="26" fill="none" stroke="#2dd4bf" stroke-opacity=".45" stroke-dasharray="3 7"/></g>
<g><animateTransform attributeName="transform" type="rotate" from="360 800 70" to="0 800 70" dur="28s" repeatCount="indefinite"/><circle cx="800" cy="70" r="46" fill="none" stroke="#2dd4bf" stroke-opacity=".3" stroke-dasharray="2 9"/></g><circle cx="834" cy="52" r="4" fill="#2dd4bf" class="pl"/>
<text x="44" y="70" font-family="{SANS}" font-size="34" font-weight="800" fill="#d1fae5" {fu(0)}>Profile Signal</text>
<text x="44" y="92" font-family="{SANS}" font-size="14" font-weight="700" fill="#5eead4" {fu(.1)}>Live GitHub stats · @{USER.lower()}</text>{cards}''', "signal.svg")

PALETTE = ["#2dd4bf", "#9f7aea", "#4a90e2", "#22d3ee", "#34d399", "#f59e0b"]
fmt = lambda v: "—" if v is None else f"{v:,}"

def streak_card(d):
    W, H = 900, 220; cur, best = streaks(d["days"]); tot = d["total"]
    col = lambda x, big, small, label, color, dl: f'''<g {fu(dl)}><text x="{x}" y="112" text-anchor="middle" font-family="{SANS}" font-size="44" font-weight="800" fill="{color}">{big}</text>
<text x="{x}" y="142" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="700" fill="#d1fae5">{label}</text>
<text x="{x}" y="164" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#5eead4" fill-opacity=".85">{small}</text></g>'''
    dash = min(1, cur / max(best, 1)) * 326.7
    ring = f'''<circle cx="450" cy="88" r="52" fill="none" stroke="#ffffff" stroke-opacity=".1" stroke-width="8"/>
<circle cx="450" cy="88" r="52" fill="none" stroke="#2dd4bf" stroke-width="8" stroke-linecap="round" stroke-dasharray="{dash:.1f} 326.7" transform="rotate(-90 450 88)"><animate attributeName="stroke-dasharray" from="0 326.7" to="{dash:.1f} 326.7" dur="1.6s" fill="freeze"/></circle>
<g {fu(.5)}><text x="450" y="102" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="800" fill="#d1fae5">{cur}</text>
<text x="450" y="162" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="700" fill="#2dd4bf">Current Streak</text>
<text x="450" y="182" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#5eead4" fill-opacity=".85">days in a row</text></g>'''
    write(W, H, f'''<rect x="24" y="24" width="852" height="172" rx="22" fill="#07191b" fill-opacity=".55" stroke="#2dd4bf" stroke-opacity=".35"/>
<line x1="300" y1="50" x2="300" y2="170" stroke="#2dd4bf" stroke-opacity=".3"/><line x1="600" y1="50" x2="600" y2="170" stroke="#2dd4bf" stroke-opacity=".3"/>
{col(150, tot, "last 12 months", "Total Contributions", "#9f7aea", .2)}{ring}{col(750, best, "days in a row", "Longest Streak", "#4a90e2", .8)}''', "streak.svg")

def stats_card(d):
    W, H = 440, 300
    rows = [("Total Commits (last year)", d["commits"], "#2dd4bf"), ("Pull Requests", d["prs"], "#9f7aea"), ("Issues", d["issues"], "#4a90e2"),
            ("Stars Earned", d["stars"], "#22d3ee"), ("Contributed To", d["contributed"], "#34d399")]
    out = ""
    for i, (lab, val, c) in enumerate(rows):
        y = 112 + i * 34
        out += f'''<g {fu(.3+i*.12)}><circle cx="46" cy="{y-5}" r="5" fill="{c}" class="pl"/><text x="64" y="{y}" font-family="{SANS}" font-size="14" font-weight="600" fill="#5eead4">{lab}</text>
<text x="400" y="{y}" text-anchor="end" font-family="{SANS}" font-size="18" font-weight="800" fill="#d1fae5">{fmt(val)}</text></g>'''
    write(W, H, f'''<rect x="20" y="20" width="400" height="260" rx="18" fill="#07191b" fill-opacity=".7" stroke="#2dd4bf" stroke-opacity=".4"/>
<text x="40" y="58" font-family="{SANS}" font-size="22" font-weight="800" fill="#d1fae5" {fu(0)}>GitHub Stats</text>
<text x="40" y="78" font-family="{MONO}" font-size="11" fill="#5eead4" fill-opacity=".85" {fu(.1)}>@{USER.lower()}</text>{out}''', "stats.svg")

def langs_card(d):
    W, H = 440, 300; langs = d["langs"]; x = 40; bar = ""
    for i, (n, pct) in enumerate(langs):
        w = 360 * pct / 100 if i < len(langs) - 1 else 400 - x
        bar += f'<rect x="{x:.1f}" y="92" width="{max(w,2):.1f}" height="10" fill="{PALETTE[i % 6]}"/>'; x += w
    rows = ""
    for i, (n, pct) in enumerate(langs):
        cx = 40 + (i % 2) * 190; cy = 138 + (i // 2) * 36
        rows += f'''<g {fu(.6+i*.12)}><circle cx="{cx+5}" cy="{cy-5}" r="5" fill="{PALETTE[i % 6]}"/><text x="{cx+18}" y="{cy}" font-family="{SANS}" font-size="14" font-weight="700" fill="#d1fae5">{n}</text>
<text x="{cx+170}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#5eead4">{pct:.1f}%</text></g>'''
    write(W, H, f'''<rect x="20" y="20" width="400" height="260" rx="18" fill="#07191b" fill-opacity=".7" stroke="#2dd4bf" stroke-opacity=".4"/>
<text x="40" y="58" font-family="{SANS}" font-size="22" font-weight="800" fill="#d1fae5" {fu(0)}>Top Languages</text>
<text x="40" y="78" font-family="{MONO}" font-size="11" fill="#5eead4" fill-opacity=".85" {fu(.1)}>by code size, public repos</text>
<clipPath id="c"><rect x="40" y="92" width="360" height="10" rx="5"><animate attributeName="width" from="0" to="360" dur="1.4s" fill="freeze"/></rect></clipPath><g clip-path="url(#c)">{bar}</g>{rows}''', "langs.svg")

if __name__ == "__main__":
    if "--demo" in sys.argv: data = demo()
    elif os.environ.get("GH_TOKEN") and "--public" not in sys.argv: data = fetch()
    else: data = fetch_public()
    header(data); city(data); signal(data); streak_card(data); stats_card(data); langs_card(data)
    print("updated:", {k: v for k, v in data.items() if k not in ("cells", "days")})

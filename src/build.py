#!/usr/bin/env python3
"""Builds Blocklog's site from src/pages into the repo root, which GitHub Pages serves from main.

    python3 -m venv .venv && .venv/bin/pip install pillow
    .venv/bin/python src/build.py

Pages: home (src/pages/home.html), support, privacy and terms (src/pages/*.body.html). Also written: 404.html, sitemap.xml,
robots.txt, llms.txt for AI tools, the icon and screenshots (from ~/blocklog-app) and the social card img/og.png.
Images are the app's own icon (made with ChatGPT) and screenshots of the app. Change UPDATED when facts are rechecked.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
APP_REPO = Path.home() / "blocklog-app"
BASE = "https://coderalert0.github.io/blocklog-site/"
APP_ID = "6833304516"
APP = f"https://apps.apple.com/us/app/id{APP_ID}"
NAME = "Blocklog"
APP_NAME = "Pilot Logbook: Blocklog"
EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
UPDATED = "2026-11-12"
UPDATED_LONG = date.fromisoformat(UPDATED).strftime("%B %-d, %Y")
DISCLAIMER = ("Blocklog's currency, night and cross-country figures are aids: check them against the regulations. Blocklog is not "
              "affiliated with the FAA, Transport Canada, CASA, EASA, the UK CAA, LogTen, ForeFlight or MyFlightbook.")
PUBLISHER = {"@type": "Organization", "name": NAME, "url": BASE, "logo": BASE + "img/icon-512.png"}
HOME_TITLE = "Blocklog: Pilot Logbook for iPhone, iPad and Mac"
HOME_DESCRIPTION = ("A pilot logbook that works out block time, night and cross-country, checks FAA currency and totals every 8710 "
                    "column. Imports LogTen, ForeFlight and MyFlightbook. Free and unlimited on one device.")
SUMMARY = ("Blocklog is a pilot logbook app for iPhone, iPad and Mac. It fills in block time, night and cross-country from the "
           "airports and times entered, checks FAA currency, totals every column of the FAA 8710 form, signs AC 61-65K "
           "endorsements, and imports logbooks from LogTen, ForeFlight and MyFlightbook. It's free and unlimited on one device; "
           "Blocklog Pro adds iCloud sync, the Mac app and printed logbook pages.")
FACTS = [
    "Free, forever, on one device: unlimited flights, FAA currency, totals with 7/30/90/365-day windows and the 8710 grid, every import and export (CSV and full JSON backup), AC 61-65K endorsements, photos on flights, charts, a route map, a people list with per-instructor totals, batch edit and 30 daily snapshots. No ads.",
    "Blocklog Pro costs $49.99 a year (first month free) or $4.99 a month in the US; Lifetime Pro is $149.99 once. One purchase covers iPhone, iPad and Mac.",
    "Pro adds iCloud sync (through the user's own private iCloud database, merged field by field), the Mac app, printable logbook pages in FAA, EASA, UK CAA, Transport Canada and CASA layouts, a one-page experience summary, saved reports (chosen figures and time windows, as PDF or CSV), more than one logbook and custom fields.",
    "If Pro ends, nothing is taken away: the logbook and everything free keep working; sync, Mac editing and printing stop.",
    "Imports LogTen (tab-separated export), ForeFlight (logbook CSV), MyFlightbook (CSV) and spreadsheets, with a preview of every flight and an undo snapshot.",
    "Currency: passenger day and night (14 CFR 61.57(a), (b)), instrument with grace period and IPC (61.57(c)), flight review (61.56), the medical certificate's expiry for the privileges used (61.23(d)), a student's 90-day solo endorsement (61.87(n), (p)), and currencies the pilot defines (for example NVG: so many flights, landings, approaches or hours in so many days). Optional reminders two weeks before any of them lapses. Night is computed from civil twilight at each airport (14 CFR 1.1).",
    "Progress toward a certificate: private, instrument, commercial and ATP (airplane) hour requirements (14 CFR 61.109, 61.65, 61.129, 61.159) counted from the logbook, free.",
    "Also free: Siri and Shortcuts (total time, currency, log a flight), a flight timer (Now for Out, Off, On and In), totals by aircraft type and by category and class, hours as decimal or hours and minutes, a duplicate finder, each flight's change history, undo after a delete, and a spreadsheet template for paper logbooks.",
    "Privacy: no account, no Blocklog server, no analytics. App Store privacy label: Data Not Collected.",
    "Runs on iPhone and iPad with iOS 17 or later and Mac with macOS 14 or later. English.",
]

CHROME = {"skip": "Skip to content", "tagline": "Every flight, every total, always yours. iPhone, iPad and Mac."}


def plain(text):
    return re.sub(r"<[^>]+>", "", text).replace("&gt;", ">").replace("&amp;", "&").replace("&nbsp;", " ").strip()


def jsonld(data):
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def page(slug, title, description, body, *, schema=(), kind="article", current="", root="",
         robots="index,follow,max-snippet:-1,max-image-preview:large"):
    url = BASE if slug == "index" else f"{BASE}{slug}.html"
    e = html.escape
    ld = "\n".join(jsonld(item) for item in schema)
    here = lambda name: ' aria-current="page"' if name == current else ""
    home = root or "./"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f8f5ec">
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Blocklog's logbook on an iPhone beside the words Every flight, every total, always yours">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}icon.png">
<link rel="apple-touch-icon" href="{root}icon.png">
<link rel="stylesheet" href="{root}style.css">
<link rel="alternate" type="text/plain" title="llms.txt" href="{root}llms.txt">
{ld}
</head>
<body>
<a class="skip" href="#main">{CHROME["skip"]}</a>
<header class="topbar">
  <div class="topbar-in">
    <a class="brand" href="{home}"><img src="{root}icon.png" alt="" width="34" height="34"><span>{NAME}</span></a>
    <nav class="nav" aria-label="Site">
      <a href="{home}#how"{here("home")}>Features</a>
      <a href="{home}#plans">Plans</a>
      <a href="{root}support.html"{here("support")}>Support</a>
      <a class="nav-cta" href="{APP}">Get the app</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer>
  <div class="in">
    <div class="foot-about">
      <a class="brand" href="{home}"><img src="{root}icon.png" alt="" width="28" height="28"><span>{NAME}</span></a>
      <p>{CHROME["tagline"]}</p>
      <p>© 2026 {NAME}. {DISCLAIMER}</p>
    </div>
    <nav aria-label="App"><p class="foot-title">App</p><a href="{APP}">App Store</a><a href="{root}support.html">Support</a><a href="{root}privacy.html"{here("privacy")}>Privacy Policy</a><a href="{root}terms.html">Terms of Use</a><a href="{root}llms.txt">llms.txt</a></nav>
  </div>
</footer>
<script src="{root}site.js"></script>
</body>
</html>
"""


def images():
    """The icon and the app's own screenshots (raw screens from scripts/store_shots.sh), as small JPEGs."""
    art = APP_REPO / "App" / "Assets.xcassets" / "AppIcon.appiconset" / "icon-ios-1024.png"
    icon = Image.open(art).convert("RGB")
    icon.resize((512, 512), Image.LANCZOS).save(ROOT / "img" / "icon-512.png", optimize=True)
    icon.resize((180, 180), Image.LANCZOS).save(ROOT / "icon.png", optimize=True)
    raw = APP_REPO / "build" / "store" / "raw"
    for scene in ["logbook", "currency", "print", "insights", "endorsements", "editor", "certificate"]:
        src = next(raw.glob(f"iphone-*-{scene}.png"), None)
        if src:
            im = Image.open(src).convert("RGB")
            im.resize((600, round(im.height * 600 / im.width)), Image.LANCZOS).save(ROOT / "img" / f"{scene}.jpg", quality=86, optimize=True)


def social_card():
    """img/og.png: 1200x630, paper-coloured, the name and promise beside the logbook screen."""
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), (248, 245, 236))
    d = ImageDraw.Draw(card)
    font = lambda size, bold=True: ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=1 if bold else 0)
    icon = Image.open(ROOT / "img" / "icon-512.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
    mask = Image.new("L", (96, 96), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 95, 95), 22, fill=255)
    card.paste(icon, (72, 76), mask)
    d.text((186, 96), NAME, font=font(56), fill=(20, 33, 61))
    y = 232
    for line, colour in [("Every flight, every total,", (20, 33, 61)), ("always yours.", (122, 31, 43))]:
        d.text((72, y), line, font=font(56), fill=colour)
        y += 70
    d.text((72, y + 26), "The pilot logbook for iPhone, iPad and Mac.", font=font(30, False), fill=(93, 100, 120))
    d.text((72, y + 66), "Free and unlimited on one device.", font=font(30, False), fill=(93, 100, 120))
    shot = Image.open(ROOT / "img" / "logbook.jpg").convert("RGB")
    sw = 300
    shot = shot.resize((sw, round(shot.height * sw / shot.width)), Image.LANCZOS)
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((W - sw - 90 + 6, 48 + 18, W - 90 + 6, 48 + shot.height + 18), 36, fill=70)
    card.paste((210, 206, 196), (0, 0), shadow.filter(ImageFilter.GaussianBlur(22)))
    smask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(smask).rounded_rectangle((0, 0, shot.width - 1, shot.height - 1), 36, fill=255)
    card.paste(shot, (W - sw - 90, 48), smask)
    card.save(ROOT / "img" / "og.png", optimize=True)


images()
social_card()

home = (PAGES / "home.html").read_text().replace("{APP}", APP)
faqs = re.findall(r"<details><summary>(.+?)</summary><p>(.+?)</p></details>", home)
home_schema = [
    {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE, "description": HOME_DESCRIPTION, "publisher": PUBLISHER, "inLanguage": "en-US"},
    {"@context": "https://schema.org", "@type": "MobileApplication", "name": APP_NAME, "alternateName": NAME, "url": BASE,
     "installUrl": APP, "downloadUrl": APP, "operatingSystem": "iOS 17.0 or later, macOS 14.0 or later", "applicationCategory": "UtilitiesApplication",
     "description": SUMMARY, "image": BASE + "img/icon-512.png",
     "screenshot": [BASE + f"img/{n}.jpg" for n in ["logbook", "currency", "print", "insights"]],
     "featureList": ["Block time, night and cross-country filled in from airports and times", "FAA currency (61.57, 61.56)",
                     "Medical certificate expiry (61.23(d)) and student solo endorsement (61.87)", "Custom currencies (NVG, company)",
                     "Currency reminders", "Progress toward private, instrument, commercial and ATP certificates",
                     "Siri and Shortcuts", "Flight timer (Out, Off, On, In)", "Totals by aircraft type and by category and class",
                     "Duplicate finder, flight history and undo",
                     "Totals for the FAA 8710 form", "LogTen, ForeFlight and MyFlightbook import", "CSV and JSON export",
                     "AC 61-65K endorsements with signatures", "Photos on flights", "Charts and a route map",
                     "Per-instructor totals", "iCloud sync (Pro)", "Mac app (Pro)",
                     "Printable FAA, EASA, UK CAA, Transport Canada and CASA logbook pages (Pro)", "Experience summary (Pro)",
                     "Multiple logbooks (Pro)", "Custom fields (Pro)"],
     "inLanguage": "en", "publisher": PUBLISHER,
     "offers": [{"@type": "Offer", "name": "Blocklog (free)", "price": "0", "priceCurrency": "USD"},
                {"@type": "Offer", "name": "Blocklog Pro, yearly", "price": "49.99", "priceCurrency": "USD"},
                {"@type": "Offer", "name": "Blocklog Pro, monthly", "price": "4.99", "priceCurrency": "USD"},
                {"@type": "Offer", "name": "Lifetime Pro", "price": "149.99", "priceCurrency": "USD"}]},
    {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faqs]},
]
(ROOT / "index.html").write_text(page("index", HOME_TITLE, HOME_DESCRIPTION, home, schema=home_schema, kind="website", current="home"))

docs = {
    "support": ("Support", "Help with Blocklog: moving from LogTen, ForeFlight or MyFlightbook, currency, sync, plans and refunds. A person answers within a day."),
    "privacy": ("Privacy Policy", "Blocklog has no account, no server and no analytics: your logbook stays on your devices and in your own iCloud."),
    "terms": ("Terms of Use", "Blocklog's terms: a record-keeping tool, your responsibility for your logbook, subscriptions, and limits of liability."),
}
for slug, (title, description) in docs.items():
    body = (PAGES / f"{slug}.body.html").read_text()
    schema = [{"@context": "https://schema.org", "@type": "WebPage", "name": f"{NAME} {title.lower()}", "url": f"{BASE}{slug}.html",
               "dateModified": UPDATED, "publisher": PUBLISHER, "inLanguage": "en-US"}]
    if slug == "support":
        qa = re.findall(r"<details><summary>(.+?)</summary><p>(.+?)</p></details>", body)
        schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in qa]})
    (ROOT / f"{slug}.html").write_text(page(slug, f"{title} · {NAME}", description, f'<div class="doc">\n{body}</div>', current=slug, schema=schema))

missing = '<div class="doc"><h1>Page not found</h1><p>That page has moved or never existed.</p><p><a href="/blocklog-site/">Go to Blocklog\'s home page</a> or <a href="/blocklog-site/support.html">get support</a>.</p></div>'
(ROOT / "404.html").write_text(page("404", f"Page not found · {NAME}", "This page could not be found.", missing, robots="noindex", root="/blocklog-site/"))

urls = [(BASE, "1.0"), (f"{BASE}support.html", "0.6"), (f"{BASE}privacy.html", "0.3"), (f"{BASE}terms.html", "0.3")]
entries = "".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED}</lastmod><priority>{p}</priority></url>\n" for u, p in urls)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n')
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
facts = "\n".join(f"- {f}" for f in FACTS)
qa = "\n\n".join(f"### {plain(q)}\n\n{plain(a)}" for q, a in faqs)
(ROOT / "llms.txt").write_text(f"""# {NAME}

> {SUMMARY}

{DISCLAIMER} Facts checked on {UPDATED_LONG}.

## Key facts

{facts}

## Questions and answers

{qa}

## Pages

- [App Store listing]({APP}): {APP_NAME}, for iPhone, iPad and Mac
- [Home page]({BASE}): What Blocklog does, plans and questions
- [Support]({BASE}support.html): Moving logbooks, currency, sync, plans and refunds
- [Privacy Policy]({BASE}privacy.html): No account, no server, no analytics
- [Terms of Use]({BASE}terms.html): Blocklog's terms, on top of Apple's standard licence agreement ({EULA})
""")
(ROOT / ".nojekyll").write_text("")
print("built home, support, privacy, terms, 404, sitemap, llms.txt")

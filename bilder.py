#!/usr/bin/env python3
"""Erzeugt die teilbaren Bilder aus den Daten. Aufruf im Projektordner: python3 bilder.py

- assets/og/branche-<slug>.png: Open-Graph-Bild 1200x630 pro Branche (Branchenname und Kurztext aus
  branchen.json bzw. artikel.json), im Markenstil mit Syne/Inter und Akzentfarbe
- assets/ablauf/<slug>.png: die Ablauf-Kette der Branchen mit Abschnitt "Was sich automatisieren lässt" als Bild

Werkzeug für die Entwicklung, nicht für build.py: braucht Playwright mit Chromium. build.py bindet die Bilder ein,
sobald die Dateien vorhanden sind. Nach Änderungen an Branchennamen, Kurztexten oder Ketten neu ausführen.
"""
import html
import json
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
SCHRIFTEN = (ROOT / "assets" / "schriften").as_uri()
LOGO = (ROOT / "logo-web.png").as_uri()
ART = {"baustein": ("Läuft automatisch, als Entwurf", "#5b5bff", "#ffffff"), "mensch": ("Mensch entscheidet", "#ffc95c", "#07071a"),
       "spaeter": ("Später geplant", "transparent", "#3b3bd6"), "vorhanden": ("Ihre Software", "#d9d9e6", "#07071a")}

STIL = """
@font-face{font-family:'Syne';font-weight:600 800;src:url(%s/syne-latin.woff2) format('woff2')}
@font-face{font-family:'Inter';font-weight:300 500;src:url(%s/inter-latin.woff2) format('woff2')}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;color:#07071a;background:#f5f5f7;-webkit-font-smoothing:antialiased}
""" % (SCHRIFTEN, SCHRIFTEN)

OG = """<!doctype html><html lang="de-CH"><head><meta charset="utf-8"><style>%s
.og{width:1200px;height:630px;position:relative;overflow:hidden;padding:64px 72px;display:flex;flex-direction:column;
    background:radial-gradient(circle at 92%% 8%%,rgba(0,0,255,.16),transparent 42%%),#f5f5f7}
.logo{height:44px;width:auto;align-self:flex-start}
.chip{margin-top:auto;align-self:flex-start;font-size:22px;font-weight:500;color:#0000ff;background:rgba(0,0,255,.08);
      border:1px solid rgba(0,0,255,.2);border-radius:999px;padding:8px 20px}
h1{font-family:'Syne',sans-serif;font-weight:800;font-size:%dpx;line-height:1.02;letter-spacing:-.03em;margin-top:22px;max-width:1056px;white-space:nowrap}
p{font-size:30px;line-height:1.35;color:#3c3c60;margin-top:20px;max-width:960px}
.fuss{display:flex;justify-content:space-between;align-items:center;margin-top:34px;font-size:22px;color:#50507a}
.balken{position:absolute;left:0;right:0;bottom:0;height:12px;background:#0000ff}
</style></head><body><div class="og">
<img class="logo" src="%s" alt="">
<span class="chip">Branche · Schweiz</span>
<h1>%s</h1>
<p>%s</p>
<div class="fuss"><span>Digitale Werkzeuge für Schweizer KMU und Vereine</span><span>meyssens.ch</span></div>
<div class="balken"></div>
</div></body></html>"""

ABLAUF = """<!doctype html><html lang="de-CH"><head><meta charset="utf-8"><style>%s
.ablauf{width:1200px;padding:56px 64px 48px;background:#ffffff}
.kopf{display:flex;justify-content:space-between;align-items:flex-start;gap:24px}
.logo{height:34px;width:auto}
.label{font-size:18px;font-weight:500;color:#0000ff;letter-spacing:.08em;text-transform:uppercase}
h1{font-family:'Syne',sans-serif;font-weight:800;font-size:46px;line-height:1.08;letter-spacing:-.03em;margin:10px 0 26px}
.legende{display:flex;flex-wrap:wrap;gap:10px 22px;margin-bottom:28px;font-size:17px;color:#3c3c60}
.legende span{display:inline-flex;align-items:center;gap:8px}
.punkt{width:16px;height:16px;border-radius:50%%;border:2px solid transparent;display:inline-block}
ol{list-style:none;position:relative}
ol::before{content:"";position:absolute;left:23px;top:24px;bottom:24px;width:3px;background:#c9c9ff}
li{position:relative;display:grid;grid-template-columns:48px 1fr;column-gap:22px;padding-bottom:16px}
.nr{width:48px;height:48px;border-radius:50%%;display:grid;place-items:center;font-family:'Inter',sans-serif;font-weight:600;font-size:20px;position:relative;z-index:1}
.karte{border:1px solid #e3e3ef;border-left:5px solid;border-radius:16px;padding:14px 18px;background:#fafaff}
.art{font-size:14px;font-weight:600;letter-spacing:.06em;text-transform:uppercase}
h2{font-size:22px;font-weight:600;margin:4px 0 4px}
.karte p{font-size:18px;line-height:1.45;color:#3c3c60}
.fuss{display:flex;justify-content:space-between;margin-top:22px;padding-top:18px;border-top:1px solid #e3e3ef;font-size:16px;color:#50507a}
</style></head><body><div class="ablauf" id="bild">
<div class="kopf"><div><span class="label">Ablauf · %s</span><h1>%s</h1></div><img class="logo" src="%s" alt=""></div>
<div class="legende">%s</div>
<ol>%s</ol>
<div class="fuss"><span>Einschätzung aus unserer Recherche, kein erprobter Ablauf. Entwürfe ja, automatischer Versand nein.</span><span>meyssens.ch</span></div>
</div></body></html>"""


def punkt(art):
    _, farbe, _ = ART[art]
    rand = "#3b3bd6" if art == "spaeter" else farbe
    return '<span class="punkt" style="background:%s;border-color:%s;%s"></span>' % (
        farbe, rand, "border-style:dashed" if art == "spaeter" else "")


def main():
    branchen = json.loads((ROOT / "branchen.json").read_text(encoding="utf-8"))
    artikel = json.loads((ROOT / "artikel.json").read_text(encoding="utf-8"))
    eintraege = [(b["slug"], b["name"], b["kurz"]) for b in branchen]
    eintraege += [(a["slug"], a["name"], a["kurz"]) for a in artikel if a["art"] == "branche"]
    (ROOT / "assets" / "og").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "ablauf").mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        b = p.chromium.launch()
        seite = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)

        def zeige(inhalt):
            datei = Path(tmp) / "bild.html"
            datei.write_text(inhalt, encoding="utf-8")
            seite.goto(datei.as_uri())
            seite.evaluate("document.fonts.ready")
            seite.wait_for_timeout(150)

        for slug, name, kurz in eintraege:
            groesse = 96 if len(name) <= 18 else 80 if len(name) <= 26 else 66
            zeige(OG % (STIL, groesse, LOGO, html.escape(name), html.escape(kurz)))
            # Titel auf eine Zeile einpassen: Syne ist breit, lange Namen werden verkleinert
            seite.evaluate("""() => { const h = document.querySelector('h1'); let g = parseFloat(getComputedStyle(h).fontSize);
                while (h.scrollWidth > 1056 && g > 40) { g -= 2; h.style.fontSize = g + 'px'; } }""")
            ziel = ROOT / "assets" / "og" / ("branche-%s.png" % slug)
            seite.screenshot(path=str(ziel), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
            print("geschrieben:", ziel.relative_to(ROOT))

        for a in (a for a in artikel if a.get("automatisierung")):
            k = a["automatisierung"]["kette"]
            arten = []
            for st in k["schritte"]:
                if st["art"] not in arten:
                    arten.append(st["art"])
            legende = "".join("<span>%s%s</span>" % (punkt(x), ART[x][0]) for x in arten)
            schritte = []
            for i, st in enumerate(k["schritte"], 1):
                text, farbe, schrift = ART[st["art"]]
                rand = "#3b3bd6" if st["art"] == "spaeter" else farbe
                schritte.append(
                    '<li><span class="nr" style="background:%s;color:%s;border:2px %s %s">%d</span>'
                    '<div class="karte" style="border-left-color:%s"><span class="art" style="color:%s">%s</span>'
                    '<h2>%s</h2><p>%s</p></div></li>'
                    % ("#ffffff" if st["art"] == "spaeter" else farbe, schrift if st["art"] != "spaeter" else "#3b3bd6",
                       "dashed" if st["art"] == "spaeter" else "solid", rand, i, rand,
                       "#3b3bd6" if st["art"] in ("spaeter", "baustein") else "#6b4100" if st["art"] == "mensch" else "#3c3c60",
                       text, html.escape(st["titel"]), html.escape(st["beispiel"])))
            zeige(ABLAUF % (STIL, html.escape(a["name"]), html.escape(k["titel"]), LOGO, legende, "".join(schritte)))
            ziel = ROOT / "assets" / "ablauf" / ("%s.png" % a["slug"])
            seite.locator("#bild").screenshot(path=str(ziel))
            print("geschrieben:", ziel.relative_to(ROOT))
        b.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tests für die Gratis-Werkzeuge unter /werkzeuge/ (ausser QR-Rechnung: test_qr_rechnung.py).

Aufruf: python3 test_werkzeuge.py [--basis http://127.0.0.1:8769]
1. Regeln in werkzeuge.py gegen erwartete Werte aus amtlichen Quellen (unabhängig abgetippt, siehe ERWARTET_*).
2. Browser (Playwright): die Rechenlogik der Seite liefert dieselben Werte wie die Python-Regeln.
3. Jede Werkzeugseite: CSP ohne Verbindungen nach aussen, kein Cookie-Banner, keine Statistik, Hinweis «keine Rechts- oder
   Steuerberatung», Quellen mit Prüfdatum, JSON-LD (WebApplication, FAQPage), Gesprächsknopf mit Kampagnenlink, Sitemap,
   keine Anfragen an fremde Server, keine Konsolenfehler, kein seitlicher Überlauf (320 bis 1920 px).
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

import werkzeuge as W

ROOT = Path(__file__).resolve().parent
BASIS = sys.argv[sys.argv.index("--basis") + 1] if "--basis" in sys.argv else "http://127.0.0.1:8769"
fehler = []


def pruefe(bedingung, text):
    if not bedingung:
        fehler.append(text)


# --- 1. Feiertage 2027: Daten aus den kantonalen Gesetzen (Recherche 24.11.2026, Quellen auf der Seite) ---
ERWARTET_FEIERTAGE_2027 = {
    "BS": "01-01 03-26 03-29 05-01 05-06 05-17 08-01 12-25 12-26",
    "BL": "01-01 03-26 03-29 05-01 05-06 05-17 08-01 12-25 12-26",
    "ZH": "01-01 03-26 03-29 05-01 05-06 05-17 08-01 12-25 12-26",
    "BE": "01-01 01-02 03-26 03-29 05-06 05-17 08-01 12-25 12-26",
    "SO": "01-01 03-26 05-01 05-06 05-27 08-01 08-15 11-01 12-25",
    "SO-BU": "01-01 03-26 05-01 05-06 08-01 12-25",
    "AG-A": "01-01 01-02 03-26 03-29 05-06 05-17 08-01 12-25 12-26",
    "AG-B": "01-01 03-26 03-29 05-06 05-17 05-27 08-01 12-25 12-26",
    "AG-C": "01-01 03-26 05-06 05-27 08-01 08-15 11-01 12-25 12-26",
    "AG-D": "01-01 03-26 05-06 05-27 08-01 08-15 11-01 12-08 12-25",
    "AG-E": "01-01 03-26 03-29 05-06 05-17 08-01 11-01 12-25 12-26",
    "AG-F": "01-01 01-02 03-26 05-06 05-27 08-01 11-01 12-25 12-26",
}
REGIONEN = {r["id"]: r for k in W.KANTONE for r in k["regionen"]}
pruefe(W.ostersonntag(2027) == dt.date(2027, 3, 28), "Ostersonntag 2027 falsch")
for jahr, erwartet in ((2024, dt.date(2024, 3, 31)), (2025, dt.date(2025, 4, 20)), (2026, dt.date(2026, 4, 5)), (2028, dt.date(2028, 4, 16))):
    pruefe(W.ostersonntag(jahr) == erwartet, "Ostersonntag %d falsch" % jahr)
pruefe(set(REGIONEN) == set(ERWARTET_FEIERTAGE_2027), "Regionen stimmen nicht mit den erwarteten überein")
for rid, erwartet in ERWARTET_FEIERTAGE_2027.items():
    ist = " ".join(sorted(W.feiertag_datum(s, 2027).strftime("%m-%d") for s in REGIONEN[rid]["tage"]))
    pruefe(ist == erwartet, "Feiertage 2027 %s: %s statt %s" % (rid, ist, erwartet))
# 2027: 261 Werktage; Beispiel Mai 2027 BL = 19 (auf der Seite)
pruefe(W.arbeitstage(REGIONEN["BL"], dt.date(2027, 1, 1), dt.date(2027, 12, 31)) == 256, "BL 2027 nicht 256")
pruefe(W.arbeitstage(REGIONEN["BL"], dt.date(2027, 5, 1), dt.date(2027, 5, 31)) == 19, "BL Mai 2027 nicht 19")
pruefe(W.arbeitstage(REGIONEN["SO-BU"], dt.date(2027, 1, 1), dt.date(2027, 12, 31)) == 258, "SO Bucheggberg 2027 nicht 258")
# halber Feiertag: SO, 1. Mai 2026 ist ein Freitag
pruefe(W.arbeitstage(REGIONEN["SO"], dt.date(2026, 5, 1), dt.date(2026, 5, 1)) == 0.5, "SO 1. Mai 2026 nicht halber Tag")

# --- Seitenprüfung (alle Werkzeuge) ---
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")


def seite_statisch(w):
    pfad = ROOT / w["pfad"].strip("/") / "index.html"
    t = pfad.read_text(encoding="utf-8")
    n = w["name"]
    pruefe("connect-src 'none'" in t, "%s: CSP ohne connect-src 'none'" % n)
    pruefe("cookie-banner" not in t and "googletagmanager" not in t and "dataLayer" not in t, "%s: Cookie-Banner oder Statistik" % n)
    pruefe("Keine Rechts- oder Steuerberatung" in t, "%s: Hinweis keine Rechts- oder Steuerberatung fehlt" % n)
    pruefe("Zuletzt geprüft am %s" % dt.date.fromisoformat(w["geprueft"]).strftime("%d.%m.%Y") in t, "%s: Prüfdatum fehlt" % n)
    pruefe(t.count("<h1") == 1, "%s: nicht genau eine H1" % n)
    pruefe("utm_campaign=%s#anfrage" % w["slug"] in t, "%s: Gesprächsknopf mit Kampagnenlink fehlt" % n)
    pruefe("<loc>https://meyssens.ch%s</loc>" % w["pfad"] in sitemap, "%s: nicht in der Sitemap" % n)
    lds = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
    typen = {g.get("@type") for x in lds for g in x.get("@graph", [x])}
    pruefe({"WebApplication", "FAQPage", "BreadcrumbList"} <= typen, "%s: JSON-LD unvollständig: %s" % (n, typen))
    pruefe("ß" not in re.sub(r"<script.*?</script>", "", t, flags=re.S), "%s: ß" % n)
    pruefe("{{" not in t and "<!-- at-" not in t, "%s: Platzhalter übrig" % n)
    for u in re.findall(r'<a href="(https?://[^"]+)"', t):
        pruefe(u.startswith("https://"), "%s: Quelle ohne https: %s" % (n, u))


def seite_browser(seite_neu, w):
    n = w["name"]
    for breite in (320, 390, 768, 1440, 1920):
        pg, fremd, konsole = seite_neu(breite)
        pg.goto(BASIS + w["pfad"], wait_until="load")
        pg.wait_for_timeout(500)
        sw = pg.evaluate("document.documentElement.scrollWidth")
        pruefe(sw <= breite, "%s %dpx: seitlicher Überlauf (%d)" % (n, breite, sw))
        pruefe(not fremd, "%s %dpx: Anfragen an fremde Server: %s" % (n, breite, fremd[:3]))
        pruefe(not konsole, "%s %dpx: Konsolenfehler: %s" % (n, breite, konsole[:2]))
        pruefe(pg.evaluate("document.cookie") == "", "%s: Cookie gesetzt" % n)
        pg.close()


def arbeitstage_browser(seite_neu):
    pg, _, _ = seite_neu(1440)
    pg.goto(BASIS + "/werkzeuge/arbeitstage/", wait_until="load")
    pg.wait_for_function("window.Arbeitstage")
    daten = json.loads(pg.text_content("#at-daten"))
    faelle = [(dt.date(2027, 1, 1), dt.date(2027, 12, 31)), (dt.date(2026, 1, 1), dt.date(2028, 12, 31)),
              (dt.date(2027, 5, 1), dt.date(2027, 5, 31)), (dt.date(2026, 4, 30), dt.date(2026, 5, 4))]
    for k in daten["kantone"]:
        for r in k["regionen"]:
            for von, bis in faelle:
                js = pg.evaluate("([d, r, v, b]) => Arbeitstage.rechne(d, r, Arbeitstage.utc(...v), Arbeitstage.utc(...b), [1,2,3,4,5], []).arbeitstage",
                                 [daten, r, [von.year, von.month, von.day], [bis.year, bis.month, bis.day]])
                py = W.arbeitstage(REGIONEN[r["id"]], von, bis)
                pruefe(js == py, "Arbeitstage %s %s–%s: Browser %s, Python %s" % (r["id"], von, bis, js, py))
    # Bedienung: Kanton Aargau, Region Baden, Jahr 2027 = 255; Zusatztag 2. Januar ändert nichts (Samstag)
    pg.select_option("#at-kanton", "AG")
    pg.select_option("#at-region", "AG-B")
    pruefe(pg.text_content(".at-zahl strong") == "255", "Bedienung AG-B 2027 nicht 255: %s" % pg.text_content(".at-zahl strong"))
    pg.check('input[name="at-extra"][value="12-24-0.5"]')   # 24.12.2027 = Freitag
    pruefe(pg.text_content(".at-zahl strong") == "254,5", "Zusatz 24.12. Nachmittag nicht abgezogen: %s" % pg.text_content(".at-zahl strong"))
    pg.fill("#at-bis", "2026-01-01")
    pruefe("vor dem Startdatum" in pg.text_content("#at-meldung"), "keine Meldung bei Enddatum vor Startdatum")
    pg.close()


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()

        def seite_neu(breite):
            ctx = b.new_context(viewport={"width": breite, "height": 900})
            pg = ctx.new_page()
            fremd, konsole = [], []
            pg.on("request", lambda r: fremd.append(r.url) if not r.url.startswith((BASIS, "data:", "blob:")) else None)
            pg.on("console", lambda m: konsole.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: konsole.append(str(e)))
            return pg, fremd, konsole

        for w in W.WERKZEUGE:
            seite_statisch(w)
            seite_browser(seite_neu, w)
        arbeitstage_browser(seite_neu)
        b.close()
    print("%d Werkzeuge geprüft" % len(W.WERKZEUGE))
    if fehler:
        print("FEHLER:\n" + "\n".join(fehler))
        sys.exit(1)
    print("Alles in Ordnung.")


if __name__ == "__main__":
    main()

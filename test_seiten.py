#!/usr/bin/env python3
"""Prüft die erzeugten Seiten. Aufruf nach build.py im Projektordner: python3 test_seiten.py

- Alle internen Links (href/src mit /) zeigen auf eine vorhandene Datei, Anker auf eine vorhandene id
- Kein Platzhalter "[Status" und kein ß auf den Langtext-Seiten
- Wortzahl der Langtext-Seiten zwischen 1500 und 2200
- JSON-LD gültig, Article und FAQPage vorhanden, FAQPage entspricht den sichtbaren Fragen
- Hinweis "keine Rechtsberatung" und "zuletzt geprüft am" vorhanden, genau 4 Weiterlesen-Links
- Jede Langtext-Seite steht in der sitemap.xml
- Abschnitt "Was sich automatisieren lässt" (Branchenseiten mit Feld "automatisierung"): 3 bis 4 Bausteinkarten
  mit je einem Formular, Ablauf-Kette, Demo mit "Beispiel", Regel, Hinweise, Wortzahl
- Bausteinseiten (produkte.json mit Feld "branche"): Hinweise, Regel, Status, Einschätzung, bei Personendaten
  Auftragsbearbeitung/Schweiz/Datenminimierung, kein ß, Wortzahl, Sitemap, verlinkt von Branchenseite und Übersicht
- Keine Platzhalter ({{...}}, [Status, TODO, Lorem) auf irgendeiner Seite
Nur Python-Standardbibliothek.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from build import (ARTEN, AUTO_WORTE, BAUSTEIN_WORTE, BEDINGUNGEN, REGEL, WORTE, ist_baustein, ohne_automatisierung,
                   worte, zwischen)

ROOT = Path(__file__).resolve().parent
fehler = []


class Seite(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])


def ziel_existiert(pfad):
    p = ROOT / pfad.lstrip("/")
    return (p / "index.html").is_file() if pfad.endswith("/") else p.is_file()


seiten = {}
for datei in sorted(ROOT.rglob("index.html")):
    if ".git" in datei.parts:
        continue
    rel = datei.parent.relative_to(ROOT)
    url = "/" if rel == Path(".") else "/%s/" % rel.as_posix()
    parser = Seite()
    text = datei.read_text(encoding="utf-8")
    parser.feed(text)
    seiten[url] = (text, parser)

geprueft = 0
for url, (text, parser) in seiten.items():
    for link in parser.links:
        if link.startswith("//") or not link.startswith(("/", "#")):
            continue
        pfad, _, anker = link.partition("#")
        pfad = pfad.split("?")[0]
        if pfad and not ziel_existiert(pfad):
            fehler.append("%s: Link ins Leere %s" % (url, link))
        if anker and anker not in (seiten.get(pfad or url, (None, Seite()))[1].ids | {"datenschutz", "impressum"}):
            fehler.append("%s: Anker fehlt %s" % (url, link))
        geprueft += 1

artikel = json.loads((ROOT / "artikel.json").read_text(encoding="utf-8"))
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
print("%-42s %s" % ("Seite", "Wörter"))
for a in artikel:
    url = "/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"])
    if url not in seiten:
        fehler.append("%s: Seite fehlt" % url)
        continue
    text, parser = seiten[url]
    sichtbar = html.unescape(re.sub(r"<script.*?</script>|<[^>]+>", " ", text, flags=re.S))
    for muss in ("Allgemeine Information, keine Rechtsberatung", "zuletzt geprüft am 25.10.2026"):
        if muss not in sichtbar:
            fehler.append("%s: Hinweis fehlt: %s" % (url, muss))
    if "[Status" in sichtbar or "ß" in sichtbar:
        fehler.append("%s: Platzhalter [Status ...] oder ß" % url)
    weiter = zwischen(text, '<section id="weiterlesen">', "</section>")
    if len(re.findall(r'<a href="/', weiter)) != 4:
        fehler.append("%s: nicht genau 4 Weiterlesen-Links" % url)
    n = worte(ohne_automatisierung(zwischen(text, '<main id="main"', '<section id="quellen"')))
    if not WORTE[0] <= n <= WORTE[1]:
        fehler.append("%s: %d Wörter" % (url, n))
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S).group(1))
    typen = {g["@type"]: g for g in ld["@graph"]}
    if not {"Article", "FAQPage", "BreadcrumbList"} <= set(typen):
        fehler.append("%s: JSON-LD unvollständig %s" % (url, sorted(typen)))
    elif [q["name"] for q in typen["FAQPage"]["mainEntity"]] != [q["frage"] for q in a["faq"]]:
        fehler.append("%s: FAQPage weicht von den sichtbaren Fragen ab" % url)
    if "<loc>https://meyssens.ch%s</loc>" % url not in sitemap:
        fehler.append("%s: fehlt in sitemap.xml" % url)
    print("%-42s %d" % (url, n))


def sichtbar_text(t):
    # Sichtbarer Text mit einfachen Leerzeichen, klein geschrieben (für den Vergleich mit Pflichtsätzen)
    t = html.unescape(re.sub(r"<script.*?</script>|<[^>]+>", " ", t, flags=re.S))
    return re.sub(r"\s+", " ", re.sub(r"\s+([.,:;])", r"\1", t)).lower()


for url, (text, parser) in seiten.items():
    for muster in ("{{", "[Status", "TODO", "Lorem"):
        if muster in text:
            fehler.append("%s: Platzhalter %s" % (url, muster))

produkte = json.loads((ROOT / "produkte.json").read_text(encoding="utf-8"))
nach_slug = {p["slug"]: p for p in produkte}
regel = " ".join(REGEL)
geprueft_neu = "zuletzt geprüft am 26.10.2026"
uebersicht = seiten.get("/unternehmen/", ("", None))[0]
for a in artikel:
    au = a.get("automatisierung")
    if not au:
        continue
    url = "/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"])
    text = seiten[url][0]
    if '<section id="automatisierung"' not in text:
        fehler.append("%s: Abschnitt automatisierung fehlt" % url)
        continue
    teil = zwischen(text, '<section id="automatisierung"', "</section>")
    s = sichtbar_text(teil)
    karten = teil.count('<article class="baustein-karte')
    if not 3 <= karten <= 4 or karten != len(au["bausteine"]):
        fehler.append("%s: %d Bausteinkarten" % (url, karten))
    if teil.count("<form ") != karten or teil.count('name="baustein"') != karten:
        fehler.append("%s: nicht genau ein Formular pro Baustein" % url)
    for slug in au["bausteine"]:
        if 'href="/produkte/%s/"' % slug not in teil:
            fehler.append("%s: kein Link auf /produkte/%s/" % (url, slug))
    if '<ol class="kette">' not in teil or teil.count('class="kette-schritt') < 4:
        fehler.append("%s: Ablauf-Kette fehlt" % url)
    if '<span class="beispiel">Beispiel</span>' not in teil or "data-wahl" not in teil:
        fehler.append("%s: Demo mit Beschriftung Beispiel fehlt" % url)
    for muss in ("Was sich automatisieren lässt", regel, "keine Rechtsberatung", geprueft_neu, "Einschätzung",
                 "in Planung", "keine Kunden und keine Referenzen"):
        if muss.lower() not in s:
            fehler.append("%s#automatisierung: fehlt: %s" % (url, muss))
    if "ß" in s:
        fehler.append("%s#automatisierung: ß" % url)
    n = worte(teil)
    if not AUTO_WORTE[0] <= n <= AUTO_WORTE[1]:
        fehler.append("%s#automatisierung: %d Wörter" % (url, n))
    if 'href="#automatisierung"' not in text:
        fehler.append("%s: Inhaltsverzeichnis ohne Eintrag zum Abschnitt" % url)
    print("%-42s %d" % (url + "#automatisierung", n))

for p in (p for p in produkte if ist_baustein(p)):
    url = "/produkte/%s/" % p["slug"]
    if url not in seiten:
        fehler.append("%s: Seite fehlt" % url)
        continue
    text = seiten[url][0]
    s = sichtbar_text(text)
    muss = ["Allgemeine Information, keine Rechtsberatung", geprueft_neu, regel, "Einschätzung", p["status"]]
    if p["personendaten"]:
        muss += list(BEDINGUNGEN)
    for m in muss:
        if m.lower() not in s:
            fehler.append("%s: fehlt: %s" % (url, m))
    if p["status"] not in ("Pilotphase", "In Planung"):
        fehler.append("%s: Status %s" % (url, p["status"]))
    if "ß" in s:
        fehler.append("%s: ß" % url)
    n = worte(zwischen(text, '<main id="main"', '<section id="quellen"'))
    if not BAUSTEIN_WORTE[0] <= n <= BAUSTEIN_WORTE[1]:
        fehler.append("%s: %d Wörter" % (url, n))
    if "<loc>https://meyssens.ch%s</loc>" % url not in sitemap:
        fehler.append("%s: fehlt in sitemap.xml" % url)
    if 'href="%s"' % url not in seiten.get("/branchen/%s/" % p["branche"], ("",))[0]:
        fehler.append("%s: nicht von der Branchenseite verlinkt" % url)
    if 'href="%s"' % url not in uebersicht:
        fehler.append("%s: nicht von der Produktübersicht verlinkt" % url)
    if '<span class="beispiel">' not in text:
        fehler.append("%s: Ansicht ohne Beschriftung Beispiel" % url)
    print("%-42s %d" % (url, n))

print("\n%d Seiten, %d interne Links geprüft" % (len(seiten), geprueft))
if fehler:
    print("\nFEHLER:\n" + "\n".join(fehler))
    sys.exit(1)
print("Alles in Ordnung.")

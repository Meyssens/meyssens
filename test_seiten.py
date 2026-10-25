#!/usr/bin/env python3
"""Prüft die erzeugten Seiten. Aufruf nach build.py im Projektordner: python3 test_seiten.py

- Alle internen Links (href/src mit /) zeigen auf eine vorhandene Datei, Anker auf eine vorhandene id
- Kein Platzhalter "[Status" und kein ß auf den Langtext-Seiten
- Wortzahl der Langtext-Seiten zwischen 1500 und 2200
- JSON-LD gültig, Article und FAQPage vorhanden, FAQPage entspricht den sichtbaren Fragen
- Hinweis "keine Rechtsberatung" und "zuletzt geprüft am" vorhanden, genau 4 Weiterlesen-Links
- Jede Langtext-Seite steht in der sitemap.xml
Nur Python-Standardbibliothek.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from build import ARTEN, WORTE, worte, zwischen

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
    n = worte(zwischen(text, '<main id="main"', '<section id="quellen"'))
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

print("\n%d Seiten, %d interne Links geprüft" % (len(seiten), geprueft))
if fehler:
    print("\nFEHLER:\n" + "\n".join(fehler))
    sys.exit(1)
print("Alles in Ordnung.")

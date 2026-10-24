#!/usr/bin/env python3
"""Erzeugt die Produktseiten, die Übersicht für Unternehmen und Vereine und die sitemap.xml.

Aufruf im Projektordner: python3 build.py
Nur Python-Standardbibliothek.

Quellen:
  produkte.json            Produktdaten
  vorlage_produkt.html     Vorlage für produkte/<slug>/index.html
  vorlage_unternehmen.html Vorlage für unternehmen/index.html
  index.html               Kopfbereich, Header, Footer, Cookie-Banner, Impressum, Datenschutz, Skripte
                           (Abschnitte zwischen <!-- name:start --> und <!-- name:ende -->)
  gemeinden/index.html     Formspree-Ziel, Einwilligung und Formular-Skript des bestehenden Kontaktformulars
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAIN = "https://meyssens.ch"
FELDER = ("slug", "name", "kurzbeschreibung", "problem", "loesung", "fuer_wen", "status")
PFEIL = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7h10M8 3l4 4-4 4" '
         'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def lies(pfad):
    return (ROOT / pfad).read_text(encoding="utf-8")


def abschnitt(text, name):
    m = re.search(r"<!-- %s:start -->\n(.*?)<!-- %s:ende -->" % (name, name), text, re.S)
    if not m:
        raise SystemExit("Abschnitt %s fehlt in index.html" % name)
    return m.group(1).rstrip("\n")


def zwischen(text, start, ende, mit_ende=False):
    i = text.index(start)
    j = text.index(ende, i)
    return text[i:j + (len(ende) if mit_ende else 0)]


def fuelle(vorlage, werte):
    def ersetze(m):
        if m.group(1) not in werte:
            raise SystemExit("Platzhalter ohne Wert: %s" % m.group(1))
        return werte[m.group(1)]
    return re.sub(r"\{\{(\w+)\}\}", ersetze, vorlage)


def schreibe(pfad, inhalt):
    ziel = ROOT / pfad
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(inhalt, encoding="utf-8")
    print("geschrieben:", pfad)


def kurz(text, laenge=155):
    # Meta-Beschreibung: ganze Sätze bis zur Länge, mindestens der erste Satz
    saetze = re.split(r"(?<=[.!?])\s+", text)
    out = saetze[0]
    for s in saetze[1:]:
        if len(out) + 1 + len(s) > laenge:
            break
        out += " " + s
    return out


def main():
    produkte = json.loads(lies("produkte.json"))
    slugs = set()
    for p in produkte:
        fehlt = [f for f in FELDER if not str(p.get(f, "")).strip()]
        if fehlt:
            raise SystemExit("%s: Felder fehlen: %s" % (p.get("slug", "?"), ", ".join(fehlt)))
        if not re.fullmatch(r"[a-z0-9-]+", p["slug"]) or p["slug"] in slugs:
            raise SystemExit("Ungültiger oder doppelter Slug: %s" % p["slug"])
        slugs.add(p["slug"])

    start = lies("index.html")
    gemeinden = lies("gemeinden/index.html")
    gemeinsam = {name: abschnitt(start, name) for name in ("head", "kopf", "fuss", "rechtliches", "skripte")}

    # Kontaktformular der Gemeinden-Seite: gleiches Ziel, gleiche Einwilligung, gleiches Absende-Skript
    formular_ziel = re.search(r'<form action="(https://formspree\.io/[^"]+)"', gemeinden).group(1)
    einwilligung = zwischen(gemeinden, '<div class="fgrp"><label style="display:flex', "</label></div>", True)
    if 'name="datenschutz-gelesen"' not in einwilligung:
        raise SystemExit("Einwilligung im Gemeinden-Formular nicht gefunden")
    formular_skript = zwischen(gemeinden, "// --- Kontaktformular", "</script>")

    vorlage_produkt = lies("vorlage_produkt.html")
    kacheln = []
    for p in produkte:
        e = {k: html.escape(str(v)) for k, v in p.items()}
        url = "%s/produkte/%s/" % (DOMAIN, p["slug"])
        hinweis = ""
        if p.get("hinweis"):
            hinweis = '  <div class="note">%s</div>' % e["hinweis"]
        werte = dict(gemeinsam, **{
            "titel": html.escape("%s – Meyssens" % p["name"]),
            "beschreibung": html.escape(kurz(p["kurzbeschreibung"])),
            "url": url,
            "name": e["name"],
            "status": e["status"],
            "kurzbeschreibung": e["kurzbeschreibung"],
            "problem": e["problem"],
            "loesung": e["loesung"],
            "fuer_wen": e["fuer_wen"],
            "hinweis": hinweis,
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        schreibe("produkte/%s/index.html" % p["slug"], fuelle(vorlage_produkt, werte))
        kacheln.append(
            '    <a href="/produkte/%s/" class="feat tile">\n'
            '      <span class="status-chip">%s</span>\n'
            '      <h3>%s</h3>\n'
            '      <p>%s</p>\n'
            '      <span class="way-go">Mehr erfahren %s</span>\n'
            '    </a>' % (p["slug"], e["status"], e["name"], e["kurzbeschreibung"], PFEIL))

    werte = dict(gemeinsam, **{
        "titel": "Für Unternehmen und Vereine – Meyssens",
        "beschreibung": html.escape("Digitale Werkzeuge für Unternehmen und Vereine: Umfragen, Newsletter, "
                                    "Vereinswebsite, Mail-Assistent und mehr. In Vorbereitung, jetzt vormerken."),
        "url": DOMAIN + "/unternehmen/",
        "kacheln": "\n".join(kacheln),
    })
    schreibe("unternehmen/index.html", fuelle(lies("vorlage_unternehmen.html"), werte))

    # Verwaiste Produktordner nur melden, nicht löschen
    for d in sorted((ROOT / "produkte").iterdir()):
        if d.is_dir() and d.name not in slugs:
            print("Hinweis: produkte/%s steht nicht in produkte.json" % d.name)

    heute = datetime.date.today().isoformat()
    seiten = [("/", "1.0"), ("/gemeinden/", "0.9"), ("/unternehmen/", "0.8")]
    seiten += [("/produkte/%s/" % p["slug"], "0.6") for p in produkte]
    zeilen = ["  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>%s</priority></url>"
              % (DOMAIN, pfad, heute, prio) for pfad, prio in seiten]
    schreibe("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(zeilen) + "\n</urlset>\n")


if __name__ == "__main__":
    main()

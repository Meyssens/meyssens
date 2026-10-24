#!/usr/bin/env python3
"""Erzeugt die Produktseiten, die Übersicht für Unternehmen und Vereine und die sitemap.xml.

Aufruf im Projektordner: python3 build.py
Nur Python-Standardbibliothek.

Quellen:
  produkte.json            Produktdaten
  branchen.json            Branchendaten
  vorlage_branche.html     Vorlage für branchen/<slug>/index.html
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
# Status-Stufen: Badge, Hinweistext und Formularknopf
STUFEN = {
    "Pilotphase": {
        "badge": "Pilotphase, Pilotpartner gesucht",
        "text": "Wir starten jetzt mit der Umsetzung und suchen drei Pilotpartner. "
                "Sie erhalten die Einrichtung kostenlos und gestalten das Produkt mit.",
        "knopf": "Pilotpartner werden",
    },
    "In Planung": {
        "badge": "In Planung",
        "text": "Dieses Produkt ist in Planung. Mit Ihrer Anfrage merken wir Sie unverbindlich vor.",
        "knopf": "Unverbindlich vormerken",
    },
}
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


def kachel(p):
    # Produktkachel mit Status-Badge, für die Unternehmen-Seite und die Branchenseiten
    e = {k: html.escape(str(v)) for k, v in p.items()}
    return ('    <a href="/produkte/%s/" class="feat tile">\n'
            '      <span class="status-chip">%s</span>\n'
            '      <h3>%s</h3>\n'
            '      <p>%s</p>\n'
            '      <span class="way-go">Mehr erfahren %s</span>\n'
            '    </a>' % (p["slug"], html.escape(STUFEN[p["status"]]["badge"]), e["name"], e["kurzbeschreibung"], PFEIL))


def karte(tag, titel, text):
    return ('    <div class="feat">\n'
            '%s'
            '      <h3>%s</h3>\n'
            '      <p>%s</p>\n'
            '    </div>' % ('      <div class="feat-tag-row">%s</div>\n' % tag if tag else "", html.escape(titel), html.escape(text)))


def demo(d, art):
    # Optionaler Verweis auf eine Beispielplattform (Feld "demo"), ohne Tracking, öffnet im neuen Tab.
    # Seiten ohne Feld bleiben unverändert (leerer Platzhalter am Zeilenende).
    if not d:
        return ""
    fehlt = [f for f in ("text", "url", "hinweis") if not str(d.get(f, "")).strip()]
    if fehlt or not d["url"].startswith("https://") or (art == "branche" and not d.get("titel")):
        raise SystemExit("Feld demo unvollständig: %s" % ", ".join(fehlt or ["url/titel"]))
    e = {k: html.escape(str(v)) for k, v in d.items()}
    knopf = ('<a href="%s" class="btn-p" target="_blank" rel="noopener">Beispielplattform öffnen %s'
             '<span class="sr-only"> (öffnet in neuem Tab)</span></a>' % (e["url"], PFEIL))
    if art == "branche":
        return ('\n  <div class="demo-box r" id="beispielplattform">\n'
                '    <div class="demo-box__text">\n'
                '      <h3>%s</h3>\n'
                '      <p>%s</p>\n'
                '      <p class="demo-box__hinweis"><strong>%s</strong></p>\n'
                '    </div>\n'
                '    <div class="demo-box__aktion">%s</div>\n'
                '  </div>' % (e["titel"], e["text"], e["hinweis"], knopf))
    return ('\n  <div class="note demo-note">%s <strong>%s</strong>\n'
            '    <div class="demo-note__aktion">%s</div>\n'
            '  </div>' % (e["text"], e["hinweis"], knopf))


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
        if p["status"] not in STUFEN:
            raise SystemExit("%s: unbekannter Status %r (erlaubt: %s)" % (p["slug"], p["status"], ", ".join(STUFEN)))
        if not re.fullmatch(r"[a-z0-9-]+", p["slug"]) or p["slug"] in slugs:
            raise SystemExit("Ungültiger oder doppelter Slug: %s" % p["slug"])
        slugs.add(p["slug"])
    nach_slug = {p["slug"]: p for p in produkte}

    branchen = json.loads(lies("branchen.json"))
    bslugs = set()
    for b in branchen:
        fehlt = [f for f in ("slug", "name", "fuer", "kurz", "beschreibung", "intro", "besonderheit") if not b.get(f)]
        for f, n in (("probleme", 3), ("szenarien", 3), ("faq", 3)):
            if len(b.get(f, [])) != n:
                fehlt.append("%s (genau %d)" % (f, n))
        if not 2 <= len(b.get("produkte", [])) <= 3:
            fehlt.append("produkte (2 bis 3)")
        if fehlt:
            raise SystemExit("Branche %s: %s" % (b.get("slug", "?"), ", ".join(fehlt)))
        unbekannt = [s for s in b["produkte"] if s not in nach_slug]
        if unbekannt:
            raise SystemExit("Branche %s: unbekannte Produkte %s" % (b["slug"], ", ".join(unbekannt)))
        if not re.fullmatch(r"[a-z0-9-]+", b["slug"]) or b["slug"] in bslugs:
            raise SystemExit("Ungültiger oder doppelter Branchen-Slug: %s" % b["slug"])
        bslugs.add(b["slug"])

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
        stufe = {k: html.escape(v) for k, v in STUFEN[p["status"]].items()}
        url = "%s/produkte/%s/" % (DOMAIN, p["slug"])
        hinweis = ""
        if p.get("hinweis"):
            hinweis = '  <div class="note">%s</div>' % e["hinweis"]
        werte = dict(gemeinsam, **{
            "titel": html.escape("%s – Meyssens" % p["name"]),
            "beschreibung": html.escape(kurz(p["kurzbeschreibung"])),
            "url": url,
            "name": e["name"],
            "status_badge": stufe["badge"],
            "status_text": stufe["text"],
            "knopf": stufe["knopf"],
            "kurzbeschreibung": e["kurzbeschreibung"],
            "problem": e["problem"],
            "loesung": e["loesung"],
            "fuer_wen": e["fuer_wen"],
            "hinweis": hinweis,
            "demo": demo(p.get("demo"), "produkt"),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        schreibe("produkte/%s/index.html" % p["slug"], fuelle(vorlage_produkt, werte))
        kacheln.append(kachel(p))

    vorlage_branche = lies("vorlage_branche.html")
    for b in branchen:
        fuer = b["fuer"]
        werte = dict(gemeinsam, **{
            "titel": html.escape("Digitale Infrastruktur für %s – Meyssens" % fuer),
            "beschreibung": html.escape(b["beschreibung"]),
            "url": "%s/branchen/%s/" % (DOMAIN, b["slug"]),
            "name": html.escape(b["name"]),
            "fuer": html.escape(fuer),
            "intro": html.escape(b["intro"]),
            "probleme": "\n".join(karte("", x["titel"], x["text"]) for x in b["probleme"]),
            "szenarien": "\n".join(karte("Beispielszenario", x["titel"], x["text"]) for x in b["szenarien"]),
            "demo": demo(b.get("demo"), "branche"),
            "besonderheit_titel": html.escape(b["besonderheit"]["titel"]),
            "besonderheit_text": html.escape(b["besonderheit"]["text"]),
            "produkte": "\n".join(kachel(nach_slug[s]) for s in b["produkte"]),
            "faq": "\n".join('    <div class="qa">\n      <h3>%s</h3>\n      <p>%s</p>\n    </div>'
                             % (html.escape(q["frage"]), html.escape(q["antwort"])) for q in b["faq"]),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        schreibe("branchen/%s/index.html" % b["slug"], fuelle(vorlage_branche, werte))

    werte = dict(gemeinsam, **{
        "titel": "Für Unternehmen und Vereine – Meyssens",
        "beschreibung": html.escape("Digitale Werkzeuge für Unternehmen und Vereine: Umfragen, Newsletter, "
                                    "Vereinswebsite, Mail-Assistent und mehr. Jetzt Pilotpartner werden."),
        "url": DOMAIN + "/unternehmen/",
        "kacheln": "\n".join(kacheln),
        "branchen": "\n".join('    <a href="/branchen/%s/">%s %s</a>' % (b["slug"], html.escape(b["name"]), PFEIL)
                               for b in branchen),
    })
    schreibe("unternehmen/index.html", fuelle(lies("vorlage_unternehmen.html"), werte))

    # Verwaiste Ordner nur melden, nicht löschen
    for ordner, bekannt, quelle in (("produkte", slugs, "produkte.json"), ("branchen", bslugs, "branchen.json")):
        for d in sorted((ROOT / ordner).iterdir()):
            if d.is_dir() and d.name not in bekannt:
                print("Hinweis: %s/%s steht nicht in %s" % (ordner, d.name, quelle))

    heute = datetime.date.today().isoformat()
    seiten = [("/", "1.0"), ("/gemeinden/", "0.9"), ("/unternehmen/", "0.8")]
    seiten += [("/produkte/%s/" % p["slug"], "0.6") for p in produkte]
    seiten += [("/branchen/%s/" % b["slug"], "0.6") for b in branchen]
    zeilen = ["  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>%s</priority></url>"
              % (DOMAIN, pfad, heute, prio) for pfad, prio in seiten]
    schreibe("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(zeilen) + "\n</urlset>\n")


if __name__ == "__main__":
    main()

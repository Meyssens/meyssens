#!/usr/bin/env python3
"""Erzeugt die Produktseiten, die Übersicht für Unternehmen und Vereine und die sitemap.xml.

Aufruf im Projektordner: python3 build.py
Nur Python-Standardbibliothek.

Quellen:
  produkte.json            Produktdaten
  branchen.json            Branchendaten
  artikel.json             Langtext-Seiten (Branchen und Ratgeber), Text in artikel/<slug>.html
  vorlage_artikel.html     Vorlage für branchen/<slug>/ und ratgeber/<slug>/ aus artikel.json
  vorlage_branche.html     Vorlage für branchen/<slug>/index.html
  vorlage_produkt.html     Vorlage für produkte/<slug>/index.html
  vorlage_unternehmen.html Vorlage für unternehmen/index.html
  index.html               Kopfbereich, Header, Footer, Cookie-Banner, Impressum, Datenschutz, Skripte
                           (Abschnitte zwischen <!-- name:start --> und <!-- name:ende -->).
                           Die Bereiche <!-- auto:name:start --> bis <!-- auto:name:ende --> der Startseite
                           (Produktansicht, Demos, In Planung, Zahlen) schreibt build.py selbst neu.
  ansichten.html           Demos (Pilotphase) und Beispielansichten (In Planung) im Gerätefenster
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


def teil(text, name):
    # Abschnitt aus ansichten.html oder None
    m = re.search(r"<!-- %s:start -->\n(.*?)<!-- %s:ende -->" % (name, name), text, re.S)
    return m.group(1).rstrip("\n") if m else None


def setze_auto(text, name, inhalt):
    # Ersetzt den Inhalt eines automatisch erzeugten Bereichs der Startseite
    muster = re.compile(r"(<!-- auto:%s:start -->\n).*?(<!-- auto:%s:ende -->)" % (name, name), re.S)
    if not muster.search(text):
        raise SystemExit("Bereich auto:%s fehlt in index.html" % name)
    return muster.sub(lambda m: m.group(1) + inhalt + "\n" + m.group(2), text)


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


def geraet(titel, inhalt, marke="Beispiel"):
    # Gerätefenster mit sichtbarer Beschriftung "Beispiel"
    return ('<figure class="geraet">\n'
            '  <div class="geraet-leiste"><i aria-hidden="true"></i><i aria-hidden="true"></i><i aria-hidden="true"></i>'
            '<span class="geraet-titel">%s</span><span class="beispiel">%s</span></div>\n'
            '  <div class="geraet-inhalt">\n%s\n  </div>\n'
            '</figure>' % (titel, marke, inhalt))


def ansicht(ansichten, p):
    # Pilotphase: interaktive Demo, sonst statische Beispielansicht
    demo_teil = teil(ansichten, "demo-" + p["slug"])
    inhalt = demo_teil or teil(ansichten, "ansicht-" + p["slug"])
    if not inhalt:
        raise SystemExit("ansichten.html: weder demo-%s noch ansicht-%s" % (p["slug"], p["slug"]))
    return geraet(html.escape(p["name"]), inhalt, "Beispiel" if demo_teil else "Beispielansicht"), bool(demo_teil)


def startseite(start, ansichten, produkte, anzahl_branchen, anzahl_ratgeber):
    # Automatisch erzeugte Bereiche der Startseite aus produkte.json und ansichten.html
    held = '<div class="buehne" data-buehne>\n%s\n</div>' % geraet("Meyssens", teil(ansichten, "held"))
    demos = []
    for p in (p for p in produkte if p["status"] == "Pilotphase"):
        bild, _ = ansicht(ansichten, p)
        demos.append('<article class="demo r">\n'
                     '  <div class="demo-text">\n'
                     '    <span class="status-chip">%s</span>\n'
                     '    <h3>%s</h3>\n'
                     '    <p>%s</p>\n'
                     '    <a class="mehr" href="/produkte/%s/">Mehr erfahren %s</a>\n'
                     '  </div>\n'
                     '  <div class="demo-bild">\n%s\n  </div>\n'
                     '</article>' % (html.escape(STUFEN[p["status"]]["badge"]), html.escape(p["name"]),
                                     html.escape(p["kurzbeschreibung"]), p["slug"], PFEIL, bild))
    geplant = [p for p in produkte if p["status"] == "In Planung"]
    schritte = []
    for i, p in enumerate(geplant, 1):
        bild, _ = ansicht(ansichten, p)
        schritte.append('  <div class="schritt%s">\n'
                        '    <div class="schritt-text">\n'
                        '      <span class="schritt-nr">%02d / %02d</span>\n'
                        '      <span class="status-chip">%s</span>\n'
                        '      <h3><a href="/produkte/%s/">%s</a></h3>\n'
                        '      <p>%s</p>\n'
                        '      <a class="mehr" href="/produkte/%s/#anfrage">%s %s</a>\n'
                        '    </div>\n'
                        '    <div class="schritt-bild">\n%s\n    </div>\n'
                        '  </div>' % (" aktiv" if i == 1 else "", i, len(geplant), html.escape(STUFEN[p["status"]]["badge"]),
                                      p["slug"], html.escape(p["name"]), html.escape(p["kurzbeschreibung"]),
                                      p["slug"], STUFEN[p["status"]]["knopf"], PFEIL, bild))
    planung = '<div class="scrolly" data-scrolly>\n%s\n</div>' % "\n".join(schritte)
    zahlen = [(len(produkte), "Produkte"),
              (sum(p["status"] == "Pilotphase" for p in produkte), "in der Pilotphase"),
              (len(geplant), "in Planung"),
              (anzahl_branchen, "Branchenseiten"),
              (anzahl_ratgeber, "Ratgeber")]
    zahlen = ('<div class="zahlen r">\n%s\n</div>\n'
              '<p class="zahlen-hinweis">Gezählt aus den Angaben dieser Website. Meyssens ist ein Einzelunternehmen '
              'in Lausen (BL). Wir haben noch keine Kunden und keine Referenzen.</p>'
              % "\n".join('  <div class="zahl"><strong>%d</strong><span>%s</span></div>' % z for z in zahlen))
    for name, inhalt in (("held", held), ("demos", "\n".join(demos)), ("planung", planung), ("zahlen", zahlen)):
        start = setze_auto(start, name, inhalt)
    return start


def produkt_ansicht(ansichten, p):
    bild, interaktiv = ansicht(ansichten, p)
    hinweis = ("Interaktives Beispiel mit erfundenen Inhalten. Das Produkt ist in der Pilotphase." if interaktiv else
               "Beispielansicht, wie das Produkt aussehen könnte. Das Produkt ist %s." % (
                   "in Planung" if p["status"] == "In Planung" else "in der Pilotphase"))
    return '<div class="r">\n%s\n</div>\n<p class="ansicht-hinweis">%s</p>' % (bild, hinweis)


def kurz(text, laenge=155, mindestens=120):
    # Meta-Beschreibung: ganze Sätze bis zur Länge, mindestens der erste Satz.
    # Ist das Ergebnis kürzer als "mindestens", wird der nächste Satz wortweise mit "…" angehängt.
    saetze = re.split(r"(?<=[.!?])\s+", text)
    out = saetze[0]
    for i, s in enumerate(saetze[1:], 1):
        if len(out) + 1 + len(s) > laenge:
            if len(out) < mindestens:
                teil = ""
                for w in s.split():
                    if len(out) + 1 + len(teil) + len(w) + 2 > laenge:
                        break
                    teil = (teil + " " + w).strip()
                if teil:
                    out += " " + teil.rstrip(",;:") + " …"
            break
        out += " " + s
    return out


def titel_branche(b):
    # Seitentitel höchstens ca. 60 Zeichen
    t = "Digitale Infrastruktur für %s – Meyssens" % b["fuer"]
    return t if len(t) <= 60 else "Digitale Lösungen für %s – Meyssens" % b["name"]


def ld(*teile):
    # Strukturierte Daten als JSON-LD (ein Block mit @graph)
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context": "https://schema.org", "@graph": list(teile)}, ensure_ascii=False)


def brotkrumen(*stufen):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(stufen, 1)]}


AUTOR = "Lionel Nickelsen"
# Langtext-Seiten: Ausgabeordner, Zurück-Link und Formularfeld je Art
ARTEN = {
    "branche": {"ordner": "branchen", "zurueck": ("/unternehmen/#branchen", "Alle Branchen"),
                "anfrage": "Interesse für Ihren Betrieb?", "betreff": "Branchenanfrage über meyssens.ch: %s",
                "feld": ("branche", "Branche")},
    "ratgeber": {"ordner": "ratgeber", "zurueck": ("/unternehmen/#ratgeber", "Alle Ratgeber"),
                 "anfrage": "Fragen zum Thema?", "betreff": "Anfrage zum Ratgeber über meyssens.ch: %s",
                 "feld": ("thema", "Thema")},
}
WORTE = (1500, 2200)


def worte(text):
    # Wörter im sichtbaren Text eines HTML-Fragments
    return len(re.findall(r"\w[\w'’.-]*", html.unescape(re.sub(r"<[^>]+>", " ", text))))


def pruefe_artikel(a, nach_slug):
    fehlt = [f for f in ("slug", "art", "name", "titel", "beschreibung", "h1", "lead", "geprueft") if not a.get(f)]
    if a.get("art") not in ARTEN:
        fehlt.append("art (branche oder ratgeber)")
    if len(a.get("weiterlesen", [])) != 4:
        fehlt.append("weiterlesen (genau 4)")
    if len(a.get("faq", [])) < 3:
        fehlt.append("faq (mindestens 3)")
    if not a.get("quellen"):
        fehlt.append("quellen")
    if not 1 <= len(a.get("produkte", [])) <= 4:
        fehlt.append("produkte (1 bis 4)")
    if fehlt:
        raise SystemExit("Artikel %s: %s" % (a.get("slug", "?"), ", ".join(fehlt)))
    unbekannt = [s for s in a["produkte"] if s not in nach_slug]
    if unbekannt:
        raise SystemExit("Artikel %s: unbekannte Produkte %s" % (a["slug"], ", ".join(unbekannt)))
    if not re.fullmatch(r"[a-z0-9-]+", a["slug"]):
        raise SystemExit("Ungültiger Artikel-Slug: %s" % a["slug"])
    if not all(q["url"].startswith("https://") for q in a["quellen"]):
        raise SystemExit("Artikel %s: Quellen brauchen https-Links" % a["slug"])


def ehrlich(produkte):
    # Ehrlichkeitsvermerk aus dem Status der Produkte auf der Seite (produkte.json)
    def liste(namen):
        return " und ".join([", ".join(namen[:-1]), namen[-1]] if len(namen) > 1 else namen)
    teile = []
    for stufe, text in (("Pilotphase", "in der Pilotphase"), ("In Planung", "in Planung")):
        namen = [p["name"] for p in produkte if p["status"] == stufe]
        if namen:
            teile.append("%s %s" % (liste(namen), text))
    return ("Meyssens ist ein Einzelunternehmen in Lausen (BL). Wir haben noch keine Kunden und keine Referenzen. "
            "Stand der hier genannten Produkte: %s. "
            "Ein Werkzeug ersetzt keine rechtliche Prüfung, und am Ende entscheidet immer ein Mensch."
            % ", ".join(teile))


START = ("Startseite", "/")
UNTERNEHMEN = ("Unternehmen und Vereine", "/unternehmen/")


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

    artikel = json.loads(lies("artikel.json"))
    for a in artikel:
        pruefe_artikel(a, nach_slug)
    aslugs = {(a["art"], a["slug"]) for a in artikel}
    if len(aslugs) != len(artikel) or {a["slug"] for a in artikel if a["art"] == "branche"} & bslugs:
        raise SystemExit("Doppelter Artikel-Slug")
    artikel_branchen = [a for a in artikel if a["art"] == "branche"]
    ratgeber = [a for a in artikel if a["art"] == "ratgeber"]

    start = lies("index.html")
    gemeinden = lies("gemeinden/index.html")
    gemeinsam = {name: abschnitt(start, name) for name in ("head", "kopf", "fuss", "rechtliches", "skripte")}

    # Kontaktformular der Gemeinden-Seite: gleiches Ziel, gleiche Einwilligung, gleiches Absende-Skript
    formular_ziel = re.search(r'<form action="(https://formspree\.io/[^"]+)"', gemeinden).group(1)
    einwilligung = zwischen(gemeinden, '<div class="fgrp"><label style="display:flex', "</label></div>", True)
    if 'name="datenschutz-gelesen"' not in einwilligung:
        raise SystemExit("Einwilligung im Gemeinden-Formular nicht gefunden")
    formular_skript = zwischen(gemeinden, "// --- Kontaktformular", "</script>")

    ansichten = lies("ansichten.html")
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
            "ansicht": produkt_ansicht(ansichten, p),
            "ld": ld(brotkrumen(START, UNTERNEHMEN, (p["name"], "/produkte/%s/" % p["slug"]))),
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
            "titel": html.escape(titel_branche(b)),
            "beschreibung": html.escape(b["beschreibung"]),
            "url": "%s/branchen/%s/" % (DOMAIN, b["slug"]),
            "name": html.escape(b["name"]),
            "fuer": html.escape(fuer),
            "intro": html.escape(b["intro"]),
            "probleme": "\n".join(karte("", x["titel"], x["text"]) for x in b["probleme"]),
            "szenarien": "\n".join(karte("Beispielszenario", x["titel"], x["text"]) for x in b["szenarien"]),
            "demo": demo(b.get("demo"), "branche"),
            # FAQPage nur aus den sichtbaren Fragen der Seite
            "ld": ld(brotkrumen(START, UNTERNEHMEN, (b["name"], "/branchen/%s/" % b["slug"])),
                     {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["frage"],
                      "acceptedAnswer": {"@type": "Answer", "text": q["antwort"]}} for q in b["faq"]]}),
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

    # Alle Seiten, auf die Langtext-Seiten intern verlinken dürfen
    bekannte_seiten = {"/", "/gemeinden/", "/unternehmen/"}
    bekannte_seiten |= {"/produkte/%s/" % s for s in slugs} | {"/branchen/%s/" % s for s in bslugs}
    bekannte_seiten |= {"/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"]) for a in artikel}

    vorlage_artikel = lies("vorlage_artikel.html")
    for a in artikel:
        art = ARTEN[a["art"]]
        pfad = "/%s/%s/" % (art["ordner"], a["slug"])
        inhalt = lies("artikel/%s.html" % a["slug"]).rstrip("\n")
        for link in a["weiterlesen"]:
            if link["url"] not in bekannte_seiten:
                raise SystemExit("Artikel %s: Weiterlesen auf unbekannte Seite %s" % (a["slug"], link["url"]))
        for ziel in re.findall(r'href="(/[^"#]*)', inhalt):
            if ziel not in bekannte_seiten:
                raise SystemExit("Artikel %s: interner Link auf unbekannte Seite %s" % (a["slug"], ziel))
        roh = inhalt + json.dumps(a, ensure_ascii=False)
        if "[Status" in roh or "ß" in roh:
            raise SystemExit("Artikel %s: Platzhalter [Status ...] oder ß im Text" % a["slug"])
        datum = datetime.date.fromisoformat(a["geprueft"])
        werte = dict(gemeinsam, **{
            "titel": html.escape(a["titel"]),
            "beschreibung": html.escape(a["beschreibung"]),
            "url": DOMAIN + pfad,
            "name": html.escape(a["name"]),
            "chip": html.escape(a["name"] if a["art"] == "branche" else "Ratgeber"),
            "h1": html.escape(a["h1"]),
            "lead": html.escape(a["lead"]),
            "autor": AUTOR,
            "geprueft": datum.strftime("%d.%m.%Y"),
            "inhalt": inhalt,
            "faq": "\n".join('    <div class="qa">\n      <h3>%s</h3>\n      <p>%s</p>\n    </div>'
                             % (html.escape(q["frage"]), html.escape(q["antwort"])) for q in a["faq"]),
            "weiterlesen": "\n".join('    <a href="%s" class="feat tile">\n      <h3>%s</h3>\n      <p>%s</p>\n'
                                     '      <span class="way-go">Weiterlesen %s</span>\n    </a>'
                                     % (l["url"], html.escape(l["titel"]), html.escape(l["grund"]), PFEIL)
                                     for l in a["weiterlesen"]),
            "ehrlich": html.escape(ehrlich([nach_slug[s] for s in a["produkte"]])),
            "produkte": "\n".join(kachel(nach_slug[s]) for s in a["produkte"]),
            "quellen": "\n".join('      <li><a href="%s" target="_blank" rel="noopener">%s</a></li>'
                                 % (html.escape(q["url"]), html.escape(q["titel"])) for q in a["quellen"]),
            "zurueck_url": art["zurueck"][0],
            "zurueck_text": art["zurueck"][1],
            "anfrage_titel": art["anfrage"],
            "betreff": html.escape(art["betreff"] % a["name"]),
            "feld": art["feld"][0],
            "feld_label": art["feld"][1],
            # Article und FAQPage nur aus dem sichtbaren Inhalt der Seite
            "ld": ld(brotkrumen(START, UNTERNEHMEN, (a["name"], pfad)),
                     {"@type": "Article", "headline": a["h1"], "description": a["beschreibung"],
                      "inLanguage": "de-CH", "dateModified": a["geprueft"], "mainEntityOfPage": DOMAIN + pfad,
                      "author": {"@type": "Person", "name": AUTOR},
                      "publisher": {"@id": DOMAIN + "/#org", "@type": "Organization", "name": "Meyssens",
                                    "logo": DOMAIN + "/logo.png"},
                      "image": DOMAIN + "/og-image.png"},
                     {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["frage"],
                      "acceptedAnswer": {"@type": "Answer", "text": q["antwort"]}} for q in a["faq"]]}),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        seite = fuelle(vorlage_artikel, werte)
        n = worte(zwischen(seite, '<main id="main"', '<section id="quellen"'))
        hinweis = "" if WORTE[0] <= n <= WORTE[1] else "  ACHTUNG: ausserhalb %d bis %d" % WORTE
        print("Wörter %s: %d%s" % (pfad, n, hinweis))
        schreibe(pfad.strip("/") + "/index.html", seite)

    werte = dict(gemeinsam, **{
        "titel": "Für Unternehmen und Vereine – Meyssens",
        "beschreibung": html.escape("Digitale Werkzeuge für Unternehmen und Vereine: Umfragen, Newsletter, "
                                    "Vereinswebsite, Mail-Assistent und mehr. Jetzt Pilotpartner werden."),
        "url": DOMAIN + "/unternehmen/",
        "kacheln": "\n".join(kacheln),
        "ld": ld(brotkrumen(START, UNTERNEHMEN)),
        "branchen": "\n".join('    <a href="/branchen/%s/">%s %s</a>' % (b["slug"], html.escape(b["name"]), PFEIL)
                               for b in sorted(branchen + artikel_branchen, key=lambda b: b["name"])),
        "ratgeber": "\n".join('    <a href="/ratgeber/%s/">%s %s</a>' % (a["slug"], html.escape(a["name"]), PFEIL)
                               for a in ratgeber),
    })
    schreibe("unternehmen/index.html", fuelle(lies("vorlage_unternehmen.html"), werte))

    neu = startseite(start, ansichten, produkte, len(branchen) + len(artikel_branchen), len(ratgeber))
    if neu != start:
        schreibe("index.html", neu)

    # Verwaiste Ordner nur melden, nicht löschen
    bslugs_alle = bslugs | {a["slug"] for a in artikel_branchen}
    for ordner, bekannt, quelle in (("produkte", slugs, "produkte.json"), ("branchen", bslugs_alle, "branchen.json/artikel.json"),
                                    ("ratgeber", {a["slug"] for a in ratgeber}, "artikel.json")):
        if not (ROOT / ordner).is_dir():
            continue
        for d in sorted((ROOT / ordner).iterdir()):
            if d.is_dir() and d.name not in bekannt:
                print("Hinweis: %s/%s steht nicht in %s" % (ordner, d.name, quelle))

    heute = datetime.date.today().isoformat()
    seiten = [("/", "1.0"), ("/gemeinden/", "0.9"), ("/unternehmen/", "0.8")]
    seiten += [("/produkte/%s/" % p["slug"], "0.6") for p in produkte]
    seiten += [("/branchen/%s/" % b["slug"], "0.6") for b in branchen]
    seiten += [("/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"]), "0.6") for a in artikel]
    zeilen = ["  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>%s</priority></url>"
              % (DOMAIN, pfad, heute, prio) for pfad, prio in seiten]
    schreibe("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(zeilen) + "\n</urlset>\n")


if __name__ == "__main__":
    main()

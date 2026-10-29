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
  vorlage_baustein.html    Vorlage für Automatisierungs-Bausteine (Einträge in produkte.json mit Feld "branche");
                           der Abschnitt "Was sich automatisieren lässt" der Branchenseite kommt aus artikel.json
                           (Feld "automatisierung")
  vorlage_unternehmen.html Vorlage für unternehmen/index.html
  index.html               Kopfbereich, Header, Footer, Cookie-Banner, Impressum, Datenschutz, Skripte
                           (Abschnitte zwischen <!-- name:start --> und <!-- name:ende -->).
                           Die Bereiche <!-- auto:name:start --> bis <!-- auto:name:ende --> der Startseite
                           (Produktansicht, Demos, In Planung, Zahlen) schreibt build.py selbst neu.
  ansichten.html           Demos (Pilotphase) und Beispielansichten (In Planung) im Gerätefenster
  gemeinden/index.html     Formspree-Ziel, Einwilligung und Formular-Skript des bestehenden Kontaktformulars.
                           build.py schreibt dort die Bereiche auto:buehne und auto:ablauf-1 bis -4 neu
                           (Beispielansichten aus ansichten.html), alles andere bleibt von Hand gepflegt.
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
        raise SystemExit("Bereich auto:%s fehlt" % name)
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


# Namen der Zielseiten für beschreibende Linktexte (in main() gefüllt)
ZIELNAMEN = {"#datenschutz": "zur Datenschutzerklärung"}
GENERISCH = re.compile(r'(<a\b[^>]*href="([^"]*)"[^>]*>)(Mehr erfahren|Unverbindlich vormerken|Beispielansicht|Beispiel ausprobieren)'
                       r'(\s*(?:<svg\b.*?</svg>)?\s*)</a>', re.S)


def beschreibend(inhalt):
    # Generische Linktexte ("Mehr erfahren") für Screenreader und Suchmaschinen um das Ziel ergänzen, sichtbar unverändert
    def ergaenze(m):
        ziel = m.group(2)
        name = ZIELNAMEN.get(ziel) or ZIELNAMEN.get(ziel.split("#")[0])
        if not name:
            return m.group(0)
        zusatz = name if ziel.startswith("#") else ("zu " + name)
        return '%s%s<span class="sr-only"> %s</span>%s</a>' % (m.group(1), m.group(3), html.escape(zusatz), m.group(4))
    return GENERISCH.sub(ergaenze, inhalt)


def schreibe(pfad, inhalt):
    if not pfad.startswith("gemeinden/"):
        inhalt = beschreibend(inhalt)
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
    planung = scrolly(ansichten, geplant)
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


def scrolly(ansichten, liste, mehr=False):
    # Sticky-Abschnitt: links der Text (bleibt stehen), rechts wechselt die Ansicht im Gerätefenster.
    # mehr=True: zusätzlich der Link "Mehr erfahren" auf die Produktseite (Unternehmen-Seite)
    schritte = []
    for i, p in enumerate(liste, 1):
        bild, _ = ansicht(ansichten, p)
        links = ('      <a class="mehr" href="/produkte/%s/">Mehr erfahren %s</a>\n' % (p["slug"], PFEIL)) if mehr else ""
        schritte.append('  <div class="schritt%s">\n'
                        '    <div class="schritt-text">\n'
                        '      <span class="schritt-nr">%02d / %02d</span>\n'
                        '      <span class="status-chip">%s</span>\n'
                        '      <h3><a href="/produkte/%s/">%s</a></h3>\n'
                        '      <p>%s</p>\n'
                        '%s'
                        '      <a class="mehr" href="/produkte/%s/#anfrage">%s %s</a>\n'
                        '    </div>\n'
                        '    <div class="schritt-bild" style="--z:%d">\n%s\n    </div>\n'
                        '  </div>' % (" aktiv" if i == 1 else "", i, len(liste), html.escape(STUFEN[p["status"]]["badge"]),
                                      p["slug"], html.escape(p["name"]), html.escape(p["kurzbeschreibung"]), links,
                                      p["slug"], STUFEN[p["status"]]["knopf"], PFEIL, i, bild))
    # Klasse "an" sofort setzen, nicht erst in demos.js (defer), sonst springt das Layout nach dem ersten Rendern
    return ('<div class="scrolly" data-scrolly style="--n:%d">\n'
            '<script>if("IntersectionObserver" in window)document.currentScript.parentNode.classList.add("an")</script>\n'
            '%s\n</div>') % (len(liste), "\n".join(schritte))


def angebot(p):
    # Angebotskarte im Gerätefenster-Stil (Branchen- und Ratgeberseiten): gleiche Texte und Links wie die Kachel,
    # dazu der Weg zur Beispielansicht und zur Anfrage
    stufe = STUFEN[p["status"]]
    return ('    <article class="angebot-karte r">\n'
            '      <div class="geraet-leiste"><i aria-hidden="true"></i><i aria-hidden="true"></i><i aria-hidden="true"></i>'
            '<span class="geraet-titel">%s</span></div>\n'
            '      <div class="angebot-inhalt">\n'
            '        <span class="status-chip">%s</span>\n'
            '        <h3><a href="/produkte/%s/">%s</a></h3>\n'
            '        <p>%s</p>\n'
            '        <div class="angebot-links"><a class="mehr" href="/produkte/%s/">Mehr erfahren %s</a>'
            '<a class="mehr" href="/produkte/%s/#ansicht">%s %s</a>'
            '<a class="mehr" href="/produkte/%s/#anfrage">%s %s</a></div>\n'
            '      </div>\n'
            '    </article>' % (html.escape(p["name"]), html.escape(stufe["badge"]), p["slug"], html.escape(p["name"]),
                               html.escape(p["kurzbeschreibung"]), p["slug"], PFEIL, p["slug"],
                               "Beispiel ausprobieren" if p["status"] == "Pilotphase" else "Beispielansicht", PFEIL,
                               p["slug"], stufe["knopf"], PFEIL))


def inhaltsverzeichnis(inhalt, mit_automatisierung=False):
    # Sprungmarken aus den Zwischentiteln des Langtexts (h2 mit id) und zu den Abschnitten danach
    ziele = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', inhalt)
    if len(ziele) != len(re.findall(r"<h2\b", inhalt)):
        raise SystemExit("Langtext: jede h2 braucht eine id für das Inhaltsverzeichnis")
    weitere = ((("automatisierung", "Was sich automatisieren lässt"),) if mit_automatisierung else ()) + (
               ("fragen", "Häufige Fragen"), ("weiterlesen", "Passend zum Thema"), ("angebot", "Was Meyssens dazu anbietet"),
               ("quellen", "Quellen und Hinweis"), ("anfrage", "Anfrage"))
    return ('<nav class="toc" aria-label="Inhalt dieser Seite">\n'
            '      <p class="toc-titel">Inhalt</p>\n'
            '      <ol>\n%s\n      </ol>\n'
            '      <ul class="toc-mehr">\n%s\n      </ul>\n'
            '    </nav>' % ("\n".join('        <li><a href="#%s">%s</a></li>' % z for z in ziele),
                          "\n".join('        <li><a href="#%s">%s</a></li>' % z for z in weitere)))


def produkt_ansicht(ansichten, p):
    bild, interaktiv = ansicht(ansichten, p)
    stand = "in Planung" if p["status"] == "In Planung" else "in der Pilotphase"
    hinweis = ("Interaktives Beispiel mit erfundenen Inhalten. Das Produkt ist %s." % stand if interaktiv else
               "Beispielansicht, wie das Produkt aussehen könnte. Das Produkt ist %s." % stand)
    return '<div class="r">\n%s\n</div>\n<p class="ansicht-hinweis">%s</p>' % (bild, hinweis)


# Automatisierungs-Bausteine (produkte.json mit Feld "branche")
BAUSTEIN_FELDER = ("branche", "mensch", "aufwand", "daten", "quellen", "geprueft")
AUFWAND = ("klein", "klein bis mittel", "mittel", "mittel bis gross", "gross")
REGEL = ("Entwürfe ja, automatischer Versand nein.",
         "Jeder Baustein bereitet vor: Entwürfe, Listen und Hinweise. Was Ihren Betrieb verlässt, gibt ein Mensch frei.")
BEDINGUNGEN = ("Vertrag zur Auftragsbearbeitung, bevor echte Daten verarbeitet werden",
               "Hosting in der Schweiz",
               "Datenminimierung: nur die Angaben, die der Ablauf wirklich braucht")
KETTE_ART = {"baustein": "Läuft automatisch, als Entwurf", "mensch": "Mensch entscheidet", "spaeter": "Später geplant",
             "vorhanden": "Ihre Software"}
# Possessivpronomen für den Anfrage-Knopf: "für mein Büro", "für meinen Betrieb", sonst "für meine Praxis"
MEIN = {"Büro": "mein", "Betrieb": "meinen"}
AUTO_WORTE = (450, 1300)  # 3 bis 4 Bausteinkarten mit Formular, Ablauf-Kette und Demo
BAUSTEIN_WORTE = (450, 1000)


def ist_baustein(p):
    return bool(p.get("branche"))


def a_bausteine(artikel, branchen=()):
    # Alle Bausteine, die auf einer Branchenseite stehen: Abschnitt "Was sich automatisieren lässt" der Langtext-Branchen
    # oder Feld "bausteine" der Branchen ohne Langtext
    return ({s for a in artikel for s in a.get("automatisierung", {}).get("bausteine", [])} |
            {s for b in branchen for s in b.get("bausteine", [])})


def qa_liste(faq):
    return "\n".join('    <div class="qa">\n      <h3>%s</h3>\n      <p>%s</p>\n    </div>'
                     % (html.escape(q["frage"]), html.escape(q["antwort"])) for q in faq)


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["frage"],
            "acceptedAnswer": {"@type": "Answer", "text": q["antwort"]}} for q in faq]}


def link_kachel(url, chip, titel, text, knopf):
    return ('    <a href="%s" class="feat tile">\n%s      <h3>%s</h3>\n      <p>%s</p>\n      <span class="way-go">%s %s</span>\n    </a>'
            % (url, '      <span class="status-chip">%s</span>\n' % html.escape(chip) if chip else "", html.escape(titel),
               html.escape(text), knopf, PFEIL))


def anfang(text, mindestens=90):
    # Erste Sätze eines Texts, bis mindestens die angegebene Länge erreicht ist (für die Bausteinkarten)
    out = ""
    for s in re.split(r"(?<=[.!?])\s+", text):
        out = (out + " " + s).strip()
        if len(out) >= mindestens:
            break
    return out


def aufwand(p):
    return "Aufwand %s, Einschätzung" % p["aufwand"]


def ohne_automatisierung(text):
    # Langtext-Wortzahl ohne den Abschnitt "Was sich automatisieren lässt" (wird getrennt gezählt)
    return re.sub(r'<section id="automatisierung".*?</section>', " ", text, flags=re.S)


def baustein_formular(p, branche, formular_ziel, einwilligung):
    # Eigenes Anfrage-Formular pro Baustein, aufklappbar in der Bausteinkarte der Branchenseite
    s, e = p["slug"], html.escape(p["name"])
    feld = ('<div class="fgrp"><label class="flabel" for="%s-%s">%s</label>'
            '<input class="finput" type="%s" id="%s-%s" name="%s" required></div>')
    return ('      <details class="baustein-anfrage">\n'
            '        <summary>Diesen Baustein anfragen</summary>\n'
            '        <form action="%s" method="POST">\n'
            '          <input type="hidden" name="_subject" value="Bausteinanfrage über meyssens.ch: %s (%s)">\n'
            '          <input type="hidden" name="branche" value="%s">\n'
            '          <div class="frow">%s%s</div>\n'
            '          %s\n          %s\n'
            '          <div class="fgrp"><label class="flabel" for="%s-baustein">Baustein</label>'
            '<input class="finput" type="text" id="%s-baustein" name="baustein" value="%s" readonly></div>\n'
            '          %s\n'
            '          <button type="submit" class="btn-p"><span>%s</span> %s</button>\n'
            '          <p role="status" aria-live="polite"></p>\n'
            '        </form>\n'
            '      </details>' % (formular_ziel, e, html.escape(branche), html.escape(branche),
                                 feld % (s, "vorname", "Vorname", "text", s, "vorname", "vorname"),
                                 feld % (s, "nachname", "Nachname", "text", s, "nachname", "nachname"),
                                 feld % (s, "organisation", "Praxis, Verwaltung, Büro oder Betrieb", "text", s, "organisation", "organisation"),
                                 feld % (s, "email", "E-Mail", "email", s, "email", "email"),
                                 s, s, e, einwilligung, STUFEN[p["status"]]["knopf"], PFEIL))


def baustein_karte(p, branche, formular_ziel, einwilligung):
    daten = ('      <p class="baustein-daten"><strong>Personendaten:</strong> nur mit Vertrag zur Auftragsbearbeitung, '
             'Hosting in der Schweiz und Datenminimierung.</p>\n') if p["personendaten"] else ""
    return ('    <article class="baustein-karte r">\n'
            '      <div class="baustein-kopf"><span class="status-chip">%s</span><span class="baustein-aufwand">%s</span></div>\n'
            '      <h3><a href="/produkte/%s/">%s</a></h3>\n'
            '      <dl class="baustein-teile">\n'
            '        <div><dt>Heute von Hand</dt><dd>%s</dd></div>\n'
            '        <div><dt>Das übernimmt der Baustein</dt><dd>%s</dd></div>\n'
            '        <div><dt>Das entscheidet der Mensch</dt><dd>%s</dd></div>\n'
            '      </dl>\n'
            '%s'
            '      <a class="mehr" href="/produkte/%s/">Mehr erfahren %s</a>\n'
            '%s\n'
            '    </article>' % (html.escape(STUFEN[p["status"]]["badge"]), html.escape(aufwand(p)), p["slug"],
                               html.escape(p["name"]), html.escape(anfang(p["problem"])), html.escape(anfang(p["loesung"])),
                               html.escape(anfang(p["mensch"])), daten, p["slug"], PFEIL,
                               baustein_formular(p, branche, formular_ziel, einwilligung)))


# Symbole der Ablauf-Schritte (inline SVG, 24er-Raster)
KETTE_SYMBOL = {
    "baustein": '<path d="M13 3 5 13.5h6L10 21l8-10.5h-6z"/>',
    "mensch": '<circle cx="12" cy="8" r="3.6"/><path d="M5 20c.6-3.8 3.4-6 7-6s6.4 2.2 7 6"/>',
    "spaeter": '<circle cx="12" cy="12" r="7.5"/><path d="M12 8v4.2l2.8 1.8"/>',
    "vorhanden": '<rect x="4" y="5" width="16" height="12" rx="2"/><path d="M9 20.5h6"/>',
}


def kette_teile(k, nach_slug, karten=None):
    # Schritte und Legende einer Ablauf-Kette.
    # Schritte: {titel, art, seite (Bausteinseite oder null), beispiel (1 Satz), hinweis (optional)}
    # karten: {nr: name} der Bausteinkarten auf derselben Seite; ein Schritt mit "karte" verweist auf die Karte
    schritte, arten = [], []
    for i, st in enumerate(k["schritte"], 1):
        art, seite, nr = st["art"], st.get("seite"), st.get("karte")
        if art not in KETTE_ART:
            raise SystemExit("Kette %s: unbekannte Art %s" % (k["titel"], art))
        if nr is not None and (seite or nr not in (karten or {})):
            raise SystemExit("Kette %s: Schritt %s mit Seite und Karte oder unbekannter Karte" % (k["titel"], st["titel"]))
        if art == "baustein" and not seite and nr is None:
            raise SystemExit("Kette %s: Schritt %s ohne Bausteinseite" % (k["titel"], st["titel"]))
        if seite and seite not in nach_slug:
            raise SystemExit("Kette %s: unbekannter Baustein %s" % (k["titel"], seite))
        if len(re.findall(r"[.!?](\s|$)", st["beispiel"])) != 1:
            raise SystemExit("Kette %s: Beispiel zu %s ist nicht genau ein Satz" % (k["titel"], st["titel"]))
        if art not in arten:
            arten.append(art)
        if seite:
            link = '<a class="ablauf-link" href="/produkte/%s/">Zum Baustein: %s %s</a>' % (
                seite, html.escape(nach_slug[seite]["name"]), PFEIL)
        elif nr is not None:
            link = '<a class="ablauf-link" href="#baustein-%d">Zum Baustein %d: %s %s</a>' % (
                nr, nr, html.escape(karten[nr]), PFEIL)
        else:
            link = ('<a class="ablauf-link" href="#ablauf-anfrage" data-schritt="%s">Noch kein eigener Baustein: '
                    'Interesse melden %s</a>' % (html.escape(st["titel"]), PFEIL))
        hinweis = '<p class="ablauf-hinweis">%s</p>' % html.escape(st["hinweis"]) if st.get("hinweis") else ""
        schritte.append(
            '      <li class="ablauf-schritt %s">\n'
            '        <span class="ablauf-marke" aria-hidden="true"><svg viewBox="0 0 24 24">%s</svg></span>\n'
            '        <svg class="ablauf-linie" aria-hidden="true" viewBox="0 0 2 10" preserveAspectRatio="none">'
            '<line x1="1" y1="0" x2="1" y2="10" vector-effect="non-scaling-stroke"/></svg>\n'
            '        <div class="ablauf-karte">\n'
            '          <span class="ablauf-art">%s</span>\n'
            '          <h4><span class="ablauf-nr">%d</span> %s</h4>\n'
            '          <p>%s</p>%s\n'
            '          %s\n'
            '        </div>\n'
            '      </li>' % (art, KETTE_SYMBOL[art], KETTE_ART[art], i, html.escape(st["titel"]),
                             html.escape(st["beispiel"]), hinweis, link))
    legende = "".join('<li class="%s"><span class="ablauf-punkt" aria-hidden="true"></span>%s</li>' % (art, KETTE_ART[art])
                      for art in arten)
    return schritte, legende


def kette_bild(k, branche, slug):
    # Ablauf als teilbares Bild (bilder.py), Alt-Text mit allen Schritten
    bild = ""
    datei = ROOT / "assets" / "ablauf" / ("%s.png" % slug)
    if slug and datei.is_file():
        breite, hoehe = png_masse(datei)
        alt = "Ablauf %s für %s als Grafik: %s." % (k["titel"], branche, "; ".join(
            "%d. %s (%s)" % (i, st["titel"], KETTE_ART[st["art"]]) for i, st in enumerate(k["schritte"], 1)))
        bild = ('    <figure class="ablauf-bild">\n'
                '      <img src="/assets/ablauf/%s.png" width="%d" height="%d" loading="lazy" decoding="async" alt="%s">\n'
                '      <figcaption>Der Ablauf als Bild zum Teilen: <a href="/assets/ablauf/%s.png" download>Grafik «%s» herunterladen (PNG)</a></figcaption>\n'
                '    </figure>\n' % (slug, breite, hoehe, html.escape(alt), slug, html.escape(k["titel"])))
    return bild


def kette(k, nach_slug, branche, formular_ziel, einwilligung, slug=None):
    # Ablauf-Kette als Scroll-Animation: ohne JS eine lesbare Liste, mit JS (demos.js) erscheint Schritt für Schritt.
    schritte, legende = kette_teile(k, nach_slug)
    knopf = "Diesen Ablauf für %s %s anfragen" % (MEIN.get(k["betrieb"], "meine"), k["betrieb"])
    bild = kette_bild(k, branche, slug)
    wert = "%s (%s)" % (k["titel"], branche)
    return ('  <div class="ablauf" id="ablauf" data-ablauf>\n'
            '    <script>if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion: reduce)").matches)'
            'document.currentScript.parentNode.classList.add("bewegt")</script>\n'
            '    <div class="ablauf-kopf">\n'
            '      <h3>Ablauf: %s</h3>\n'
            '      <p>%s</p>\n'
            '      <ul class="ablauf-legende" aria-label="Legende">%s</ul>\n'
            '    </div>\n'
            '    <ol class="ablauf-liste">\n%s\n    </ol>\n'
            '    <div class="ablauf-ende">\n'
            '      <span class="ablauf-marke" aria-hidden="true"><svg viewBox="0 0 24 24"><path pathLength="1" d="m6 12.5 4 4 8-9"/></svg></span>\n'
            '      <div class="ablauf-ziel">\n'
            '        <p class="ablauf-ziel-text">%s</p>\n'
            '        <a class="btn-p ablauf-cta" href="#ablauf-anfrage"><span>%s</span> %s</a>\n'
            '        <p class="ablauf-mikro">Die Bausteine sind in Planung. Wir merken Ihren Betrieb unverbindlich vor und antworten per E-Mail.</p>\n'
            '      </div>\n'
            '    </div>\n'
            '    <p class="kette-legende">Die Verknüpfung ist eine Einschätzung aus unserer Recherche, kein erprobter Ablauf.</p>\n'
            '%s'
            '    <form class="ablauf-form" id="ablauf-anfrage" action="%s" method="POST">\n'
            '      <h4>%s</h4>\n'
            '      <input type="hidden" name="_subject" value="Ablauf-Anfrage über meyssens.ch: %s">\n'
            '      <input type="hidden" name="branche" value="%s">\n'
            '      <div class="fgrp"><label class="flabel" for="ab-ablauf">Ablauf</label>'
            '<input class="finput" type="text" id="ab-ablauf" name="ablauf" value="%s" readonly></div>\n'
            '      <div class="frow"><div class="fgrp"><label class="flabel" for="ab-name">Name</label>'
            '<input class="finput" type="text" id="ab-name" name="name" autocomplete="name" required></div>'
            '<div class="fgrp"><label class="flabel" for="ab-email">E-Mail</label>'
            '<input class="finput" type="email" id="ab-email" name="email" autocomplete="email" required></div></div>\n'
            '      <div class="fgrp"><label class="flabel" for="ab-nachricht">Nachricht (optional)</label>'
            '<textarea class="ftextarea" id="ab-nachricht" name="nachricht" rows="3" '
            'placeholder="Zum Beispiel: welche Software Sie heute nutzen"></textarea></div>\n'
            '      %s\n'
            '      <button type="submit" class="btn-p"><span>Ablauf anfragen</span> %s</button>\n'
            '      <p role="status" aria-live="polite"></p>\n'
            '    </form>\n'
            '  </div>\n'
            '  <a class="anfrage-fest" href="#ablauf-anfrage" data-anfrage-fest hidden>Ablauf anfragen %s</a>'
            % (html.escape(k["titel"]), html.escape(k["text"]), legende, "\n".join(schritte),
               html.escape(k["abschluss"]), html.escape(knopf), PFEIL, bild,
               formular_ziel, html.escape(knopf), html.escape(wert), html.escape(branche), html.escape(wert),
               einwilligung.replace('id="', 'id="ab-').replace('for="', 'for="ab-'), PFEIL, PFEIL))


def automatisierung(a, nach_slug, ansichten, formular_ziel, einwilligung):
    # Abschnitt "Was sich automatisieren lässt" einer Branchenseite (artikel.json, Feld "automatisierung")
    au = a.get("automatisierung")
    if not au:
        return ""
    bausteine = [nach_slug[s] for s in au["bausteine"]]
    d = nach_slug[au["demo"]]
    bild, interaktiv = ansicht(ansichten, d)
    if not interaktiv:
        raise SystemExit("Branche %s: für die Demo fehlt demo-%s in ansichten.html" % (a["slug"], d["slug"]))
    datum = datetime.date.fromisoformat(au["geprueft"]).strftime("%d.%m.%Y")
    return ('<section id="automatisierung" class="dunkel">\n'
            '  <div class="kopf-mitte r">\n'
            '    <span class="s-label">Automatisierung</span>\n'
            '    <h2>Was sich automatisieren lässt</h2>\n'
            '    <p class="s-lead">%s</p>\n'
            '  </div>\n'
            '  <p class="regel r"><strong>%s</strong> %s</p>\n'
            '%s\n'
            '  <div class="baustein-raster">\n%s\n  </div>\n'
            '  <article class="demo auto-demo r">\n'
            '    <div class="demo-text">\n'
            '      <span class="status-chip">%s</span>\n'
            '      <h3>%s</h3>\n'
            '      <p>%s</p>\n'
            '      <a class="mehr" href="/produkte/%s/">Mehr erfahren %s</a>\n'
            '    </div>\n'
            '    <div class="demo-bild">\n%s\n    </div>\n'
            '  </article>\n'
            '  <p class="auto-hinweis r">Allgemeine Information, keine Rechtsberatung. Alle Bausteine auf dieser Seite sind '
            'in Planung, Meyssens hat noch keine Kunden und keine Referenzen. Angaben zum Aufwand und zur Reihenfolge sind '
            'Einschätzungen, keine gemessenen Werte. Vor einem Einsatz mit Personendaten prüfen wir die rechtlichen Fragen '
            'im Einzelfall. Zuletzt geprüft am %s.</p>\n'
            '</section>' % (html.escape(au["intro"]), REGEL[0], REGEL[1],
                            kette(au["kette"], nach_slug, a["name"], formular_ziel, einwilligung, a["slug"]),
                            "\n".join(baustein_karte(p, a["name"], formular_ziel, einwilligung) for p in bausteine),
                            html.escape(STUFEN[d["status"]]["badge"]),
                            html.escape(d["name"]), html.escape(d["kurzbeschreibung"]), d["slug"], PFEIL, bild, datum))


# Branchen ohne Langtext mit Feld "automatisierungen": 10 Bausteine (nur einige mit eigener Seite), 3 Ablauf-Ketten
# und ein gemeinsames Anfrage-Formular
AUTOMATISIERUNGEN_WORTE = (900, 2400)
EINTRAG_FELDER = ("nr", "name", "heute", "auto", "mensch", "daten", "aufwand")


def eintrag_karte(x, nach_slug):
    # Kompakte Karte eines der 10 Bausteine: mit eigener Seite verlinkt, sonst Interesse über das Ablauf-Formular
    s = x.get("seite")
    name = html.escape(x["name"])
    titel = '<a href="/produkte/%s/">%s</a>' % (s, name) if s else name
    chips = '<span class="status-chip">%s</span>' % html.escape(STUFEN[nach_slug[s]["status"]]["badge"] if s else "In Planung")
    if x.get("start"):
        chips += '<span class="status-chip start-chip">Startempfehlung</span>'
    offen = ('      <p class="baustein-offen"><strong>Noch zu klären:</strong> %s</p>\n' % html.escape(x["offen"])
             if x.get("offen") else "")
    link = ('      <a class="mehr" href="/produkte/%s/">Mehr erfahren %s</a>\n' % (s, PFEIL) if s else
            '      <a class="mehr" href="#ablauf-anfrage" data-baustein="%s">Interesse an diesem Baustein melden %s</a>\n'
            % (name, PFEIL))
    return ('    <article class="baustein-karte kompakt r" id="baustein-%d">\n'
            '      <div class="baustein-kopf"><span class="baustein-nr" aria-hidden="true">%d</span>%s'
            '<span class="baustein-aufwand">Aufwand %s, Einschätzung</span></div>\n'
            '      <h3>%s</h3>\n'
            '      <dl class="baustein-teile">\n'
            '        <div><dt>Heute von Hand, Einschätzung</dt><dd>%s</dd></div>\n'
            '        <div><dt>Das übernimmt der Baustein</dt><dd>%s</dd></div>\n'
            '        <div><dt>Das entscheidet der Mensch</dt><dd>%s</dd></div>\n'
            '      </dl>\n'
            '      <p class="baustein-daten"><strong>Daten:</strong> %s</p>\n'
            '%s%s'
            '    </article>' % (x["nr"], x["nr"], chips, html.escape(x["aufwand"]), titel, html.escape(x["heute"]),
                               html.escape(x["auto"]), html.escape(x["mensch"]), html.escape(x["daten"]), offen, link))


def ablauf_block(k, nach_slug, branche, nr, slug, karten):
    # Eine von mehreren Ablauf-Ketten einer Seite; der Knopf wählt die Kette im gemeinsamen Formular vor
    schritte, legende = kette_teile(k, nach_slug, karten)
    wert = "%s (%s)" % (k["titel"], branche)
    return ('  <div class="ablauf" id="ablauf-%d" data-ablauf>\n'
            '    <script>if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion: reduce)").matches)'
            'document.currentScript.parentNode.classList.add("bewegt")</script>\n'
            '    <div class="ablauf-kopf">\n'
            '      <h3>Ablauf: %s</h3>\n'
            '      <p>%s</p>\n'
            '      <ul class="ablauf-legende" aria-label="Legende">%s</ul>\n'
            '    </div>\n'
            '    <ol class="ablauf-liste">\n%s\n    </ol>\n'
            '    <div class="ablauf-ende">\n'
            '      <span class="ablauf-marke" aria-hidden="true"><svg viewBox="0 0 24 24"><path pathLength="1" d="m6 12.5 4 4 8-9"/></svg></span>\n'
            '      <div class="ablauf-ziel">\n'
            '        <p class="ablauf-ziel-text">%s</p>\n'
            '        <a class="btn-p ablauf-cta" href="#ablauf-anfrage" data-ablauf-wahl="%s"><span>Diesen Ablauf für %s %s anfragen</span> %s</a>\n'
            '        <p class="ablauf-mikro">Die Bausteine sind in Planung. Wir merken Ihren Betrieb unverbindlich vor und antworten per E-Mail.</p>\n'
            '      </div>\n'
            '    </div>\n'
            '    <p class="kette-legende">Die Verknüpfung ist eine Einschätzung aus unserer Recherche, kein erprobter Ablauf.</p>\n'
            '%s'
            '  </div>' % (nr, html.escape(k["titel"]), html.escape(k["text"]), legende, "\n".join(schritte),
                         html.escape(k["abschluss"]), html.escape(wert), MEIN.get(k["betrieb"], "meine"), html.escape(k["betrieb"]), PFEIL,
                         kette_bild(k, branche, slug)))


def automatisierungen(b, nach_slug, ratgeber, formular_ziel, einwilligung):
    # Abschnitt "Automatisierungen" einer Branche ohne Langtext (branchen.json, Feld "automatisierungen")
    au = b.get("automatisierungen")
    if not au:
        return ""
    name = b["name"]
    werte = ["%s (%s)" % (k["titel"], name) for k in au["ketten"]]
    optionen = "".join('<option>%s</option>' % html.escape(w) for w in werte + ["Mehrere Abläufe oder einzelne Bausteine (%s)" % name])
    betrieb = au["ketten"][0]["betrieb"]
    r = ratgeber[au["ratgeber"]]
    datum = datetime.date.fromisoformat(au["geprueft"]).strftime("%d.%m.%Y")
    return ('<section id="automatisierung" class="dunkel">\n'
            '  <div class="kopf-mitte r">\n'
            '    <span class="s-label">Automatisierung</span>\n'
            '    <h2>Automatisierungen für %s</h2>\n'
            '    <p class="s-lead">%s</p>\n'
            '  </div>\n'
            '  <p class="regel r"><strong>%s</strong> %s</p>\n'
            '  <p class="auto-start r">%s</p>\n'
            '  <div class="baustein-raster">\n%s\n  </div>\n'
            '  <div class="ablauf-gruppe" id="ablauf">\n'
            '  <div class="kopf-mitte r">\n'
            '    <h3 class="ablauf-gruppe-titel">Drei Abläufe, in denen die Bausteine zusammenspielen</h3>\n'
            '    <p class="s-lead">%s</p>\n'
            '  </div>\n'
            '%s\n'
            '  <form class="ablauf-form" id="ablauf-anfrage" action="%s" method="POST">\n'
            '    <h4>Einen Ablauf für %s %s anfragen</h4>\n'
            '    <input type="hidden" name="_subject" value="Ablauf-Anfrage über meyssens.ch: %s">\n'
            '    <input type="hidden" name="branche" value="%s">\n'
            '    <div class="fgrp"><label class="flabel" for="ab-ablauf">Ablauf</label>'
            '<select class="fselect" id="ab-ablauf" name="ablauf">%s</select></div>\n'
            '    <div class="frow"><div class="fgrp"><label class="flabel" for="ab-name">Name</label>'
            '<input class="finput" type="text" id="ab-name" name="name" autocomplete="name" required></div>'
            '<div class="fgrp"><label class="flabel" for="ab-email">E-Mail</label>'
            '<input class="finput" type="email" id="ab-email" name="email" autocomplete="email" required></div></div>\n'
            '    <div class="fgrp"><label class="flabel" for="ab-nachricht">Nachricht (optional)</label>'
            '<textarea class="ftextarea" id="ab-nachricht" name="nachricht" rows="3" '
            'placeholder="Zum Beispiel: welche Software Sie heute nutzen"></textarea></div>\n'
            '    %s\n'
            '    <button type="submit" class="btn-p"><span>Ablauf anfragen</span> %s</button>\n'
            '    <p role="status" aria-live="polite"></p>\n'
            '  </form>\n'
            '  </div>\n'
            '  <p class="auto-ratgeber r">Passend dazu im Ratgeber: <a href="/ratgeber/%s/">%s</a></p>\n'
            '  <p class="auto-hinweis r">Allgemeine Information, keine Rechtsberatung. Alle zehn Bausteine auf dieser Seite '
            'sind in Planung, Meyssens hat noch keine Kunden und keine Referenzen. Angaben zum Aufwand, zur Handarbeit von heute '
            'und zur Reihenfolge sind Einschätzungen, keine gemessenen Werte. Was mit «Noch zu klären» markiert ist, haben wir '
            'nicht belegt. Vor einem Einsatz mit Personendaten gelten ein Vertrag zur Auftragsbearbeitung, Hosting in der '
            'Schweiz und Datenminimierung, und wir prüfen die rechtlichen Fragen im Einzelfall. Zuletzt geprüft am %s.</p>\n'
            '</section>\n'
            '<a class="anfrage-fest" href="#ablauf-anfrage" data-anfrage-fest hidden>Ablauf anfragen %s</a>\n'
            % (html.escape(name), html.escape(au["intro"]), REGEL[0], REGEL[1], html.escape(au["start"]),
               "\n".join(eintrag_karte(x, nach_slug) for x in au["liste"]), html.escape(au["ketten_intro"]),
               "\n".join(ablauf_block(k, nach_slug, name, i, "%s-%d" % (b["slug"], i), {x["nr"]: x["name"] for x in au["liste"]})
                         for i, k in enumerate(au["ketten"], 1)),
               formular_ziel, MEIN.get(betrieb, "meine"), html.escape(betrieb), html.escape(name), html.escape(name), optionen,
               einwilligung.replace('id="', 'id="ab-').replace('for="', 'for="ab-'), PFEIL,
               r["slug"], html.escape(r["name"]), datum, PFEIL))


def pruefe_automatisierungen(b, nach_slug, ratgeber_slugs):
    au = b["automatisierungen"]
    fehlt = [f for f in ("intro", "start", "ketten_intro", "geprueft", "ratgeber") if not au.get(f)]
    if len(au.get("liste", [])) != 10:
        fehlt.append("liste (genau 10)")
    if len(au.get("ketten", [])) != 3:
        fehlt.append("ketten (genau 3)")
    if fehlt:
        raise SystemExit("Automatisierungen %s: %s" % (b["slug"], ", ".join(fehlt)))
    if au["ratgeber"] not in ratgeber_slugs:
        raise SystemExit("Automatisierungen %s: unbekannter Ratgeber %s" % (b["slug"], au["ratgeber"]))
    for i, x in enumerate(au["liste"], 1):
        fehlt = [f for f in EINTRAG_FELDER if not x.get(f)]
        if x.get("nr") != i or x.get("aufwand") not in AUFWAND or fehlt:
            raise SystemExit("Automatisierungen %s, Baustein %s: %s" % (b["slug"], i, ", ".join(fehlt) or "nr oder aufwand"))
        s = x.get("seite")
        if s and (s not in b.get("bausteine", []) or nach_slug[s]["aufwand"] != x["aufwand"]):
            raise SystemExit("Automatisierungen %s: %s nicht in bausteine oder Aufwand weicht ab" % (b["slug"], s))
    if sorted(x["seite"] for x in au["liste"] if x.get("seite")) != sorted(b.get("bausteine", [])):
        raise SystemExit("Automatisierungen %s: jede Bausteinseite braucht genau einen Eintrag in der Liste" % b["slug"])
    betriebe = {k.get("betrieb") for k in au["ketten"]}
    if len(betriebe) != 1 or not all(k.get(f) for k in au["ketten"] for f in ("titel", "text", "abschluss", "schritte")):
        raise SystemExit("Automatisierungen %s: Kette unvollständig oder Betrieb uneinheitlich" % b["slug"])
    roh = json.dumps(au, ensure_ascii=False)
    if "ß" in roh:
        raise SystemExit("Automatisierungen %s: ß im Text" % b["slug"])


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


# Organisation und Website: auf jeder erzeugten Seite, nur belegte Angaben (Impressum), keine Bewertungen
ORG = {"@type": "Organization", "@id": DOMAIN + "/#org", "name": "Meyssens", "url": DOMAIN + "/", "logo": DOMAIN + "/logo.png",
       "email": "lionel@meyssens.ch", "founder": {"@id": DOMAIN + "/ueber-uns/#person"},
       "address": {"@type": "PostalAddress", "addressLocality": "Lausen", "addressRegion": "BL", "addressCountry": "CH"}}
WEBSITE = {"@type": "WebSite", "@id": DOMAIN + "/#website", "name": "Meyssens", "url": DOMAIN + "/", "inLanguage": "de-CH",
           "publisher": {"@id": DOMAIN + "/#org"}}
SCHWEIZ = {"@type": "Country", "name": "Schweiz"}


PERSON = {"@type": "Person", "@id": DOMAIN + "/ueber-uns/#person", "name": "Lionel Nickelsen", "url": DOMAIN + "/ueber-uns/",
          "worksFor": {"@id": DOMAIN + "/#org"}}


def ld(*teile):
    # Strukturierte Daten als JSON-LD (ein Block mit @graph), immer mit Organisation und Website
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context": "https://schema.org", "@graph": [ORG, WEBSITE, PERSON] + list(teile)}, ensure_ascii=False)


def seo_kopf(url):
    # Nur eine Sprachfassung (Deutsch, Schweiz): hreflang auf sich selbst und als x-default
    return ('<link rel="alternate" hreflang="de-CH" href="%s">\n<link rel="alternate" hreflang="x-default" href="%s">'
            % (url, url))


def dienst(p, url, branche=None):
    # Service für Produkt- und Bausteinseiten; keine Preise, keine Bewertungen
    d = {"@type": "Service", "@id": url + "#dienst", "name": p["name"], "description": p["kurzbeschreibung"], "url": url,
         "provider": {"@id": DOMAIN + "/#org"}, "areaServed": SCHWEIZ, "availableLanguage": "de-CH",
         "audience": {"@type": "BusinessAudience", "audienceType": branche or "Unternehmen und Vereine in der Schweiz"}}
    if p.get("status"):
        d["additionalProperty"] = {"@type": "PropertyValue", "name": "Status", "value": p["status"]}
    return d


def h1_html(text):
    # Teil nach dem Doppelpunkt hervorgehoben, wie im bisherigen Stil
    vor, _, nach = text.partition(": ")
    return "%s: <span class=\"hl\">%s</span>" % (html.escape(vor), html.escape(nach)) if nach else html.escape(text)


def brotkrumen(*stufen):
    return {"@type": "BreadcrumbList", "@id": DOMAIN + stufen[-1][1] + "#brotkrumen", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(stufen, 1)]}


# Sichtbare Brotkrumen, gleiche Stufen wie BreadcrumbList im JSON-LD
STUFE_BRANCHEN = ("Branchen", "/branchen/")
STUFE_RATGEBER = ("Ratgeber", "/ratgeber/")
STUFE_PRODUKTE = ("Produkte", "/produkte/")
STUFE_UEBER = ("Über uns", "/ueber-uns/")
OG_STANDARD = ("/og-image.png", "Meyssens – Digitale Infrastruktur für Organisationen")
# Stand der Seiten ohne eigenes Prüfdatum (Startseite, Übersichten, Über uns, Produkte): bei inhaltlichen Änderungen anpassen
SEITEN_STAND = "2026-10-28"


def krumen(*stufen):
    teile = ['<li><a href="%s">%s</a></li>' % (u, html.escape(n)) for n, u in stufen[:-1]]
    teile.append('<li aria-current="page">%s</li>' % html.escape(stufen[-1][0]))
    return '  <nav class="brotkrumen" aria-label="Brotkrumen"><ol>%s</ol></nav>' % "".join(teile)


def bild_objekt(bild):
    pfad, alt = bild
    return {"@type": "ImageObject", "url": DOMAIN + pfad, "width": 1200, "height": 630, "caption": alt}


def seitenkopf(stufen, titel, bild=OG_STANDARD):
    # Kopfwerte (Brotkrumen, Open-Graph-Bild) und JSON-LD (BreadcrumbList, WebPage mit Bild) einer Seite
    url = DOMAIN + stufen[-1][1]
    webseite = {"@type": "WebPage", "@id": url, "url": url, "name": titel, "inLanguage": "de-CH",
                "isPartOf": {"@id": DOMAIN + "/#website"}, "breadcrumb": {"@id": url + "#brotkrumen"},
                "primaryImageOfPage": bild_objekt(bild)}
    return ({"krumen": krumen(*stufen), "og_bild": DOMAIN + bild[0], "og_alt": html.escape(bild[1])},
            [brotkrumen(*stufen), webseite])


def og_branche(slug, name):
    # Teilbares Bild pro Branche (bilder.py), sonst das allgemeine Bild
    pfad = "/assets/og/branche-%s.png" % slug
    return (pfad, "%s: digitale Werkzeuge von Meyssens" % name) if (ROOT / pfad.lstrip("/")).is_file() else OG_STANDARD


def png_masse(pfad):
    # Breite und Höhe aus dem PNG-Kopf (IHDR)
    with open(pfad, "rb") as f:
        kopf = f.read(24)
    return int.from_bytes(kopf[16:20], "big"), int.from_bytes(kopf[20:24], "big")


def verwandt_abschnitt(links):
    # "Das könnte Sie auch interessieren": 3 Kacheln mit beschreibendem Linktext
    return ('<section id="verwandt">\n  <div class="r">\n    <span class="s-label">Weiterlesen</span>\n'
            '    <h2>Das könnte Sie auch interessieren</h2>\n  </div>\n  <div class="feat-grid r">\n%s\n  </div>\n</section>\n\n'
            % "\n".join(link_kachel(u, art, name, text, "Mehr zu " + html.escape(name)) for u, art, name, text in links))


def verwandte(netz, info, url, anzahl=3):
    # Thematisch passende Seiten aus den Verknüpfungen der Daten: zuerst je eine andere Seitenart
    # (Branche, Baustein oder Produkt, Ratgeber), dann weitere direkte Nachbarn, dann Nachbarn der Nachbarn
    wunsch = {"branche": ("baustein", "ratgeber", "produkt", "branche"), "baustein": ("branche", "ratgeber", "baustein", "produkt"),
              "ratgeber": ("branche", "baustein", "produkt", "ratgeber")}[info[url]["typ"]]
    eigene = set(netz.get(url, []))
    # Ähnlichste Nachbarn zuerst: Anteil gemeinsamer Verknüpfungen (Jaccard), bei Gleichstand Reihenfolge der Daten
    def aehnlich(n):
        andere = set(netz.get(n, []))
        return len(eigene & andere) / max(1, len(eigene | andere))
    nachbarn = sorted((n for n in netz.get(url, []) if n != url), key=lambda n: -aehnlich(n))
    zweite = [m for n in nachbarn for m in netz.get(n, []) if m != url and m not in nachbarn]
    wahl = []
    for typ in wunsch:
        for n in nachbarn:
            if info[n]["typ"] == typ and n not in wahl:
                wahl.append(n)
                break
    for n in nachbarn + zweite:
        if len(wahl) >= anzahl:
            break
        if n not in wahl:
            wahl.append(n)
    return [(n, info[n]["art"], info[n]["name"], info[n]["text"]) for n in wahl[:anzahl]]


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
    # Wörter im sichtbaren Text eines HTML-Fragments, ohne Navigation (Inhaltsverzeichnis)
    text = re.sub(r"<nav\b.*?</nav>", " ", text, flags=re.S)
    return len(re.findall(r"\w[\w'’.-]*", html.unescape(re.sub(r"<[^>]+>", " ", text))))


def pruefe_artikel(a, nach_slug):
    fehlt = [f for f in ("slug", "art", "name", "titel", "beschreibung", "h1", "lead", "geprueft", "veroeffentlicht")
             if not a.get(f)]
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
        if ist_baustein(p):
            fehlt = [f for f in BAUSTEIN_FELDER if not p.get(f)]
            if p.get("aufwand") not in AUFWAND:
                fehlt.append("aufwand (%s)" % ", ".join(AUFWAND))
            if not isinstance(p.get("personendaten"), bool):
                fehlt.append("personendaten (true oder false)")
            if not all(q["url"].startswith("https://") for q in p.get("quellen", [])):
                fehlt.append("quellen mit https-Links")
            if fehlt:
                raise SystemExit("Baustein %s: %s" % (p["slug"], ", ".join(fehlt)))
    nach_slug = {p["slug"]: p for p in produkte}
    allgemein = [p for p in produkte if not ist_baustein(p)]

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
    for a in artikel:
        au = a.get("automatisierung")
        if not au:
            continue
        fehlt = [f for f in ("intro", "kette", "demo", "geprueft") if not au.get(f)]
        if not 3 <= len(au.get("bausteine", [])) <= 4:
            fehlt.append("bausteine (3 bis 4)")
        if fehlt or a["art"] != "branche":
            raise SystemExit("Automatisierung %s: %s" % (a["slug"], ", ".join(fehlt) or "nur auf Branchenseiten"))
        for s in au["bausteine"]:
            if s not in nach_slug or nach_slug[s].get("branche") != a["slug"]:
                raise SystemExit("Automatisierung %s: %s ist kein Baustein dieser Branche" % (a["slug"], s))
        if au["demo"] not in au["bausteine"]:
            raise SystemExit("Automatisierung %s: Demo muss einer der Bausteine sein" % a["slug"])
    for b in branchen:
        for x in b.get("bausteine", []):
            if x not in nach_slug or nach_slug[x].get("branche") != b["slug"]:
                raise SystemExit("Branche %s: %s ist kein Baustein dieser Branche" % (b["slug"], x))
    for p in produkte:
        if ist_baustein(p) and p["slug"] not in a_bausteine(artikel, branchen):
            raise SystemExit("Baustein %s steht auf keiner Branchenseite" % p["slug"])
        for q in p.get("faq", []):
            if not q.get("frage") or not q.get("antwort"):
                raise SystemExit("Baustein %s: FAQ unvollständig" % p["slug"])
    ratgeber = [a for a in artikel if a["art"] == "ratgeber"]
    nach_ratgeber = {a["slug"]: a for a in ratgeber}
    for b in (b for b in branchen if b.get("automatisierungen")):
        pruefe_automatisierungen(b, nach_slug, nach_ratgeber)

    # Seiten und ihre Verknüpfungen aus den Daten: Branche ↔ Bausteine/Produkte ↔ Ratgeber
    info, netz = {}, {}
    def verbinde(a, b):
        for x, y in ((a, b), (b, a)):
            netz.setdefault(x, [])
            if y not in netz[x]:
                netz[x].append(y)
    for p in produkte:
        info["/produkte/%s/" % p["slug"]] = {"typ": "baustein" if ist_baustein(p) else "produkt",
                                             "art": "Baustein" if ist_baustein(p) else "Produkt",
                                             "name": p["name"], "text": anfang(p["kurzbeschreibung"], 70)}
    for b in branchen:
        info["/branchen/%s/" % b["slug"]] = {"typ": "branche", "art": "Branche", "name": b["name"], "text": b["kurz"]}
    for a in artikel:
        info["/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"])] = {
            "typ": "branche" if a["art"] == "branche" else "ratgeber", "art": "Branche" if a["art"] == "branche" else "Ratgeber",
            "name": a["name"], "text": a.get("kurz") or anfang(a["beschreibung"], 70)}
    for b in branchen:
        for x in b.get("bausteine", []) + b["produkte"]:
            verbinde("/branchen/%s/" % b["slug"], "/produkte/%s/" % x)
    for a in artikel:
        url_a = "/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"])
        ziele = ["/produkte/%s/" % x for x in a.get("automatisierung", {}).get("bausteine", []) + a["produkte"]]
        ziele += [l["url"] for l in a["weiterlesen"]] + re.findall(r'href="(/[^"#]*)', lies("artikel/%s.html" % a["slug"]))
        for z in ziele:
            if z in info:
                verbinde(url_a, z)
    for r in ratgeber:
        for b in branchen:
            if set(r["produkte"]) & set(b["produkte"] + b.get("bausteine", [])) or \
                    b.get("automatisierungen", {}).get("ratgeber") == r["slug"]:
                verbinde("/ratgeber/%s/" % r["slug"], "/branchen/%s/" % b["slug"])
    ZIELNAMEN.update({u: x["name"] for u, x in info.items()})
    for p in (p for p in produkte if ist_baustein(p)):
        verbinde("/produkte/%s/" % p["slug"], "/branchen/%s/" % p["branche"])
        for l in p.get("weiterlesen", []):
            if l["url"] in info:
                verbinde("/produkte/%s/" % p["slug"], l["url"])

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
    for p in allgemein:
        e = {k: html.escape(str(v)) for k, v in p.items()}
        stufe = {k: html.escape(v) for k, v in STUFEN[p["status"]].items()}
        url = "%s/produkte/%s/" % (DOMAIN, p["slug"])
        hinweis = ""
        if p.get("hinweis"):
            hinweis = '  <div class="note">%s</div>' % e["hinweis"]
        kopf, seitenld = seitenkopf((START, STUFE_PRODUKTE, (p["name"], "/produkte/%s/" % p["slug"])),
                               p.get("seo_titel") or "%s – Meyssens" % p["name"])
        werte = dict(gemeinsam, **kopf, **{
            "titel": html.escape(p.get("seo_titel") or "%s – Meyssens" % p["name"]),
            "beschreibung": html.escape(p.get("seo_beschreibung") or kurz(p["kurzbeschreibung"])),
            "url": url,
            "seo_kopf": seo_kopf(url),
            "name": e["name"],
            "h1": html.escape(p.get("h1") or p["name"]),
            "status_badge": stufe["badge"],
            "status_text": stufe["text"],
            "knopf": stufe["knopf"],
            "kurzbeschreibung": e["kurzbeschreibung"],
            "problem": e["problem"],
            "loesung": e["loesung"],
            "fuer_wen": e["fuer_wen"],
            "hinweis": hinweis,
            "schweiz": e["schweiz"],
            "demo": demo(p.get("demo"), "produkt"),
            "ansicht": produkt_ansicht(ansichten, p),
            "ld": ld(*seitenld, dienst(p, url)),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        schreibe("produkte/%s/index.html" % p["slug"], fuelle(vorlage_produkt, werte))

    vorlage_branche = lies("vorlage_branche.html")
    for b in branchen:
        fuer = b["fuer"]
        burl = "/branchen/%s/" % b["slug"]
        kopf, seitenld = seitenkopf((START, STUFE_BRANCHEN, (b["name"], burl)), b.get("seo_titel") or titel_branche(b),
                               og_branche(b["slug"], b["name"]))
        werte = dict(gemeinsam, **kopf, **{
            "verwandt": verwandt_abschnitt(verwandte(netz, info, burl)),
            "titel": html.escape(b.get("seo_titel") or titel_branche(b)),
            "beschreibung": html.escape(b.get("seo_beschreibung") or b["beschreibung"]),
            "url": "%s/branchen/%s/" % (DOMAIN, b["slug"]),
            "seo_kopf": seo_kopf("%s/branchen/%s/" % (DOMAIN, b["slug"])),
            "h1": h1_html(b.get("h1") or "Digitale Infrastruktur für %s" % fuer),
            "name": html.escape(b["name"]),
            "fuer": html.escape(fuer),
            "intro": html.escape(b["intro"]),
            "probleme": "\n".join(karte("", x["titel"], x["text"]) for x in b["probleme"]),
            "szenarien": "\n".join(karte("Beispielszenario", x["titel"], x["text"]) for x in b["szenarien"]),
            "demo": demo(b.get("demo"), "branche"),
            # FAQPage nur aus den sichtbaren Fragen der Seite
            "ld": ld(*seitenld,
                     {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["frage"],
                      "acceptedAnswer": {"@type": "Answer", "text": q["antwort"]}} for q in b["faq"]]}),
            "besonderheit_titel": html.escape(b["besonderheit"]["titel"]),
            "besonderheit_text": html.escape(b["besonderheit"]["text"]),
            "schweiz": html.escape(b["schweiz"]),
            "produkte": "\n".join(angebot(nach_slug[s]) for s in b["produkte"]),
            "sprung_auto": '<a href="#automatisierung">Automatisierungen</a>' if b.get("automatisierungen") else "",
            "bausteine_abschnitt": automatisierungen(b, nach_slug, nach_ratgeber, formular_ziel, einwilligung) if b.get("automatisierungen") else ('<section id="bausteine">\n  <div class="r">\n    <span class="s-label">Automatisierung</span>\n'
                                    '    <h2>Bausteine für %s</h2>\n    <p class="s-lead">%s Entwürfe ja, automatischer Versand nein: '
                                    'Was Ihren Betrieb verlässt, gibt ein Mensch frei.</p>\n  </div>\n  <div class="angebot-raster">\n%s\n  </div>\n'
                                    '</section>\n' % (html.escape(b["name"]), html.escape(b.get("bausteine_intro", "")),
                                                     "\n".join(angebot(nach_slug[x]) for x in b["bausteine"]))
                                    if b.get("bausteine") else ""),
            "faq": qa_liste(b["faq"]),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        seite = fuelle(vorlage_branche, werte)
        if b.get("automatisierungen"):
            n = worte(zwischen(seite, '<section id="automatisierung"', "</section>"))
            hinweis = "" if AUTOMATISIERUNGEN_WORTE[0] <= n <= AUTOMATISIERUNGEN_WORTE[1] else "  ACHTUNG: ausserhalb %d bis %d" % AUTOMATISIERUNGEN_WORTE
            print("Wörter /branchen/%s/#automatisierung: %d%s" % (b["slug"], n, hinweis))
        schreibe("branchen/%s/index.html" % b["slug"], seite)

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
        stufe_a = STUFE_BRANCHEN if a["art"] == "branche" else STUFE_RATGEBER
        bild_a = og_branche(a["slug"], a["name"]) if a["art"] == "branche" else OG_STANDARD
        kopf, seitenld = seitenkopf((START, stufe_a, (a["name"], pfad)), a["titel"], bild_a)
        werte = dict(gemeinsam, **kopf, **{
            "verwandt": verwandt_abschnitt(verwandte(netz, info, pfad)),
            "titel": html.escape(a["titel"]),
            "beschreibung": html.escape(a["beschreibung"]),
            "url": DOMAIN + pfad,
            "seo_kopf": seo_kopf(DOMAIN + pfad),
            "name": html.escape(a["name"]),
            "chip": html.escape(a["name"] if a["art"] == "branche" else "Ratgeber"),
            "h1": html.escape(a["h1"]),
            "lead": html.escape(a["lead"]),
            "autor": AUTOR,
            "geprueft": datum.strftime("%d.%m.%Y"),
            "inhalt": inhalt,
            "toc": inhaltsverzeichnis(inhalt, bool(a.get("automatisierung"))),
            "automatisierung": automatisierung(a, nach_slug, ansichten, formular_ziel, einwilligung),
            "faq": "\n".join('    <div class="qa">\n      <h3>%s</h3>\n      <p>%s</p>\n    </div>'
                             % (html.escape(q["frage"]), html.escape(q["antwort"])) for q in a["faq"]),
            "weiterlesen": "\n".join('    <a href="%s" class="feat tile">\n      <h3>%s</h3>\n      <p>%s</p>\n'
                                     '      <span class="way-go">Weiterlesen %s</span>\n    </a>'
                                     % (l["url"], html.escape(l["titel"]), html.escape(l["grund"]), PFEIL)
                                     for l in a["weiterlesen"]),
            "ehrlich": html.escape(ehrlich([nach_slug[s] for s in a["produkte"]])),
            "produkte": "\n".join(angebot(nach_slug[s]) for s in a["produkte"]),
            "quellen": "\n".join('      <li><a href="%s" target="_blank" rel="noopener">%s</a></li>'
                                 % (html.escape(q["url"]), html.escape(q["titel"])) for q in a["quellen"]),
            "zurueck_url": art["zurueck"][0],
            "zurueck_text": art["zurueck"][1],
            "anfrage_titel": art["anfrage"],
            "betreff": html.escape(art["betreff"] % a["name"]),
            "feld": art["feld"][0],
            "feld_label": art["feld"][1],
            # Article und FAQPage nur aus dem sichtbaren Inhalt der Seite
            "ld": ld(*seitenld,
                     {"@type": "Article", "headline": a["h1"], "description": a["beschreibung"],
                      "inLanguage": "de-CH", "datePublished": a["veroeffentlicht"], "dateModified": a["geprueft"],
                      "mainEntityOfPage": {"@id": DOMAIN + pfad}, "author": {"@id": DOMAIN + "/ueber-uns/#person"},
                      "publisher": {"@id": DOMAIN + "/#org"}, "image": bild_objekt(bild_a)},
                     {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["frage"],
                      "acceptedAnswer": {"@type": "Answer", "text": q["antwort"]}} for q in a["faq"]]}),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        seite = fuelle(vorlage_artikel, werte)
        n = worte(ohne_automatisierung(zwischen(seite, '<main id="main"', '<section id="quellen"')))
        hinweis = "" if WORTE[0] <= n <= WORTE[1] else "  ACHTUNG: ausserhalb %d bis %d" % WORTE
        print("Wörter %s: %d%s" % (pfad, n, hinweis))
        if a.get("automatisierung"):
            n = worte(zwischen(seite, '<section id="automatisierung"', "</section>"))
            hinweis = "" if AUTO_WORTE[0] <= n <= AUTO_WORTE[1] else "  ACHTUNG: ausserhalb %d bis %d" % AUTO_WORTE
            print("Wörter %s#automatisierung: %d%s" % (pfad, n, hinweis))
        schreibe(pfad.strip("/") + "/index.html", seite)

    vorlage_baustein = lies("vorlage_baustein.html")
    nach_branche = {a["slug"]: a for a in artikel_branchen}
    nach_branche.update({b["slug"]: b for b in branchen})
    for p in (p for p in produkte if ist_baustein(p)):
        b = nach_branche[p["branche"]]
        langtext = "automatisierung" in b
        reihe = b["automatisierung"]["bausteine"] if langtext else b.get("bausteine", [])
        e = {k: html.escape(str(v)) for k, v in p.items() if isinstance(v, str)}
        stufe = {k: html.escape(v) for k, v in STUFEN[p["status"]].items()}
        pfad = "/produkte/%s/" % p["slug"]
        roh = json.dumps(p, ensure_ascii=False)
        if "[Status" in roh or "ß" in roh:
            raise SystemExit("Baustein %s: Platzhalter [Status ...] oder ß im Text" % p["slug"])
        andere = [nach_slug[s] for s in reihe if s != p["slug"]]
        daten = ('    <ul class="bedingungen">\n%s\n    </ul>\n' % "\n".join("      <li>%s</li>" % html.escape(x) for x in BEDINGUNGEN)
                 if p["personendaten"] else "")
        kopf, seitenld = seitenkopf((START, STUFE_BRANCHEN, (b["name"], "/branchen/%s/" % b["slug"]), (p["name"], pfad)),
                               p.get("seo_titel") or "%s – Meyssens" % p["name"], og_branche(b["slug"], b["name"]))
        werte = dict(gemeinsam, **kopf, **{
            "verwandt": verwandt_abschnitt(verwandte(netz, info, pfad)),
            "titel": html.escape(p.get("seo_titel") or "%s – Meyssens" % p["name"]),
            "beschreibung": html.escape(p.get("seo_beschreibung") or kurz(p["kurzbeschreibung"])),
            "url": DOMAIN + pfad,
            "seo_kopf": seo_kopf(DOMAIN + pfad),
            "name": e["name"],
            "branche": html.escape(b["name"]),
            "branche_url": "/branchen/%s/" % b["slug"],
            "branche_anker": "#automatisierung" if langtext or b.get("automatisierungen") else "#bausteine",
            "status_badge": stufe["badge"],
            "status_text": stufe["text"],
            "knopf": stufe["knopf"],
            "kurzbeschreibung": e["kurzbeschreibung"],
            "problem": e["problem"],
            "loesung": e["loesung"],
            "mensch": e["mensch"],
            "fuer_wen": e["fuer_wen"],
            "aufwand": e["aufwand"],
            "daten": e["daten"],
            "bedingungen": daten,
            "regel": "<strong>%s</strong> %s" % REGEL,
            "geprueft": datetime.date.fromisoformat(p["geprueft"]).strftime("%d.%m.%Y"),
            "ansicht": produkt_ansicht(ansichten, p),
            # Weitere Bausteine der Branche und Weiterlesen-Links
            "weitere": ('<section id="weitere" class="flaeche">\n  <div class="r">\n    <span class="s-label">%s</span>\n'
                        '    <h2>%s</h2>\n    <p class="s-lead">%s</p>\n  </div>\n  <div class="feat-grid zwei r">\n%s\n  </div>\n</section>\n'
                        % (html.escape(b["name"]),
                           "Weitere Bausteine für %s" % html.escape(b["name"]) if andere and not p.get("weiterlesen")
                           else "Weitere Bausteine und passende Seiten" if andere else "Passend zum Thema",
                           'Ausgewählt für diese Branche, mit Ablauf-Grafik und Beispiel auf der <a href="/branchen/%s/#automatisierung">'
                           'Branchenseite</a>.' % b["slug"] if langtext else
                           'Alle zehn geplanten Bausteine für %s und drei Abläufe stehen auf der <a href="/branchen/%s/#automatisierung">'
                           'Branchenseite</a>.' % (html.escape(b["name"]), b["slug"]) if b.get("automatisierungen") else
                           'Alle Bausteine für %s stehen auf der <a href="/branchen/%s/#bausteine">Branchenseite</a>.'
                           % (html.escape(b["name"]), b["slug"]),
                           "\n".join([link_kachel("/produkte/%s/" % x["slug"], STUFEN[x["status"]]["badge"], x["name"],
                                              x["kurzbeschreibung"], "Mehr erfahren") for x in andere] +
                                     [link_kachel(l["url"], None, l["titel"], l["grund"], "Weiterlesen")
                                      for l in p.get("weiterlesen", [])]))),
            "faq_abschnitt": ('\n<section id="fragen">\n  <div class="r">\n    <span class="s-label">Fragen</span>\n'
                              '    <h2>Häufige Fragen</h2>\n  </div>\n  <div class="qa-list r">\n%s\n  </div>\n</section>\n'
                              % qa_liste(p["faq"]) if p.get("faq") else ""),
            "quellen": "\n".join('      <li><a href="%s" target="_blank" rel="noopener">%s</a></li>'
                                 % (html.escape(q["url"]), html.escape(q["titel"])) for q in p["quellen"]),
            "ld": ld(*seitenld, dienst(p, DOMAIN + pfad, b["name"]), *([faq_ld(p["faq"])] if p.get("faq") else [])),
            "formular_ziel": formular_ziel,
            "einwilligung": einwilligung,
            "formular_skript": formular_skript,
        })
        seite = fuelle(vorlage_baustein, werte)
        n = worte(zwischen(seite, '<main id="main"', '<section id="quellen"'))
        hinweis = "" if BAUSTEIN_WORTE[0] <= n <= BAUSTEIN_WORTE[1] else "  ACHTUNG: ausserhalb %d bis %d" % BAUSTEIN_WORTE
        print("Wörter %s: %d%s" % (pfad, n, hinweis))
        schreibe(pfad.strip("/") + "/index.html", seite)

    kopf, seitenld = seitenkopf((START, UNTERNEHMEN), "Digitale Werkzeuge für Schweizer KMU und Vereine | Meyssens")
    werte = dict(gemeinsam, **kopf, **{
        "titel": "Digitale Werkzeuge für Schweizer KMU und Vereine | Meyssens",
        "beschreibung": html.escape("Umfragen, Newsletter, Vereinswebsite, Mail-Assistent und Bausteine für Praxen, "
                                    "Verwaltungen und Büros in der Schweiz. Jetzt Pilotpartner werden."),
        "url": DOMAIN + "/unternehmen/",
        "seo_kopf": seo_kopf(DOMAIN + "/unternehmen/"),
        "produkte": scrolly(ansichten, allgemein, mehr=True),
        # Bausteine nach Branche: zuerst die Branchen mit Abschnitt "Was sich automatisieren lässt", dann die übrigen
        "bausteine": "\n".join(
            '    <div class="auto-gruppe r">\n      <h3><a href="/branchen/%s/%s">%s</a></h3>\n      <ul>\n%s\n      </ul>\n    </div>'
            % (a["slug"], anker, html.escape(a["name"]), "\n".join(
                '        <li><a href="/produkte/%s/">%s %s</a><span class="status-chip">%s</span></li>'
                % (s, html.escape(nach_slug[s]["name"]), PFEIL, html.escape(STUFEN[nach_slug[s]["status"]]["badge"]))
                for s in liste))
            for a, anker, liste in [(a, "#automatisierung", a["automatisierung"]["bausteine"])
                                    for a in artikel_branchen if a.get("automatisierung")] +
                                   [(b, "#automatisierung" if b.get("automatisierungen") else "#bausteine", b["bausteine"])
                                    for b in branchen if b.get("bausteine")]),
        "ld": ld(*seitenld),
        "branchen": "\n".join('    <a href="/branchen/%s/">%s %s</a>' % (b["slug"], html.escape(b["name"]), PFEIL)
                               for b in sorted(branchen + artikel_branchen, key=lambda b: b["name"])),
        "ratgeber": "\n".join('    <a href="/ratgeber/%s/">%s %s</a>' % (a["slug"], html.escape(a["name"]), PFEIL)
                               for a in ratgeber),
    })
    schreibe("unternehmen/index.html", fuelle(lies("vorlage_unternehmen.html"), werte))

    # Übersichtsseiten (Brotkrumen-Stufen) und Über uns, alle aus vorlage_seite.html
    vorlage_seite = lies("vorlage_seite.html")
    def raster(eintraege, rid=""):
        return '  <div class="feat-grid r"%s>\n%s\n  </div>' % (' id="%s"' % rid if rid else "", "\n".join(
            link_kachel(u, art, name, text, "Mehr zu " + html.escape(name)) for u, art, name, text in eintraege))
    # Suchfeld über dem Branchen-Raster: filtert beim Tippen (assets/demos.js), ohne JavaScript ausgeblendet
    branchen_suche = (
        '  <div class="r" id="branchen-suche">\n'
        '    <label class="sr-only" for="branchen-suchfeld">Branche suchen</label>\n'
        '    <input class="finput" type="search" id="branchen-suchfeld" placeholder="Branche suchen" autocomplete="off" '
        'aria-controls="branchen-raster">\n'
        '    <p class="sr-only" id="branchen-treffer" aria-live="polite"></p>\n'
        '    <p id="branchen-leer" hidden>Keine Branche gefunden.</p>\n  </div>\n')
    def abschnitt_html(anker, label, titel, inhalt, klasse=""):
        return ('<section id="%s"%s>\n  <div class="r">\n    <span class="s-label">%s</span>\n    <h2>%s</h2>\n  </div>\n%s\n</section>\n'
                % (anker, ' class="%s"' % klasse if klasse else "", label, titel, inhalt))
    def eintrag(u):
        return (u, info[u]["art"], info[u]["name"], info[u]["text"])
    alle_branchen = sorted([u for u in info if info[u]["typ"] == "branche"], key=lambda u: info[u]["name"])
    pilot = sum(p["status"] == "Pilotphase" for p in allgemein)
    uebersichten = [
        ((START, STUFE_BRANCHEN), "Branchen: digitale Werkzeuge für Schweizer KMU | Meyssens",
         "Zahnarztpraxen, Immobilienverwaltungen, Architekturbüros, Pflege, Bau, Treuhand und mehr: Werkzeuge "
         "für Ihre Branche. Branche wählen und ansehen.",
         "Branchen", "Werkzeuge für <span class=\"hl\">Ihre Branche.</span>",
         "Für jede Branche zeigen wir, wo digitale Werkzeuge im Alltag entlasten können, was rechtlich gilt und welche "
         "Bausteine wir planen. Alle Angaben beziehen sich auf die Schweiz.",
         abschnitt_html("alle", "Branchen", "Alle Branchen",
                        branchen_suche + raster([eintrag(u) for u in alle_branchen], "branchen-raster"))),
        ((START, STUFE_RATGEBER), "Ratgeber für Schweizer KMU: nDSG, Offerten | Meyssens",
         "Ratgeber mit Quellen und Prüfdatum: nDSG, Aufbewahrungsfristen, Mängelrüge 2026, Patientenformulare, "
         "Sicherheitsnachweis, Spitex und mehr. Jetzt lesen.",
         "Ratgeber", "Ratgeber mit <span class=\"hl\">Quellen.</span>",
         "Kurze Leitfäden zu Fragen aus dem Alltag Schweizer KMU, Praxen, Verwaltungen und Vereine. Jeder Ratgeber nennt "
         "seine Quellen und das Datum der letzten Prüfung. Allgemeine Information, keine Rechtsberatung.",
         abschnitt_html("alle", "Ratgeber", "Alle Ratgeber", raster(
             [eintrag("/ratgeber/%s/" % a["slug"]) for a in ratgeber]))),
        ((START, STUFE_PRODUKTE), "Produkte und Bausteine für Schweizer KMU | Meyssens",
         "Umfragen, Newsletter, Website-Chatbot und Bausteine für Praxen, Verwaltungen, Büros und Spitex. Status ehrlich "
         "angegeben. Jetzt ansehen und vormerken.",
         "Produkte", "Produkte und <span class=\"hl\">Bausteine.</span>",
         "%d Produkte sind in der Pilotphase, alle weiteren Produkte und Bausteine sind in Planung. Den Stand nennen wir auf "
         "jeder Seite." % pilot,
         abschnitt_html("produkte", "Produkte", "Werkzeuge für Unternehmen und Vereine",
                        raster([eintrag("/produkte/%s/" % p["slug"]) for p in allgemein])) + "\n" +
         abschnitt_html("bausteine", "Bausteine", "Bausteine nach Branche",
                        raster([eintrag("/produkte/%s/" % p["slug"]) for p in produkte if ist_baustein(p)]), "flaeche")),
    ]
    bausteine_alle = [p for p in produkte if ist_baustein(p)]
    ueber_inhalt = (
        abschnitt_html("wer", "Wer", "Wer hinter Meyssens steht",
            '  <div class="artikel-text r">\n'
            '    <p>Meyssens ist ein Einzelunternehmen in Lausen im Kanton Basel-Landschaft, gegründet von Lionel Nickelsen. '
            'Die Firma ist als Einzelfirma im Kanton Basel-Landschaft eingetragen. Wir haben noch keine Kunden und keine '
            'Referenzen und sagen das auf unseren Seiten offen.</p>\n  </div>') + "\n" +
        abschnitt_html("angebot", "Angebot", "Was wir anbieten",
            '  <div class="artikel-text r">\n'
            '    <p>Für Gemeinden betreiben wir eine Beteiligungsplattform auf Basis der Open-Source-Software Decidim, als '
            'verwalteten Dienst mit Hosting, Updates, Backups und Sicherheit. Mehr dazu auf der Seite '
            '<a href="/gemeinden/">Für Gemeinden</a>.</p>\n'
            '    <p>Für Unternehmen und Vereine entwickeln wir schlanke Werkzeuge. Stand heute sind %d von %d Produkten in der '
            'Pilotphase, die übrigen und alle %d Bausteine sind in Planung. Die Übersicht steht unter '
            '<a href="/produkte/">Produkte und Bausteine</a>, die Branchen unter <a href="/branchen/">Branchen</a>.</p>\n'
            '  </div>' % (pilot, len(allgemein), len(bausteine_alle)), "flaeche") + "\n" +
        abschnitt_html("arbeitsweise", "Arbeitsweise", "Wie wir arbeiten",
            '  <div class="artikel-text r">\n    <ul>\n'
            '      <li><strong>Persönlich:</strong> Sie erreichen uns direkt, ohne Ticketsystem.</li>\n'
            '      <li><strong>Entwürfe ja, automatischer Versand nein:</strong> Unsere Bausteine bereiten vor. Was Ihren '
            'Betrieb verlässt, gibt ein Mensch frei.</li>\n'
            '      <li><strong>Pilotpartner gestalten mit:</strong> Pilotpartner erhalten die Einrichtung kostenlos und '
            'gestalten das Produkt mit.</li>\n'
            '      <li><strong>Ehrliche Angaben:</strong> Jede Produktseite nennt den Status. Angaben zum Aufwand sind als '
            'Einschätzung gekennzeichnet, Ratgeber nennen Quellen und das Datum der letzten Prüfung.</li>\n'
            '    </ul>\n  </div>') + "\n" +
        abschnitt_html("datenschutz-prinzipien", "Datenschutz", "Datenschutz-Prinzipien",
            '  <div class="artikel-text r">\n'
            '    <p>Die Beteiligungsplattform für Gemeinden wird ausschliesslich in der Schweiz gehostet. Für Personendaten in '
            'unseren Bausteinen gelten drei Bedingungen: %s.</p>\n'
            '    <p>Diese Website selbst wird über GitHub Pages (GitHub, Inc., USA) ausgeliefert. Die Einzelheiten stehen in der '
            '<a href="#datenschutz" onclick="document.getElementById(\'datenschutz-modal\').style.display=\'flex\'">'
            'Datenschutzerklärung</a>.</p>\n  </div>' % ", ".join(BEDINGUNGEN), "flaeche") + "\n" +
        abschnitt_html("kontakt", "Kontakt", "Kontakt und Standort",
            '  <div class="artikel-text r">\n'
            '    <p>Meyssens, Lausen, Basel-Landschaft, Schweiz<br>E-Mail: <a href="mailto:lionel@meyssens.ch">lionel@meyssens.ch</a></p>\n'
            '    <p><a class="btn-p" href="mailto:lionel@meyssens.ch">E-Mail an Lionel Nickelsen %s</a></p>\n'
            '  </div>' % PFEIL))
    uebersichten.append(((START, STUFE_UEBER), "Über uns: Meyssens aus Lausen BL | Meyssens",
        "Wer hinter Meyssens steht: Einzelunternehmen von Lionel Nickelsen in Lausen BL, Arbeitsweise und "
        "Datenschutz-Prinzipien. Jetzt mehr lesen.",
        "Über uns", "Über <span class=\"hl\">Meyssens.</span>",
        "Ein Einzelunternehmen aus Lausen im Kanton Basel-Landschaft: digitale Werkzeuge für Gemeinden, Unternehmen und "
        "Vereine, persönlich begleitet.", ueber_inhalt))
    for stufen, titel, beschreibung, chip, h1, lead, inhalt in uebersichten:
        pfad = stufen[-1][1]
        kopf, seitenld = seitenkopf(stufen, titel)
        extra = [{"@type": "AboutPage", "@id": DOMAIN + pfad + "#ueber", "url": DOMAIN + pfad, "about": {"@id": DOMAIN + "/#org"},
                  "mainEntity": {"@id": DOMAIN + "/ueber-uns/#person"}}] if pfad == "/ueber-uns/" else []
        werte = dict(gemeinsam, **kopf, **{
            "titel": html.escape(titel), "beschreibung": html.escape(beschreibung), "url": DOMAIN + pfad,
            "seo_kopf": seo_kopf(DOMAIN + pfad), "chip": chip, "h1": h1, "lead": html.escape(lead), "inhalt": inhalt,
            "ld": ld(*seitenld, *extra)})
        schreibe(pfad.strip("/") + "/index.html", fuelle(vorlage_seite, werte))

    # 404-Seite (GitHub Pages liefert /404.html mit Status 404 aus): nicht indexieren, nicht in der Sitemap
    werte = dict(gemeinsam, **{
        "titel": "Seite nicht gefunden | Meyssens",
        "beschreibung": "Diese Seite gibt es nicht. Zu den Werkzeugen für Schweizer KMU und Vereine, den Branchen oder zur Startseite.",
        "url": DOMAIN + "/404.html",
        "links": "\n".join('    <a class="feat tile" href="%s">\n      <h3>%s</h3>\n      <p>%s</p>\n      <span class="way-go">Öffnen %s</span>\n    </a>'
                           % (u, html.escape(t), html.escape(x), PFEIL) for u, t, x in (
                               ("/unternehmen/", "Für Unternehmen und Vereine", "Werkzeuge und Bausteine für Schweizer KMU, Praxen, Verwaltungen und Vereine."),
                               ("/unternehmen/#branchen", "Branchen", "Zahnarztpraxen, Immobilienverwaltungen, Architekturbüros, Pflege und weitere."),
                               ("/unternehmen/#ratgeber", "Ratgeber", "nDSG für KMU, Offertanfragen, Online-Abstimmung im Verein, Website-Chatbot."),
                               ("/", "Startseite", "Überblick über Meyssens."))),
    })
    schreibe("404.html", fuelle(lies("vorlage_404.html"), werte))

    # Gemeinden-Seite: Bühne unter dem Hero und Ansichten im Sticky-Abschnitt "Ablauf"
    neu_g = setze_auto(gemeinden, "buehne", '<div class="buehne" data-buehne>\n%s\n</div>' % geraet(
        '<span data-i18n="g.demo.titel">Mitwirken in Beispielgemeinde</span>', teil(ansichten, "gemeinden-held"),
        '<span data-i18n="g.beispiel">Beispiel</span>'))
    for i in range(1, 5):
        neu_g = setze_auto(neu_g, "ablauf-%d" % i, geraet(
            '<span data-i18n="g.ablauf%d.titel">%s</span>' % (i, teil(ansichten, "gemeinden-ablauf-%d-titel" % i)),
            teil(ansichten, "gemeinden-ablauf-%d" % i), '<span data-i18n="g.beispielansicht">Beispielansicht</span>'))
    if neu_g != gemeinden:
        schreibe("gemeinden/index.html", neu_g)

    neu = startseite(start, ansichten, allgemein, len(branchen) + len(artikel_branchen), len(ratgeber))
    if beschreibend(neu) != start:
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

    # lastmod: Prüfdatum der Seite, sonst SEITEN_STAND (Startseite, Übersichten, Über uns, Produkte ohne Prüfdatum)
    seiten = [("/", "1.0", SEITEN_STAND), ("/gemeinden/", "0.9", SEITEN_STAND), ("/unternehmen/", "0.8", SEITEN_STAND),
              ("/branchen/", "0.7", SEITEN_STAND), ("/produkte/", "0.7", SEITEN_STAND), ("/ratgeber/", "0.7", SEITEN_STAND),
              ("/ueber-uns/", "0.5", SEITEN_STAND)]
    seiten += [("/produkte/%s/" % p["slug"], "0.6", p.get("geprueft", SEITEN_STAND)) for p in produkte]
    seiten += [("/branchen/%s/" % b["slug"], "0.6", b.get("automatisierungen", {}).get("geprueft", SEITEN_STAND)) for b in branchen]
    seiten += [("/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"]), "0.6", a["geprueft"]) for a in artikel]
    zeilen = ["  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>%s</priority></url>"
              % (DOMAIN, pfad, stand, prio) for pfad, prio, stand in seiten]
    schreibe("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(zeilen) + "\n</urlset>\n")


if __name__ == "__main__":
    main()

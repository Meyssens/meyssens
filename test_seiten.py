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
- Ablauf-Kette als Scroll-Animation: jeder Schritt mit Art, genau einem Beispielsatz, bisherigem Hinweis und genau
  einem Link (Bausteinseite oder Anfrage), Abschluss, Anfrage-Knopf mit Betrieb, kurzes Formular (Name, E-Mail,
  Freitext) mit vorausgefüllter Branche und Kette, fester Anfrage-Knopf, Animation nur ohne reduzierte Bewegung
- Abschnitt "Automatisierungen" (Branchen mit Feld "automatisierungen"): genau 10 Bausteinkarten mit Status
  In Planung, Einschätzung zur Handarbeit, Mensch-Entscheid, Daten, offene Punkte, Link auf die eigene Seite oder auf
  das Formular; genau 3 Ablauf-Ketten wie oben (Links auf Bausteinseite, Karte oder Anfrage), ein gemeinsames Formular
  mit Auswahl der Kette, fester Anfrage-Knopf, Ratgeber-Link, Regel, Hinweise, Prüfdatum, Wortzahl
- Bausteinseiten (produkte.json mit Feld "branche"): Hinweise, Regel, Status, Einschätzung, bei Personendaten
  Auftragsbearbeitung/Schweiz/Datenminimierung, kein ß, Wortzahl, Sitemap, verlinkt von Branchenseite und Übersicht
- Keine Platzhalter ({{...}}, [Status, TODO, Lorem) auf irgendeiner Seite
- SEO (alle Seiten ausser /gemeinden/): Titel <= 60 Zeichen und eindeutig, Beschreibung <= 155 Zeichen mit
  Handlungsaufforderung und eindeutig, genau eine H1, keine übersprungene Überschriftenebene, Canonical, hreflang de-CH
  und x-default, lang="de-CH", Open-Graph-Bild, alt-Texte, JSON-LD mit Organization, WebSite, BreadcrumbList,
  FAQPage genau dann wenn sichtbare Fragen, Service mit areaServed Schweiz auf Produkt- und Bausteinseiten,
  keine Bewertungen; im Inhalt der Unternehmensseiten kein Bezug auf Deutschland
- 404.html: vorhanden, noindex, ohne Canonical, nicht in der Sitemap; robots.txt verweist auf die Sitemap
- Ratgeber und Bausteine: jede Seite endet mit dem Anfrage-Formular (Abschnitt #anfrage mit Formular und Knopf),
  Ratgeber sind von einer Branchenseite und der Übersicht verlinkt, Bausteine mit FAQ haben mindestens 3 Fragen,
  Branchen ohne Langtext zeigen ihre Bausteine im Abschnitt #bausteine
- Technik (alle Seiten ausser /gemeinden/): sichtbare Brotkrumen gleich BreadcrumbList, WebPage mit ImageObject,
  og:image und twitter:image auf vorhandene Datei, keine generischen Linktexte ohne Ziel, Bilder mit Massen und
  lazy loading ausser dem ersten Bild, "Das könnte Sie auch interessieren" mit 3 Links auf Branchen-, Baustein- und
  Ratgeberseiten, Über uns in Kopf und Fuss mit Person im JSON-LD, Article mit datePublished und dateModified,
  keine SearchAction ohne Suche, jede Seite von der Startseite in höchstens 3 Klicks erreichbar, keine verwaiste
  Seite, Sitemap mit lastmod (Prüfdatum, wo vorhanden)
Nur Python-Standardbibliothek.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from build import (ARTEN, AUTO_WORTE, AUTOMATISIERUNGEN_WORTE, MEIN, KETTE_ART, BAUSTEIN_WORTE, BEDINGUNGEN, REGEL, WORTE, ist_baustein, ohne_automatisierung,
                   worte, zwischen)

ROOT = Path(__file__).resolve().parent


def datum(iso):
    # "2026-10-27" -> "27.10.2026", wie auf den Seiten angezeigt
    j, m, t = iso.split("-")
    return "%s.%s.%s" % (t, m, j)
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
lastmod_alle = dict(re.findall(r"<loc>https://meyssens\.ch([^<]+)</loc><lastmod>([^<]+)</lastmod>", sitemap))
print("%-42s %s" % ("Seite", "Wörter"))
for a in artikel:
    url = "/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"])
    if url not in seiten:
        fehler.append("%s: Seite fehlt" % url)
        continue
    text, parser = seiten[url]
    sichtbar = html.unescape(re.sub(r"<script.*?</script>|<[^>]+>", " ", text, flags=re.S))
    for muss in ("Allgemeine Information, keine Rechtsberatung", "zuletzt geprüft am " + datum(a["geprueft"])):
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
BETRIEBE = ("Praxis", "Verwaltung", "Büro", "Einrichtung", "Betrieb")


def pruefe_ablauf(a, teil):
    # Ablauf-Kette einer Branchenseite gegen artikel.json prüfen
    k, f = a["automatisierung"]["kette"], []
    if '<div class="ablauf" id="ablauf" data-ablauf>' not in teil:
        return ["Ablauf-Kette fehlt"]
    ablauf = teil[teil.index('<div class="ablauf"'):teil.index('<div class="baustein-raster">')]
    if 'prefers-reduced-motion: reduce' not in ablauf or 'classList.add("bewegt")' not in ablauf:
        f.append("Animation ohne Prüfung auf reduzierte Bewegung")
    f += pruefe_schritte(k, ablauf)
    if k.get("betrieb") not in BETRIEBE:
        name = st["titel"]
        if art != st["art"] or KETTE_ART[art] not in li:
            f.append("Schritt %s: Art fehlt oder falsch" % name)
        if html.escape(st["beispiel"]) not in li or len(re.findall(r"[.!?](\s|$)", st["beispiel"])) != 1:
            f.append("Schritt %s: nicht genau ein Beispielsatz" % name)
        if st.get("hinweis") and html.escape(st["hinweis"]) not in li:
            f.append("Schritt %s: bisheriger Hinweis fehlt" % name)
        links = re.findall(r'<a [^>]*href="([^"]+)"', li)
        soll = ("/produkte/%s/" % st["seite"] if st.get("seite") else
                "#baustein-%d" % st["karte"] if st.get("karte") is not None else "#ablauf-anfrage")
        if links != [soll]:
            f.append("Schritt %s: Link %s statt %s" % (name, links, soll))
    return f


def pruefe_schritte(k, ablauf):
    # Schritte einer Ablauf-Kette: Art, genau ein Beispielsatz, bisheriger Hinweis, genau ein Link
    f = []
    schritte = re.findall(r'<li class="ablauf-schritt (\w+)">(.*?)</li>', ablauf, flags=re.S)
    if len(schritte) != len(k["schritte"]) or len(schritte) < 4:
        f.append("%d statt %d Schritte" % (len(schritte), len(k["schritte"])))
    for (art, li), st in zip(schritte, k["schritte"]):
        name = st["titel"]
        if art != st["art"] or KETTE_ART[art] not in li:
            f.append("Schritt %s: Art fehlt oder falsch" % name)
        if html.escape(st["beispiel"]) not in li or len(re.findall(r"[.!?](\s|$)", st["beispiel"])) != 1:
            f.append("Schritt %s: nicht genau ein Beispielsatz" % name)
        if st.get("hinweis") and html.escape(st["hinweis"]) not in li:
            f.append("Schritt %s: bisheriger Hinweis fehlt" % name)
        links = re.findall(r'<a [^>]*href="([^"]+)"', li)
        soll = ("/produkte/%s/" % st["seite"] if st.get("seite") else
                "#baustein-%d" % st["karte"] if st.get("karte") is not None else "#ablauf-anfrage")
        if links != [soll]:
            f.append("Schritt %s: Link %s statt %s" % (name, links, soll))
    return f


def pruefe_ablauf(a, teil):
    # Ablauf-Kette einer Branchenseite gegen artikel.json prüfen
    k, f = a["automatisierung"]["kette"], []
    if '<div class="ablauf" id="ablauf" data-ablauf>' not in teil:
        return ["Ablauf-Kette fehlt"]
    ablauf = teil[teil.index('<div class="ablauf"'):teil.index('<div class="baustein-raster">')]
    if 'prefers-reduced-motion: reduce' not in ablauf or 'classList.add("bewegt")' not in ablauf:
        f.append("Animation ohne Prüfung auf reduzierte Bewegung")
    f += pruefe_schritte(k, ablauf)
    if k.get("betrieb") not in BETRIEBE:
        f.append("Betrieb %s" % k.get("betrieb"))
    knopf = "Diesen Ablauf für %s %s anfragen" % (MEIN.get(k.get("betrieb"), "meine"), k.get("betrieb"))
    try:
        reihenfolge = [ablauf.index(x) for x in ('<ol class="ablauf-liste">', html.escape(k["abschluss"]),
                                                 '<a class="btn-p ablauf-cta" href="#ablauf-anfrage"><span>%s</span>' % knopf,
                                                 '<form class="ablauf-form" id="ablauf-anfrage"')]
        if reihenfolge != sorted(reihenfolge):
            f.append("Reihenfolge Kette, Abschluss, Knopf, Formular stimmt nicht")
    except ValueError:
        f.append("Abschluss, Knopf oder Formular fehlt")
    form = ablauf[ablauf.find('<form class="ablauf-form"'):ablauf.find("</form>")]
    felder = set(re.findall(r'name="([^"]+)"', form))
    if felder != {"_subject", "branche", "ablauf", "name", "email", "nachricht", "datenschutz-gelesen"}:
        f.append("Formularfelder %s" % sorted(felder))
    if 'name="branche" value="%s"' % html.escape(a["name"]) not in form or \
            not re.search(r'name="ablauf" value="%s \(%s\)" readonly' % (re.escape(html.escape(k["titel"])),
                                                                          re.escape(html.escape(a["name"]))), form):
        f.append("Branche oder Kette im Formular nicht vorausgefüllt")
    if not re.search(r'<a class="anfrage-fest" href="#ablauf-anfrage" data-anfrage-fest hidden>', teil):
        f.append("fester Anfrage-Knopf fehlt")
    return f


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
    if teil.count("<form ") != karten + 1 or teil.count('name="baustein"') != karten:
        fehler.append("%s: nicht genau ein Formular pro Baustein plus eines zum Ablauf" % url)
    for slug in au["bausteine"]:
        if 'href="/produkte/%s/"' % slug not in teil:
            fehler.append("%s: kein Link auf /produkte/%s/" % (url, slug))
    fehler += ["%s#ablauf: %s" % (url, f) for f in pruefe_ablauf(a, teil)]
    if '<span class="beispiel">Beispiel</span>' not in teil or "data-wahl" not in teil:
        fehler.append("%s: Demo mit Beschriftung Beispiel fehlt" % url)
    for muss in ("Was sich automatisieren lässt", regel, "keine Rechtsberatung", "zuletzt geprüft am " + datum(au["geprueft"]),
                 "Einschätzung",
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
    muss = ["Allgemeine Information, keine Rechtsberatung", "zuletzt geprüft am " + datum(p["geprueft"]), regel,
            "Einschätzung", p["status"]]
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

# --- SEO ---
CTA = re.compile(r"\b(anfragen|vormerken|lesen|ansehen|ausprobieren|entdecken|werden|umsetzen|testen)\b", re.I)
DE_BEZUG = re.compile(r"Deutschland|Bundesland|Bundesländer|DSGVO|\bEuro\b|€|Landkreis")
DE_ERLAUBT = {"/ratgeber/offertanfragen-beantworten/": 1}  # zitierte Studie aus Deutschland, als Quelle gekennzeichnet
titel_gesehen, beschr_gesehen = {}, {}


def kopf_wert(text, muster):
    m = re.search(muster, text, flags=re.S)
    return html.unescape(m.group(1)).strip() if m else None


for url, (text, parser) in sorted(seiten.items()):
    if url == "/gemeinden/":
        continue
    kopf = text[:text.index("</head>")]
    t = kopf_wert(kopf, r"<title>(.*?)</title>") or ""
    d = kopf_wert(kopf, r'<meta name="description" content="([^"]*)"') or ""
    if not t or len(t) > 60:
        fehler.append("%s: Titel %d Zeichen" % (url, len(t)))
    if not d or len(d) > 155 or not CTA.search(d):
        fehler.append("%s: Beschreibung %d Zeichen oder ohne Handlungsaufforderung" % (url, len(d)))
    for wert, gesehen, art in ((t, titel_gesehen, "Titel"), (d, beschr_gesehen, "Beschreibung")):
        if wert in gesehen:
            fehler.append("%s: %s doppelt mit %s" % (url, art, gesehen[wert]))
        gesehen[wert] = url
    rumpf = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", text[text.index("<body"):], flags=re.S)
    ebenen = [int(x) for x in re.findall(r"<h([1-6])\b", rumpf)]
    if ebenen.count(1) != 1:
        fehler.append("%s: %d H1" % (url, ebenen.count(1)))
    if any(b > a + 1 for a, b in zip(ebenen, ebenen[1:])):
        fehler.append("%s: Überschriftenebene übersprungen" % url)
    soll = "https://meyssens.ch" + url
    if kopf_wert(kopf, r'<link rel="canonical" href="([^"]+)"') != soll:
        fehler.append("%s: Canonical fehlt oder falsch" % url)
    for sprache in ("de-CH", "x-default"):
        if '<link rel="alternate" hreflang="%s" href="%s">' % (sprache, soll) not in kopf:
            fehler.append("%s: hreflang %s fehlt" % (url, sprache))
    if '<html lang="de-CH">' not in text[:200]:
        fehler.append("%s: lang nicht de-CH" % url)
    if '<meta property="og:image" content="https://meyssens.ch/' not in kopf:
        fehler.append("%s: og:image fehlt" % url)
    if re.search(r"<img\b(?![^>]*\balt=)[^>]*>", text):
        fehler.append("%s: Bild ohne alt" % url)
    typen, roh = [], " ".join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.S))
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.S):
        for g in json.loads(blk).get("@graph", []):
            typen.append(g["@type"])
            if g["@type"] == "Service" and g.get("areaServed", {}).get("name") != "Schweiz":
                fehler.append("%s: Service ohne areaServed Schweiz" % url)
    for typ in ("Organization", "WebSite", "BreadcrumbList"):
        if typ not in typen:
            fehler.append("%s: JSON-LD ohne %s" % (url, typ))
    hat_faq = '<section id="fragen"' in text and '<div class="qa">' in text
    if hat_faq != ("FAQPage" in typen):
        fehler.append("%s: FAQPage passt nicht zu den sichtbaren Fragen" % url)
    if url.startswith("/produkte/") and url != "/produkte/" and "Service" not in typen:
        fehler.append("%s: JSON-LD ohne Service" % url)
    if re.search(r"aggregateRating|\"Review\"|reviewRating", roh):
        fehler.append("%s: Bewertungen in JSON-LD" % url)
    if url != "/":
        inhalt = sichtbar_text(text[text.index("<main"):text.index("</main>")]) if "<main" in text else ""
        n = len(DE_BEZUG.findall(html.unescape(re.sub(r"<[^>]+>", " ", text[text.index("<main"):text.index("</main>")]))))
        if n > DE_ERLAUBT.get(url, 0):
            fehler.append("%s: %d Bezüge auf Deutschland im Inhalt" % (url, n))

seite404 = (ROOT / "404.html").read_text(encoding="utf-8") if (ROOT / "404.html").is_file() else ""
if not seite404 or 'content="noindex' not in seite404 or 'rel="canonical"' in seite404 or "404.html" in sitemap:
    fehler.append("404.html fehlt, ist indexierbar, hat Canonical oder steht in der Sitemap")
for ziel in re.findall(r'href="(/[^"#?]*)', seite404):
    if not ziel_existiert(ziel):
        fehler.append("404.html: toter Link %s" % ziel)
if "Sitemap: https://meyssens.ch/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
    fehler.append("robots.txt ohne Sitemap")

# --- Ratgeber, Bausteine, Branchen mit Bausteinen ---
branchen_daten = json.loads((ROOT / "branchen.json").read_text(encoding="utf-8"))
branchen_seiten = " ".join(t for u, (t, _) in seiten.items() if u.startswith("/branchen/"))
ziele = ["/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"]) for a in artikel if a["art"] == "ratgeber"]
ziele += ["/produkte/%s/" % p["slug"] for p in produkte if ist_baustein(p)]
for url in ziele:
    text = seiten.get(url, ("",))[0]
    hauptteil = text[text.find("<main"):text.find("</main>")]
    letzter = re.findall(r'<section id="([^"]+)"', hauptteil)[-1:] or [None]
    anfrage = zwischen(text, '<section id="anfrage"', "</section>") if '<section id="anfrage"' in text else ""
    if letzter != ["anfrage"] or "<form " not in anfrage or '<button type="submit"' not in anfrage:
        fehler.append("%s: endet nicht mit Anfrage-Formular und Knopf" % url)
for a in (a for a in artikel if a["art"] == "ratgeber"):
    url = "/ratgeber/%s/" % a["slug"]
    if 'href="%s"' % url not in branchen_seiten:
        fehler.append("%s: von keiner Branchenseite verlinkt" % url)
    if 'href="%s"' % url not in uebersicht:
        fehler.append("%s: nicht von der Übersicht verlinkt" % url)
for p in (p for p in produkte if ist_baustein(p) and p.get("faq")):
    if len(p["faq"]) < 3 or '<section id="fragen"' not in seiten.get("/produkte/%s/" % p["slug"], ("",))[0]:
        fehler.append("/produkte/%s/: FAQ mit weniger als 3 Fragen oder nicht sichtbar" % p["slug"])
for b in (b for b in branchen_daten if b.get("bausteine") and not b.get("automatisierungen")):
    text = seiten.get("/branchen/%s/" % b["slug"], ("",))[0]
    teil = zwischen(text, '<section id="bausteine">', "</section>") if '<section id="bausteine">' in text else ""
    for x in b["bausteine"]:
        if 'href="/produkte/%s/"' % x not in teil:
            fehler.append("/branchen/%s/: Baustein %s fehlt im Abschnitt #bausteine" % (b["slug"], x))

# --- Abschnitt "Automatisierungen" der Branchen ohne Langtext ---
FORMFELDER = {"_subject", "branche", "ablauf", "name", "email", "nachricht", "datenschutz-gelesen"}
for b in (b for b in branchen_daten if b.get("automatisierungen")):
    au, url = b["automatisierungen"], "/branchen/%s/" % b["slug"]
    text = seiten.get(url, ("",))[0]
    if '<section id="automatisierung"' not in text:
        fehler.append("%s: Abschnitt automatisierung fehlt" % url)
        continue
    teil = zwischen(text, '<section id="automatisierung"', "</section>")
    s = sichtbar_text(teil)
    karten = re.findall(r'<article class="baustein-karte kompakt r" id="baustein-(\d+)">(.*?)</article>', teil, flags=re.S)
    if [int(n) for n, _ in karten] != list(range(1, 11)) or len(au["liste"]) != 10:
        fehler.append("%s: nicht genau 10 Bausteinkarten 1 bis 10" % url)
    for (n, karte), x in zip(karten, au["liste"]):
        ks = sichtbar_text(karte)
        stand = nach_slug[x["seite"]]["status"] if x.get("seite") else "In Planung"
        for muss in ("In Planung", "Heute von Hand, Einschätzung", "Das übernimmt der Baustein", "Das entscheidet der Mensch",
                     "Daten:", "Aufwand %s, Einschätzung" % x["aufwand"]):
            if muss.lower() not in ks:
                fehler.append("%s#baustein-%s: fehlt: %s" % (url, n, muss))
        if stand != "In Planung":
            fehler.append("%s#baustein-%s: Status %s statt In Planung" % (url, n, stand))
        if x.get("offen") and ("noch zu klären" not in ks or sichtbar_text(html.escape(x["offen"])) not in ks):
            fehler.append("%s#baustein-%s: offener Punkt fehlt" % (url, n))
        ziel = 'href="/produkte/%s/"' % x["seite"] if x.get("seite") else 'href="#ablauf-anfrage" data-baustein='
        if ziel not in karte:
            fehler.append("%s#baustein-%s: Link auf Bausteinseite oder Formular fehlt" % (url, n))
        if bool(x.get("start")) != ("Startempfehlung" in karte):
            fehler.append("%s#baustein-%s: Startempfehlung stimmt nicht" % (url, n))
    if sorted(x["seite"] for x in au["liste"] if x.get("seite")) != sorted(b["bausteine"]) or not 3 <= len(b["bausteine"]) <= 4:
        fehler.append("%s: nicht 3 bis 4 eigene Bausteinseiten" % url)
    if len(au["ketten"]) != 3:
        fehler.append("%s: nicht genau 3 Ketten" % url)
    for i, k in enumerate(au["ketten"], 1):
        start = '<div class="ablauf" id="ablauf-%d" data-ablauf>' % i
        if start not in teil:
            fehler.append("%s: Kette %d fehlt" % (url, i))
            continue
        block = teil[teil.index(start):]
        block = block[:block.index('<div class="ablauf" id="ablauf-%d"' % (i + 1))] if i < 3 else block[:block.index('<form ')]
        f = pruefe_schritte(k, block)
        if 'prefers-reduced-motion: reduce' not in block or 'classList.add("bewegt")' not in block:
            f.append("Animation ohne Prüfung auf reduzierte Bewegung")
        if k.get("betrieb") not in BETRIEBE:
            f.append("Betrieb %s" % k.get("betrieb"))
        knopf = '<span>Diesen Ablauf für %s %s anfragen</span>' % (MEIN.get(k.get("betrieb"), "meine"), k.get("betrieb"))
        wert = html.escape("%s (%s)" % (k["titel"], b["name"]))
        try:
            reihenfolge = [block.index(x) for x in ('<ol class="ablauf-liste">', html.escape(k["abschluss"]),
                                                    'href="#ablauf-anfrage" data-ablauf-wahl="%s">%s' % (wert, knopf))]
            if reihenfolge != sorted(reihenfolge):
                f.append("Reihenfolge Kette, Abschluss, Knopf stimmt nicht")
        except ValueError:
            f.append("Abschluss oder Knopf fehlt")
        if "<option>%s</option>" % wert not in teil:
            f.append("Kette nicht im Formular auswählbar")
        fehler += ["%s#ablauf-%d: %s" % (url, i, x) for x in f]
    if text.count('id="ablauf-anfrage"') != 1 or teil.count("<form ") != 1:
        fehler.append("%s: nicht genau ein gemeinsames Ablauf-Formular" % url)
    form = teil[teil.find('<form class="ablauf-form"'):teil.find("</form>")]
    if set(re.findall(r'name="([^"]+)"', form)) != FORMFELDER or 'name="branche" value="%s"' % html.escape(b["name"]) not in form:
        fehler.append("%s: Formularfelder oder Branche im Ablauf-Formular falsch" % url)
    if '<a class="anfrage-fest" href="#ablauf-anfrage" data-anfrage-fest hidden>' not in text:
        fehler.append("%s: fester Anfrage-Knopf fehlt" % url)
    if 'href="/ratgeber/%s/"' % au["ratgeber"] not in teil:
        fehler.append("%s: Ratgeber-Link fehlt" % url)
    for muss in ["Automatisierungen für", regel, "keine Rechtsberatung", "zuletzt geprüft am " + datum(au["geprueft"]),
                 "Einschätzung", "in Planung", "keine Kunden und keine Referenzen", "Startempfehlung"] + list(BEDINGUNGEN[1:2]):
        if muss.lower() not in s:
            fehler.append("%s#automatisierung: fehlt: %s" % (url, muss))
    if "vertrag zur auftragsbearbeitung" not in s or "datenminimierung" not in s:
        fehler.append("%s#automatisierung: Bedingungen für Personendaten fehlen" % url)
    if "ß" in s:
        fehler.append("%s#automatisierung: ß" % url)
    n = worte(teil)
    if not AUTOMATISIERUNGEN_WORTE[0] <= n <= AUTOMATISIERUNGEN_WORTE[1]:
        fehler.append("%s#automatisierung: %d Wörter" % (url, n))
    if '<a href="#automatisierung">' not in text[:text.index('<section id="alltag"')]:
        fehler.append("%s: Sprungmarke zum Abschnitt fehlt" % url)
    if lastmod_alle.get(url) != au["geprueft"]:
        fehler.append("%s: lastmod nicht gleich Prüfdatum" % url)
    print("%-42s %d" % (url + "#automatisierung", n))

# --- Technik: Brotkrumen, Bilder, verwandte Links, Über uns, Erreichbarkeit, Sitemap ---
GENERISCH = re.compile(r"(?i)(hier|hier klicken|klicken sie hier|click here|mehr|mehr erfahren|weiter|weiterlesen|link|"
                       r"details|beispielansicht|beispiel ausprobieren|unverbindlich vormerken)")
lastmod = dict(re.findall(r"<loc>https://meyssens\.ch([^<]+)</loc><lastmod>([^<]+)</lastmod>", sitemap))
for url, (text, parser) in sorted(seiten.items()):
    if url == "/gemeinden/":
        continue
    graph = [g for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.S)
             for g in json.loads(blk).get("@graph", [])]
    typen = [g["@type"] for g in graph]
    if "SearchAction" in json.dumps(graph):
        fehler.append("%s: SearchAction ohne Suche" % url)
    webseite = [g for g in graph if g["@type"] == "WebPage"]
    if not webseite or webseite[0].get("primaryImageOfPage", {}).get("@type") != "ImageObject":
        fehler.append("%s: WebPage mit ImageObject fehlt" % url)
    if url != "/":
        kette = next((g for g in graph if g["@type"] == "BreadcrumbList"), {"itemListElement": []})["itemListElement"]
        soll = [(x["name"], x["item"].replace("https://meyssens.ch", "")) for x in kette]
        nav = re.search(r'<nav class="brotkrumen" aria-label="Brotkrumen"><ol>(.*?)</ol></nav>', text)
        ist = []
        if nav:
            ist = [(html.unescape(n), u) for u, n in re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', nav.group(1))]
            ist += [(html.unescape(n), url) for n in re.findall(r'<li aria-current="page">([^<]+)</li>', nav.group(1))]
        if not nav or ist != soll or len(soll) < 2:
            fehler.append("%s: sichtbare Brotkrumen fehlen oder passen nicht zum JSON-LD" % url)
    og = re.search(r'<meta property="og:image" content="https://meyssens\.ch(/[^"]+)">', text)
    tw = re.search(r'<meta name="twitter:image" content="https://meyssens\.ch(/[^"]+)">', text)
    if not og or not tw or og.group(1) != tw.group(1) or not (ROOT / og.group(1).lstrip("/")).is_file():
        fehler.append("%s: og:image/twitter:image fehlt, weicht ab oder Datei fehlt" % url)
    for m in re.finditer(r"<a\b[^>]*>(.*?)</a>", text, flags=re.S):
        sichtbar_link = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip(" →")
        if GENERISCH.fullmatch(sichtbar_link):
            fehler.append("%s: Linktext ohne Ziel: %s" % (url, sichtbar_link))
    rumpf = text[text.index("<body"):]
    bilder = re.findall(r"<img\b[^>]*>", rumpf)
    for i, b in enumerate(bilder):
        if not re.search(r'\bwidth="\d+"', b) or not re.search(r'\bheight="\d+"', b):
            fehler.append("%s: Bild ohne width/height" % url)
        if i > 0 and 'loading="lazy"' not in b:
            fehler.append("%s: Bild %d ohne loading=lazy" % (url, i + 1))
        if i == 0 and 'loading="lazy"' in b:
            fehler.append("%s: erstes Bild darf nicht lazy sein" % url)
    if 'href="/ueber-uns/"' not in zwischen(text, "<body", "<main") or \
            'href="/ueber-uns/"' not in text[text.index("<footer"):] if "<footer" in text else True:
        fehler.append("%s: Über uns nicht in Kopf und Fuss verlinkt" % url)
    if url not in lastmod or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod.get(url, "")):
        fehler.append("%s: lastmod fehlt in der Sitemap" % url)

typen_ueber = json.dumps(re.findall(r'<script type="application/ld\+json">(.*?)</script>', seiten.get("/ueber-uns/", ("",))[0], flags=re.S))
if '\\"@type\\": \\"Person\\"' not in typen_ueber or "AboutPage" not in typen_ueber:
    fehler.append("/ueber-uns/: Seite fehlt oder ohne Person/AboutPage im JSON-LD")
for a in artikel:
    url = "/%s/%s/" % (ARTEN[a["art"]]["ordner"], a["slug"])
    graph = [g for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', seiten[url][0], flags=re.S)
             for g in json.loads(blk).get("@graph", [])]
    art = next((g for g in graph if g["@type"] == "Article"), {})
    if art.get("datePublished") != a.get("veroeffentlicht") or art.get("dateModified") != a["geprueft"] or \
            art.get("image", {}).get("@type") != "ImageObject":
        fehler.append("%s: Article ohne datePublished/dateModified/ImageObject" % url)
    if lastmod.get(url) != a["geprueft"]:
        fehler.append("%s: lastmod nicht gleich Prüfdatum" % url)
for p in (p for p in produkte if ist_baustein(p)):
    if lastmod.get("/produkte/%s/" % p["slug"]) != p["geprueft"]:
        fehler.append("/produkte/%s/: lastmod nicht gleich Prüfdatum" % p["slug"])

# "Das könnte Sie auch interessieren": 3 verschiedene, vorhandene Ziele, nicht die Seite selbst
for url, (text, parser) in seiten.items():
    soll_block = url.startswith(("/branchen/", "/ratgeber/")) and url.count("/") == 3 or \
                 (url.startswith("/produkte/") and url.count("/") == 3 and
                  any(ist_baustein(p) and url == "/produkte/%s/" % p["slug"] for p in produkte))
    if not soll_block:
        continue
    teil = zwischen(text, '<section id="verwandt">', "</section>") if '<section id="verwandt">' in text else ""
    ziele = re.findall(r'<a href="([^"]+)" class="feat tile">', teil)
    if len(ziele) != 3 or len(set(ziele)) != 3 or url in ziele or not all(z in seiten for z in ziele):
        fehler.append("%s: 'Das könnte Sie auch interessieren' ohne 3 gültige Links" % url)

# Erreichbarkeit: Breitensuche ab der Startseite über interne Links, höchstens 3 Klicks, keine verwaiste Seite
tiefe, offen = {"/": 0}, ["/"]
while offen:
    u = offen.pop(0)
    for ziel in seiten[u][1].links:
        ziel = ziel.split("#")[0].split("?")[0]
        if ziel in seiten and ziel not in tiefe:
            tiefe[ziel] = tiefe[u] + 1
            offen.append(ziel)
for url in seiten:
    if url not in tiefe:
        fehler.append("%s: verwaist, von der Startseite nicht erreichbar" % url)
    elif tiefe[url] > 3:
        fehler.append("%s: %d Klicks von der Startseite entfernt" % (url, tiefe[url]))
print("Klicktiefe ab Startseite:", dict(sorted(__import__("collections").Counter(tiefe.values()).items())))

print("\n%d Seiten, %d interne Links geprüft" % (len(seiten), geprueft))
if fehler:
    print("\nFEHLER:\n" + "\n".join(fehler))
    sys.exit(1)
print("Alles in Ordnung.")

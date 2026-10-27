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
- Bausteinseiten (produkte.json mit Feld "branche"): Hinweise, Regel, Status, Einschätzung, bei Personendaten
  Auftragsbearbeitung/Schweiz/Datenminimierung, kein ß, Wortzahl, Sitemap, verlinkt von Branchenseite und Übersicht
- Keine Platzhalter ({{...}}, [Status, TODO, Lorem) auf irgendeiner Seite
- SEO (alle Seiten ausser /gemeinden/): Titel <= 60 Zeichen und eindeutig, Beschreibung <= 155 Zeichen mit
  Handlungsaufforderung und eindeutig, genau eine H1, keine übersprungene Überschriftenebene, Canonical, hreflang de-CH
  und x-default, lang="de-CH", Open-Graph-Bild, alt-Texte, JSON-LD mit Organization, WebSite, BreadcrumbList,
  FAQPage genau dann wenn sichtbare Fragen, Service mit areaServed Schweiz auf Produkt- und Bausteinseiten,
  keine Bewertungen; im Inhalt der Unternehmensseiten kein Bezug auf Deutschland
- 404.html: vorhanden, noindex, ohne Canonical, nicht in der Sitemap; robots.txt verweist auf die Sitemap
Nur Python-Standardbibliothek.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from build import (ARTEN, AUTO_WORTE, KETTE_ART, BAUSTEIN_WORTE, BEDINGUNGEN, REGEL, WORTE, ist_baustein, ohne_automatisierung,
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
BETRIEBE = ("Praxis", "Verwaltung", "Büro", "Einrichtung")


def pruefe_ablauf(a, teil):
    # Ablauf-Kette einer Branchenseite gegen artikel.json prüfen
    k, f = a["automatisierung"]["kette"], []
    if '<div class="ablauf" id="ablauf" data-ablauf>' not in teil:
        return ["Ablauf-Kette fehlt"]
    ablauf = teil[teil.index('<div class="ablauf"'):teil.index('<div class="baustein-raster">')]
    if 'prefers-reduced-motion: reduce' not in ablauf or 'classList.add("bewegt")' not in ablauf:
        f.append("Animation ohne Prüfung auf reduzierte Bewegung")
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
        soll = "/produkte/%s/" % st["seite"] if st.get("seite") else "#ablauf-anfrage"
        if links != [soll]:
            f.append("Schritt %s: Link %s statt %s" % (name, links, soll))
    if k.get("betrieb") not in BETRIEBE:
        f.append("Betrieb %s" % k.get("betrieb"))
    knopf = "Diesen Ablauf für meine %s anfragen" % k.get("betrieb")
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
    if teil.count("<form ") != karten + 1 or teil.count('name="baustein"') != karten:
        fehler.append("%s: nicht genau ein Formular pro Baustein plus eines zum Ablauf" % url)
    for slug in au["bausteine"]:
        if 'href="/produkte/%s/"' % slug not in teil:
            fehler.append("%s: kein Link auf /produkte/%s/" % (url, slug))
    fehler += ["%s#ablauf: %s" % (url, f) for f in pruefe_ablauf(a, teil)]
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
    if url.startswith("/produkte/") and "Service" not in typen:
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

print("\n%d Seiten, %d interne Links geprüft" % (len(seiten), geprueft))
if fehler:
    print("\nFEHLER:\n" + "\n".join(fehler))
    sys.exit(1)
print("Alles in Ordnung.")

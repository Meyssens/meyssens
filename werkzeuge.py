"""Gratis-Werkzeuge unter /werkzeuge/ (ausser der QR-Rechnung, die in build.py steht).

Jedes Werkzeug: Texte, Fragen und Quellen hier, Inhalt (Formular, Beispiel, Erklärung) in werkzeug_<slug>.html,
Rechenlogik in assets/<datei>.js. Alle Berechnungen laufen im Browser; die Seiten haben eine Content Security Policy
ohne Verbindungen nach aussen und kein Cookie-Banner (keine Statistik).
Zahlen, Sätze und Feiertage nur aus amtlichen Quellen; Quelle und Prüfdatum stehen auf der Seite.
"""

WERKZEUGE_UEBERSICHT = {
    "pfad": "/werkzeuge/",
    "titel": "Gratis-Werkzeuge für Schweizer KMU | Meyssens",
    "beschreibung": "Kostenlose Rechner und Vorlagen für Schweizer KMU, ohne Anmeldung und ohne Cookies. Ihre Eingaben bleiben im "
                    "Browser. Jetzt ausprobieren.",
    "h1": "Gratis-Werkzeuge für Schweizer KMU",
    "lead": "Rechner und Vorlagen für die Büroarbeit: ohne Anmeldung, ohne Cookies. Ihre Eingaben bleiben auf Ihrem Gerät.",
}

WERKZEUGE = []


# ---------------------------------------------------------------------------------------------------------------
# W7 Arbeitstage mit kantonalen Feiertagen
# Feiertage, die nach kantonalem Recht den Sonntagen gleichgestellt sind (Art. 20a ArG), dazu der 1. August
# (Art. 110 Abs. 3 BV). Recherche: Gesetzessammlungen der Kantone, geprüft am 24.11.2026. Bräuche (Berchtoldstag
# ohne Gesetz, Heiligabend usw.) zählen nicht dazu; der Rechner bietet sie nur als freiwillige Zusatztage an.
# typ "fix": (Monat, Tag); typ "ostern": Abstand in Tagen zum Ostersonntag; halb: nur ab 12 Uhr (SO, 1. Mai)
import datetime as _dt

FEIERTAGE = {
    "neujahr": ("Neujahr", "fix", (1, 1)),
    "berchtold": ("Berchtoldstag", "fix", (1, 2)),
    "karfreitag": ("Karfreitag", "ostern", -2),
    "ostermontag": ("Ostermontag", "ostern", 1),
    "1mai": ("1. Mai", "fix", (5, 1)),
    "1mai_halb": ("1. Mai (ab 12 Uhr)", "fix", (5, 1)),
    "auffahrt": ("Auffahrt", "ostern", 39),
    "pfingstmontag": ("Pfingstmontag", "ostern", 50),
    "fronleichnam": ("Fronleichnam", "ostern", 60),
    "bundesfeier": ("Bundesfeiertag", "fix", (8, 1)),
    "himmelfahrt": ("Mariä Himmelfahrt", "fix", (8, 15)),
    "allerheiligen": ("Allerheiligen", "fix", (11, 1)),
    "empfaengnis": ("Mariä Empfängnis", "fix", (12, 8)),
    "weihnacht": ("Weihnachtstag", "fix", (12, 25)),
    "stephan": ("Stephanstag", "fix", (12, 26)),
}
HALBE_TAGE = {"1mai_halb"}

_NORDWEST = ["neujahr", "karfreitag", "ostermontag", "1mai", "auffahrt", "pfingstmontag", "bundesfeier", "weihnacht", "stephan"]
KANTONE = [
    {"id": "BS", "name": "Basel-Stadt", "recht": "Gesetz über öffentliche Ruhetage und Ladenöffnung (RLG), SG 811.100, § 2",
     "url": "https://www.gesetzessammlung.bs.ch/app/de/texts_of_law/811.100",
     "regionen": [{"id": "BS", "name": "ganzer Kanton", "tage": _NORDWEST}]},
    {"id": "BL", "name": "Basel-Landschaft", "recht": "Ruhetagsgesetz (RTG), SGS 547, § 2 und § 10",
     "url": "https://bl.clex.ch/app/de/texts_of_law/547",
     "regionen": [{"id": "BL", "name": "ganzer Kanton", "tage": _NORDWEST}]},
    {"id": "SO", "name": "Solothurn", "recht": "Wirtschafts- und Arbeitsgesetz (WAG), BGS 940.11, § 46",
     "url": "https://bgs.so.ch/app/de/texts_of_law/940.11",
     "regionen": [
         {"id": "SO", "name": "Kanton ohne Bezirk Bucheggberg",
          "tage": ["neujahr", "karfreitag", "1mai_halb", "auffahrt", "fronleichnam", "bundesfeier", "himmelfahrt", "allerheiligen", "weihnacht"]},
         {"id": "SO-BU", "name": "Bezirk Bucheggberg",
          "tage": ["neujahr", "karfreitag", "1mai_halb", "auffahrt", "bundesfeier", "weihnacht"]}]},
    {"id": "AG", "name": "Aargau", "recht": "Einführungsgesetz zum Arbeitsrecht (EG ArR), SAR 961.200, § 6",
     "url": "https://gesetzessammlungen.ag.ch/app/de/texts_of_law/961.200",
     "regionen": [
         {"id": "AG-A", "name": "Bezirke Aarau, Brugg, Kulm, Lenzburg, Zofingen und Gemeinde Bergdietikon",
          "tage": ["neujahr", "berchtold", "karfreitag", "ostermontag", "auffahrt", "pfingstmontag", "bundesfeier", "weihnacht", "stephan"]},
         {"id": "AG-B", "name": "Bezirk Baden (ohne Bergdietikon)",
          "tage": ["neujahr", "karfreitag", "ostermontag", "auffahrt", "pfingstmontag", "fronleichnam", "bundesfeier", "weihnacht", "stephan"]},
         {"id": "AG-C", "name": "Bezirk Bremgarten",
          "tage": ["neujahr", "karfreitag", "auffahrt", "fronleichnam", "bundesfeier", "himmelfahrt", "allerheiligen", "weihnacht", "stephan"]},
         {"id": "AG-D", "name": "Bezirke Laufenburg und Muri; Hellikon, Mumpf, Obermumpf, Schupfart, Stein, Wegenstetten",
          "tage": ["neujahr", "karfreitag", "auffahrt", "fronleichnam", "bundesfeier", "himmelfahrt", "allerheiligen", "empfaengnis", "weihnacht"]},
         {"id": "AG-E", "name": "Kaiseraugst, Magden, Möhlin, Olsberg, Rheinfelden, Wallbach, Zeiningen, Zuzgen",
          "tage": ["neujahr", "karfreitag", "ostermontag", "auffahrt", "pfingstmontag", "bundesfeier", "allerheiligen", "weihnacht", "stephan"]},
         {"id": "AG-F", "name": "Bezirk Zurzach",
          "tage": ["neujahr", "berchtold", "karfreitag", "auffahrt", "fronleichnam", "bundesfeier", "allerheiligen", "weihnacht", "stephan"]}]},
    {"id": "BE", "name": "Bern", "recht": "Gesetz über die Ruhe an öffentlichen Feiertagen (FRG), BSG 555.1, Art. 2",
     "url": "https://www.belex.sites.be.ch/app/de/texts_of_law/555.1",
     "regionen": [{"id": "BE", "name": "ganzer Kanton",
                   "tage": ["neujahr", "berchtold", "karfreitag", "ostermontag", "auffahrt", "pfingstmontag", "bundesfeier", "weihnacht", "stephan"]}]},
    {"id": "ZH", "name": "Zürich", "recht": "Ruhetags- und Ladenöffnungsgesetz (RLG), LS 822.4, § 1",
     "url": "https://www.zh.ch/de/politik-staat/gesetze-beschluesse/gesetzessammlung/zhlex-ls/erlass-822_4-2000_06_26-2004_05_01-045.html",
     "regionen": [{"id": "ZH", "name": "ganzer Kanton", "tage": _NORDWEST}]},
]


def ostersonntag(jahr):
    # Gregorianischer Osteralgorithmus (Meeus/Jones/Butcher)
    a, b, c = jahr % 19, jahr // 100, jahr % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    monat = (h + l - 7 * m + 114) // 31
    tag = ((h + l - 7 * m + 114) % 31) + 1
    return _dt.date(jahr, monat, tag)


def feiertag_datum(schluessel, jahr):
    _, typ, wert = FEIERTAGE[schluessel]
    return _dt.date(jahr, *wert) if typ == "fix" else ostersonntag(jahr) + _dt.timedelta(days=wert)


def arbeitstage(region, von, bis, werktage=(0, 1, 2, 3, 4)):
    # Arbeitstage im Zeitraum (beide Grenzen eingeschlossen): Werktage minus Feiertage, die auf einen Werktag fallen
    frei = {}
    for jahr in range(von.year, bis.year + 1):
        for s in region["tage"]:
            d = feiertag_datum(s, jahr)
            frei[d] = max(frei.get(d, 0), 0.5 if s in HALBE_TAGE else 1)
    n, tag = 0.0, von
    while tag <= bis:
        if tag.weekday() in werktage:
            n += 1 - frei.get(tag, 0)
        tag += _dt.timedelta(days=1)
    return n


MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]


def zahl_ch(n):
    return ("%g" % n).replace(".", ",")


def arbeitstage_tabelle(jahr=2027):
    # Statische Tabelle für die Seite: Arbeitstage Mo–Fr pro Monat und Kanton (Hauptregion; Regionen AG/SO im Rechner)
    import html
    spalten = [(k, k["regionen"][0]) for k in KANTONE]
    kopf = "".join('<th scope="col">%s%s</th>' % (k["id"], "<sup>*</sup>" if len(k["regionen"]) > 1 else "") for k, _ in spalten)
    zeilen = []
    for m in range(1, 13):
        von = _dt.date(jahr, m, 1)
        bis = (_dt.date(jahr + (m == 12), m % 12 + 1, 1) - _dt.timedelta(days=1))
        zeilen.append('<tr><th scope="row">%s</th>%s</tr>' % (MONATE[m - 1], "".join(
            "<td>%s</td>" % zahl_ch(arbeitstage(r, von, bis)) for _, r in spalten)))
    total = "".join("<td><strong>%s</strong></td>" % zahl_ch(arbeitstage(r, _dt.date(jahr, 1, 1), _dt.date(jahr, 12, 31))) for _, r in spalten)
    zeilen.append('<tr class="at-total"><th scope="row">Total %d</th>%s</tr>' % (jahr, total))
    fuss = "".join("<li><sup>*</sup> %s: %s. Andere Regionen im Rechner oben.</li>" % (html.escape(k["name"]), html.escape(r["name"]))
                   for k, r in spalten if len(k["regionen"]) > 1)
    return ('<div class="tabelle-scroll"><table class="qr-tabelle at-tabelle"><caption>Arbeitstage %d (Montag bis Freitag, '
            'ohne gesetzliche Feiertage)</caption><thead><tr><th scope="col">Monat</th>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<ul class="at-fuss">%s</ul>' % (jahr, kopf, "".join(zeilen), fuss))


def feiertage_liste(jahr=2027):
    # Liste aller gesetzlichen Feiertage je Kanton und Region mit Datum (für die Seite)
    import html
    teile = []
    for k in KANTONE:
        for r in k["regionen"]:
            tage = sorted((feiertag_datum(s, jahr), s) for s in r["tage"])
            teile.append('<details class="at-kanton"><summary>%s%s</summary><ul>%s</ul><p class="at-recht">%s</p></details>' % (
                html.escape(k["name"]), (" · " + html.escape(r["name"])) if len(k["regionen"]) > 1 else "",
                "".join("<li><span>%s</span> %s</li>" % (d.strftime("%d.%m.%Y"), html.escape(FEIERTAGE[s][0])
                        + ("" if d.weekday() < 5 else " (%s)" % ("Samstag" if d.weekday() == 5 else "Sonntag"))) for d, s in tage),
                html.escape(k["recht"])))
    return "\n".join(teile)


def feiertage_json():
    import json
    return json.dumps({"feiertage": {s: {"name": v[0], "typ": v[1], "wert": v[2], "halb": s in HALBE_TAGE} for s, v in FEIERTAGE.items()},
                       "kantone": [{"id": k["id"], "name": k["name"], "regionen": k["regionen"]} for k in KANTONE]},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


WERKZEUGE.append({
    "slug": "arbeitstage",
    "pfad": "/werkzeuge/arbeitstage/",
    "name": "Arbeitstage berechnen",
    "kurz": "Arbeitstage zwischen zwei Daten mit den gesetzlichen Feiertagen von BS, BL, SO, AG, BE und ZH, dazu die Tabelle 2027.",
    "titel": "Arbeitstage 2027 berechnen: mit Feiertagen | Meyssens",
    "beschreibung": "Arbeitstage 2027 für Basel, Baselland, Solothurn, Aargau, Bern und Zürich: Rechner mit gesetzlichen Feiertagen "
                    "und Tabelle pro Monat. Jetzt ausprobieren.",
    "h1": "Arbeitstage 2027 berechnen: mit kantonalen Feiertagen",
    "lead": "Arbeitstage zwischen zwei Daten, mit den gesetzlichen Feiertagen Ihres Kantons und Ihrer Region. Dazu die Tabelle "
            "2027 pro Monat für Basel-Stadt, Basel-Landschaft, Solothurn, Aargau, Bern und Zürich.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_arbeitstage.html",
    "skripte": ["/assets/arbeitstage.js"],
    "ersetzen": {"<!-- at-daten -->": feiertage_json, "<!-- at-tabelle -->": arbeitstage_tabelle, "<!-- at-liste -->": feiertage_liste},
    "gespraech": {"titel": "Fristen und Termine nicht von Hand nachführen",
                  "text": "Wer Fristen, Lohnläufe oder Termine plant, rechnet Arbeitstage nicht nur einmal. Ein Ablauf kann Fristen aus "
                          "Belegen und Verträgen auslesen, in einen Kalender eintragen und rechtzeitig eine Erinnerung als Entwurf "
                          "vorbereiten. Im Gratis-Prozess-Check (30 Minuten) sagen wir offen, was sich in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Wie viele Arbeitstage hat 2027?",
         "antwort": "2027 hat 261 Werktage von Montag bis Freitag. In Basel-Stadt, Basel-Landschaft, Bern und Zürich fallen fünf "
                    "gesetzliche Feiertage auf einen Werktag, es bleiben 256 Arbeitstage. In den anderen Regionen sind es je nach "
                    "Feiertagen zwischen 255 und 258."},
        {"frage": "Was zählt als gesetzlicher Feiertag?",
         "antwort": "Der 1. August ist nach der Bundesverfassung den Sonntagen gleichgestellt. Dazu können die Kantone höchstens acht "
                    "weitere Feiertage den Sonntagen gleichstellen (Art. 20a Arbeitsgesetz). Nur diese Tage zieht der Rechner ab."},
        {"frage": "Ist der Berchtoldstag ein Feiertag?",
         "antwort": "Gesetzlich nur in Bern und in den Aargauer Bezirken Aarau, Brugg, Kulm, Lenzburg, Zofingen, Zurzach sowie in "
                    "Bergdietikon. Anderswo ist der 2. Januar oft frei, aber nicht gesetzlich. Im Rechner können Sie ihn zusätzlich "
                    "abziehen."},
        {"frage": "Was passiert, wenn ein Feiertag auf ein Wochenende fällt?",
         "antwort": "Dann gibt es keinen zusätzlichen freien Tag, und der Rechner zieht nichts ab. 2027 betrifft das den 1. Mai, den "
                    "1. und 15. August sowie den 25. und 26. Dezember."},
        {"frage": "Werden meine Eingaben gespeichert?",
         "antwort": "Nein. Der Rechner läuft vollständig in Ihrem Browser. Die Seite setzt keine Cookies und verbietet Verbindungen "
                    "nach aussen technisch per Content Security Policy."},
    ],
    "quellen": [
        ("Bundesverfassung, Art. 110 Abs. 3 (1. August)", "https://www.fedlex.admin.ch/eli/cc/1999/404/de#art_110"),
        ("Arbeitsgesetz, Art. 20a (Feiertage)", "https://www.fedlex.admin.ch/eli/cc/1966/57_57_57/de#art_20_a"),
        ("Basel-Stadt: Gesetz über öffentliche Ruhetage und Ladenöffnung (RLG), SG 811.100, § 2", "https://www.gesetzessammlung.bs.ch/app/de/texts_of_law/811.100"),
        ("Basel-Landschaft: Ruhetagsgesetz (RTG), SGS 547, § 2 und § 10", "https://bl.clex.ch/app/de/texts_of_law/547"),
        ("Solothurn: Wirtschafts- und Arbeitsgesetz (WAG), BGS 940.11, § 46", "https://bgs.so.ch/app/de/texts_of_law/940.11"),
        ("Aargau: Einführungsgesetz zum Arbeitsrecht (EG ArR), SAR 961.200, § 6", "https://gesetzessammlungen.ag.ch/app/de/texts_of_law/961.200"),
        ("Bern: Gesetz über die Ruhe an öffentlichen Feiertagen (FRG), BSG 555.1, Art. 2", "https://www.belex.sites.be.ch/app/de/texts_of_law/555.1"),
        ("Zürich: Ruhetags- und Ladenöffnungsgesetz (RLG), LS 822.4, § 1", "https://www.zh.ch/de/politik-staat/gesetze-beschluesse/gesetzessammlung/zhlex-ls/erlass-822_4-2000_06_26-2004_05_01-045.html"),
        ("Kanton Basel-Stadt: Feiertage (Daten 2027)", "https://www.bs.ch/themen/arbeit-und-steuern/feiertage-im-kanton-basel-stadt"),
        ("Kanton Zürich: Feiertage", "https://zh.ch/de/wirtschaft-arbeit/arbeitsbedingungen/arbeitsssicherheit-gesundheitsschutz/arbeits-ruhezeiten/feiertage.html"),
    ],
})


# ---------------------------------------------------------------------------------------------------------------
# Gemeinsame Formularteile für Briefe (W1 Mahnung, W2 Rechnung, W3 Offerte)
def adress_felder(praefix, legende, beispiel, kontakt=False):
    import html
    b = beispiel

    def feld(k, label, auto="off", breite="", wert=""):
        return ('<div class="fgrp%s"><label class="flabel" for="%s-%s">%s</label><input class="finput" type="text" id="%s-%s" '
                'autocomplete="%s" maxlength="70" value="%s"></div>' % (breite, praefix, k, label, praefix, k, auto, html.escape(wert)))
    return ('<fieldset><legend>%s</legend>%s%s<div class="frow strasse">%s%s</div><div class="frow drei">%s%s%s</div>%s</fieldset>' % (
        legende, feld("name", "Name oder Firma", "organization", wert=b.get("name", "")),
        feld("zusatz", "Zusatz (optional, z. B. Abteilung oder Person)", wert=b.get("zusatz", "")),
        feld("strasse", "Strasse", "address-line1", wert=b.get("strasse", "")), feld("nr", "Nr.", wert=b.get("nr", "")),
        feld("plz", "PLZ", "postal-code", wert=b.get("plz", "")), feld("ort", "Ort", "address-level2", wert=b.get("ort", "")),
        feld("land", "Land", "country", wert=b.get("land", "CH")),
        feld("kontakt", "Kontakt für Rückfragen (optional, z. B. Telefon oder E-Mail)", wert=b.get("kontakt", "")) if kontakt else ""))


FENSTER_FELDER = (
    '<details class="qr-details br-fenster"><summary>Fenstercouvert und Druck</summary>'
    '<p class="qr-hilfe">Die Empfängeradresse steht im Adressfeld für Couverts mit Fenster. Die Lage der Fenster ist nicht bei allen '
    'Couverts gleich: Drucken Sie den ersten Brief zur Probe und passen Sie die Abstände bei Bedarf an.</p>'
    '<label class="qr-wahl"><input type="radio" name="br-fenster" id="br-fenster-rechts" value="rechts" checked> Fenster rechts</label>'
    '<label class="qr-wahl"><input type="radio" name="br-fenster" id="br-fenster-links" value="links"> Fenster links</label>'
    '<div class="frow"><div class="fgrp"><label class="flabel" for="br-fenster-x">Abstand vom linken Rand (mm)</label>'
    '<input class="finput" type="number" id="br-fenster-x" value="118" min="10" max="130" step="1"></div>'
    '<div class="fgrp"><label class="flabel" for="br-fenster-y">Abstand vom oberen Rand (mm)</label>'
    '<input class="finput" type="number" id="br-fenster-y" value="52" min="30" max="80" step="1"></div></div></details>')


def qr_felder(praefix, beispiel_iban="CH44 3199 9123 0008 8901 2"):
    return ('<fieldset><legend>QR-Zahlteil (optional)</legend>'
            '<label class="qr-wahl"><input type="checkbox" id="%s-qr"> QR-Zahlteil unten auf dem Brief anfügen</label>'
            '<div id="%s-qr-felder" hidden>'
            '<div class="fgrp"><label class="flabel" for="%s-iban">IBAN oder QR-IBAN (CH oder LI)</label>'
            '<input class="finput" type="text" id="%s-iban" autocomplete="off" spellcheck="false" placeholder="%s"></div>'
            '<div class="fgrp"><label class="flabel" for="%s-referenz">Referenz (optional; mit QR-IBAN Pflicht)</label>'
            '<input class="finput" type="text" id="%s-referenz" autocomplete="off" spellcheck="false"></div>'
            '<p class="qr-hilfe">Der Zahlteil folgt den Vorgaben der SIX (Version 2.4). Empfänger ist der Absender oben, Zahlungspflichtiger '
            'die Empfängeradresse. Mehr dazu beim Werkzeug <a href="/werkzeuge/qr-rechnung/">QR-Rechnung erstellen</a>.</p></div></fieldset>'
            % (praefix, praefix, praefix, praefix, beispiel_iban, praefix, praefix))


# ---------------------------------------------------------------------------------------------------------------
# W1 Mahnung mit Verzugszins
BEISPIEL_ABSENDER = {"name": "Muster Elektro GmbH", "strasse": "Beispielweg", "nr": "12", "plz": "4410", "ort": "Liestal",
                     "kontakt": "Tel. 061 000 00 00 · buero@muster-elektro.example"}
BEISPIEL_EMPFAENGER = {"name": "Beispiel Immobilien AG", "zusatz": "Buchhaltung", "strasse": "Testgasse", "nr": "5",
                       "plz": "4051", "ort": "Basel"}


def mahnung_absender():
    return adress_felder("ab", "Ihr Betrieb (Absender)", BEISPIEL_ABSENDER, kontakt=True)


def mahnung_empfaenger():
    return adress_felder("em", "Kunde (Empfänger)", BEISPIEL_EMPFAENGER)


def mahnung_qr():
    return qr_felder("mq")


def fenster_felder():
    return FENSTER_FELDER


WERKZEUGE.append({
    "slug": "mahnung",
    "pfad": "/werkzeuge/mahnung/",
    "name": "Mahnung mit Verzugszins",
    "kurz": "Verzugszins nach Art. 104 OR berechnen und Zahlungserinnerung, Mahnung oder letzte Mahnung als PDF erstellen, auf Wunsch mit QR-Zahlteil.",
    "titel": "Mahnung erstellen: Verzugszins-Rechner Schweiz | Meyssens",
    "beschreibung": "Verzugszins nach OR berechnen und Mahnung als PDF erstellen, auf Wunsch mit QR-Zahlteil. Gratis, ohne Anmeldung, "
                    "im Browser. Jetzt ausprobieren.",
    "h1": "Mahnung erstellen: mit Verzugszins nach OR",
    "lead": "Verzugszins berechnen und Zahlungserinnerung, Mahnung oder letzte Mahnung als PDF erstellen, auf Wunsch mit QR-Zahlteil. "
            "Ihre Angaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_mahnung.html",
    "skripte": ["/assets/qrcode.js", "/assets/qr-rechnung.js", "/assets/brief-pdf.js", "/assets/mahnung.js"],
    "ersetzen": {"<!-- absender -->": mahnung_absender, "<!-- empfaenger -->": mahnung_empfaenger, "<!-- qr -->": mahnung_qr,
                 "<!-- fenster -->": fenster_felder},
    "gespraech": {"titel": "Offene Rechnungen im Blick, ohne Liste von Hand",
                  "text": "Ein Ablauf kann fällige Rechnungen erkennen, Zahlungserinnerungen als Entwurf vorbereiten und Ihnen zur "
                          "Freigabe vorlegen. Versendet wird nichts ohne Sie. Im Gratis-Prozess-Check (30 Minuten) sagen wir offen, "
                          "was sich in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Wie hoch ist der Verzugszins in der Schweiz?",
         "antwort": "Fünf Prozent pro Jahr (Art. 104 Abs. 1 OR), auch wenn vertraglich ein tieferer Zins gilt. Ein höherer "
                    "vertraglicher Zins gilt auch während des Verzugs (Abs. 2). Zinseszins ist ausgeschlossen (Art. 105 Abs. 3 OR)."},
        {"frage": "Ab wann schuldet der Kunde Verzugszins?",
         "antwort": "Ab Verzug. Mit einem vereinbarten Verfalltag (zum Beispiel «zahlbar bis 31. Januar») kommt der Kunde mit Ablauf "
                    "dieses Tages in Verzug. Ohne festen Termin braucht es eine Mahnung (Art. 102 OR)."},
        {"frage": "Wie rechnet das Werkzeug die Tage?",
         "antwort": "Mit den effektiven Kalendertagen ab dem Verfalltag oder dem Eingang der Mahnung bis zum Stichtag, geteilt durch "
                    "365. So rechnet zum Beispiel das Appellationsgericht Basel-Stadt. Das Gesetz selbst legt die Tageszählung nicht fest."},
        {"frage": "Darf ich eine Mahngebühr verlangen?",
         "antwort": "Das Gesetz kennt keine pauschale Mahngebühr. Sie ist in der Regel nur geschuldet, wenn sie vereinbart ist, etwa in "
                    "Ihren AGB, oder als nachgewiesener Schaden nach Art. 106 OR. Das Werkzeug fügt sie nur auf ausdrücklichen Wunsch an."},
        {"frage": "Was kommt nach der letzten Mahnung?",
         "antwort": "Zahlt der Kunde nicht, ist eine Betreibung möglich. Das Betreibungsbegehren geht an das Betreibungsamt am Wohnsitz "
                    "oder Sitz des Schuldners, auch online über EasyGov (Art. 67 SchKG)."},
        {"frage": "Werden meine Angaben gespeichert?",
         "antwort": "Nein. Berechnung und PDF entstehen in Ihrem Browser. Die Seite setzt keine Cookies und verbietet Verbindungen nach "
                    "aussen technisch per Content Security Policy."},
    ],
    "quellen": [
        ("Obligationenrecht, Art. 102 (Verzug)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_102"),
        ("Obligationenrecht, Art. 104 (Verzugszins)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_104"),
        ("Obligationenrecht, Art. 105 (kein Zinseszins)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_105"),
        ("Obligationenrecht, Art. 106 (weiterer Schaden)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_106"),
        ("Appellationsgericht Basel-Stadt, ZB.2018.5 vom 3.7.2018, E. 3.5 (Tageszählung effektive Tage/365)",
         "https://entscheidsuche.ch/docs/BS_Omni/BS_APG_001_ZB-2018-5_nodate.html"),
        ("SchKG, Art. 46 (Betreibungsort)", "https://www.fedlex.admin.ch/eli/cc/11/529_488_529/de#art_46"),
        ("SchKG, Art. 67 und 69 (Betreibungsbegehren, Zahlungsbefehl)", "https://www.fedlex.admin.ch/eli/cc/11/529_488_529/de#art_67"),
        ("KMU-Portal des Bundes: Was tun bei Zahlungsverzug?", "https://www.kmu.admin.ch/de/was-tun-bei-zahlungsverzug-und-zahlungsausfaellen"),
        ("SIX, Implementation Guidelines QR-Rechnung, Version 2.4", "https://www.six-group.com/dam/download/banking-services/standardization/qr-bill/ig-qr-bill-v2.4-de.pdf"),
    ],
})

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


# ---------------------------------------------------------------------------------------------------------------
# W2 Rechnung und W3 Offerte (gemeinsames Formular, Logik in assets/beleg.js)
BEISPIEL_RECHNUNG = [
    {"text": "Arbeit Elektromonteur gemäss Rapport", "menge": "6.5", "einheit": "h", "preis": "98.00", "satz": 8.1},
    {"text": "Material gemäss Rapport (Kabel, Dosen, Schalter)", "menge": "1", "einheit": "Psch.", "preis": "184.50", "satz": 8.1},
    {"text": "Kleinmaterial und Fahrzeug", "menge": "1", "einheit": "Psch.", "preis": "45.00", "satz": 8.1},
]
BEISPIEL_OFFERTE = [
    {"text": "Demontage der bestehenden Unterverteilung", "menge": "3", "einheit": "h", "preis": "98.00", "satz": 8.1},
    {"text": "Neue Unterverteilung inkl. Montage", "menge": "1", "einheit": "Stk.", "preis": "1450.00", "satz": 8.1},
    {"text": "Inbetriebnahme, Mess- und Prüfprotokoll", "menge": "1", "einheit": "Psch.", "preis": "380.00", "satz": 8.1},
]


def beleg_formular(art):
    import html
    import json
    rechnung = art == "rechnung"
    if rechnung:
        meta = ('<div class="frow"><div class="fgrp"><label class="flabel" for="bl-nr">Rechnungsnummer</label><input class="finput" type="text" id="bl-nr" maxlength="30" value="2027-024"></div>'
                '<div class="fgrp"><label class="flabel" for="bl-datum">Rechnungsdatum</label><input class="finput" type="date" id="bl-datum" value="2027-02-15"></div></div>'
                '<div class="frow"><div class="fgrp"><label class="flabel" for="bl-leistungsjahr">Leistungsdatum oder -zeitraum (falls anders als das Rechnungsdatum)</label><input class="finput" type="text" id="bl-leistungsjahr" maxlength="40" value="08.02.2027"></div>'
                '<div class="fgrp"><label class="flabel" for="bl-frist">Zahlbar innert Tagen</label><input class="finput" type="text" inputmode="numeric" id="bl-frist" value="30"></div></div>'
                '<div class="fgrp"><label class="flabel" for="bl-referenz">Ihre Referenz oder Auftrag (optional)</label><input class="finput" type="text" id="bl-referenz" maxlength="60" value="Auftrag vom 01.02.2027"></div>')
        einleitung, schluss = "", "Vielen Dank für Ihren Auftrag."
    else:
        meta = ('<div class="frow"><div class="fgrp"><label class="flabel" for="bl-nr">Offertnummer</label><input class="finput" type="text" id="bl-nr" maxlength="30" value="O-2027-007"></div>'
                '<div class="fgrp"><label class="flabel" for="bl-datum">Datum</label><input class="finput" type="date" id="bl-datum" value="2027-02-15"></div></div>'
                '<div class="frow"><div class="fgrp"><label class="flabel" for="bl-gueltig">Gültig bis</label><input class="finput" type="date" id="bl-gueltig" value="2027-03-31"></div>'
                '<div class="fgrp"><label class="flabel" for="bl-referenz">Objekt oder Projekt (optional)</label><input class="finput" type="text" id="bl-referenz" maxlength="60" value="Ersatz Unterverteilung, Testgasse 5"></div></div>'
                '<label class="qr-wahl"><input type="checkbox" id="bl-ungefaehr"> Preise sind ungefähre Angaben (Kostenschätzung)</label>'
                '<label class="qr-wahl"><input type="checkbox" id="bl-unverbindlich"> Offerte als «unverbindlich» kennzeichnen</label>'
                '<label class="qr-wahl"><input type="checkbox" id="bl-annahme" checked> Zeile für die Annahme mit Unterschrift</label>')
        einleitung, schluss = "Gerne offerieren wir Ihnen die folgenden Arbeiten:", "Bei Fragen sind wir gerne für Sie da."
    titel = "Rechnung" if rechnung else "Offerte"
    beispiel = BEISPIEL_RECHNUNG if rechnung else BEISPIEL_OFFERTE
    return (
        '<section id="werkzeug" class="flaeche">\n  <h2 class="sr-only">%s erstellen</h2>\n'
        '  <div class="qr-raster wz-eingabe-zuerst">\n'
        '    <form id="bl-formular" class="ccard qr-formular" data-art="%s" novalidate>\n'
        '      <noscript><p class="note">Das Werkzeug braucht JavaScript. Es rechnet alles in Ihrem Browser und sendet nichts.</p></noscript>\n'
        '      <p class="wz-beispielhinweis">Die Felder enthalten ein Beispiel mit erfundenen Daten. <button type="button" class="qr-klein" id="bl-leeren">Felder leeren</button></p>\n'
        '      <fieldset><legend>%s</legend>%s</fieldset>\n'
        '      <fieldset><legend>Mehrwertsteuer</legend>'
        '<label class="qr-wahl"><input type="checkbox" id="bl-pflichtig" checked> Mein Betrieb ist MWST-pflichtig</label>'
        '<div class="fgrp" id="bl-uid-grp"><label class="flabel" for="bl-uid">MWST-Nummer</label><input class="finput" type="text" id="bl-uid" '
        'maxlength="24" placeholder="CHE-123.456.789 MWST" value="CHE-123.456.789 MWST"></div>'
        '<div id="bl-ohne-grp" hidden><label class="qr-wahl"><input type="checkbox" id="bl-hinweis-ohne" checked> Hinweis «Nicht MWST-pflichtig» anfügen</label>'
        '<p class="qr-hilfe">Wer nicht im MWST-Register eingetragen ist, darf keine MWST ausweisen (Art. 27 MWSTG).</p></div>'
        '%s</fieldset>\n'
        '      <fieldset><legend>Positionen</legend><div id="bl-positionen" class="bl-positionen"></div>'
        '<button type="button" class="qr-klein" id="bl-neu">Position hinzufügen</button>'
        '<p class="qr-hilfe">Preise ohne MWST. Höchstens 12 Positionen auf einer Seite.</p></fieldset>\n'
        '      <fieldset><legend>Texte</legend>'
        '<div class="fgrp"><label class="flabel" for="bl-ort">Ort und Datum im Brief</label><input class="finput" type="text" id="bl-ort" maxlength="60" value="Liestal, 15. Februar 2027"></div>'
        '<div class="fgrp"><label class="flabel" for="bl-einleitung">Einleitung (optional)</label><textarea class="ftextarea" id="bl-einleitung" maxlength="400">%s</textarea></div>'
        '<div class="fgrp"><label class="flabel" for="bl-schluss">Schlusssatz (optional)</label><textarea class="ftextarea" id="bl-schluss" maxlength="400">%s</textarea></div>'
        '<div class="fgrp"><label class="flabel" for="bl-unterschrift">Name unter dem Brief</label><input class="finput" type="text" id="bl-unterschrift" maxlength="60" value="Anna Muster"></div>'
        '</fieldset>\n      %s\n      %s\n      %s\n      %s\n'
        '      <script type="application/json" id="bl-beispiel">%s</script>\n'
        '    </form>\n'
        '    <div class="qr-seite">\n'
        '      <div class="ccard mg-rechnung" id="bl-ergebnis" aria-live="polite"><p class="at-was">Das Werkzeug braucht JavaScript.</p></div>\n'
        '      <div id="bl-meldungen" class="wz-meldungen" role="alert"></div>\n'
        '      <div class="qr-knoepfe"><button type="button" class="btn-p" id="bl-pdf">%s als PDF herunterladen</button></div>\n'
        '      <figure class="geraet br-vorschau-geraet"><div class="geraet-leiste"><i aria-hidden="true"></i><i aria-hidden="true"></i><i aria-hidden="true"></i>'
        '<span class="geraet-titel">Vorschau</span></div><div class="br-vorschau" id="bl-vorschau"></div></figure>\n'
        '    </div>\n  </div>\n</section>' % (
            titel, art, titel, meta,
            '<label class="qr-wahl"><input type="checkbox" id="bl-fuenfer"> Total auf 5 Rappen runden (Praxis, keine gesetzliche Pflicht)</label>',
            html.escape(einleitung), html.escape(schluss),
            adress_felder("ab", "Ihr Betrieb (Absender)", BEISPIEL_ABSENDER, kontakt=True),
            adress_felder("em", "Kunde (Empfänger)", BEISPIEL_EMPFAENGER),
            qr_felder("rq") if rechnung else "", FENSTER_FELDER,
            json.dumps(beispiel, ensure_ascii=False).replace("</", "<\\/"), titel))


def rechnung_formular():
    return beleg_formular("rechnung")


def offerte_formular():
    return beleg_formular("offerte")


MWST_QUELLEN = [
    ("Mehrwertsteuergesetz, Art. 25 (Steuersätze)", "https://www.fedlex.admin.ch/eli/cc/2009/615/de#art_25"),
    ("Mehrwertsteuergesetz, Art. 26 (Rechnung)", "https://www.fedlex.admin.ch/eli/cc/2009/615/de#art_26"),
    ("Mehrwertsteuergesetz, Art. 27 (unrichtiger oder unberechtigter Steuerausweis)", "https://www.fedlex.admin.ch/eli/cc/2009/615/de#art_27"),
    ("ESTV: MWST-Steuersätze", "https://www.estv.admin.ch/de/mwst-steuersaetze-schweiz"),
    ("ESTV: MWST-Info 16 Buchführung und Rechnungsstellung", "https://www.gate.estv.admin.ch/mwst-webpublikationen/public/pages/taxInfos/tableOfContent.xhtml"),
    ("Bundesrat: Zusatzfinanzierung der AHV (Abstimmung vom 29.11.2026)", "https://www.admin.ch/de/ahv-zusatzfinanzierung"),
]

_DATENSCHUTZ_FAQ = {"frage": "Werden meine Angaben gespeichert?",
                    "antwort": "Nein. Berechnung und PDF entstehen in Ihrem Browser. Die Seite setzt keine Cookies und verbietet "
                               "Verbindungen nach aussen technisch per Content Security Policy."}

WERKZEUGE.append({
    "slug": "rechnung",
    "pfad": "/werkzeuge/rechnung/",
    "name": "Rechnung erstellen",
    "kurz": "Rechnung mit Positionen und MWST als PDF, auf Wunsch mit QR-Zahlteil. Ohne Anmeldung, im Browser.",
    "titel": "Rechnung erstellen: gratis mit MWST und QR | Meyssens",
    "beschreibung": "Rechnung gratis erstellen: Positionen, MWST 8,1 %, 2,6 % oder 3,8 %, PDF mit QR-Zahlteil. Ohne Anmeldung, Daten "
                    "bleiben im Browser. Jetzt ausprobieren.",
    "h1": "Rechnung erstellen: gratis, mit MWST und QR-Zahlteil",
    "lead": "Positionen erfassen, Mehrwertsteuer berechnen und die Rechnung als PDF herunterladen, auf Wunsch mit QR-Zahlteil. "
            "Ihre Angaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_rechnung.html",
    "skripte": ["/assets/qrcode.js", "/assets/qr-rechnung.js", "/assets/brief-pdf.js", "/assets/beleg.js"],
    "ersetzen": {"<!-- beleg-formular -->": rechnung_formular},
    "gespraech": {"titel": "Rechnungen direkt aus dem Rapport",
                  "text": "Wer jede Woche Rechnungen schreibt, verliert die Zeit beim Abtippen von Stunden und Material. Ein Ablauf kann "
                          "aus erfassten Rapporten Rechnungsentwürfe vorbereiten, die Sie prüfen und freigeben. Im Gratis-Prozess-Check "
                          "(30 Minuten) sagen wir offen, was sich in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Welche MWST-Sätze gelten?",
         "antwort": "Seit dem 1. Januar 2024 gelten 8,1 % (Normalsatz), 2,6 % (reduzierter Satz) und 3,8 % (Beherbergung), "
                    "Art. 25 MWSTG. Für 2026 und 2027 ist keine Änderung beschlossen."},
        {"frage": "Was muss auf einer Rechnung stehen?",
         "antwort": "Für MWST-pflichtige Betriebe nennt Art. 26 MWSTG unter anderem Name und Ort beider Seiten, die MWST-Nummer, "
                    "Datum, Art und Umfang der Leistung, das Entgelt sowie Steuersatz und Steuerbetrag."},
        {"frage": "Darf ich ohne MWST-Nummer Mehrwertsteuer verrechnen?",
         "antwort": "Nein. Wer nicht im MWST-Register eingetragen ist, darf keine Steuer ausweisen; eine trotzdem ausgewiesene Steuer "
                    "ist geschuldet (Art. 27 MWSTG). Schalten Sie im Werkzeug «MWST-pflichtig» aus."},
        {"frage": "Muss ich auf 5 Rappen runden?",
         "antwort": "Nein. Das Gesetz schreibt keine Rundung vor, die Musterrechnung der ESTV zeigt Rappenbeträge. Das Runden auf "
                    "5 Rappen ist eine verbreitete Praxis und im Werkzeug eine Option."},
        _DATENSCHUTZ_FAQ,
    ],
    "quellen": MWST_QUELLEN + [
        ("Mehrwertsteuergesetz, Art. 10 (Befreiung von der Steuerpflicht)", "https://www.fedlex.admin.ch/eli/cc/2009/615/de#art_10"),
        ("Mehrwertsteuerverordnung, Art. 57 (Kassenzettel)", "https://www.fedlex.admin.ch/eli/cc/2009/828/de#art_57"),
        ("Swissmint: Häufige Fragen (kleinste Münze)", "https://www.swissmint.ch/de/haeufige-fragen"),
        ("SIX, Implementation Guidelines QR-Rechnung, Version 2.4", "https://www.six-group.com/dam/download/banking-services/standardization/qr-bill/ig-qr-bill-v2.4-de.pdf"),
    ],
})

WERKZEUGE.append({
    "slug": "offerte",
    "pfad": "/werkzeuge/offerte/",
    "name": "Offerte erstellen",
    "kurz": "Offerte mit Positionen, MWST und Gültigkeitsfrist als PDF, mit Zeile für die Annahme. Ohne Anmeldung, im Browser.",
    "titel": "Offerte erstellen: gratis Vorlage mit MWST | Meyssens",
    "beschreibung": "Offerte gratis erstellen: Positionen, MWST, Gültigkeitsfrist und Annahmezeile, als PDF. Ohne Anmeldung, Daten bleiben "
                    "im Browser. Jetzt ausprobieren.",
    "h1": "Offerte erstellen: gratis, mit MWST und Gültigkeitsfrist",
    "lead": "Positionen erfassen, Mehrwertsteuer berechnen und die Offerte als PDF herunterladen, mit Gültigkeitsfrist und Zeile für "
            "die Annahme. Ihre Angaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_offerte.html",
    "skripte": ["/assets/qrcode.js", "/assets/qr-rechnung.js", "/assets/brief-pdf.js", "/assets/beleg.js"],
    "ersetzen": {"<!-- beleg-formular -->": offerte_formular},
    "gespraech": {"titel": "Offertanfragen schneller beantworten",
                  "text": "Ein Ablauf kann Anfragen sortieren, die nötigen Angaben nachfragen und einen Offertentwurf aus Ihren Ansätzen "
                          "vorbereiten. Sie prüfen und senden selbst. Im Gratis-Prozess-Check (30 Minuten) sagen wir offen, was sich "
                          "in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Wie lange bin ich an eine Offerte gebunden?",
         "antwort": "Mit einer Frist bis zu deren Ablauf (Art. 3 OR). Ohne Frist, bis Sie bei normalem Postlauf eine Antwort erwarten "
                    "dürfen (Art. 5 OR). Mit dem Zusatz «unverbindlich» entsteht keine Bindung (Art. 7 OR)."},
        {"frage": "Was gilt bei einer Kostenschätzung?",
         "antwort": "Wird ein ungefährer Ansatz ohne Zutun der Kundschaft unverhältnismässig überschritten, kann sie vom Vertrag "
                    "zurücktreten oder bei Bauten eine Herabsetzung verlangen (Art. 375 OR). Eine feste Prozentgrenze nennt das Gesetz nicht."},
        {"frage": "Gehört die MWST in die Offerte?",
         "antwort": "Für MWST-pflichtige Betriebe ist es üblich und klar, die Preise ohne MWST, die Steuer pro Satz und das Total "
                    "zu zeigen. Nicht MWST-pflichtige Betriebe dürfen keine Steuer ausweisen (Art. 27 MWSTG)."},
        _DATENSCHUTZ_FAQ,
    ],
    "quellen": MWST_QUELLEN + [
        ("Obligationenrecht, Art. 3 bis 7 (Antrag und Bindung)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_3"),
        ("Obligationenrecht, Art. 374 und 375 (Preis beim Werkvertrag, Kostenansatz)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_375"),
    ],
})

WERKZEUGE.append({
    "slug": "mwst-rechner",
    "pfad": "/werkzeuge/mwst-rechner/",
    "name": "MWST-Rechner",
    "kurz": "Mehrwertsteuer zu einem Betrag dazurechnen oder herausrechnen, mit 8,1 %, 2,6 % und 3,8 %.",
    "titel": "MWST-Rechner Schweiz 2026: 8,1 %, 2,6 %, 3,8 % | Meyssens",
    "beschreibung": "MWST-Rechner für die Schweiz: Mehrwertsteuer dazurechnen oder herausrechnen, mit 8,1 %, 2,6 % und 3,8 %. Gratis, "
                    "ohne Anmeldung. Jetzt ausprobieren.",
    "h1": "MWST-Rechner Schweiz: dazurechnen und herausrechnen",
    "lead": "Mehrwertsteuer zu einem Betrag dazurechnen oder aus einem Betrag herausrechnen, mit den Sätzen seit 2024. "
            "Ihre Eingaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_mwst.html",
    "skripte": ["/assets/mwst.js"],
    "gespraech": {"titel": "Belege automatisch erfassen",
                  "text": "Wer viele Belege von Hand abtippt, rechnet die Mehrwertsteuer immer wieder nach. Ein Ablauf kann Lieferant, "
                          "Betrag und MWST aus Belegen auslesen und einen Buchungsvorschlag vorbereiten, den Sie prüfen. Im "
                          "Gratis-Prozess-Check (30 Minuten) sagen wir offen, was sich in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Wie rechne ich die MWST aus einem Betrag heraus?",
         "antwort": "Betrag mit MWST × Satz / (100 + Satz). Bei 8,1 % also × 8,1 / 108,1. In CHF 1 081.00 stecken so CHF 81.00 "
                    "Mehrwertsteuer."},
        {"frage": "Welche Sätze gelten 2026 und 2027?",
         "antwort": "8,1 % (Normalsatz), 2,6 % (reduzierter Satz) und 3,8 % (Beherbergung), seit dem 1. Januar 2024 (Art. 25 MWSTG). "
                    "Für 2026 und 2027 ist keine Änderung beschlossen."},
        {"frage": "Wird auf 5 Rappen gerundet?",
         "antwort": "Nein, der Rechner rundet auf den Rappen. Das Gesetz schreibt keine Rundung vor; die Rundung auf 5 Rappen ist "
                    "eine Praxis beim Bargeld."},
        _DATENSCHUTZ_FAQ,
    ],
    "quellen": MWST_QUELLEN + [("Mehrwertsteuergesetz, Art. 37 (Saldosteuersatz)", "https://www.fedlex.admin.ch/eli/cc/2009/615/de#art_37")],
})

ARG_QUELLEN = [
    ("Arbeitsgesetz (ArG), Art. 9, 12, 13 und 46", "https://www.fedlex.admin.ch/eli/cc/1966/57_57_57/de"),
    ("Verordnung 1 zum Arbeitsgesetz (ArGV 1), Art. 25, 73, 73a und 73b", "https://www.fedlex.admin.ch/eli/cc/2000/243/de"),
    ("Obligationenrecht, Art. 321c (Überstunden)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_321_c"),
    ("KMU-Portal des Bundes: Arbeitszeiterfassung", "https://www.kmu.admin.ch/de/arbeitszeiterfassung-pflicht-fuer-arbeitgebende"),
]

WERKZEUGE.append({
    "slug": "arbeitszeit",
    "pfad": "/werkzeuge/arbeitszeit/",
    "name": "Arbeitszeit erfassen",
    "kurz": "Monatsblatt mit Beginn, Ende und Pause, Feiertagen nach Kanton, Soll/Ist und Überzeit-Hinweis; als PDF oder CSV.",
    "titel": "Arbeitszeiterfassung Vorlage 2027: Monatsblatt | Meyssens",
    "beschreibung": "Arbeitszeiterfassung gratis: Monatsblatt mit Feiertagen nach Kanton, Soll, Überstunden und Überzeit, als PDF oder "
                    "CSV. Jetzt ausprobieren.",
    "h1": "Arbeitszeiterfassung: Monatsblatt mit Soll und Überstunden",
    "lead": "Zeiten pro Tag erfassen, Soll und Überstunden berechnen und das Monatsblatt als PDF oder Tabelle herunterladen, "
            "mit den Feiertagen Ihres Kantons. Ihre Eingaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_arbeitszeit.html",
    "skripte": ["/assets/qrcode.js", "/assets/qr-rechnung.js", "/assets/arbeitstage.js", "/assets/arbeitszeit.js"],
    "ersetzen": {"<!-- at-daten -->": feiertage_json},
    "gespraech": {"titel": "Rapporte und Arbeitszeit ohne Abtippen",
                  "text": "Ein Ablauf kann Zeiten aus Rapporten oder einer App übernehmen, Abweichungen markieren und die Monatsauswertung "
                          "für die Lohnabrechnung vorbereiten. Im Gratis-Prozess-Check (30 Minuten) sagen wir offen, was sich in Ihrem "
                          "Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Muss ich die Arbeitszeit erfassen?",
         "antwort": "Ja, grundsätzlich für alle Mitarbeitenden, die dem Arbeitsgesetz unterstehen (Art. 46 ArG, Art. 73 ArGV 1). "
                    "Vereinfachte Erfassung oder Verzicht sind nur unter den Voraussetzungen von Art. 73a und 73b ArGV 1 möglich."},
        {"frage": "Was ist der Unterschied zwischen Überstunden und Überzeit?",
         "antwort": "Überstunden gehen über die vertragliche Arbeitszeit hinaus (Art. 321c OR). Überzeit geht über die gesetzliche "
                    "Höchstarbeitszeit von 45 oder 50 Stunden pro Woche hinaus (Art. 9 und 12 ArG)."},
        {"frage": "Wie lange muss ich die Unterlagen aufbewahren?",
         "antwort": "Mindestens fünf Jahre (Art. 73 Abs. 2 ArGV 1)."},
        _DATENSCHUTZ_FAQ,
    ],
    "quellen": ARG_QUELLEN + [("Kantonale Feiertage: Quellen beim Werkzeug Arbeitstage berechnen", "https://meyssens.ch/werkzeuge/arbeitstage/")],
})

WERKZEUGE.append({
    "slug": "ferien",
    "pfad": "/werkzeuge/ferien/",
    "name": "Ferienanspruch berechnen",
    "kurz": "Ferientage bei Teilzeit, Eintritt oder Austritt und Ferienzuschlag bei Stundenlohn nach Art. 329a OR.",
    "titel": "Ferienanspruch berechnen: Teilzeit und Austritt | Meyssens",
    "beschreibung": "Ferienanspruch berechnen: Teilzeit, Eintritt oder Austritt im Jahr, Ferienzuschlag bei Stundenlohn (8,33 %, "
                    "10,64 %, 13,04 %). Jetzt ausprobieren.",
    "h1": "Ferienanspruch berechnen: Teilzeit, Eintritt und Austritt",
    "lead": "Ferientage bei Teilzeit und für ein angebrochenes Dienstjahr berechnen, dazu den Ferienzuschlag bei Stundenlohn. "
            "Ihre Eingaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_ferien.html",
    "skripte": ["/assets/ferien.js"],
    "gespraech": {"titel": "Ferien und Absenzen ohne Excel-Liste",
                  "text": "Ein Ablauf kann Ferienanträge erfassen, Saldi nachführen und die Angaben für die Lohnabrechnung vorbereiten. "
                          "Im Gratis-Prozess-Check (30 Minuten) sagen wir offen, was sich in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Wie viele Ferien sind gesetzlich vorgeschrieben?",
         "antwort": "Mindestens vier Wochen pro Dienstjahr, bis zum vollendeten 20. Altersjahr mindestens fünf Wochen (Art. 329a OR)."},
        {"frage": "Wie berechne ich Ferien bei Teilzeit?",
         "antwort": "Die Ferienwochen bleiben gleich, die Tage richten sich nach den Arbeitstagen pro Woche: Bei 3 Tagen pro Woche "
                    "sind 5 Wochen 15 Ferientage."},
        {"frage": "Wie hoch ist der Ferienzuschlag bei Stundenlohn?",
         "antwort": "Rechnerisch Ferienwochen geteilt durch die übrigen Wochen: 8,33 % bei 4, 10,64 % bei 5, 13,04 % bei 6 Wochen. "
                    "Er ist nur ausnahmsweise zulässig und muss im Vertrag und in jeder Lohnabrechnung ausgewiesen sein (BGE 129 III 493)."},
        _DATENSCHUTZ_FAQ,
    ],
    "quellen": [
        ("Obligationenrecht, Art. 329a (Dauer der Ferien)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_329_a"),
        ("Obligationenrecht, Art. 329b und 329d (Kürzung, Ferienlohn)", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_329_d"),
        ("BGE 129 III 493 (Ferienlohn im Stundenlohn)", "https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F129-III-493%3Ade&lang=de&type=show_document"),
        ("BGE 149 III 202 (Ferienlohn, Ausweis in der Lohnabrechnung)", "https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F149-III-202%3Ade&lang=de&type=show_document"),
    ],
})

WERKZEUGE.append({
    "slug": "lohnfortzahlung",
    "pfad": "/werkzeuge/lohnfortzahlung/",
    "name": "Lohnfortzahlung bei Krankheit",
    "kurz": "Dauer der Lohnfortzahlung nach Basler, Berner oder Zürcher Skala für das aktuelle Dienstjahr (Art. 324a OR).",
    "titel": "Lohnfortzahlung Krankheit: Basler Skala Rechner | Meyssens",
    "beschreibung": "Lohnfortzahlung bei Krankheit berechnen: Basler, Berner und Zürcher Skala nach Dienstjahr, mit Tabelle und "
                    "Quellen. Gratis, im Browser. Jetzt ausprobieren.",
    "h1": "Lohnfortzahlung bei Krankheit: Basler, Berner, Zürcher Skala",
    "lead": "Wie lange der Lohn bei Krankheit weiterbezahlt wird, nach Dienstjahr und Skala, mit Tabelle und Quellen. "
            "Ihre Eingaben bleiben in Ihrem Browser.",
    "geprueft": "2026-11-24",
    "veroeffentlicht": "2026-11-24",
    "inhalt": "werkzeug_lohnfortzahlung.html",
    "skripte": ["/assets/lohnfortzahlung.js"],
    "gespraech": {"titel": "Absenzen und Fristen im Blick",
                  "text": "Ein Ablauf kann Absenzen pro Dienstjahr zusammenzählen, an Meldefristen der Taggeldversicherung erinnern und "
                          "Unterlagen für das Treuhandbüro vorbereiten. Im Gratis-Prozess-Check (30 Minuten) sagen wir offen, was sich "
                          "in Ihrem Betrieb lohnt.",
                  "knopf": "Gratis-Prozess-Check anfragen"},
    "faq": [
        {"frage": "Wie lange muss der Lohn bei Krankheit bezahlt werden?",
         "antwort": "Im ersten Dienstjahr drei Wochen, danach für eine angemessene längere Zeit (Art. 324a OR). Wie lange, regeln "
                    "die Skalen der Gerichte, zum Beispiel die Basler, Berner oder Zürcher Skala."},
        {"frage": "Gilt die Dauer pro Krankheit oder pro Jahr?",
         "antwort": "Pro Dienstjahr. Mehrere Absenzen im selben Dienstjahr werden zusammengezählt, mit dem neuen Dienstjahr entsteht "
                    "der Anspruch neu."},
        {"frage": "Was gilt mit einer Krankentaggeldversicherung?",
         "antwort": "Vertrag oder Gesamtarbeitsvertrag können eine andere Regelung vorsehen, wenn sie mindestens gleichwertig ist "
                    "(Art. 324a Abs. 4 OR). Dann gelten die Leistungen der Versicherung statt der Skala."},
        _DATENSCHUTZ_FAQ,
    ],
    "quellen": [
        ("Obligationenrecht, Art. 324a", "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_324_a"),
        ("Amt für Wirtschaft und Arbeit Basel-Stadt: Merkblatt Lohn (Basler Skala), Stand 1.1.2024", "https://media.bs.ch/original_file/e19d2e11d1e77cd9c999cc9d51ccc85cfbfa1439/06-merkblatt-lohn-0.pdf"),
        ("Zivilgerichte des Kantons Bern: Krankheit (Berner Skala)", "https://www.zsg.justice.be.ch/de/start/themen/zivilrecht/arbeitsrecht/krankheit.html"),
        ("Gerichte des Kantons Zürich: Arbeitsverhinderung (Skalen)", "https://www.gerichte-zh.ch/de/themen/arbeit/waehrend-arbeitsverhaeltnis/arbeitsverhinderung"),
        ("Bericht des Bundesrates vom 19.8.2026 (Postulat 24.3465)", "https://www.bag.admin.ch/dam/de/sd-web/o28MVudm68Ve/Bericht%20des%20Bundesrates%20in%20Erf%C3%BCllung%20des%20Postulates%2024.3465.pdf"),
    ],
})

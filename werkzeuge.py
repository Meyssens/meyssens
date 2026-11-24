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

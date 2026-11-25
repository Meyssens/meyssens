"""Pakete für Unternehmen (Entscheid Lionel, 24.11.2026): Mahnwesen, Anfragen, Service-Erinnerungen (Garage).

Preise nur als «ab»; verbindlicher Preis nach 20 Minuten kostenlosem Gespräch, je nach Aufwand. Mindestlaufzeit 12 Monate für den
Monatsbetrag. Anbindung an andere Software: Einrichtung nach Aufwand. Vorher/Nachher sind Beispielrechnungen mit
angenommenen Werten, keine Kundenergebnisse. Seiten baut build.py (paket_seite) mit vorlage_loesung.html.
"""

PAKETE_STAND = "2026-11-24"
PREIS_HINWEIS = "Verbindlicher Preis nach 20 Minuten kostenlosem Gespräch, je nach Aufwand."
PILOT = "Pilotbetrieb: die ersten 3 Monate ohne Monatsbetrag, Einrichtung nach Angebot."
MWST = "Alle Preise in CHF, Endpreise, nicht MWST-pflichtig."
LAUFZEIT = "Mindestlaufzeit 12 Monate für den Monatsbetrag."
ANBINDUNG = "Anbindung an andere Software: Einrichtung nach Aufwand."

START_WEG = [
    {"symbol": "gespraech", "titel": "Gespräch", "text": "20 Minuten, kostenlos: Sie zeigen uns, wie es heute läuft und welche Software Sie nutzen."},
    {"symbol": "angebot", "titel": "Vorschlag", "text": "Sie erhalten einen verbindlichen Preis für Einrichtung und Monatsbetrag, je nach Aufwand."},
    {"symbol": "betrieb", "titel": "Start", "text": "Wir richten das Paket ein und prüfen es mit Ihnen an echten Fällen. Danach läuft es, Sie geben frei."},
]

PAKETE = [
    {
        "slug": "mahnwesen", "pfad": "/mahnwesen/", "name": "Mahnwesen", "sitemap": True,
        "kurz": "QR-Rechnung, Erinnerung, Mahnstufen und Zahlungsabgleich: Offene Rechnungen werden bezahlt, ohne dass Sie nachführen.",
        "titel": "Mahnwesen automatisieren: Paket für KMU | Meyssens",
        "beschreibung": "QR-Rechnung, Zahlungserinnerung, Mahnstufen und Zahlungsabgleich als Paket. Einrichtung ab CHF 3'500. Jetzt Preis anfragen.",
        "h1": "Mahnwesen: offene Rechnungen im Griff",
        "lead": "QR-Rechnung, Erinnerung, Mahnstufen und Zahlungsabgleich in einem Ablauf. Was Ihren Betrieb verlässt, geben Sie frei.",
        "einrichtung": "CHF 3'500", "monat": "CHF 290",
        "schritte": [
            {"symbol": "qr", "titel": "Rechnung", "zeile": "2027-018 · CHF 2 400.00", "text": "QR-Rechnung nach SIX-Standard, aus Ihrer Software oder neu erstellt."},
            {"symbol": "eingang", "titel": "Erinnerung", "zeile": "Fällig seit 10 Tagen", "text": "Freundliche Erinnerung als Entwurf, sobald die Frist abläuft."},
            {"symbol": "vorschlag", "titel": "Mahnung", "zeile": "2. Stufe, mit Verzugszins", "text": "Mahnstufen nach Ihren Regeln, mit Verzugszins, wenn Sie das wollen."},
            {"symbol": "zahlung", "titel": "Zahlung eingegangen", "zeile": "Abgeglichen, Mahnlauf gestoppt", "text": "Zahlungen aus dem E-Banking werden den offenen Rechnungen zugeordnet."},
        ],
        "leistungen": [
            ("QR-Rechnung", "Rechnungen mit QR-Zahlteil nach den Vorgaben der SIX, mit Referenz für den automatischen Abgleich."),
            ("Erinnerung", "Freundliche Zahlungserinnerung kurz nach Ablauf der Frist, als Entwurf zur Freigabe."),
            ("Mahnstufen", "Mahnung und letzte Mahnung nach Ihren Fristen; Verzugszins nach Obligationenrecht auf Wunsch."),
            ("Zahlungsabgleich", "Zahlungseingänge aus dem E-Banking (zum Beispiel als camt-Datei) werden zugeordnet; bezahlte Rechnungen fallen aus dem Mahnlauf."),
        ],
        "beispiel": {
            "annahme": "Annahmen: 80 Rechnungen pro Monat, davon 16 mit Erinnerung und 5 mit Mahnung.",
            "vorher": [("Offene Posten prüfen", "80 × 1 Min.", 80), ("Erinnerungen schreiben", "16 × 8 Min.", 128),
                       ("Mahnungen schreiben", "5 × 12 Min.", 60), ("Zahlungen zuordnen", "80 × 1,5 Min.", 120)],
            "nachher": [("Entwürfe prüfen und freigeben", "21 × 1 Min.", 21), ("Ausnahmen beim Abgleich klären", "8 × 3 Min.", 24)],
        },
        "faq": [
            {"frage": "Was kostet das Paket Mahnwesen?", "antwort": "Einrichtung ab CHF 3'500, Betrieb ab CHF 290 pro Monat, Mindestlaufzeit 12 Monate für den Monatsbetrag. Den verbindlichen Preis nennen wir nach 20 Minuten kostenlosem Gespräch, je nach Aufwand."},
            {"frage": "Werden Mahnungen ohne mich verschickt?", "antwort": "Nein, ausser Sie wünschen es ausdrücklich. Erinnerungen und Mahnungen entstehen als Entwurf, Sie geben frei."},
            {"frage": "Funktioniert das mit meiner Buchhaltungssoftware?", "antwort": "Das prüfen wir im Gespräch. Die Anbindung an andere Software richten wir nach Aufwand ein; der Preis steht im Vorschlag."},
            {"frage": "Wie hoch ist der Verzugszins?", "antwort": "Fünf Prozent pro Jahr nach Art. 104 OR, ausser vertraglich ist mehr vereinbart. Ob und ab welcher Stufe er erscheint, legen Sie fest."},
        ],
        "thema": "Paket Mahnwesen: verbindlicher Preis",
    },
    {
        "slug": "anfragen", "pfad": "/anfragen/", "name": "Anfragen", "sitemap": True,
        "kurz": "Anfrage beantworten in Minuten, Nachfassen und Terminbuchung: Interessenten erhalten rasch eine Antwort und einen Termin.",
        "titel": "Anfragen beantworten: Paket für KMU | Meyssens",
        "beschreibung": "Anfragen in Minuten beantworten, nachfassen und Termine buchen lassen, als Paket. Einrichtung ab CHF 4'500. Jetzt Preis anfragen.",
        "h1": "Anfragen: Antwort in Minuten",
        "lead": "Jede Anfrage erhält rasch eine passende Antwort, offene Anfragen werden nachgefasst, und Interessenten buchen selbst einen Termin. Sie geben frei.",
        "einrichtung": "CHF 4'500", "monat": "CHF 390",
        "schritte": [
            {"symbol": "eingang", "titel": "Anfrage", "zeile": "Website, 14:02", "text": "Anfragen aus Formular und E-Mail landen an einem Ort."},
            {"symbol": "vorschlag", "titel": "Antwort", "zeile": "Entwurf bereit, 14:04", "text": "Antwortentwurf mit den passenden Angaben, in Minuten bereit zur Freigabe."},
            {"symbol": "gespraech", "titel": "Nachfassen", "zeile": "Nach 3 Tagen", "text": "Bleibt die Antwort aus, liegt ein Nachfass-Entwurf bereit."},
            {"symbol": "freigabe", "titel": "Termin gebucht", "zeile": "Di, 10:30", "text": "Interessenten wählen selbst einen freien Termin aus Ihrem Kalender."},
        ],
        "leistungen": [
            ("Anfragen sammeln", "Anfragen aus dem Kontaktformular und aus dem Postfach an einem Ort, nach Thema sortiert."),
            ("Antwort in Minuten", "Antwortentwurf mit Ihren Angaben, Preisen und Unterlagen, bereit zur Freigabe."),
            ("Nachfassen", "Freundliches Nachfassen nach Tagen, die Sie festlegen, als Entwurf."),
            ("Terminbuchung", "Freie Termine aus Ihrem Kalender, die Interessenten selbst buchen."),
        ],
        "beispiel": {
            "annahme": "Annahmen: 40 Anfragen pro Monat, davon 20 mit Nachfassen und 15 mit Termin.",
            "vorher": [("Antworten schreiben", "40 × 12 Min.", 480), ("Nachfassen", "20 × 5 Min.", 100), ("Termin abstimmen", "15 × 10 Min.", 150)],
            "nachher": [("Antwortentwürfe prüfen und senden", "40 × 3 Min.", 120), ("Nachfassen freigeben", "20 × 1 Min.", 20), ("Gebuchte Termine bestätigen", "15 × 1 Min.", 15)],
        },
        "faq": [
            {"frage": "Was kostet das Paket Anfragen?", "antwort": "Einrichtung ab CHF 4'500, Betrieb ab CHF 390 pro Monat, Mindestlaufzeit 12 Monate für den Monatsbetrag. Den verbindlichen Preis nennen wir nach 20 Minuten kostenlosem Gespräch, je nach Aufwand."},
            {"frage": "Antwortet ein Programm an meiner Stelle?", "antwort": "Nein. Es bereitet die Antwort vor, Sie oder Ihr Team geben frei. Auf Wunsch können einfache Eingangsbestätigungen direkt gehen."},
            {"frage": "Welcher Kalender lässt sich anbinden?", "antwort": "Das prüfen wir im Gespräch. Die Anbindung an andere Software richten wir nach Aufwand ein; der Preis steht im Vorschlag."},
            {"frage": "Was passiert mit den Daten der Interessenten?", "antwort": "Wir bearbeiten sie in Ihrem Auftrag. Vor dem Start schliessen wir einen Vertrag zur Auftragsbearbeitung ab."},
        ],
        "thema": "Paket Anfragen: verbindlicher Preis",
    },
    {
        "slug": "garage", "pfad": "/garage/", "name": "Service-Erinnerungen", "sitemap": True, "quelle": True,
        "kurz": "Service, Reifenwechsel und MFK: Kundinnen und Kunden werden rechtzeitig erinnert und buchen den Termin.",
        "titel": "Service-Erinnerungen für Garagen: Paket | Meyssens",
        "beschreibung": "Erinnerungen an Service, Reifenwechsel und MFK für Garagen, mit Terminvorschlag. Einrichtung ab CHF 3'900. Jetzt Preis anfragen.",
        "h1": "Service-Erinnerungen: Service, Reifen, MFK",
        "lead": "Ihre Kundinnen und Kunden werden an Service, Reifenwechsel und MFK erinnert und erhalten einen Terminvorschlag. Sie geben frei.",
        "einrichtung": "CHF 3'900", "monat": "CHF 290",
        "schritte": [
            {"symbol": "daten", "titel": "Fällig", "zeile": "Service, 12 Monate", "text": "Fällige Fahrzeuge aus Ihrem Garagenprogramm: Service, Reifen, MFK."},
            {"symbol": "eingang", "titel": "Erinnerung", "zeile": "SMS oder E-Mail", "text": "Erinnerung mit Terminvorschlag, als Entwurf zur Freigabe."},
            {"symbol": "gespraech", "titel": "Antwort", "zeile": "«Passt am Donnerstag»", "text": "Antworten landen beim Fahrzeug; Unklares legen wir Ihnen vor."},
            {"symbol": "freigabe", "titel": "Termin gebucht", "zeile": "Do, 07:30", "text": "Der Termin steht im Werkstattplan."},
        ],
        "leistungen": [
            ("Service", "Erinnerung nach Datum oder Kilometerstand, so wie Ihr Garagenprogramm die Fälligkeit führt."),
            ("Reifenwechsel", "Saisonale Erinnerung im Frühling und Herbst, mit freien Terminen."),
            ("MFK", "Hinweis, wenn eine MFK ansteht, mit Angebot für die Vorbereitung."),
            ("Terminbuchung", "Kundinnen und Kunden wählen einen freien Termin; der Werkstattplan bleibt bei Ihnen."),
        ],
        "beispiel": {
            "annahme": "Annahmen: rund 220 Erinnerungen pro Monat (Service, Reifen, MFK), Liste wöchentlich, 30 Rückfragen.",
            "vorher": [("Liste fälliger Fahrzeuge erstellen", "4 × 30 Min.", 120), ("Kunden anrufen oder anschreiben", "220 × 4 Min.", 880)],
            "nachher": [("Versand prüfen und freigeben", "4 × 10 Min.", 40), ("Rückfragen beantworten", "30 × 3 Min.", 90)],
        },
        "faq": [
            {"frage": "Was kostet das Paket Service-Erinnerungen?", "antwort": "Einrichtung ab CHF 3'900, Betrieb ab CHF 290 pro Monat, Mindestlaufzeit 12 Monate für den Monatsbetrag. Den verbindlichen Preis nennen wir nach 20 Minuten kostenlosem Gespräch, je nach Aufwand."},
            {"frage": "Dürfen wir Kunden per SMS oder E-Mail erinnern?", "antwort": "An Kundinnen und Kunden, mit denen Sie in Kontakt stehen, mit Angabe des Absenders und einer einfachen Abmeldung. Wer sich abmeldet, erhält keine Erinnerungen mehr."},
            {"frage": "Funktioniert das mit unserem Garagenprogramm?", "antwort": "Das prüfen wir im Gespräch. Die Anbindung an andere Software richten wir nach Aufwand ein; der Preis steht im Vorschlag."},
            {"frage": "Bucht das System MFK-Termine beim Strassenverkehrsamt?", "antwort": "Nein. Das Aufgebot kommt vom Strassenverkehrsamt. Das Paket erinnert Ihre Kundschaft und bietet die Vorbereitung bei Ihnen an."},
        ],
        "thema": "Paket Service-Erinnerungen: verbindlicher Preis",
    },
]

# Gemeinden (Entscheid Lionel, 24.11.2026): Pilot gratis; danach gestaffelt nach Einwohnern
GEMEINDE_STUFEN = [("unter 2'000 Einwohner", "CHF 2'900 pro Jahr"), ("2'000 bis 5'000 Einwohner", "CHF 4'900 pro Jahr"),
                   ("über 5'000 Einwohner", "Preis nach Einwohnerzahl, auf Anfrage")]
GEMEINDE_AUSBAU = ("Später als Ausbau möglich: Abläufe für die Verwaltung, zum Beispiel Baugesuche oder Raumreservationen. "
                   "Den Umfang besprechen wir mit Ihnen.")

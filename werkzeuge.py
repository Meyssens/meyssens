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

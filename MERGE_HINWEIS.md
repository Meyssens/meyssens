# Hinweis zum Zusammenführen von `seo-inhalte` und `werkzeuge`

Stand: 25.11.2026. Beide Branches gehen von `main` (58f21c1) aus und berühren dieselben Dateien. Diese Datei wird nicht veröffentlicht (`_config.yml`).

## Konflikt `/garage/`

| | `werkzeuge` | `seo-inhalte` (gilt, Entscheid Lionel 25.11.2026) |
|---|---|---|
| Inhalt | Zielseite für den Briefpost-Test (Gratis-Hilfen, Garagen-Beispiel, Formular) | Paket «Service-Erinnerungen» (Ablauf-Animation, Beispielrechnung, Preis ab CHF 3'900 / ab CHF 290 pro Monat, Formular) |
| Erzeugt von | `build.py`: Liste `BRIEF_SEITEN`, Funktion `brief_zielseiten()` | `pakete.py` (Eintrag `slug: garage`), `build.py`: `paket_seiten()` |
| Suchmaschinen | `noindex`, nicht in der Sitemap | indexierbar, in der Sitemap |
| Formular | «Pilot anfragen» mit Quelle-Feld (alle Formulare über `quelle_felder()`) | «Pilot anfragen» mit Quelle-Feld (nur `/garage/`, Einbau in `paket_seiten()`) |

**So lösen:**
1. In `build.py` den Eintrag mit `"pfad": "/garage/"` aus `BRIEF_SEITEN` (Branch `werkzeuge`) **entfernen**. `/treuhand/` bleibt als Brief-Zielseite.
2. `garage/index.html` beim Konflikt **nicht von Hand mischen**: nach dem Zusammenführen `python3 build.py` ausführen; die Datei entsteht dann aus `pakete.py` neu.
3. Quelle-Feld: Nach dem Merge gibt es zwei Einbauwege (generisch `quelle_felder()` aus `werkzeuge` für alle Formulare und den Einbau in `paket_seiten()`). **Den Einbau in `paket_seiten()` entfernen** (die Zeilen mit `if p.get("quelle")` bis `raise SystemExit("Paket %s: Quelle-Feld …")` sowie `"quelle": True` in `pakete.py`), sonst erhält `/garage/` das Feld doppelt. Die doppelten Definitionen `QUELLEN`, `QUELLE_MARKER`, `FORM_RE`, `EINW_RE`, `quelle_feld()` in `build.py` auf **eine** reduzieren (Fassung aus `werkzeuge`).
4. `assets/demos.js`, `assets/anfrage.js`, `assets/stil.css`: Der Block «Formularfeld «Wie haben Sie von uns erfahren?»» ist in beiden Branches wortgleich. Bei einem Konflikt **einmal** behalten.
5. Brief-Zielseite Garage: Der QR-Code im Serienbrief (`~/ms/unternehmen/brief_serienbrief.py`) zeigt auf `https://meyssens.ch/garage/?utm_source=brief…`. Er führt nach dem Merge auf die Paketseite; das Quelle-Feld belegt «Brief» weiterhin vor. Die Brieftexte (Gratis-Hilfen: Offerte, Rechnung, Mahnung) passen dann nur noch teilweise zur Seite: vor dem Versand im Januar prüfen.

## Weitere Überschneidungen

- **Datenschutzerklärung:** `werkzeuge` ergänzt einen Satz zum Quelle-Feld und erweitert den Werkzeug-Absatz (in `index.html` und `gemeinden/index.html`). `seo-inhalte` ändert die Datenschutzerklärung nicht. Beim Merge die Fassung aus `werkzeuge` übernehmen.
- **Texte «Gratis-Prozess-Check (30 Minuten)»:** In `seo-inhalte` überall durch «20 Minuten kostenloses Gespräch» ersetzt (`PROZESS_CHECK`, Knöpfe «Kostenloses Gespräch anfragen»). Die Werkzeugseiten in `werkzeuge` (`werkzeuge.py`, Abschnitt «gespraech» und Texte) nennen noch «Gratis-Prozess-Check (30 Minuten)»: nach dem Merge angleichen.
- **Pilot für Unternehmen:** `seo-inhalte` nennt «Pilotbetrieb: die ersten 3 Monate ohne Monatsbetrag, Einrichtung nach Angebot». Die Zielseite `/treuhand/` in `werkzeuge` nennt «4 statt 3 Monate Pilot kostenlos» (Partnermodell B), die Partnerunterlage ebenso. Bewusst nicht geändert (Entscheid Lionel), aber widersprüchlich: siehe Bericht vom 25.11.2026.
- **`test_seiten.py`:** Beide Branches nehmen `noindex`-Seiten von der Sitemap-Prüfung aus (gleiche Logik, leicht anderer Kommentar) und `werkzeuge` erweitert `FORMFELDER` und `worte()`. Beide Änderungen behalten.
- **`_config.yml`:** Einträge beider Branches behalten (`werkzeuge.py`, `werkzeug_*.html`, `test_werkzeuge.py`, `pakete.py`, `MERGE_HINWEIS.md` …).
- Nach dem Merge: `python3 build.py`, `python3 test_seiten.py`, `python3 test_werkzeuge.py`, `python3 test_qr_rechnung.py`, `python3 kontrast_buttons.py`.

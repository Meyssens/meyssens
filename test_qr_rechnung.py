#!/usr/bin/env python3
"""Prüft das Werkzeug QR-Rechnung (assets/qr-rechnung.js) im Browser. Aufruf im Projektordner: python3 test_qr_rechnung.py

- Inhalt des QR-Codes für die drei Beispiele aus Anhang A der SIX Implementation Guidelines 2.4 (Zeichen für Zeichen)
- Prüfziffern: QR-Referenz (Modulo 10 rekursiv), Creditor Reference (ISO 11649), IBAN (Modulo 97)
- Regeln: QR-IBAN nur mit QR-Referenz und nur in CHF, QR-Referenz nur mit QR-IBAN, Betrag, Längen, Zeichensatz,
  strukturierte Adresse (PLZ und Ort Pflicht), höchstens 997 Zeichen, QR-Code höchstens Version 25 (117 Module)
- Layout: Schriftgrössen 11/8/10 und 11/6/8 Pkt., QR-Code 46 x 46 mm, Schweizer Kreuz 7 x 7 mm mittig, Eckmarken bei fehlendem
  Betrag und Zahler, Hinweis «Vor der Einzahlung abzutrennen», kein Header (SPC, 0200, 1) im Sichtteil
- PDF: Aufbau (Kopf, xref, Seitengrösse A4), optional QR-Code aus dem PDF gelesen (wenn Ghostscript und zxingcpp vorhanden)
- Werkzeugseite: keine Anfrage nach aussen beim Erstellen (Content Security Policy connect-src 'none')
Braucht Playwright mit Chromium, sonst nur Python-Standardbibliothek.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
fehler = []

# Anhang A, Beispiele 1 bis 3 (Tabellen 17 bis 19), Zeilenschaltung CR+LF
LEER7 = [""] * 7
BEISPIELE = [
    ({"konto": "CH64 3196 1000 0044 2155 7", "ze_name": "Max Muster & Söhne", "ze_strasse": "Musterstrasse", "ze_nr": "123",
      "ze_plz": "8000", "ze_ort": "Seldwyla", "ze_land": "CH", "waehrung": "CHF", "betrag": "50.00",
      "referenz": "00 00082 07791 22585 74212 86694", "mitteilung": "Bezahlung der Reise", "mit_zahler": True,
      "zp_name": "Simon Muster", "zp_strasse": "Musterstrasse", "zp_nr": "1", "zp_plz": "8000", "zp_ort": "Seldwyla", "zp_land": "CH"},
     ["SPC", "0200", "1", "CH6431961000004421557", "S", "Max Muster & Söhne", "Musterstrasse", "123", "8000", "Seldwyla", "CH"]
     + LEER7 + ["50.00", "CHF", "S", "Simon Muster", "Musterstrasse", "1", "8000", "Seldwyla", "CH", "QRR",
                "000008207791225857421286694", "Bezahlung der Reise", "EPD"]),
    ({"konto": "CH4431999123000889012", "ze_name": "Max Muster & Söhne", "ze_strasse": "Musterstrasse", "ze_nr": "123",
      "ze_plz": "8000", "ze_ort": "Seldwyla", "ze_land": "CH", "waehrung": "CHF", "betrag": "1949.75",
      "referenz": "210000000003139471430009017", "mitteilung": "Auftrag vom 15.10.2020", "mit_zahler": True,
      "zp_name": "Simon Muster", "zp_strasse": "Musterstrasse", "zp_nr": "1", "zp_plz": "8000", "zp_ort": "Seldwyla", "zp_land": "CH"},
     ["SPC", "0200", "1", "CH4431999123000889012", "S", "Max Muster & Söhne", "Musterstrasse", "123", "8000", "Seldwyla", "CH"]
     + LEER7 + ["1949.75", "CHF", "S", "Simon Muster", "Musterstrasse", "1", "8000", "Seldwyla", "CH", "QRR",
                "210000000003139471430009017", "Auftrag vom 15.10.2020", "EPD"]),
    ({"konto": "CH52 0483 5012 3456 7100 0", "ze_name": "Muster Stiftung", "ze_strasse": "Postfach", "ze_plz": "3001",
      "ze_ort": "Bern", "ze_land": "CH", "waehrung": "CHF"},
     ["SPC", "0200", "1", "CH5204835012345671000", "S", "Muster Stiftung", "Postfach", "", "3001", "Bern", "CH"]
     + LEER7 + ["", "CHF"] + LEER7 + ["NON", "", "", "EPD"]),
]
GUT = dict(BEISPIELE[1][0])
# (Änderung gegenüber GUT, Teil der erwarteten Fehlermeldung)
REGELN = [
    ({"konto": "CH4431999123000889013"}, "Prüfziffer der IBAN"),
    ({"konto": "DE89370400440532013000"}, "CH oder LI"),
    ({"referenz": "210000000003139471430009018"}, "Prüfziffer der QR-Referenz"),
    ({"referenz": "RF18539007547034"}, "QR-Referenz (27 Ziffern) Pflicht"),
    ({"waehrung": "EUR"}, "nur noch für Rechnungen in CHF"),
    ({"konto": "CH9300762011623852957"}, "nur mit einer QR-IBAN"),
    ({"konto": "CH9300762011623852957", "referenz": "RF18539007547035"}, "RF-Referenz ist ungültig"),
    ({"betrag": "12.345"}, "zwei Nachkommastellen"),
    ({"betrag": "0.00"}, "mindestens 0.01"),
    ({"ze_plz": ""}, "Postleitzahl Zahlungsempfänger fehlt"),
    ({"ze_ort": ""}, "Ort Zahlungsempfänger fehlt"),
    ({"ze_plz": "CH-8000"}, "ohne vorangestellten Landescode"),
    ({"ze_name": "x" * 71}, "höchstens 70 Zeichen"),
    ({"ze_strasse": "", "ze_nr": "5"}, "Hausnummer steht allein"),
    ({"ze_name": "Łukasz Muster"}, "nicht darstellen"),
    ({"ze_name": "Muster 中"}, "nicht zulässig"),
    ({"mitteilung": "x" * 141}, "höchstens 140 Zeichen"),
    ({"zp_ort": ""}, "Ort Zahlungspflichtiger fehlt"),
]

SKRIPT = """async (args) => {
  const Q = window.QRRechnung, aus = {beispiele: [], regeln: []};
  for (const e of args.beispiele) {
    const p = Q.erstelle(e);
    aus.beispiele.push({ok: p.ok, fehler: p.fehler.map(f => f.text), inhalt: p.ok ? p.daten.inhalt : null,
      module: p.ok ? Q.qrMatrix(p.daten.inhalt).length : 0, ops: p.ok ? p.entwurf.ops.map(o => o.t === 'qr' ? {t: 'qr', x: o.x, y: o.y, groesse: o.groesse} : o) : []});
  }
  for (const [aenderung, _] of args.regeln) {
    const p = Q.pruefe(Object.assign({}, args.gut, aenderung));
    aus.regeln.push(p.fehler.map(f => f.text));
  }
  aus.qrr = Q.qrReferenz('21000000000313947143000901');
  aus.scor = Q.scorReferenz('539007547034');
  aus.typo = Q.pruefe(Object.assign({}, args.gut, {mitteilung: 'A – „B“ ’C’'})).daten.mitteilung;
  const lang = Q.pruefe(Object.assign({}, args.gut, {mitteilung: 'x'.repeat(140), ze_name: 'y'.repeat(70), zp_name: 'z'.repeat(70)}));
  aus.lang = lang.ok ? Q.qrMatrix(lang.daten.inhalt).length : -1;
  const p = Q.erstelle(args.gut);
  aus.pdf = Array.from(Q.pdf(p.entwurf, 'Test'));
  return aus;
}"""


def main():
    seite_html = ROOT / "werkzeuge" / "qr-rechnung" / "index.html"
    if not seite_html.is_file():
        print("werkzeuge/qr-rechnung/index.html fehlt, zuerst build.py ausführen")
        sys.exit(1)
    text = seite_html.read_text(encoding="utf-8")
    if "connect-src 'none'" not in text or "form-action 'none'" not in text:
        fehler.append("Werkzeugseite: Content Security Policy ohne connect-src/form-action 'none'")
    with sync_playwright() as p:
        b = p.chromium.launch()
        seite = b.new_page()
        anfragen = []
        def liefern(route):
            # Seite aus dem Projektordner ausliefern, alles andere blockieren
            url = route.request.url
            if not url.startswith("http://meyssens.test/"):
                return route.abort()
            pfad = ROOT / url.split("http://meyssens.test/", 1)[1].split("?")[0]
            route.fulfill(path=str(pfad / "index.html" if url.endswith("/") else pfad))
        seite.route("**/*", liefern)
        seite.goto("http://meyssens.test/werkzeuge/qr-rechnung/")
        seite.wait_for_function("window.QRRechnung")
        seite.on("request", lambda r: anfragen.append(r.url))
        aus = seite.evaluate(SKRIPT, {"beispiele": [e for e, _ in BEISPIELE], "regeln": REGELN, "gut": GUT})
        # Bedienung: Beispiel ausfüllen, PDF herunterladen, dabei keine Anfrage nach aussen
        seite.click("#qr-beispiel")
        with seite.expect_download() as d:
            seite.click("[data-qr-download=pdf]")
        if not d.value.suggested_filename.endswith(".pdf"):
            fehler.append("Download: kein PDF")
        if [u for u in anfragen if not u.startswith(("blob:", "data:"))]:
            fehler.append("Werkzeug sendet Anfragen: %s" % anfragen)
        b.close()

    for (eingabe, soll), ist in zip(BEISPIELE, aus["beispiele"]):
        if not ist["ok"]:
            fehler.append("Beispiel %s: Fehler %s" % (eingabe["ze_name"], ist["fehler"]))
            continue
        if ist["inhalt"] != "\r\n".join(soll):
            fehler.append("Beispiel %s: Inhalt weicht ab:\n%r\n%r" % (eingabe["ze_name"], ist["inhalt"], "\r\n".join(soll)))
        if ist["module"] > 117:
            fehler.append("Beispiel %s: QR-Code grösser als Version 25" % eingabe["ze_name"])
        ops = ist["ops"]
        texte = [o for o in ops if o["t"] == "text"]
        groessen = {o["text"]: o["pt"] for o in texte}
        for titel, pt in (("Zahlteil", 11), ("Empfangsschein", 11)):
            if groessen.get(titel) != pt or not next(o for o in texte if o["text"] == titel)["fett"]:
                fehler.append("Beispiel: Titel %s nicht %d Pkt. fett" % (titel, pt))
        kopf = [o for o in texte if o["text"] == "Konto / Zahlbar an"]
        if sorted(o["pt"] for o in kopf) != [6, 8] or not all(o["fett"] for o in kopf):
            fehler.append("Beispiel: Überschriften nicht 6 Pkt. (Empfangsschein) und 8 Pkt. (Zahlteil) fett")
        if any(o["text"] in ("SPC", "0200") for o in texte):
            fehler.append("Beispiel: Header im Sichtteil")
        if "Vor der Einzahlung abzutrennen" not in groessen:
            fehler.append("Beispiel: Hinweis «Vor der Einzahlung abzutrennen» fehlt")
        qr = next(o for o in ops if o["t"] == "qr")
        kreuz = next(o for o in ops if o["t"] == "kreuz")
        if qr["groesse"] != 46 or abs(kreuz["x"] + 3.5 - (qr["x"] + 23)) > 1e-9 or abs(kreuz["y"] + 3.5 - (qr["y"] + 23)) > 1e-9:
            fehler.append("Beispiel: QR-Code nicht 46 mm oder Kreuz nicht mittig")
        werte = [o for o in texte if not o["fett"]]
        if not all(o["pt"] in (8, 10) for o in werte if o["text"] != "Vor der Einzahlung abzutrennen"):
            fehler.append("Beispiel: Werte nicht 8 oder 10 Pkt.")
        if ops and qr["x"] < 62 + 5:
            fehler.append("Beispiel: QR-Code ragt in den Empfangsschein")
        leer = not eingabe.get("betrag")
        linien = sum(1 for o in ops if o["t"] == "linie")
        if leer and linien < 2 + 8 * 4:
            fehler.append("Beispiel ohne Betrag und Zahler: Eckmarken fehlen")

    for (aenderung, erwartet), meldungen in zip(REGELN, aus["regeln"]):
        if not any(erwartet in m for m in meldungen):
            fehler.append("Regel %s: erwartet «%s», erhalten %s" % (json.dumps(aenderung, ensure_ascii=False)[:60], erwartet, meldungen))
    if aus["qrr"] != "210000000003139471430009017":
        fehler.append("QR-Referenz: %s" % aus["qrr"])
    if aus["scor"] != "RF18539007547034":
        fehler.append("Creditor Reference: %s" % aus["scor"])
    if aus["typo"] != "A - \"B\" 'C'":
        fehler.append("Typografische Zeichen nicht ersetzt: %r" % aus["typo"])
    if not 0 < aus["lang"] <= 117:
        fehler.append("Langer Inhalt: QR-Code mit %d Modulen" % aus["lang"])

    pdf = bytes(aus["pdf"])
    if not pdf.startswith(b"%PDF-1.4") or b"/MediaBox [0 0 595.276 841.89]" not in pdf or not pdf.rstrip().endswith(b"%%EOF"):
        fehler.append("PDF: Aufbau fehlerhaft")
    try:
        import zxingcpp
        from PIL import Image
        if shutil.which("gs"):
            with tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / "t.pdf").write_bytes(pdf)
                subprocess.run(["gs", "-q", "-sDEVICE=png16m", "-r300", "-o", str(Path(tmp) / "t.png"), str(Path(tmp) / "t.pdf")], check=True)
                gelesen = zxingcpp.read_barcodes(Image.open(Path(tmp) / "t.png"))
            if not gelesen or gelesen[0].text != "\r\n".join(BEISPIELE[1][1]):
                fehler.append("PDF: QR-Code nicht lesbar oder Inhalt falsch")
            else:
                print("PDF: QR-Code gelesen, Inhalt stimmt")
    except ImportError:
        print("Hinweis: zxingcpp nicht installiert, QR-Code im PDF nicht gelesen")

    print("%d Beispiele, %d Regeln geprüft" % (len(BEISPIELE), len(REGELN)))
    if fehler:
        print("\nFEHLER:\n" + "\n".join(fehler))
        sys.exit(1)
    print("Alles in Ordnung.")


if __name__ == "__main__":
    main()

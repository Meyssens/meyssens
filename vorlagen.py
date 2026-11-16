#!/usr/bin/env python3
"""Erzeugt die Gratis-Vorlagen zum Herunterladen. Aufruf im Projektordner: python3 vorlagen.py

- downloads/regierapport-vorlage.pdf    Regierapport A4 zum Ausdrucken (Ratgeber /ratgeber/regierapport-vorlage/)
- downloads/regierapport-vorlage.xlsx   dasselbe als Excel mit Formeln (Stunden x Ansatz, Summen, MWST 8,1 %)
- downloads/checkliste-steuerunterlagen.pdf   Mandanten-Checkliste, 2 Seiten (Ratgeber /ratgeber/steuerunterlagen-einsammeln/)
- downloads/checkliste-steuerunterlagen.docx  dieselbe Checkliste als Word-Datei, mit Platz für Logo und Kontaktangaben
- assets/vorlagen/<name>-vorschau.png  Vorschaubild der ersten PDF-Seite (420 x 594) für die Ratgeber (braucht Ghostscript)

Werkzeug für die Entwicklung, nicht für build.py: braucht Playwright mit Chromium, openpyxl und python-docx.
Nach Änderungen an den Texten neu ausführen. Alle Vorlagen enthalten keine Personendaten.
"""
import html
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ZIEL = ROOT / "downloads"
SCHRIFTEN = (ROOT / "assets" / "schriften").as_uri()
LOGO = (ROOT / "logo-web.png").as_uri()
MWST = 0.081

STIL = """
@font-face{font-family:'Inter';font-weight:800;src:url(%s/inter-800-latin.woff2) format('woff2')}
@font-face{font-family:'Inter';font-weight:300 600;src:url(%s/inter-latin.woff2) format('woff2')}
@page{size:A4;margin:12mm 12mm 11mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',Arial,sans-serif;font-size:8.6pt;color:#07071a;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1{font-weight:800;font-size:20pt;letter-spacing:-.03em}
h2{font-size:9.5pt;font-weight:600;margin:3.4mm 0 1.4mm;color:#0000c8;text-transform:uppercase;letter-spacing:.06em}
table{width:100%%;border-collapse:collapse}
td,th{border:0.6pt solid #9a9ab8;padding:1.2mm 1.6mm;vertical-align:top;text-align:left}
th{background:#eeeeff;font-weight:600;font-size:7.6pt}
.l{color:#50507a;font-size:7pt;display:block;margin-bottom:.6mm}
.fuss{position:fixed;bottom:0;left:0;right:0;font-size:6.8pt;color:#6b6b8a;display:flex;justify-content:space-between}
.kasten{display:inline-block;width:3.2mm;height:3.2mm;border:0.8pt solid #07071a;margin-right:1.4mm;vertical-align:-0.6mm}
""" % (SCHRIFTEN, SCHRIFTEN)


def zeilen(n, spalten):
    return "".join("<tr>%s</tr>" % "".join('<td style="height:5.9mm"></td>' for _ in range(spalten)) for _ in range(n))


REGIE = """<!doctype html><html lang="de-CH"><head><meta charset="utf-8"><style>%s
.kopf{display:grid;grid-template-columns:1fr 62mm;gap:5mm;align-items:start}
.logo{border:0.8pt dashed #9a9ab8;height:13mm;display:flex;align-items:center;justify-content:center;color:#6b6b8a;font-size:7.5pt}
.nr td{height:7.5mm}
.zwei{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.summe td{height:5.4mm;padding-top:.8mm;padding-bottom:.8mm}
.summe .w{width:36mm}
.unterschrift td{height:12mm}
.hinweis{font-size:7.2pt;color:#3c3c60;margin-top:1.6mm;line-height:1.4}
.fuss{position:static;margin-top:1.5mm}
</style></head><body>
<div class="kopf">
  <div><div class="logo">Firma / Logo</div><h1 style="margin-top:2.5mm">Regierapport</h1></div>
  <table class="nr"><tr><td><span class="l">Rapport-Nr.</span></td></tr><tr><td><span class="l">Datum / Woche</span></td></tr><tr><td><span class="l">Blatt</span>&nbsp;&nbsp;&nbsp;&nbsp;von</td></tr></table>
</div>
<h2>Auftrag</h2>
<table>
  <tr><td style="width:50%%"><span class="l">Auftraggeber / Bauherrschaft</span><br>&nbsp;</td><td><span class="l">Objekt, Adresse</span><br>&nbsp;</td></tr>
  <tr><td><span class="l">Offerte / Werkvertrag Nr.</span>&nbsp;</td><td><span class="l">Bauleitung</span>&nbsp;</td></tr>
  <tr><td><span class="l">Regiearbeit angeordnet von (Name)</span>&nbsp;</td><td><span class="l">angeordnet am (Datum, Zeit)</span>&nbsp;</td></tr>
  <tr><td colspan="2" style="height:10mm"><span class="l">Was wurde in Regie gemacht und warum? (nicht in der Offerte enthalten, Störung, Zusatzwunsch ...)</span></td></tr>
</table>
<h2>Arbeit</h2>
<table>
  <tr><th style="width:15mm">Datum</th><th style="width:30mm">Name</th><th style="width:22mm">Funktion</th><th>Tätigkeit</th><th style="width:19mm">von - bis</th><th style="width:12mm">Std.</th><th style="width:15mm">Ansatz</th><th style="width:19mm">Betrag CHF</th></tr>
  %s
</table>
<h2>Material</h2>
<table>
  <tr><th style="width:24mm">Art.-Nr.</th><th>Bezeichnung</th><th style="width:15mm">Menge</th><th style="width:13mm">Einheit</th><th style="width:17mm">Preis</th><th style="width:19mm">Betrag CHF</th></tr>
  %s
</table>
<div class="zwei">
  <div>
    <h2>Geräte, Fahrzeuge, Entsorgung</h2>
    <table><tr><th>Bezeichnung</th><th style="width:13mm">Std. / Tage</th><th style="width:15mm">Ansatz</th><th style="width:17mm">Betrag</th></tr>%s</table>
  </div>
  <div>
    <h2>Total</h2>
    <table class="summe">
      <tr><td>Arbeit</td><td class="w"></td></tr><tr><td>Material</td><td class="w"></td></tr><tr><td>Geräte, Fahrzeuge</td><td class="w"></td></tr>
      <tr><td>Zwischentotal</td><td class="w"></td></tr><tr><td>MWST 8,1 %%</td><td class="w"></td></tr><tr><td><strong>Total CHF</strong></td><td class="w"></td></tr>
    </table>
  </div>
</div>
<h2>Bemerkungen, Vorbehalte, Beilagen</h2>
<table><tr><td style="height:11mm"><span class="kasten"></span>Fotos&nbsp;&nbsp;&nbsp;<span class="kasten"></span>Lieferschein&nbsp;&nbsp;&nbsp;<span class="kasten"></span>Mess- und Prüfprotokoll (Elektro)&nbsp;&nbsp;&nbsp;<span class="kasten"></span>Sicherheitsnachweis nötig</td></tr></table>
<h2>Unterschriften</h2>
<table class="unterschrift"><tr>
  <td style="width:50%%"><span class="l">Unternehmer: Name, Datum, Unterschrift</span></td>
  <td><span class="l">Auftraggeber oder Bauleitung: Name, Datum, Unterschrift</span></td>
</tr></table>
<p class="hinweis">Mit der Unterschrift bestätigt die Gegenseite die rapportierte Arbeit und das Material. Einwände bitte unter «Bemerkungen, Vorbehalte» festhalten. Ansätze gemäss Offerte oder Werkvertrag. Rapport zeitnah, am besten am selben Tag, zur Unterschrift vorlegen und Kopie abgeben.</p>
<div class="fuss"><span>Vorlage: meyssens.ch/ratgeber/regierapport-vorlage, frei verwendbar und anpassbar. Ohne Gewähr, keine Rechtsberatung.</span><span>Stand 16.11.2026</span></div>
</body></html>"""

PUNKTE = [
    ("Allgemein", [
        "Veranlagungsverfügung und Steuererklärung des Vorjahres (falls neu bei uns)",
        "Änderungen im Jahr 2026: Heirat, Trennung, Geburt, Umzug, Stellenwechsel, Pensionierung",
        "Kinder in Ausbildung: Ausbildungsbestätigung",
        "Zugangsdaten oder Code für die Steuererklärung, falls bereits erhalten",
    ]),
    ("Einkommen", [
        "Lohnausweis(e) aller Arbeitgeber",
        "Bescheinigungen über Taggelder (Arbeitslosen-, Kranken-, Unfallversicherung, EO)",
        "Rentenbescheinigungen (AHV, IV, Pensionskasse, Lebensversicherung)",
        "Kapitalauszahlungen aus Pensionskasse oder Säule 3a",
        "Nebenerwerb, Honorare, Verwaltungsratsentschädigungen",
        "Erhaltene Unterhaltsbeiträge (Alimente)",
        "Selbständige: Jahresrechnung (Bilanz, Erfolgsrechnung), AHV-Abrechnung",
    ]),
    ("Vermögen per 31. Dezember", [
        "Steuerauszug oder eSteuerauszug aller Banken (Konten, Wertschriften, Depots)",
        "Kryptowährungen: Bestand und Börse per 31. Dezember",
        "Lebens- und Rentenversicherungen: Rückkaufswert",
        "Erbschaften, Schenkungen, gewährte oder erhaltene Darlehen",
        "Schulden: Saldo und Zinsen (Hypotheken, Kredite, Leasing)",
    ]),
    ("Abzüge", [
        "Bescheinigung Säule 3a",
        "Einkäufe in die Pensionskasse (Bestätigung)",
        "Krankenkassen: Prämienbescheinigung, Prämienverbilligung",
        "Krankheits- und Zahnarztkosten, die Sie selbst bezahlt haben, mit Rückerstattungen",
        "Kosten für die Betreuung von Kindern durch Dritte",
        "Weiterbildungskosten, die nicht der Arbeitgeber bezahlt hat",
        "Spendenbestätigungen",
        "Bezahlte Unterhaltsbeiträge (Alimente) mit Beleg",
        "Arbeitsweg und auswärtige Verpflegung: Angaben, falls nicht im Lohnausweis",
    ]),
    ("Liegenschaften", [
        "Hypothekarzinsbescheinigung und Saldo per 31. Dezember",
        "Rechnungen für Unterhalt und Energiesparmassnahmen",
        "Vermietete Objekte: Mieteinnahmen und Nebenkostenabrechnung",
        "Kauf oder Verkauf im Jahr 2026: Kaufvertrag, Abrechnung",
    ]),
]

CHECKLISTE = """<!doctype html><html lang="de-CH"><head><meta charset="utf-8"><style>%s
.kopf{display:grid;grid-template-columns:1fr 70mm;gap:6mm;align-items:start;margin-bottom:3mm}
.logo{border:0.8pt dashed #9a9ab8;height:22mm;display:flex;align-items:center;justify-content:center;color:#6b6b8a;font-size:7.5pt;text-align:center;padding:2mm}
.einleitung{font-size:9pt;line-height:1.5;margin:2mm 0 1mm;color:#3c3c60}
ul{list-style:none}
li{display:grid;grid-template-columns:5mm 1fr 18mm;gap:1mm;padding:.85mm 0;border-bottom:0.5pt solid #d9d9e6;font-size:8.5pt;line-height:1.3}
li .k{width:3.4mm;height:3.4mm;border:0.8pt solid #07071a;margin-top:.4mm}
li .n{font-size:6.8pt;color:#6b6b8a;text-align:right}
.abschnitt{break-inside:avoid}
.seite2{break-before:page}
.felder td{height:9mm}
</style></head><body>
<div class="kopf">
  <div><h1>Unterlagen für Ihre Steuererklärung 2026</h1>
  <p class="einleitung">Bitte kreuzen Sie an, was Sie beilegen. Was für Sie nicht zutrifft, lassen Sie leer. Fehlt etwas, melden wir uns. Belege für das Jahr 2026, Vermögen und Schulden per 31. Dezember 2026.</p></div>
  <div class="logo">Logo und Kontakt Ihres Treuhandbüros</div>
</div>
<table class="felder"><tr><td style="width:50%%"><span class="l">Name, Vorname</span></td><td><span class="l">Bitte einreichen bis</span></td></tr></table>
%s
<div class="seite2">
<h2>So übermitteln Sie die Unterlagen</h2>
<table class="felder">
  <tr><td><span class="kasten"></span>Hochladen über den Link, den Sie von uns erhalten haben</td></tr>
  <tr><td><span class="kasten"></span>Per Post oder persönlich an die Adresse oben</td></tr>
  <tr><td><span class="kasten"></span>Anderer Weg nach Absprache: </td></tr>
</table>
<p class="einleitung">Bitte senden Sie Ausweise, Steuerauszüge und Kontodaten nicht als gewöhnliche E-Mail-Beilage, sondern über den vereinbarten Weg. eSteuerauszüge Ihrer Bank bitte als PDF-Datei weitergeben, nicht ausgedruckt: Der Strichcode lässt sich nach dem Ausdrucken nicht mehr auslesen.</p>
<h2>Fragen an Sie</h2>
<table class="felder">
  <tr><td><span class="l">Gab es 2026 grössere Ausgaben oder Einnahmen, die wir kennen sollten?</span></td></tr>
  <tr><td><span class="l">Möchten Sie eine Fristerstreckung? Bis wann sind Sie erreichbar?</span></td></tr>
  <tr><td style="height:24mm"><span class="l">Bemerkungen</span></td></tr>
</table>
<h2>Bestätigung</h2>
<table class="felder"><tr><td style="height:16mm;width:50%%"><span class="l">Ort, Datum</span></td><td><span class="l">Unterschrift</span></td></tr></table>
</div>
<div class="fuss"><span>Vorlage: meyssens.ch/ratgeber/steuerunterlagen-einsammeln, frei verwendbar und anpassbar. Massgebend sind die Wegleitung und die Formulare Ihres Kantons.</span><span>Stand 16.11.2026</span></div>
</body></html>"""


def checkliste_html():
    teile = []
    for titel, punkte in PUNKTE:
        teile.append('<div class="abschnitt"><h2>%s</h2><ul>%s</ul></div>' % (html.escape(titel), "".join(
            '<li><span class="k"></span><span>%s</span><span class="n">liegt bei</span></li>' % html.escape(p) for p in punkte)))
    return CHECKLISTE % (STIL, "\n".join(teile))


def pdf(seite, inhalt, ziel):
    with tempfile.TemporaryDirectory() as tmp:
        datei = Path(tmp) / "vorlage.html"
        datei.write_text(inhalt, encoding="utf-8")
        seite.goto(datei.as_uri())
        seite.evaluate("document.fonts.ready")
        seite.pdf(path=str(ziel), format="A4", print_background=True, prefer_css_page_size=True)
    print("geschrieben:", ziel.relative_to(ROOT))


def regie_excel(ziel):
    wb = Workbook()
    ws = wb.active
    ws.title = "Regierapport"
    duenn = Side(style="thin", color="9A9AB8")
    rahmen = Border(left=duenn, right=duenn, top=duenn, bottom=duenn)
    kopf = PatternFill("solid", fgColor="EEEEFF")
    fett = Font(name="Arial", bold=True, size=10)
    normal = Font(name="Arial", size=10)
    breiten = {"A": 12, "B": 22, "C": 16, "D": 38, "E": 13, "F": 9, "G": 11, "H": 14}
    for s, b in breiten.items():
        ws.column_dimensions[s].width = b

    def zelle(ref, wert=None, f=normal, fuellung=None, form=None):
        c = ws[ref]
        if wert is not None:
            c.value = wert
        c.font = f
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=True)
        if fuellung:
            c.fill = fuellung
        if form:
            c.number_format = form
        return c

    ws["A1"] = "Regierapport"
    ws["A1"].font = Font(name="Arial", bold=True, size=18)
    ws["F1"] = "Rapport-Nr."
    ws["F2"] = "Datum / Woche"
    for r in (1, 2):
        ws["F%d" % r].font = Font(name="Arial", size=8, color="50507A")
        ws.merge_cells("G%d:H%d" % (r, r))
        zelle("G%d" % r)
    felder = [("Auftraggeber / Bauherrschaft", "Objekt, Adresse"), ("Offerte / Werkvertrag Nr.", "Bauleitung"),
              ("Regie angeordnet von", "angeordnet am")]
    r = 4
    for links, rechts in felder:
        zelle("A%d" % r, links, Font(name="Arial", size=8, color="50507A"))
        ws.merge_cells("B%d:D%d" % (r, r))
        zelle("B%d" % r)
        zelle("E%d" % r, rechts, Font(name="Arial", size=8, color="50507A"))
        ws.merge_cells("F%d:H%d" % (r, r))
        zelle("F%d" % r)
        r += 1
    zelle("A%d" % r, "Was und warum in Regie?", Font(name="Arial", size=8, color="50507A"))
    ws.merge_cells("B%d:H%d" % (r, r))
    zelle("B%d" % r)
    ws.row_dimensions[r].height = 30

    r += 2
    ws["A%d" % r] = "Arbeit"
    ws["A%d" % r].font = fett
    r += 1
    for i, t in enumerate(["Datum", "Name", "Funktion", "Tätigkeit", "von - bis", "Std.", "Ansatz", "Betrag CHF"]):
        zelle("%s%d" % ("ABCDEFGH"[i], r), t, fett, kopf)
    funktion = DataValidation(type="list", formula1='"Chefmonteur/in,Monteur/in,Hilfsmonteur/in,Lernende/r,Projektleiter/in"',
                              allow_blank=True)
    ws.add_data_validation(funktion)
    arbeit_von = r + 1
    for _ in range(10):
        r += 1
        zelle("A%d" % r, form="DD.MM.YYYY")
        for s in "BCDE":
            zelle("%s%d" % (s, r))
        funktion.add("C%d" % r)
        zelle("F%d" % r, form="0.00")
        zelle("G%d" % r, form="#,##0.00")
        zelle("H%d" % r, '=IF(F{0}="","",F{0}*G{0})'.format(r), form="#,##0.00")
    arbeit_bis = r

    r += 2
    ws["A%d" % r] = "Material"
    ws["A%d" % r].font = fett
    r += 1
    for s, t in zip("ABCDEFGH", ["Art.-Nr.", "Bezeichnung", "", "", "Menge", "Einheit", "Preis", "Betrag CHF"]):
        zelle("%s%d" % (s, r), t, fett, kopf)
    ws.merge_cells("B%d:D%d" % (r, r))
    material_von = r + 1
    for _ in range(8):
        r += 1
        zelle("A%d" % r)
        ws.merge_cells("B%d:D%d" % (r, r))
        zelle("B%d" % r)
        zelle("E%d" % r, form="0.00")
        zelle("F%d" % r)
        zelle("G%d" % r, form="#,##0.00")
        zelle("H%d" % r, '=IF(E{0}="","",E{0}*G{0})'.format(r), form="#,##0.00")
    material_bis = r

    r += 2
    ws["A%d" % r] = "Geräte, Fahrzeuge, Entsorgung"
    ws["A%d" % r].font = fett
    r += 1
    for s, t in zip("ABCDEFGH", ["Bezeichnung", "", "", "", "Std. / Tage", "", "Ansatz", "Betrag CHF"]):
        zelle("%s%d" % (s, r), t, fett, kopf)
    ws.merge_cells("A%d:D%d" % (r, r))
    ws.merge_cells("E%d:F%d" % (r, r))
    geraet_von = r + 1
    for _ in range(3):
        r += 1
        ws.merge_cells("A%d:D%d" % (r, r))
        zelle("A%d" % r)
        ws.merge_cells("E%d:F%d" % (r, r))
        zelle("E%d" % r, form="0.00")
        zelle("G%d" % r, form="#,##0.00")
        zelle("H%d" % r, '=IF(E{0}="","",E{0}*G{0})'.format(r), form="#,##0.00")
    geraet_bis = r

    r += 2
    summen = [("Arbeit", "=SUM(H%d:H%d)" % (arbeit_von, arbeit_bis)), ("Material", "=SUM(H%d:H%d)" % (material_von, material_bis)),
              ("Geräte, Fahrzeuge", "=SUM(H%d:H%d)" % (geraet_von, geraet_bis))]
    erste = r
    for t, f in summen:
        zelle("G%d" % r, t)
        zelle("H%d" % r, f, form="#,##0.00")
        r += 1
    zelle("G%d" % r, "Zwischentotal", fett)
    zelle("H%d" % r, "=SUM(H%d:H%d)" % (erste, r - 1), fett, form="#,##0.00")
    zw = r
    r += 1
    zelle("F%d" % r, "MWST-Satz")
    zelle("E%d" % r, MWST, form="0.0%")
    zelle("G%d" % r, "MWST")
    zelle("H%d" % r, "=ROUND(H%d*E%d,2)" % (zw, r), form="#,##0.00")
    r += 1
    zelle("G%d" % r, "Total CHF", fett)
    zelle("H%d" % r, "=H%d+H%d" % (zw, r - 1), fett, form="#,##0.00")

    r += 2
    ws["A%d" % r] = "Bemerkungen, Vorbehalte, Beilagen (Fotos, Lieferschein, Mess- und Prüfprotokoll)"
    ws["A%d" % r].font = fett
    r += 1
    ws.merge_cells("A%d:H%d" % (r, r))
    zelle("A%d" % r)
    ws.row_dimensions[r].height = 42
    r += 2
    ws.merge_cells("A%d:D%d" % (r, r))
    zelle("A%d" % r, "Unternehmer: Name, Datum, Unterschrift", Font(name="Arial", size=8, color="50507A"))
    ws.merge_cells("E%d:H%d" % (r, r))
    zelle("E%d" % r, "Auftraggeber oder Bauleitung: Name, Datum, Unterschrift", Font(name="Arial", size=8, color="50507A"))
    ws.row_dimensions[r].height = 48
    r += 2
    ws["A%d" % r] = ("Vorlage: meyssens.ch/ratgeber/regierapport-vorlage, frei verwendbar. "
                     "Ansätze gemäss Offerte oder Werkvertrag. Ohne Gewähr, keine Rechtsberatung.")
    ws["A%d" % r].font = Font(name="Arial", size=8, color="6B6B8A")

    ws.print_area = "A1:H%d" % r
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    wb.properties.creator = "Meyssens"
    wb.properties.title = "Regierapport-Vorlage"
    wb.save(ziel)
    print("geschrieben:", ziel.relative_to(ROOT))


def checkliste_word(ziel):
    from docx import Document
    from docx.shared import Pt, Mm

    d = Document()
    for s in d.sections:
        s.page_height, s.page_width = Mm(297), Mm(210)
        s.left_margin = s.right_margin = Mm(18)
        s.top_margin = s.bottom_margin = Mm(16)
    stil = d.styles["Normal"]
    stil.font.name = "Arial"
    stil.font.size = Pt(10)
    kopf = d.add_table(rows=1, cols=2)
    kopf.cell(0, 0).text = "Unterlagen für Ihre Steuererklärung 2026"
    kopf.cell(0, 0).paragraphs[0].runs[0].font.size = Pt(16)
    kopf.cell(0, 0).paragraphs[0].runs[0].bold = True
    kopf.cell(0, 1).text = "[Logo und Kontakt Ihres Treuhandbüros]"
    d.add_paragraph("Bitte kreuzen Sie an, was Sie beilegen. Was für Sie nicht zutrifft, lassen Sie leer. Belege für das Jahr "
                    "2026, Vermögen und Schulden per 31. Dezember 2026.")
    d.add_paragraph("Name, Vorname: ______________________    Bitte einreichen bis: ____________")
    for titel, punkte in PUNKTE:
        d.add_heading(titel, level=2)
        for p in punkte:
            d.add_paragraph("☐  " + p)
    d.add_heading("So übermitteln Sie die Unterlagen", level=2)
    for p in ("Hochladen über den Link, den Sie von uns erhalten haben", "Per Post oder persönlich an die Adresse oben",
              "Anderer Weg nach Absprache: ____________________"):
        d.add_paragraph("☐  " + p)
    d.add_paragraph("Bitte senden Sie Ausweise, Steuerauszüge und Kontodaten nicht als gewöhnliche E-Mail-Beilage. "
                    "eSteuerauszüge bitte als PDF-Datei weitergeben, nicht ausgedruckt.")
    d.add_heading("Bemerkungen", level=2)
    d.add_paragraph("\n\n")
    d.add_paragraph("Ort, Datum: ____________________    Unterschrift: ____________________")
    fuss = d.sections[0].footer.paragraphs[0]
    fuss.text = ("Vorlage: meyssens.ch/ratgeber/steuerunterlagen-einsammeln, frei verwendbar und anpassbar. "
                 "Massgebend sind die Wegleitung und die Formulare Ihres Kantons.")
    fuss.runs[0].font.size = Pt(7)
    d.core_properties.author = "Meyssens"
    d.core_properties.title = "Checkliste Steuerunterlagen"
    d.save(ziel)
    print("geschrieben:", ziel.relative_to(ROOT))


def vorschau(quelle, ziel):
    # Erste Seite als PNG, 420 x 594 Pixel, mit feinem Rand
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        roh = Path(tmp) / "seite.png"
        subprocess.run(["gs", "-q", "-sDEVICE=png16m", "-r150", "-dFirstPage=1", "-dLastPage=1", "-o", str(roh), str(quelle)], check=True)
        bild = Image.open(roh).convert("RGB").resize((418, 592), Image.LANCZOS)
    rahmen = Image.new("RGB", (420, 594), (217, 217, 230))
    rahmen.paste(bild, (1, 1))
    rahmen.quantize(colors=96, dither=Image.Dither.NONE).save(ziel, optimize=True)
    print("geschrieben:", ziel.relative_to(ROOT))


def main():
    ZIEL.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        seite = b.new_page()
        pdf(seite, REGIE % (STIL, zeilen(7, 8), zeilen(4, 6), zeilen(2, 4)), ZIEL / "regierapport-vorlage.pdf")
        pdf(seite, checkliste_html(), ZIEL / "checkliste-steuerunterlagen.pdf")
        b.close()
    for name in ("regierapport-vorlage", "checkliste-steuerunterlagen"):
        vorschau(ZIEL / ("%s.pdf" % name), ROOT / "assets" / "vorlagen" / ("%s-vorschau.png" % name))
    regie_excel(ZIEL / "regierapport-vorlage.xlsx")
    checkliste_word(ZIEL / "checkliste-steuerunterlagen.docx")


if __name__ == "__main__":
    main()

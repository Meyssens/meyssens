#!/usr/bin/env python3
"""Erzeugt die Screenshots der Beispielplattform https://demo.meyssens.ch neu.

Aufruf im Projektordner:  python3 demo_screenshots.py
Danach:                   python3 build.py && python3 test_seiten.py

Braucht Playwright mit Chromium (pip install playwright, playwright install chromium) und Pillow.
Schreibt nach assets/beispiel/:
  demo-desktop.webp (1800 px), demo-desktop-960.webp   Startseite der Demo am Computer (1440 x 900, scharf mit 2x)
  demo-handy.webp (780 px)                             Karten-Umfrage auf der Demo-Startseite am Handy (390 x 844, 3x)

Hinweise:
- Das Cookie-Fenster der Demo wird per Skript geschlossen («Alle akzeptieren»), es erscheint nicht im Bild.
- Die Karte lädt im Browser des Skripts hochauflösende OpenStreetMap-Kacheln (detectRetina), damit sie scharf ist.
  Auf der Demo selbst ändert sich nichts. Die Kartennachweise von Leaflet bleiben im Bild sichtbar.
- Steht auf der Startseite der Demo «DSGVO-konform», wird das Desktop-Bild oberhalb dieser Zeile abgeschnitten
  (auf meyssens.ch heisst es «Datenschutz nach DSGVO-Anforderungen»).
- Bricht mit einer Meldung ab, wenn die Schrift Inter nicht geladen ist oder Kartenkacheln fehlen, damit kein
  halb geladenes Bild in die Website gelangt.
"""
import asyncio
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

DEMO = "https://demo.meyssens.ch/"
ZIEL = Path(__file__).resolve().parent / "assets" / "beispiel"

# Leaflet vor dem Laden der Karte auf hochauflösende Kacheln umstellen (nur in diesem Browser)
RETINA = """(() => {
  let v; const fix = L => { try { L.TileLayer.prototype.options.detectRetina = true; window.__retina = 1 } catch (e) {} };
  Object.defineProperty(window, 'L', {configurable: true, get() { return v }, set(x) { v = x; fix(x) }});
  const t = setInterval(() => { if (window.L && !window.__retina) fix(window.L) }, 1); setTimeout(() => clearInterval(t), 20000);
})()"""
KACHELN_FERTIG = "sel => [...document.querySelectorAll(sel + ' .leaflet-tile')].every(i => i.complete && i.naturalWidth)"


def speichere(bild, name, breite, qualitaet):
    bild = bild.convert("RGB")
    if bild.width != breite:
        bild = bild.resize((breite, round(bild.height * breite / bild.width)), Image.LANCZOS)
    pfad = ZIEL / name
    bild.save(pfad, "WEBP", quality=qualitaet, method=6)
    print("geschrieben: %s (%d x %d, %d KB)" % (pfad.relative_to(ZIEL.parent.parent), bild.width, bild.height,
                                                pfad.stat().st_size // 1024))


async def seite(browser, **kontext):
    # Lädt die Startseite der Demo; bis zu vier Versuche, falls CSS oder die Schrift Inter (noch) nicht geladen sind
    for versuch in range(1, 5):
        k = await browser.new_context(locale="de-DE", **kontext)
        await k.add_init_script(RETINA)
        s = await k.new_page()
        await s.goto(DEMO, wait_until="load", timeout=90000)
        await s.wait_for_timeout(1200)
        await s.evaluate("document.querySelector('#dc-dialog-accept')?.click()")
        await s.wait_for_timeout(800)
        schriften = await s.evaluate("document.fonts.ready.then(() => [...document.fonts].filter(f => f.status == 'loaded')"
                                     ".map(f => f.family).join(','))")
        if "Inter" in schriften:
            return k, s
        print("Versuch %d: Schrift Inter nicht geladen (geladen: %s), neuer Versuch ..." % (versuch, schriften or "keine"))
        await k.close()
        await asyncio.sleep(10)
    raise SystemExit("Abbruch: Schrift Inter auf der Demo nicht geladen. Bitte später nochmals versuchen.")


async def karte_bereit(s, sel):
    await s.locator(sel).scroll_into_view_if_needed()
    await s.wait_for_function(KACHELN_FERTIG, arg=sel, timeout=45000)
    await s.wait_for_timeout(1200)


async def main():
    ZIEL.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # 1. Desktop: Startseite oben, 1440 x 900, doppelte Auflösung
        k, s = await seite(browser, viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        await s.evaluate("scrollTo(0, 0)")
        await s.wait_for_timeout(600)
        hoehe = await s.evaluate("""() => {
          const el = [...document.querySelectorAll('body *')].find(e => e.children.length < 4 && /DSGVO-konform/.test(e.textContent)
                       && e.getBoundingClientRect().top < innerHeight);
          return el ? Math.floor(el.getBoundingClientRect().top - 28) : innerHeight }""")
        bild = Image.open(BytesIO(await s.screenshot(clip={"x": 0, "y": 0, "width": 1440, "height": min(900, hoehe)})))
        if hoehe < 900:
            print("Hinweis: Desktop-Bild oberhalb von «DSGVO-konform» abgeschnitten (Höhe %d px)" % hoehe)
        speichere(bild, "demo-desktop.webp", 1800, 74)
        speichere(bild, "demo-desktop-960.webp", 960, 78)

        await k.close()

        # 2. Handy: Abschnitt Karten-Umfrage der Startseite, 390 x 844, dreifache Auflösung
        k, s = await seite(browser, viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
        abschnitt = await s.evaluate("""() => { const m = document.querySelector('#md-map') || document.querySelector('.leaflet-container');
          if (!m) return null; const sec = m.closest('section') || m; return Math.max(0, sec.getBoundingClientRect().top + scrollY) }""")
        if abschnitt is None:
            raise SystemExit("Abbruch: keine Karte auf der Demo-Startseite gefunden")
        sel = "#md-map" if await s.locator("#md-map").count() else ".leaflet-container"
        await karte_bereit(s, sel)
        # Erst etwas oberhalb, dann nach unten zum Abschnitt scrollen: Der Kopf der Demo blendet sich beim
        # Hochscrollen ein und würde sonst den Titel verdecken
        await s.evaluate("y => scrollTo(0, Math.max(0, y - 400))", abschnitt)
        await s.wait_for_timeout(500)
        await s.evaluate("y => scrollTo(0, y)", abschnitt)
        await s.wait_for_timeout(900)
        await s.wait_for_function(KACHELN_FERTIG, arg=sel, timeout=45000)
        bild = Image.open(BytesIO(await s.screenshot()))
        speichere(bild, "demo-handy.webp", 780, 76)
        await k.close()
        await browser.close()
    print("Fertig. Jetzt python3 build.py und python3 test_seiten.py ausführen.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)
